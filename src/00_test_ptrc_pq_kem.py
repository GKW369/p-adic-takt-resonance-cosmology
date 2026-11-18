# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.5.0
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
pTRC Post-Quantum Ring-KEM v4.5.0 Verification Suite (FO-CCA2 + comp5 + Hybrid AEAD).
File: src/00_test_ptrc_pq_kem.py (Complete)
"""

from __future__ import annotations

import ctypes
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ptrc_crystal_aead import (  # noqa: E402
    PTRC_CRYPT_OK,
    ptrc_aead_decrypt,
    ptrc_aead_encrypt,
)
from ptrc_pq_kem import (  # noqa: E402
    PTRC_KEM_CT_BYTES_LIGHT,
    PTRC_KEM_CT_BYTES_STD,
    PTRC_KEM_K_LIGHT,
    PTRC_KEM_K_STD,
    PTRC_KEM_OK,
    PTRC_KEM_PK_BYTES_LIGHT,
    PTRC_KEM_PK_BYTES_STD,
    PTRC_KEM_SEED_BYTES,
    PTRC_KEM_SK_BYTES_LIGHT,
    PTRC_KEM_SK_BYTES_STD,
    PTRC_KEM_SS_BYTES,
    load_c_pq_kem_library,
    ptrc_kem_decaps_ex,
    ptrc_kem_encaps_ex,
    ptrc_kem_keygen_ex,
)


def verify_profile(k: int, label: str, pk_len: int, sk_len: int, ct_len: int, lib: ctypes.CDLL | None) -> None:
    seed = bytes(((i * 37 + k * 19 + 11) & 0xFF) | 1 for i in range(PTRC_KEM_SEED_BYTES))
    coins = bytes(((i * 53 + k * 29 + 7) & 0xFF) | 1 for i in range(PTRC_KEM_SEED_BYTES))

    pk_py, sk_py = ptrc_kem_keygen_ex(k, seed)
    assert len(pk_py) == pk_len and len(sk_py) == sk_len

    ct_py, ss_enc_py = ptrc_kem_encaps_ex(k, pk_py, coins)
    assert len(ct_py) == ct_len and len(ss_enc_py) == PTRC_KEM_SS_BYTES

    ss_dec_py = ptrc_kem_decaps_ex(k, sk_py, ct_py)
    assert ss_dec_py == ss_enc_py, f"[{label}] Python KEM shared secret mismatch"

    # FO-CCA2 1-bit tamper implicit rejection check
    tampered_ct = bytearray(ct_py)
    tampered_ct[-1] ^= 0x01
    ss_rej_py = ptrc_kem_decaps_ex(k, sk_py, bytes(tampered_ct))
    assert ss_rej_py != ss_enc_py, f"[{label}] FO-CCA2 failed to reject tampered ciphertext"
    assert len(ss_rej_py) == PTRC_KEM_SS_BYTES

    # Hybrid PQ-KEM + 512-bit Constant-Time Crystal AEAD roundtrip
    nonce = bytes(((i * 13 + k * 7 + 3) & 0xFF) | 1 for i in range(16))
    msg = f"pTRC v4.5.0 Hybrid PQ-AEAD Payload ({label})".encode("utf-8")
    aad = b"PQ_HYBRID_AAD_210_137"
    aead_ct, aead_tag = ptrc_aead_encrypt(ss_enc_py, nonce, msg, aad=aad)
    rc_aead, recovered = ptrc_aead_decrypt(ss_dec_py, nonce, aead_ct, aead_tag, aad=aad)
    assert rc_aead == PTRC_CRYPT_OK and recovered == msg

    if lib is not None:
        c_seed = (ctypes.c_uint8 * PTRC_KEM_SEED_BYTES).from_buffer_copy(seed)
        c_coins = (ctypes.c_uint8 * PTRC_KEM_SEED_BYTES).from_buffer_copy(coins)
        c_pk = (ctypes.c_uint8 * pk_len)()
        c_sk = (ctypes.c_uint8 * sk_len)()
        c_ct = (ctypes.c_uint8 * ct_len)()
        c_ss_enc = (ctypes.c_uint8 * PTRC_KEM_SS_BYTES)()
        c_ss_dec = (ctypes.c_uint8 * PTRC_KEM_SS_BYTES)()
        c_ss_rej = (ctypes.c_uint8 * PTRC_KEM_SS_BYTES)()

        t0 = time.perf_counter_ns()
        rc_kg = lib.ptrc_kem_keygen_ex(k, c_seed, c_pk, c_sk)
        t1 = time.perf_counter_ns()
        rc_en = lib.ptrc_kem_encaps_ex(k, c_pk, c_coins, c_ct, c_ss_enc)
        t2 = time.perf_counter_ns()
        rc_de = lib.ptrc_kem_decaps_ex(k, c_sk, c_ct, c_ss_dec)
        t3 = time.perf_counter_ns()

        assert rc_kg == PTRC_KEM_OK and rc_en == PTRC_KEM_OK and rc_de == PTRC_KEM_OK
        assert bytes(c_pk) == pk_py, f"[{label}] C11 vs Python PK parity mismatch"
        assert bytes(c_sk) == sk_py, f"[{label}] C11 vs Python SK parity mismatch"
        assert bytes(c_ct) == ct_py, f"[{label}] C11 vs Python CT parity mismatch"
        assert bytes(c_ss_enc) == ss_enc_py, f"[{label}] C11 vs Python Encaps SS parity mismatch"
        assert bytes(c_ss_dec) == ss_dec_py, f"[{label}] C11 vs Python Decaps SS parity mismatch"

        c_tampered = (ctypes.c_uint8 * ct_len).from_buffer_copy(bytes(tampered_ct))
        rc_rej = lib.ptrc_kem_decaps_ex(k, c_sk, c_tampered, c_ss_rej)
        assert rc_rej == PTRC_KEM_OK
        assert bytes(c_ss_rej) == ss_rej_py, f"[{label}] C11 vs Python FO reject key parity mismatch"

        kg_us = max(1, (t1 - t0) // 1000)
        en_us = max(1, (t2 - t1) // 1000)
        de_us = max(1, (t3 - t2) // 1000)
        print(
            f"  [{label}] C11<->Py 100% Parity OK | Keygen={kg_us}us, Encaps={en_us}us, "
            f"Decaps={de_us}us (Total={kg_us + en_us + de_us}us)"
        )
    else:
        print(f"  [{label}] Python Reference + FO-CCA2 + Hybrid AEAD OK (C11 shared lib not built)")


def main() -> None:
    print("=== pTRC v4.5.0 Post-Quantum Ring-KEM (FO-CCA2 + comp5) Verification ===")
    lib = load_c_pq_kem_library(ROOT)
    verify_profile(
        PTRC_KEM_K_STD,
        "Profile A: 512-Dim Standard (k=2)",
        PTRC_KEM_PK_BYTES_STD,
        PTRC_KEM_SK_BYTES_STD,
        PTRC_KEM_CT_BYTES_STD,
        lib,
    )
    verify_profile(
        PTRC_KEM_K_LIGHT,
        "Profile B: 256-Dim Ultra-Light IoT (k=1)",
        PTRC_KEM_PK_BYTES_LIGHT,
        PTRC_KEM_SK_BYTES_LIGHT,
        PTRC_KEM_CT_BYTES_LIGHT,
        lib,
    )
    print("=== ALL POST-QUANTUM RING-KEM v4.5.0 AUDITS PASSED ===")


if __name__ == "__main__":
    main()
