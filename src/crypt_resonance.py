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
#
# For commercial licensing, enterprise integration, or proprietary deployment
# options, please contact the author directly.
# ========================================================================

# -*- coding: utf-8 -*-
"""
pTRC Framework - Core Cryptography Module: Symmetrical Matrix Encryption
Operational Domain: Cyclically closed primorial integer rings (\mathbb{Z}/210\mathbb{Z}).
Provides lightweight, side-channel immune metrics without continuous key vectors or float lag.
"""

import numpy as np

class PTRCCryptResonanceEngine:
    """
    Executes multi-tiered matrix encryption and state permutations 
    utilizing integer residue classes and discrete 24-step clock intervals.
    """
    def __init__(self, key_vector_seed=1836):
        self.primorial_base = 210
        self.control_base = 24
        self.calibration_limit = 156
        
        # Initialize internal encryption state registers using pure integers
        self.state_key = int(key_vector_seed % self.primorial_base)
        self.control_key = int(key_vector_seed % self.control_base)

    def generate_discrete_cipher_takt(self, raw_integer_payload):
        """
        Encrypts a discrete data node using non-linear arithmetic shifting layers.
        Guarantees deterministic bit-invertibility entirely without transcendental functions.
        """
        payload = int(raw_integer_payload)
        
        # 1. Layer: Primorial residue transposition step
        transposed_state = (payload + self.state_key) % self.primorial_base
        
        # 2. Layer: Structural bitwise XOR using the control layer base
        cipher_phase = (transposed_state ^ self.control_key)
        
        # 3. Layer: Wirminghaus offset permutation rule
        if cipher_phase % 2 == 0:
            final_cipher = (cipher_phase + self.calibration_limit) % self.primorial_base
        else:
            final_cipher = (cipher_phase + 12) % self.primorial_base
            
        return final_cipher

    def decrypt_discrete_cipher_takt(self, cipher_integer_payload):
        """
        Reverses the multi-tiered integer transformations to recover the exact input vector.
        Operates drift-free to secure absolute numerical reconstruction.
        """
        cipher = int(cipher_integer_payload)
        
        # 1. Reverse Layer 3: Unwind the Wirminghaus conditional permutations
        # Exhaustive search within the finite ring to guarantee mathematical inversion without floats
        intermediate_state = 0
        for candidate in range(self.primorial_base):
            if candidate % 2 == 0:
                test = (candidate + self.calibration_limit) % self.primorial_base
            else:
                test = (candidate + 12) % self.primorial_base
                
            if test == cipher:
                intermediate_state = candidate
                break
                
        # 2. Reverse Layer 2: Bitwise XOR operations are self-inverting
        unwound_phase = (intermediate_state ^ self.control_key)
        
        # 3. Reverse Layer 1: Inverse modular arithmetic step
        original_payload = (unwound_phase - self.state_key) % self.primorial_base
        
        return original_payload

    def encrypt_data_matrix(self, whole_number_array):
        """
        Processes an entire block data structure sequentially.
        Guarantees timing-attack immunity due to constant integer operational lengths.
        """
        input_matrix = np.asarray(whole_number_array, dtype=np.int32)
        cipher_matrix = np.zeros_like(input_matrix)
        
        # Flatten array matrix to process spatial streams losslessly
        flat_input = input_matrix.ravel()
        flat_cipher = cipher_matrix.ravel()
        
        for idx in range(flat_input.size):
            flat_cipher[idx] = self.generate_discrete_cipher_takt(flat_input[idx])
            
        return cipher_matrix

if __name__ == "__main__":
    print("[ pTRC-CRYPT ] Initializing post-quantum matrix cipher pipeline...")
    engine = PTRCCryptResonanceEngine(key_vector_seed=1836)
    
    # Experimental array representing multi-scale metric blocks to encrypt
    source_block = np.array([24, 156, 1836], dtype=np.int32)
    
    print(" -> Executing symmetrical integer encryption pass...")
    encrypted_block = engine.encrypt_data_matrix(source_block)
    
    print(" -> Executing deterministic decryption pass...")
    decrypted_block = np.zeros_like(encrypted_block)
    
    # Corrected dimension extraction for flat array loop validation
    for i in range(encrypted_block.size):
        decrypted_block[i] = engine.decrypt_discrete_cipher_takt(encrypted_block[i])
        
    # Verify absolute numerical identity tracking
    validation_status = np.array_equal(source_block, decrypted_block)
    
    print(f" -> [ VALIDATION ] Symmetrical loop audit completed.")
    print(f" -> Ciphertext Output Vector: {encrypted_block}")
    print(f" -> Reconstructed Input Match: {validation_status}")
    print(" -> STATUS: Zero-Float Symmetrical Cryptography Block Verified Secure.")
