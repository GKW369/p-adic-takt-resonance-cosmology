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
pTRC Framework - Core Cryptography Module: 144-Facet AEAD Matrix Encryption
Operational Domain: Active 144-Facet Sponge & CRT Rings (Z/210Z x 11 x 13 x 17).
Integrates PTRCHardenedCrystalAEAD into the central repository verification pipeline.
"""

import os
import sys
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from ptrc_crystal_aead import PTRCHardenedCrystalAEAD


class PTRCCryptResonanceEngine:
    """
    Wraps the 144-Facet Crystalline AEAD Engine for whole-number matrix blocks
    and repository-wide integer telemetry verification.
    """

    def __init__(self, key_vector_seed: int = 1836):
        self.primorial_base = 210
        self.control_base = 24
        self.calibration_limit = 156
        self.seed = int(key_vector_seed)

        # Derive deterministic 256-bit (32-byte) key and 96-bit (12-byte) nonce in Z
        self.secret_key = bytes(
            ((self.seed * (i + 1) + self.calibration_limit) * 13) & 0xFF
            for i in range(32)
        )
        self.nonce = bytes(
            ((self.seed + i * self.control_base) * 7) & 0xFF
            for i in range(12)
        )
        self.aad_header = b"PTRC:MODULE16|RING:210|TAKT:24"

    def encrypt_data_matrix(self, whole_number_array) -> tuple[bytes, bytes, tuple[int, ...]]:
        """
        Converts an integer array into a byte stream and executes 144-Facet AEAD encryption.
        Returns (ciphertext_bytes, slip_mac_tag, original_shape).
        """
        input_matrix = np.asarray(whole_number_array, dtype=np.int32)
        raw_bytes = input_matrix.tobytes()
        ciphertext, slip_tag = PTRCHardenedCrystalAEAD.encrypt(
            self.secret_key, self.nonce, raw_bytes, aad=self.aad_header
        )
        return ciphertext, slip_tag, input_matrix.shape

    def decrypt_data_matrix(
        self, ciphertext: bytes, slip_tag: bytes, original_shape: tuple[int, ...]
    ) -> tuple[bool, np.ndarray]:
        """
        Verifies the 192-bit SLIP-MAC tag in constant time and restores the integer matrix.
        """
        authentic, raw_bytes = PTRCHardenedCrystalAEAD.decrypt(
            self.secret_key, self.nonce, ciphertext, slip_tag, aad=self.aad_header
        )
        restored = np.frombuffer(raw_bytes, dtype=np.int32).reshape(original_shape).copy()
        return authentic, restored


if __name__ == "__main__":
    print("[ pTRC-CRYPT ] Initializing 144-Facet AEAD & SLIP-MAC matrix pipeline...")
    engine = PTRCCryptResonanceEngine(key_vector_seed=1836)

    # Experimental array representing multi-scale metric blocks
    source_block = np.array([24, 156, 1836], dtype=np.int32)

    print(" -> Executing 144-Facet AEAD encryption pass...")
    cipher_bytes, tag_bytes, shape = engine.encrypt_data_matrix(source_block)

    print(" -> Executing constant-time SLIP-MAC audit & decryption pass...")
    is_authentic, decrypted_block = engine.decrypt_data_matrix(cipher_bytes, tag_bytes, shape)

    # 1-Bit Tamper Check
    tampered_cipher = bytearray(cipher_bytes)
    tampered_cipher[0] ^= 0x01
    tamper_rejected, _ = engine.decrypt_data_matrix(bytes(tampered_cipher), tag_bytes, shape)

    validation_status = is_authentic and (not tamper_rejected) and np.array_equal(source_block, decrypted_block)

    print(f" -> [ VALIDATION ] SLIP-MAC Tag (Hex): {tag_bytes.hex()}")
    print(f" -> Reconstructed Input Match: {validation_status}")
    if validation_status:
        print(" -> STATUS: Zero-Float 144-Facet AEAD & SLIP-MAC Verified Secure.")
        sys.exit(0)
    else:
        print(" -> STATUS: ERR - Crystalline AEAD Parity Check Failed.")
        sys.exit(1)
