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
pTRC Framework - Cross-Language Bit-Parity & Hygiene Audit (C vs. Python)
Verifies 100% bit-exact parity, Zero-Float compliance, and 1-bit tamper rejection.
"""

import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
EMBEDDED_CRYPTO_DIR = os.path.join(ROOT_DIR, "embedded", "crypto")

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from ptrc_crystal_aead import PTRCHardenedCrystalAEAD


def audit_zero_float_hygiene(filepath: str) -> list[str]:
    """Prüft auf verbotene float-Typen oder analoge '/' Divisionen."""
    violations = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            stripped = line.strip()
            if stripped.startswith(("#", "//", "/*", "*", '"""', "'''")):
                continue
            code_part = stripped.split("#")[0].split("//")[0]
            if re.search(r"\bfloat\b|\bdouble\b", code_part):
                violations.append(f"Line {line_no}: Verbotener Gleitkomma-Typ gefunden")
            # Prüfe auf einfaches '/' (ignoriere '//' und '/*')
            cleaned = code_part.replace("//", "").replace("/*", "").replace("*/", "")
            if "/" in cleaned:
                violations.append(f"Line {line_no}: Verbotene analoge Division '/' gefunden")
    return violations


def run_full_audit() -> int:
    print("=" * 78)
    print("  pTRC CRYPTOGRAPHY AUDIT // C vs. PYTHON BIT-PARITY & ZERO-FLOAT CHECK")
    print("=" * 78)

    # 1. Zero-Float Hygiene-Check auf allen neuen Dateien
    files_to_check = [
        os.path.join(SCRIPT_DIR, "ptrc_crystal_aead.py"),
        os.path.join(SCRIPT_DIR, "00_ptrc_crypt_demo.py"),
        os.path.join(SCRIPT_DIR, "crypt_resonance.py"),
        os.path.join(EMBEDDED_CRYPTO_DIR, "ptrc_crystal.h"),
        os.path.join(EMBEDDED_CRYPTO_DIR, "ptrc_crystal.c"),
        os.path.join(EMBEDDED_CRYPTO_DIR, "ptrc_crypt_demo.c"),
    ]

    hygiene_ok = True
    for fp in files_to_check:
        if not os.path.exists(fp):
            print(f"[-] FEHLT: {os.path.relpath(fp, ROOT_DIR)}")
            hygiene_ok = False
            continue
        errs = audit_zero_float_hygiene(fp)
        if errs:
            print(f"[-] HYGIENE-FEHLER in {os.path.basename(fp)}: {errs}")
            hygiene_ok = False
        else:
            print(f"[OK] Zero-Float Hygiene: {os.path.relpath(fp, ROOT_DIR)}")

    if not hygiene_ok:
        return 1

    print("-" * 78)

    # 2. C-Demo kompilieren und ausführen
    c_bin = os.path.join(EMBEDDED_CRYPTO_DIR, "ptrc_hardware_demo")
    compile_cmd = [
        "gcc", "-O3", "-Wall", "-Wextra",
        os.path.join(EMBEDDED_CRYPTO_DIR, "ptrc_crystal.c"),
        os.path.join(EMBEDDED_CRYPTO_DIR, "ptrc_crypt_demo.c"),
        "-o", c_bin,
    ]
    subprocess.run(compile_cmd, check=True)
    c_out = subprocess.check_output([c_bin], text=True)

    c_cipher_match = re.search(r"ENCRYPTED \(Hex\):\s*([0-9a-fA-F]+)", c_out)
    c_tag_match = re.search(r"SLIP-MAC\s*\(Hex\):\s*([0-9a-fA-F]+)", c_out)

    if not c_cipher_match or not c_tag_match:
        print("[-] C-Ausgabe konnte nicht geparst werden.")
        return 1

    c_cipher_hex = c_cipher_match.group(1).lower()
    c_tag_hex = c_tag_match.group(1).lower()

    # 3. Identische Berechnung in Python
    aad_bytes = b"NODE:01|RING:210|TAKT:1836"
    payload_bytes = b"MINT-Matrix-Core-Initialized: True. 144-Facet AEAD + SLIP-MAC Active."
    secret_key = bytes([
        0x18, 0x36, 0x21, 0x00, 0x15, 0x60, 0x24, 0x48,
        0x01, 0x05, 0x07, 0x11, 0x13, 0x17, 0x19, 0x23,
        0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22,
        0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x12, 0x34,
    ])
    nonce = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C])

    py_cipher, py_tag = PTRCHardenedCrystalAEAD.encrypt(secret_key, nonce, payload_bytes, aad=aad_bytes)
    py_cipher_hex = py_cipher.hex().lower()
    py_tag_hex = py_tag.hex().lower()

    cipher_parity = (c_cipher_hex == py_cipher_hex)
    tag_parity = (c_tag_hex == py_tag_hex)

    print(f"[{'OK' if cipher_parity else 'FAIL'}] Ciphertext Bit-Parität (C == Python) : {cipher_parity}")
    print(f"[{'OK' if tag_parity else 'FAIL'}] SLIP-MAC Bit-Parität   (C == Python) : {tag_parity}")

    # 4. Null-Byte- und Edge-Case-Test (alle Bytes 0x00 bis 0xFF)
    all_bytes = bytes(range(256))
    ct_edge, tag_edge = PTRCHardenedCrystalAEAD.encrypt(secret_key, nonce, all_bytes, aad=b"EDGE")
    ok_edge, pt_edge = PTRCHardenedCrystalAEAD.decrypt(secret_key, nonce, ct_edge, tag_edge, aad=b"EDGE")
    edge_valid = ok_edge and (pt_edge == all_bytes)
    print(f"[{'OK' if edge_valid else 'FAIL'}] 0x00..0xFF Vollbereich ohne Null-Verlust : {edge_valid}")

    # 5. Header-Manipulations-Test (AAD Tamper)
    aad_tamper_ok, _ = PTRCHardenedCrystalAEAD.decrypt(secret_key, nonce, ct_edge, tag_edge, aad=b"EDGF")
    print(f"[{'OK' if not aad_tamper_ok else 'FAIL'}] Header-Manipulation (AAD) abgewiesen    : {not aad_tamper_ok}")

    print("=" * 78)
    if cipher_parity and tag_parity and edge_valid and (not aad_tamper_ok):
        print(" -> GESAMTSTATUS: ALLE 144-FACETTEN-TESTS 100% BESTANDEN.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(run_full_audit())
  
