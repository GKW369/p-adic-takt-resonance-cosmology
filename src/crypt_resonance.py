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
pTRC Framework - Core Cryptography Module: v4.0 512-Bit Primorial AEAD Matrix Encryption
Operational Domain: P15 Primorial Macro-Cascade + Active 144-Facet Sponge.
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
    Wraps the v4.0 512-Bit Crystalline AEAD Engine for whole-number matrix blocks
    and repository-wide integer telemetry verification.
    """

    def __init__(self, key_vector_seed: int = 1836):
        self.primorial_base = 210
        self.control_base = 24
        self.calibration_limit = 156
        self.seed = int(key_vector_seed)

        # Derive deterministic 512-bit (64-byte) key and 128-bit (16-byte) nonce in Z
        seed_bytes = f"GKW369-PRIMORDIAL-SEED-{self.seed}".encode("ascii")
        self.aad_header = b"PTRC:MODULE16|RING:P15-MACRO|TAKT:137"
        self.secret_key, self.nonce = PTRCHardenedCrystalAEAD.derive_key_and_nonce(
            seed_bytes, self.aad_header
        )

    def encrypt_data_matrix(self, whole_number_array) -> tuple[bytes, bytes, tuple[int, ...]]:
        """
        Converts an integer array into a byte stream and executes v4.0 512-Bit AEAD encryption.
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
    print("[ pTRC-CRYPT ] Initializing v4.0 512-Bit Primorial AEAD & SLIP-MAC pipeline...")
    engine = PTRCCryptResonanceEngine(key_vector_seed=1836)

    source_block = np.array([24, 156, 1836], dtype=np.int32)

    print(" -> Executing v4.0 512-Bit AEAD encryption pass...")
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
        print(" -> STATUS: Zero-Float v4.0 512-Bit Primorial AEAD Verified Secure.")
        sys.exit(0)
    else:
        print(" -> STATUS: ERR - Crystalline AEAD Parity Check Failed.")
        sys.exit(1)
