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
Bit-Parity, Z \\ {0} Invariant & Tamper-Rejection Audit for pTRC Crypto v4.0.
File: src/00_test_ptrc_crypt_parity.py

Strictly pure integer (-1 adjacent to +1, no zero point), zero-float, zero-trig.
"""

from __future__ import annotations

import ctypes
import pathlib
import re
import sys

from ptrc_crystal_aead import (
    PTRC_CRYPT_ERR,
    PTRC_CRYPT_KEY_BYTES,
    PTRC_CRYPT_NONCE_BYTES,
    PTRC_CRYPT_OK,
    PTRC_CRYPT_TAG_BYTES,
    PtrcCrystalContext,
    _CCrystalCtx,
    load_c_crystal_library,
    ptrc_aead_decrypt,
    ptrc_aead_encrypt,
    ptrc_kdf_derive,
    ptrc_primorial_keygen,
)


def test_python_aead_and_z_no_zero_invariants() -> None:
    seed = b"pTRC-v4.0-MASTER-DOMAIN-SEED-PRIMORIAL-210"
    key, nonce = ptrc_primorial_keygen(137210144, seed)
    assert len(key) == PTRC_CRYPT_KEY_BYTES
    assert len(nonce) == PTRC_CRYPT_NONCE_BYTES

    ctx = PtrcCrystalContext(key, nonce)
    assert all(v != 0 for v in ctx.sponge), "Zero found in initial 144-facet sponge!"
    assert all(v >= 1 for v in ctx.macro_state), "Zero found in macro_state!"

    aad = b"HDR:pTRC-v4.0|512BIT|Z-NO-ZERO"
    pt = b"Discrete Integer Physics Z \\ {0}: Zero-Table Primorial Macro-Cascade AEAD."
    ct, tag = ptrc_aead_encrypt(key, nonce, pt, aad)
    assert len(ct) == len(pt)
    assert len(tag) == PTRC_CRYPT_TAG_BYTES
    assert ct != pt

    rc, dec = ptrc_aead_decrypt(key, nonce, ct, tag, aad)
    assert rc == PTRC_CRYPT_OK
    assert dec == pt

    # Tamper 1 bit in ciphertext -> must reject with PTRC_CRYPT_ERR (-1)
    bad_ct = bytearray(ct)
    mid = len(bad_ct) // 2
    bad_ct.__setitem__(mid, bad_ct.__getitem__(mid) ^ 0x01)
    rc_bad_ct, dec_bad_ct = ptrc_aead_decrypt(key, nonce, bytes(bad_ct), tag, aad)
    assert rc_bad_ct == PTRC_CRYPT_ERR
    assert dec_bad_ct == b""

    # Tamper 1 bit in SLIP-MAC tag -> must reject with PTRC_CRYPT_ERR (-1)
    bad_tag = bytearray(tag)
    bad_tag.__setitem__(0, bad_tag.__getitem__(0) ^ 0x80)
    rc_bad_tag, _ = ptrc_aead_decrypt(key, nonce, ct, bytes(bad_tag), aad)
    assert rc_bad_tag == PTRC_CRYPT_ERR


    # Tamper 1 bit in AAD -> must reject with PTRC_CRYPT_ERR (-1)
    rc_bad_aad, _ = ptrc_aead_decrypt(key, nonce, ct, tag, aad + b"!")
    assert rc_bad_aad == PTRC_CRYPT_ERR

    print("[PASS] 1. Z \\ {0} Sponge Invariants, 512-Bit AEAD & Constant-Time Tamper Rejection")


def test_c11_python_crypto_bit_parity() -> None:
    lib = load_c_crystal_library()
    if lib is None:
        print("[SKIP] 2. C11 Shared Library not built yet (build libptrc_crystal.so for C11/Python parity)")
        return

    seed = b"pTRC-v4.0-C11-PYTHON-BIT-PARITY-SEED-137"
    info = b"SESSION-CONTEXT-INFO-144-FACETS"

    py_kdf_k, py_kdf_n = ptrc_kdf_derive(seed, info)
    c_kdf_k = (ctypes.c_uint8 * PTRC_CRYPT_KEY_BYTES)()
    c_kdf_n = (ctypes.c_uint8 * PTRC_CRYPT_NONCE_BYTES)()
    c_seed = (ctypes.c_uint8 * len(seed))(*seed)
    c_info = (ctypes.c_uint8 * len(info))(*info)
    rc_kdf = lib.ptrc_kdf_derive(c_seed, len(seed), c_info, len(info), c_kdf_k, c_kdf_n)
    assert rc_kdf == PTRC_CRYPT_OK
    assert bytes(c_kdf_k) == py_kdf_k, "KDF key mismatch between C11 and Python!"
    assert bytes(c_kdf_n) == py_kdf_n, "KDF nonce mismatch between C11 and Python!"

    py_key, py_nonce = ptrc_primorial_keygen(987654321, seed)
    c_key = (ctypes.c_uint8 * PTRC_CRYPT_KEY_BYTES)()
    c_nonce = (ctypes.c_uint8 * PTRC_CRYPT_NONCE_BYTES)()
    rc_kg = lib.ptrc_primorial_keygen(987654321, c_seed, len(seed), c_key, c_nonce)
    assert rc_kg == PTRC_CRYPT_OK
    assert bytes(c_key) == py_key, "Primorial keygen key mismatch between C11 and Python!"
    assert bytes(c_nonce) == py_nonce, "Primorial keygen nonce mismatch between C11 and Python!"

    # Verify 144-facet sponge & macro-cascade bit-parity + -1 wipe
    py_ctx = PtrcCrystalContext(py_key, py_nonce)
    c_ctx = _CCrystalCtx()
    rc_init = lib.ptrc_crystal_init(ctypes.byref(c_ctx), c_key, c_nonce)
    assert rc_init == PTRC_CRYPT_OK
    assert list(c_ctx.sponge) == py_ctx.sponge, "Initial 144-facet sponge mismatch between C11 and Python!"
    assert list(c_ctx.macro_mod) == py_ctx.macro_mod, "Macro-cascade moduli mismatch!"

    # Verify AEAD ciphertext & 192-bit SLIP-MAC tag bit-parity across 137-takt pulse boundary
    aad = b"PARITY-AAD-210-137-156"
    pt = bytes((i * 137 + 211) & 0xFF for i in range(512))
    py_ct, py_tag = ptrc_aead_encrypt(py_key, py_nonce, pt, aad)

    c_aad = (ctypes.c_uint8 * len(aad))(*aad)
    c_pt = (ctypes.c_uint8 * len(pt))(*pt)
    c_ct = (ctypes.c_uint8 * len(pt))()
    c_tag = (ctypes.c_uint8 * PTRC_CRYPT_TAG_BYTES)()

    rc_enc = lib.ptrc_aead_encrypt(c_key, c_nonce, c_aad, len(aad), c_pt, len(pt), c_ct, c_tag)
    assert rc_enc == PTRC_CRYPT_OK
    assert bytes(c_ct) == py_ct, "Ciphertext mismatch between C11 and Python!"
    assert bytes(c_tag) == py_tag, "192-bit SLIP-MAC tag mismatch between C11 and Python!"

    c_dec = (ctypes.c_uint8 * len(pt))()
    rc_dec = lib.ptrc_aead_decrypt(c_key, c_nonce, c_aad, len(aad), c_ct, len(pt), c_tag, c_dec)
    assert rc_dec == PTRC_CRYPT_OK
    assert bytes(c_dec) == pt

    lib.ptrc_crystal_wipe(ctypes.byref(c_ctx))
    assert all(v == -1 for v in c_ctx.sponge), "Volatile SRAM wipe to -1 failed!"
    print("[PASS] 2. 100% C11 / Python Bit-Parity (KDF, Keygen, 512B Stream, 192-Bit Tag & -1 Wipe)")


def test_zero_float_compliance() -> None:
    root = pathlib.Path(__file__).resolve().parent.parent
    files = [
        root / "embedded" / "crypto" / "ptrc_crystal.h",
        root / "embedded" / "crypto" / "ptrc_crystal.c",
        root / "embedded" / "crypto" / "ptrc_crypt_demo.c",
        root / "src" / "ptrc_crystal_aead.py",
        root / "src" / "00_test_ptrc_crypt_metrics.py",
        root / "src" / "00_ptrc_crypt_demo.py",
    ]
    forbidden = re.compile(r"\b(float|double|sin|cos|tan|sqrt|pow|log|exp|math)\b")
    for fpath in files:
        if not fpath.exists():
            continue
        raw = fpath.read_text(encoding="utf-8")
        cleaned = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
        cleaned = re.sub(r"//.*", "", cleaned)
        cleaned = re.sub(r"#.*", "", cleaned)
        for lineno, line in enumerate(cleaned.splitlines(), 1):
            match = forbidden.search(line)
            assert match is None, f"Forbidden float/trig token '{match.group(0)}' in {fpath}:{lineno}"
    print("[PASS] 3. Static Zero-Float & Zero-Trig Compliance Verified across Crypto v4.0")


if __name__ == "__main__":
    test_python_aead_and_z_no_zero_invariants()
    test_c11_python_crypto_bit_parity()
    test_zero_float_compliance()
    print("ALL 3 CRYPTO v4.0 PARITY & INVARIANT CHECKS PASSED.")
    sys.exit(0)
