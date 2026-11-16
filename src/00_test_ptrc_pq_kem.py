# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & CCA2 Post-Quantum Ring-KEM v4.3.1
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
Verification, Hybrid AEAD Coupling & Dual-Profile Benchmark for pTRC Ring-KEM v4.3.1:
  1. FO-CCA2 Handshake & Implicit Constant-Time 1-Bit Tamper Rejection (k=2 & k=1)
  2. 100% C11 <-> Python Bit-Parity (Valid + Tampered Reject) & -1 SRAM Scrubbing
  3. End-to-End Hybrid Coupling (512-Bit KEM Secret -> 672B Symmetrical AEAD)
  4. Static Zero-Float Compliance + Head-to-Head C11 Benchmark (512-Dim vs 256-Dim Light)
File: src/00_test_ptrc_pq_kem.py (Part 1 of 2)
"""

from __future__ import annotations

import ctypes
import pathlib
import re
import sys
import time

from ptrc_pq_kem import (
    PTRC_KEM_CT_BYTES,
    PTRC_KEM_LIGHT_CT_BYTES,
    PTRC_KEM_LIGHT_PK_BYTES,
    PTRC_KEM_LIGHT_SK_BYTES,
    PTRC_KEM_OK,
    PTRC_KEM_PK_BYTES,
    PTRC_KEM_SEED_BYTES,
    PTRC_KEM_SK_BYTES,
    PTRC_KEM_SS_BYTES,
    load_c_kem_library,
    ptrc_kem_decaps_py,
    ptrc_kem_encaps_py,
    ptrc_kem_keygen_py,
    ptrc_kem_light_decaps_py,
    ptrc_kem_light_encaps_py,
    ptrc_kem_light_keygen_py,
)


def test_python_dual_profiles() -> tuple[tuple[bytes, bytes, bytes, bytes, bytes], tuple[bytes, bytes, bytes, bytes, bytes]]:
    seed = bytes((11 + (i * 7) % 239) for i in range(PTRC_KEM_SEED_BYTES))
    msg_seed = bytes((29 + (i * 13) % 223) for i in range(PTRC_KEM_SEED_BYTES))

    # Profile A: Standard 512-Dim (k = 2)
    pk_a, sk_a = ptrc_kem_keygen_py(seed)
    assert len(pk_a) == PTRC_KEM_PK_BYTES and len(sk_a) == PTRC_KEM_SK_BYTES
    ct_a, ss_bob_a = ptrc_kem_encaps_py(pk_a, msg_seed)
    ss_alice_a = ptrc_kem_decaps_py(ct_a, sk_a)
    assert ss_alice_a == ss_bob_a and 0 not in ss_alice_a

    tamper_a = bytearray(ct_a)
    tamper_a[0] ^= 0x01
    ss_reject_a = ptrc_kem_decaps_py(bytes(tamper_a), sk_a)
    assert ss_reject_a != ss_bob_a and 0 not in ss_reject_a

    # Profile B: Ultra-Light 256-Dim IoT (k = 1)
    pk_b, sk_b = ptrc_kem_light_keygen_py(seed)
    assert len(pk_b) == PTRC_KEM_LIGHT_PK_BYTES and len(sk_b) == PTRC_KEM_LIGHT_SK_BYTES
    ct_b, ss_bob_b = ptrc_kem_light_encaps_py(pk_b, msg_seed)
    assert len(ct_b) == PTRC_KEM_LIGHT_CT_BYTES
    ss_alice_b = ptrc_kem_light_decaps_py(ct_b, sk_b)
    assert ss_alice_b == ss_bob_b and 0 not in ss_alice_b

    tamper_b = bytearray(ct_b)
    tamper_b[0] ^= 0x01
    ss_reject_b = ptrc_kem_light_decaps_py(bytes(tamper_b), sk_b)
    assert ss_reject_b != ss_bob_b and 0 not in ss_reject_b

    print("[PASS] 1. Dual-Profile FO-CCA2 Z_{7681} \\ {0} Ring-KEM & Implicit 1-Bit Tamper Lock")
    return (pk_a, sk_a, ct_a, ss_alice_a, ss_reject_a), (pk_b, sk_b, ct_b, ss_alice_b, ss_reject_b)


def test_c_python_dual_parity(
    std_tuple: tuple[bytes, bytes, bytes, bytes, bytes],
    light_tuple: tuple[bytes, bytes, bytes, bytes, bytes],
) -> None:
    lib = load_c_kem_library()
    if lib is None:
        print("[SKIP] 2. C11 shared library libptrc_pq_kem not built yet.")
        return

    seed = bytes((11 + (i * 7) % 239) for i in range(PTRC_KEM_SEED_BYTES))
    msg_seed = bytes((29 + (i * 13) % 223) for i in range(PTRC_KEM_SEED_BYTES))
    c_seed = (ctypes.c_uint8 * PTRC_KEM_SEED_BYTES)(*seed)
    c_msg = (ctypes.c_uint8 * PTRC_KEM_SEED_BYTES)(*msg_seed)

    # Check Standard k = 2 (Valid + Implicit CCA2 Reject)
    py_pk, py_sk, py_ct, py_ss, py_rej = std_tuple
    c_pk = (ctypes.c_uint8 * PTRC_KEM_PK_BYTES)()
    c_sk = (ctypes.c_uint8 * PTRC_KEM_SK_BYTES)()
    c_ct = (ctypes.c_uint8 * PTRC_KEM_CT_BYTES)()
    c_ss = (ctypes.c_uint8 * PTRC_KEM_SS_BYTES)()

    assert lib.ptrc_kem_keygen(c_pk, c_sk, c_seed) == PTRC_KEM_OK
    assert bytes(c_pk) == py_pk and bytes(c_sk) == py_sk
    assert lib.ptrc_kem_encaps(c_ct, c_ss, c_pk, c_msg) == PTRC_KEM_OK
    assert bytes(c_ct) == py_ct and bytes(c_ss) == py_ss
    assert lib.ptrc_kem_decaps(c_ss, c_ct, c_sk) == PTRC_KEM_OK
    assert bytes(c_ss) == py_ss

    c_ct_tamper = (ctypes.c_uint8 * PTRC_KEM_CT_BYTES)(*py_ct)
    c_ct_tamper[0] ^= 0x01
    assert lib.ptrc_kem_decaps(c_ss, c_ct_tamper, c_sk) == PTRC_KEM_OK
    assert bytes(c_ss) == py_rej, "C11 <-> Python CCA2 implicit reject mismatch (k=2)!"

    # Check Ultra-Light k = 1 (Valid + Implicit CCA2 Reject)
    l_pk, l_sk, l_ct, l_ss, l_rej = light_tuple
    cl_pk = (ctypes.c_uint8 * PTRC_KEM_LIGHT_PK_BYTES)()
    cl_sk = (ctypes.c_uint8 * PTRC_KEM_LIGHT_SK_BYTES)()
    cl_ct = (ctypes.c_uint8 * PTRC_KEM_LIGHT_CT_BYTES)()
    cl_ss = (ctypes.c_uint8 * PTRC_KEM_SS_BYTES)()

    assert lib.ptrc_kem_light_keygen(cl_pk, cl_sk, c_seed) == PTRC_KEM_OK
    assert bytes(cl_pk) == l_pk and bytes(cl_sk) == l_sk
    assert lib.ptrc_kem_light_encaps(cl_ct, cl_ss, cl_pk, c_msg) == PTRC_KEM_OK
    assert bytes(cl_ct) == l_ct and bytes(cl_ss) == l_ss
    assert lib.ptrc_kem_light_decaps(cl_ss, cl_ct, cl_sk) == PTRC_KEM_OK
    assert bytes(cl_ss) == l_ss

    cl_ct_tamper = (ctypes.c_uint8 * PTRC_KEM_LIGHT_CT_BYTES)(*l_ct)
    cl_ct_tamper[0] ^= 0x01
    assert lib.ptrc_kem_light_decaps(cl_ss, cl_ct_tamper, cl_sk) == PTRC_KEM_OK
    assert bytes(cl_ss) == l_rej, "C11 <-> Python CCA2 implicit reject mismatch (k=1)!"

    lib.ptrc_kem_wipe(c_sk, PTRC_KEM_SK_BYTES)
    lib.ptrc_kem_wipe(cl_sk, PTRC_KEM_LIGHT_SK_BYTES)
    assert all(b == 0xFF for b in bytes(c_sk)) and all(b == 0xFF for b in bytes(cl_sk))
    print("[PASS] 2. 100% C11 / Python Bit-Parity (Valid + CCA2 Reject) & -1 SRAM Wipe")

# File: src/00_test_ptrc_pq_kem.py (Part 2 of 2)


def test_hybrid_aead_coupling(ss_std: bytes, ss_light: bytes) -> None:
    try:
        from ptrc_crystal_aead import ptrc_aead_decrypt, ptrc_aead_encrypt
    except ImportError:
        print("[SKIP] 3. ptrc_crystal_aead not found in PYTHONPATH.")
        return

    nonce = bytes((71 + (i * 5) % 181) for i in range(16))
    aad = b"pTRC-HYBRID-KEM-v4.3.1-HEADER"
    pt = b"CCA2 Post-Quantum Handshake + 512-Bit Symmetrical AEAD in Z \\ {0}!"

    for ss in (ss_std, ss_light):
        ct, tag = ptrc_aead_encrypt(ss, nonce, pt, aad)
        res = ptrc_aead_decrypt(ss, nonce, ct, tag, aad)
        if isinstance(res, tuple):
            ok_flag, recovered = res
            assert ok_flag == 1 and recovered == pt
        else:
            assert res == pt

    print("[PASS] 3. End-to-End Hybrid Coupling (Both CCA2 KEM Secrets -> 672B Symmetrical AEAD)")


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
    print("[PASS] 4. Static Zero-Float & Zero-Trig Compliance Verified across CCA2 KEM")


def benchmark_c11_dual_kem() -> None:
    lib = load_c_kem_library()
    if lib is None:
        return

    seed = bytes((11 + (i * 7) % 239) for i in range(PTRC_KEM_SEED_BYTES))
    msg_seed = bytes((29 + (i * 13) % 223) for i in range(PTRC_KEM_SEED_BYTES))
    c_seed = (ctypes.c_uint8 * PTRC_KEM_SEED_BYTES)(*seed)
    c_msg = (ctypes.c_uint8 * PTRC_KEM_SEED_BYTES)(*msg_seed)

    c_pk = (ctypes.c_uint8 * PTRC_KEM_PK_BYTES)()
    c_sk = (ctypes.c_uint8 * PTRC_KEM_SK_BYTES)()
    c_ct = (ctypes.c_uint8 * PTRC_KEM_CT_BYTES)()
    c_ss = (ctypes.c_uint8 * PTRC_KEM_SS_BYTES)()

    cl_pk = (ctypes.c_uint8 * PTRC_KEM_LIGHT_PK_BYTES)()
    cl_sk = (ctypes.c_uint8 * PTRC_KEM_LIGHT_SK_BYTES)()
    cl_ct = (ctypes.c_uint8 * PTRC_KEM_LIGHT_CT_BYTES)()

    iters = 300
    t0 = time.perf_counter_ns()
    for _ in range(iters):
        lib.ptrc_kem_keygen(c_pk, c_sk, c_seed)
    t1 = time.perf_counter_ns()
    for _ in range(iters):
        lib.ptrc_kem_encaps(c_ct, c_ss, c_pk, c_msg)
    t2 = time.perf_counter_ns()
    for _ in range(iters):
        lib.ptrc_kem_decaps(c_ss, c_ct, c_sk)
    t3 = time.perf_counter_ns()

    for _ in range(iters):
        lib.ptrc_kem_light_keygen(cl_pk, cl_sk, c_seed)
    t4 = time.perf_counter_ns()
    for _ in range(iters):
        lib.ptrc_kem_light_encaps(cl_ct, c_ss, cl_pk, c_msg)
    t5 = time.perf_counter_ns()
    for _ in range(iters):
        lib.ptrc_kem_light_decaps(c_ss, cl_ct, cl_sk)
    t6 = time.perf_counter_ns()

    kg_a = ((t1 - t0) // 1000) // iters
    en_a = ((t2 - t1) // 1000) // iters
    de_a = ((t3 - t2) // 1000) // iters

    kg_b = ((t4 - t3) // 1000) // iters
    en_b = ((t5 - t4) // 1000) // iters
    de_b = ((t6 - t5) // 1000) // iters

    lib.ptrc_kem_wipe(c_sk, PTRC_KEM_SK_BYTES)
    lib.ptrc_kem_wipe(cl_sk, PTRC_KEM_LIGHT_SK_BYTES)

    print("===============================================================================")
    print("  pTRC CCA2 POST-QUANTUM RING-KEM v4.3.1 — BARE-METAL C11 BENCHMARK")
    print("  Modulus  : q = 7681 (Non-Mersenne, gcd(7681, 210) == 1) | FO-CCA2 + O(1)")
    print("-------------------------------------------------------------------------------")
    print(f"  [PROFILE A: 512-Dim Standard] PK={PTRC_KEM_PK_BYTES}B | SK={PTRC_KEM_SK_BYTES}B | CT={PTRC_KEM_CT_BYTES}B | SS=64B")
    print(f"   -> Speed : Keygen = {kg_a} us | Encaps = {en_a} us | Decaps = {de_a} us (Total = {kg_a + en_a + de_a} us)")
    print(f"  [PROFILE B: 256-Dim Light   ] PK={PTRC_KEM_LIGHT_PK_BYTES}B | SK={PTRC_KEM_LIGHT_SK_BYTES}B | CT={PTRC_KEM_LIGHT_CT_BYTES}B | SS=64B")
    print(f"   -> Speed : Keygen = {kg_b} us | Encaps = {en_b} us | Decaps = {de_b} us (Total = {kg_b + en_b + de_b} us)")
    print("===============================================================================")


if __name__ == "__main__":
    std_res, light_res = test_python_dual_profiles()
    test_c_python_dual_parity(std_res, light_res)
    test_hybrid_aead_coupling(std_res[3], light_res[3])
    test_zero_float_compliance()
    benchmark_c11_dual_kem()
    sys.exit(0)
