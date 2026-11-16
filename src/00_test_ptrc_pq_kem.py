# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Post-Quantum Ring-KEM v4.2
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program (see the LICENSE file in the root directory).
# If not, see <https://gnu.org>.
# ==============================================================================

r"""
Verification, Hybrid AEAD Coupling & Throughput Audit for pTRC Ring-KEM v4.2:
  1. Asymmetric Keygen -> Encaps -> Decaps in Z_{7681} \ {0} + 1-Bit Tamper Rejection
  2. 100% C11 <-> Python Bit-Parity & Volatile -1 (0xFF) SRAM Scrubbing
  3. End-to-End Hybrid Handshake -> 512-Bit Symmetrical AEAD Encryption
  4. Static Zero-Float & Zero-Trig Compliance + Bare-Metal C11 Handshake Speed
File: src/00_test_ptrc_pq_kem.py
"""

from __future__ import annotations

import ctypes
import pathlib
import re
import sys
import time

from ptrc_pq_kem import (
    PTRC_KEM_CT_BYTES,
    PTRC_KEM_OK,
    PTRC_KEM_PK_BYTES,
    PTRC_KEM_SEED_BYTES,
    PTRC_KEM_SK_BYTES,
    PTRC_KEM_SS_BYTES,
    load_c_kem_library,
    ptrc_kem_decaps_py,
    ptrc_kem_encaps_py,
    ptrc_kem_keygen_py,
)


def test_python_kem_handshake_and_tamper() -> tuple[bytes, bytes, bytes, bytes]:
    seed = bytes((11 + (i * 7) % 239) for i in range(PTRC_KEM_SEED_BYTES))
    coins = bytes((29 + (i * 13) % 223) for i in range(PTRC_KEM_SEED_BYTES))

    pk, sk = ptrc_kem_keygen_py(seed)
    assert len(pk) == PTRC_KEM_PK_BYTES
    assert len(sk) == PTRC_KEM_SK_BYTES
    assert 0 not in pk[:PTRC_KEM_SEED_BYTES]

    ct, ss_bob = ptrc_kem_encaps_py(pk, coins)
    assert len(ct) == PTRC_KEM_CT_BYTES
    assert len(ss_bob) == PTRC_KEM_SS_BYTES
    assert 0 not in ss_bob, "Shared secret violated Z \\ {0} invariant!"

    ss_alice = ptrc_kem_decaps_py(ct, sk)
    assert ss_alice == ss_bob, "Asymmetric KEM decapsulation mismatch!"

    # 1-bit tamper in ciphertext must fail to recover the shared secret
    tampered = bytearray(ct)
    tampered[48] ^= 0x01
    ss_tampered = ptrc_kem_decaps_py(bytes(tampered), sk)
    assert ss_tampered != ss_bob, "1-bit ciphertext tamper was not rejected!"

    print("[PASS] 1. Asymmetric Z_{7681} \\ {0} Ring-KEM Handshake & 1-Bit Tamper Rejection")
    return pk, sk, ct, ss_alice


def test_c_python_kem_parity(
    py_pk: bytes,
    py_sk: bytes,
    py_ct: bytes,
    py_ss: bytes,
) -> None:
    lib = load_c_kem_library()
    if lib is None:
        print("[SKIP] 2. C11 shared library libptrc_pq_kem not built yet.")
        return

    seed = bytes((11 + (i * 7) % 239) for i in range(PTRC_KEM_SEED_BYTES))
    coins = bytes((29 + (i * 13) % 223) for i in range(PTRC_KEM_SEED_BYTES))

    c_seed = (ctypes.c_uint8 * PTRC_KEM_SEED_BYTES)(*seed)
    c_coins = (ctypes.c_uint8 * PTRC_KEM_SEED_BYTES)(*coins)
    c_pk = (ctypes.c_uint8 * PTRC_KEM_PK_BYTES)()
    c_sk = (ctypes.c_uint8 * PTRC_KEM_SK_BYTES)()
    c_ct = (ctypes.c_uint8 * PTRC_KEM_CT_BYTES)()
    c_ss_bob = (ctypes.c_uint8 * PTRC_KEM_SS_BYTES)()
    c_ss_alice = (ctypes.c_uint8 * PTRC_KEM_SS_BYTES)()

    assert lib.ptrc_kem_keygen(c_pk, c_sk, c_seed) == PTRC_KEM_OK
    assert bytes(c_pk) == py_pk, "C11 <-> Python Public Key mismatch!"
    assert bytes(c_sk) == py_sk, "C11 <-> Python Secret Key mismatch!"

    assert lib.ptrc_kem_encaps(c_ct, c_ss_bob, c_pk, c_coins) == PTRC_KEM_OK
    assert bytes(c_ct) == py_ct, "C11 <-> Python Ciphertext mismatch!"
    assert bytes(c_ss_bob) == py_ss, "C11 <-> Python Encaps Shared Secret mismatch!"

    assert lib.ptrc_kem_decaps(c_ss_alice, c_ct, c_sk) == PTRC_KEM_OK
    assert bytes(c_ss_alice) == py_ss, "C11 <-> Python Decaps Shared Secret mismatch!"

    # Verify volatile SRAM wipe restores secret buffers to -1 (0xFF)
    lib.ptrc_kem_wipe(c_sk, PTRC_KEM_SK_BYTES)
    assert all(b == 0xFF for b in bytes(c_sk)), "KEM SRAM wipe did not restore all bytes to -1 (0xFF)!"
    print("[PASS] 2. 100% C11 / Python Bit-Parity (PK, SK, CT, 512-Bit SS) & -1 SRAM Wipe")


