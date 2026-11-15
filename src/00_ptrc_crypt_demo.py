# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.0
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

"""
Interactive Terminal Demonstration for pTRC v4.0 512-Bit Primorial AEAD Engine.
File: src/00_ptrc_crypt_demo.py
"""

from __future__ import annotations

import ctypes
import time

from ptrc_crystal_aead import (
    PTRC_CRYPT_ERR,
    PTRC_CRYPT_FACETS,
    PTRC_CRYPT_OK,
    PTRC_PRIMORIAL_210,
    PTRC_TAKT_137,
    PtrcCrystalContext,
    _CCrystalCtx,
    load_c_crystal_library,
    ptrc_aead_decrypt,
    ptrc_aead_encrypt,
    ptrc_primorial_keygen,
)


def main() -> None:
    print("===============================================================================")
    print("  pTRC CRYPTO v4.0 — 512-BIT PRIMORIAL MACRO-CASCADE & 192-BIT SLIP-MAC AEAD")
    print(f"  Axioms   : Z \\ {{0}} (No Zero) | {PTRC_CRYPT_FACETS} Facets | Base {PTRC_PRIMORIAL_210} | {PTRC_TAKT_137}-Takt Mirror")
    print("===============================================================================")

    domain_seed = b"pTRC-v4.0-INTERACTIVE-TERMINAL-DOMAIN-210"
    t0 = time.perf_counter_ns()
    key, nonce = ptrc_primorial_keygen(137210144, domain_seed)
    ctx = PtrcCrystalContext(key, nonce)

    aad = b"HDR:pTRC-v4.0|512BIT|192MAC|Z-NO-ZERO"
    plaintext = b"Discrete Integer Physics Z \\ {0}: Zero-Table Primorial Macro-Cascade AEAD."
    ciphertext, tag = ptrc_aead_encrypt(key, nonce, plaintext, aad)
    rc_ok, recovered = ptrc_aead_decrypt(key, nonce, ciphertext, tag, aad)
    t1 = time.perf_counter_ns()

    tampered_tag = bytearray(tag)
    tampered_tag.__setitem__(0, tampered_tag.__getitem__(0) ^ 0x01)
    rc_tamper, _ = ptrc_aead_decrypt(key, nonce, ciphertext, bytes(tampered_tag), aad)

    m0, m1, m2, m3 = ctx.macro_mod
    print(f" + Macro-Moduli (64-bit): M0={m0} | M1={m1}")
    print(f" + Macro-Moduli (Tail)  : M2={m2} | M3={m3}")
    print(f" + Ciphertext (Hex 24B) : {ciphertext[:24].hex()}...")
    print(f" + 192-Bit SLIP-MAC Tag : {tag.hex()}")
    print(f" + Authentic Decryption : {'PASS' if (rc_ok == PTRC_CRYPT_OK and recovered == plaintext) else 'FAIL'}")
    print(f" + Tamper Rejection     : {'PASS' if rc_tamper == PTRC_CRYPT_ERR else 'FAIL'}")

    lib = load_c_crystal_library()
    if lib is not None:
        c_ctx = _CCrystalCtx()
        print(f" + C11 Native Kernel    : ACTIVE (sizeof(ctx)={ctypes.sizeof(c_ctx)} bytes, Zero malloc)")
    else:
        print(" + C11 Native Kernel    : Build libptrc_crystal.so via CMake/gcc")

    elapsed_us = (t1 - t0) // 1000
    print(f" + End-to-End Latency   : {elapsed_us} us (Pure Integer Z \\ {{0}}, No Zero Point)")
    print("===============================================================================")


if __name__ == "__main__":
    main()
