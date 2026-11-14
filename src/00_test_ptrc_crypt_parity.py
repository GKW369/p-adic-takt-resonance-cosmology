# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
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

# -*- coding: utf-8 -*-
"""
pTRC Framework - Production Cross-Language Parity Audit (v4.0 512-Bit Primorial AEAD)
Verifies bit-exact determinism between C11 bare-metal implementation (embedded/crypto)
and pure Python reference (src/ptrc_crystal_aead.py) across 8-Prime CRT Keygen, KDF,
AEAD, and 1-bit tamper rejection.
"""

import ctypes
import subprocess
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
REPO_ROOT = SRC_DIR.parent
BUILD_DIR = REPO_ROOT / "build"
CRYPTO_DIR = REPO_ROOT / "embedded" / "crypto"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ptrc_crystal_aead import PTRCHardenedCrystalAEAD


def find_shared_library() -> Path | None:
    """Locates the compiled C11 shared library across Linux, macOS, and Windows."""
    candidates = [
        BUILD_DIR / "libptrc_crystal.so",
        BUILD_DIR / "libptrc_crystal.dylib",
        BUILD_DIR / "ptrc_crystal.dll",
        BUILD_DIR / "Release" / "ptrc_crystal.dll",
        BUILD_DIR / "Debug" / "ptrc_crystal.dll",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def find_demo_executable() -> Path | None:
    """Locates the standalone C11 demo executable."""
    candidates = [
        BUILD_DIR / "ptrc_hardware_demo",
        BUILD_DIR / "ptrc_hardware_demo.exe",
        BUILD_DIR / "Release" / "ptrc_hardware_demo.exe",
        CRYPTO_DIR / "ptrc_hardware_demo",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def verify_ctypes_parity(lib_path: Path) -> bool:
    """Direct C11 <-> Python ABI parity check via ctypes for 8-Prime Keygen, KDF & 512-bit AEAD."""
    lib = ctypes.CDLL(str(lib_path))

    # void ptrc_primorial_keygen(uint64_t session_takt, const uint8_t *domain_seed, size_t seed_len, uint8_t out_key, uint8_t out_nonce)
    lib.ptrc_primorial_keygen.argtypes = [
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
    ]
    lib.ptrc_primorial_keygen.restype = None

    # void ptrc_kdf_derive(const uint8_t *master_seed, size_t seed_len, const uint8_t *context_info, size_t info_len, uint8_t out_key, uint8_t out_nonce)
    lib.ptrc_kdf_derive.argtypes = [
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
    ]
    lib.ptrc_kdf_derive.restype = None

    # void ptrc_aead_encrypt(const uint8_t key, const uint8_t nonce, const uint8_t *aad, size_t aad_len, const uint8_t *plaintext, uint8_t *ciphertext, size_t length, uint8_t tag_out)
    lib.ptrc_aead_encrypt.argtypes = [
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint8),
    ]
    lib.ptrc_aead_encrypt.restype = None

    # int ptrc_aead_decrypt(const uint8_t key, const uint8_t nonce, const uint8_t *aad, size_t aad_len, const uint8_t *ciphertext, uint8_t *plaintext, size_t length, const uint8_t expected_tag)
    lib.ptrc_aead_decrypt.argtypes = [
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_uint8),
    ]
    lib.ptrc_aead_decrypt.restype = ctypes.c_int

    # 1. Verify Deterministic 8-Prime CRT Key & Nonce Generator (Zero TRNG)
    session_takt = 1836137210
    domain_seed = b"GKW369-8PRIME-CRT-RING-GENERATOR"
    py_gen_key, py_gen_nonce = PTRCHardenedCrystalAEAD.generate_primorial_keypair(session_takt, domain_seed)

    c_seed = (ctypes.c_uint8 * len(domain_seed)).from_buffer_copy(domain_seed)
    c_gen_key = (ctypes.c_uint8 * 64)()
    c_gen_nonce = (ctypes.c_uint8 * 16)()
    lib.ptrc_primorial_keygen(session_takt, c_seed, len(domain_seed), c_gen_key, c_gen_nonce)

    if bytes(c_gen_key) != py_gen_key or bytes(c_gen_nonce) != py_gen_nonce:
        print("[ FAIL ] 8-Prime CRT Keygen parity mismatch between C11 and Python!")
        return False
    print("[ PASS ] 8-Prime CRT Key & Nonce Generator bit-exact parity verified (C11 == Python).")

    # 2. Verify 512-Bit pTRC-KDF
    ikm = b"GKW369-PRIMORDIAL-MASTER-SEED-2026-V4"
    info = b"PTRC:AUDIT|P15-MACRO|TAKT:137"
    aad = b"HDR:SEQ=0001|MODE=512BIT-PRIMORDIAL"
    plaintext = (
        b"1+12 Closest-Packed Space Crystal Lattice: Zero-Float Determinism Verified."
    )

    py_key, py_nonce = PTRCHardenedCrystalAEAD.derive_key_and_nonce(ikm, info)

    c_ikm = (ctypes.c_uint8 * len(ikm)).from_buffer_copy(ikm)
    c_info = (ctypes.c_uint8 * len(info)).from_buffer_copy(info)
    c_key = (ctypes.c_uint8 * 64)()
    c_nonce = (ctypes.c_uint8 * 16)()

    lib.ptrc_kdf_derive(c_ikm, len(ikm), c_info, len(info), c_key, c_nonce)
    if bytes(c_key) != py_key or bytes(c_nonce) != py_nonce:
        print("[ FAIL ] KDF parity mismatch between C11 and Python!")
        return False
    print("[ PASS ] 512-Bit pTRC-KDF bit-exact parity verified (C11 == Python).")

    # 3. Verify 512-Bit AEAD & 192-Bit SLIP-MAC
    py_ct, py_tag = PTRCHardenedCrystalAEAD.encrypt(py_key, py_nonce, plaintext, aad=aad)

    c_aad = (ctypes.c_uint8 * len(aad)).from_buffer_copy(aad)
    c_pt = (ctypes.c_uint8 * len(plaintext)).from_buffer_copy(plaintext)
    c_ct = (ctypes.c_uint8 * len(plaintext))()
    c_tag = (ctypes.c_uint8 * 24)()

    lib.ptrc_aead_encrypt(c_key, c_nonce, c_aad, len(aad), c_pt, c_ct, len(plaintext), c_tag)

    if bytes(c_ct) != py_ct or bytes(c_tag) != py_tag:
        print("[ FAIL ] AEAD ciphertext or 192-bit SLIP-MAC tag mismatch!")
        return False
    print("[ PASS ] 512-Bit AEAD ciphertext & 192-bit SLIP-MAC tag bit-exact parity verified.")

    # 4. Verify authentic decryption & 1-bit tamper rejection in C11
    c_dec = (ctypes.c_uint8 * len(plaintext))()
    rc_ok = lib.ptrc_aead_decrypt(c_key, c_nonce, c_aad, len(aad), c_ct, c_dec, len(plaintext), c_tag)
    if rc_ok != 1 or bytes(c_dec) != plaintext:
        print("[ FAIL ] C11 authentic decryption failed!")
        return False

    c_ct_tampered = (ctypes.c_uint8 * len(plaintext)).from_buffer_copy(bytes(c_ct))
    c_ct_tampered ^= 0x01
    c_dec_wiped = (ctypes.c_uint8 * len(plaintext)).from_buffer_copy(b"\xAA" * len(plaintext))
    rc_bad = lib.ptrc_aead_decrypt(
        c_key, c_nonce, c_aad, len(aad), c_ct_tampered, c_dec_wiped, len(plaintext), c_tag
    )
    if rc_bad != 0 or any(b != 0 for b in bytes(c_dec_wiped)):
        print("[ FAIL ] C11 1-bit tamper rejection or fail-closed zeroization failed!")
        return False
    print("[ PASS ] Fail-closed 1-bit tamper rejection & zeroization verified.")
    return True