def test_hybrid_aead_coupling(shared_secret_512: bytes) -> None:
    try:
        from ptrc_crystal_aead import ptrc_aead_decrypt, ptrc_aead_encrypt
    except ImportError:
        print("[SKIP] 3. ptrc_crystal_aead not found in PYTHONPATH.")
        return

    nonce = bytes((71 + (i * 5) % 181) for i in range(16))
    aad = b"pTRC-HYBRID-KEM-v4.2-HEADER"
    pt = b"Post-Quantum Asymmetric Handshake + 512-Bit Symmetrical AEAD in Z \\ {0}!"

    ct, tag = ptrc_aead_encrypt(shared_secret_512, nonce, pt, aad)
    res = ptrc_aead_decrypt(shared_secret_512, nonce, ct, tag, aad)
    if isinstance(res, tuple):
        ok_flag, recovered = res
        assert ok_flag == 1 and recovered == pt, f"Hybrid AEAD decryption failed: {ok_flag}"
    else:
        assert res == pt, "Hybrid AEAD decryption failed!"
    print("[PASS] 3. End-to-End Hybrid Coupling (512-Bit KEM Secret -> 672B Symmetrical AEAD)")


def test_zero_float_compliance() -> None:
    root = pathlib.Path(__file__).resolve().parent.parent
    files = [
        root / "embedded" / "crypto" / "ptrc_pq_kem.h",
        root / "embedded" / "crypto" / "ptrc_pq_kem.c",
        root / "src" / "ptrc_pq_kem.py",
    ]
    forbidden = re.compile(r"\b(float|double|sin|cos|tan|sqrt|pow|log|exp|math)\b")
    for fpath in files:
        if not fpath.exists():
            continue
        raw = fpath.read_text(encoding="utf-8")
        cleaned = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
        cleaned = re.sub(r'r?""".*?"""', "", cleaned, flags=re.S)
        cleaned = re.sub(r"r?'''.*?'''", "", cleaned, flags=re.S)
        cleaned = re.sub(r"//.*", "", cleaned)
        cleaned = re.sub(r"#.*", "", cleaned)
        for lineno, line in enumerate(cleaned.splitlines(), 1):
            match = forbidden.search(line)
            assert match is None, f"Forbidden float/trig token '{match.group(0)}' in {fpath}:{lineno}"
    print("[PASS] 4. Static Zero-Float & Zero-Trig Compliance Verified across Post-Quantum KEM")


def benchmark_c11_kem() -> None:
    lib = load_c_kem_library()
    if lib is None:
        return

    seed = bytes((11 + (i * 7) % 239) for i in range(PTRC_KEM_SEED_BYTES))
    coins = bytes((29 + (i * 13) % 223) for i in range(PTRC_KEM_SEED_BYTES))
    c_seed = (ctypes.c_uint8 * PTRC_KEM_SEED_BYTES)(*seed)
    c_coins = (ctypes.c_uint8 * PTRC_KEM_SEED_BYTES)(*coins)
    c_pk = (ctypes.c_uint8 * PTRC_KEM_PK_BYTES)()
    c_sk = (ctypes.c_uint8 * PTRC_KEM_SK_BYTES)()
    c_ct = (ctypes.c_uint8 * PTRC_KEM_CT_BYTES)()
    c_ss = (ctypes.c_uint8 * PTRC_KEM_SS_BYTES)()

    iters = 200
    t0 = time.perf_counter_ns()
    for _ in range(iters):
        lib.ptrc_kem_keygen(c_pk, c_sk, c_seed)
    t1 = time.perf_counter_ns()
    for _ in range(iters):
        lib.ptrc_kem_encaps(c_ct, c_ss, c_pk, c_coins)
    t2 = time.perf_counter_ns()
    for _ in range(iters):
        lib.ptrc_kem_decaps(c_ss, c_ct, c_sk)
    t3 = time.perf_counter_ns()

    kg_us = ((t1 - t0) // 1000) // iters
    en_us = ((t2 - t1) // 1000) // iters
    de_us = ((t3 - t2) // 1000) // iters
    lib.ptrc_kem_wipe(c_sk, PTRC_KEM_SK_BYTES)

    print("===============================================================================")
    print("  pTRC POST-QUANTUM RING-KEM v4.2 — BARE-METAL C11 HANDSHAKE BENCHMARK")
    print(f"  Modulus  : q = 7681 (Non-Mersenne, gcd(7681, 210) == 1) | Lattice: 2 x 256")
    print(f"  Sizes    : PK = {PTRC_KEM_PK_BYTES} B | SK = {PTRC_KEM_SK_BYTES} B | CT = {PTRC_KEM_CT_BYTES} B | Shared Secret = {PTRC_KEM_SS_BYTES} B")
    print(f"  Speed    : Keygen = {kg_us} us | Encaps = {en_us} us | Decaps = {de_us} us")
    print("===============================================================================")


if __name__ == "__main__":
    pk_b, sk_b, ct_b, ss_b = test_python_kem_handshake_and_tamper()
    test_c_python_kem_parity(pk_b, sk_b, ct_b, ss_b)
    test_hybrid_aead_coupling(ss_b)
    test_zero_float_compliance()
    benchmark_c11_kem()
    sys.exit(0)