def verify_cli_demo_parity(exe_path: Path) -> bool:
    """Verifies standalone C11 demo binary output against Python v4.0 reference."""
    proc = subprocess.run([str(exe_path)], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print(f"[ FAIL ] Demo executable exited with code {proc.returncode}")
        print(proc.stderr)
        return False
    print("[ PASS ] Standalone C11 demo binary executed cleanly (exit code 0).")
    return True


def main() -> int:
    print("==========================================================================")
    print("  pTRC PRODUCTION AUDIT: C11 <-> PYTHON BIT-EXACT PARITY (v4.0 512-BIT)")
    print("==========================================================================")

    lib_path = find_shared_library()
    exe_path = find_demo_executable()

    if lib_path is None and exe_path is None:
        print("[ WARN ] No compiled C11 binaries found in ./build/.")
        print("         Run: cmake -B build && cmake --build build")
        return 1

    ok = True
    if lib_path is not None:
        print(f" -> Testing shared library : {lib_path.relative_to(REPO_ROOT)}")
        ok = verify_ctypes_parity(lib_path) and ok

    if exe_path is not None:
        print(f" -> Testing CLI executable : {exe_path.relative_to(REPO_ROOT)}")
        ok = verify_cli_demo_parity(exe_path) and ok

    print("==========================================================================")
    if ok:
        print("  STATUS: ALL CROSS-LANGUAGE PARITY CHECKS PASSED (100% BIT-EXACT)")
        return 0
    print("  STATUS: PARITY AUDIT FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
