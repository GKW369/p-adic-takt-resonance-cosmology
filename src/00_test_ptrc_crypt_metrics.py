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
pTRC Framework - Production Cryptographic Avalanche & Entropy Audit (v4.0 512-Bit)
Evaluates:
  1. Strict Avalanche Criterion (SAC) across all 512 Key Bits, 128 Nonce Bits, and Plaintext Bits.
  2. Shannon Entropy (bits/byte) over multi-kilobyte ciphertext streams.
  3. 192-Bit SLIP-MAC Tag Avalanche diffusion.
"""

import math
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ptrc_crystal_aead import PTRCHardenedCrystalAEAD


def hamming_distance(b1: bytes, b2: bytes) -> int:
    """Counts differing bits between two equal-length byte sequences."""
    return sum((x ^ y).bit_count() for x, y in zip(b1, b2))


def shannon_entropy(data: bytes) -> float:
    """Computes Shannon entropy in bits per byte (ideal random = 8.0000)."""
    if not data:
        return 0.0
    counts = [0] * 256
    for byte in data:
        counts[byte] += 1
    total = len(data)
    entropy = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            entropy -= p * math.log2(p)
    return entropy


def run_sac_audit() -> bool:
    print("==========================================================================")
    print("  pTRC PRODUCTION AUDIT: 512-BIT STRICT AVALANCHE & ENTROPY METRICS (v4.0)")
    print("==========================================================================")

    base_key, base_nonce = PTRCHardenedCrystalAEAD.derive_key_and_nonce(
        b"GKW369-SAC-BENCHMARK-MASTER-KEY-2026",
        b"PTRC:SAC-AUDIT|P15-PRIMORDIAL",
    )
    aad = b"PTRC-HEADER-V4-512BIT"
    plaintext = bytes((i * 73 + 19) & 0xFF for i in range(64))  # 512-bit block

    ref_ct, ref_tag = PTRCHardenedCrystalAEAD.encrypt(base_key, base_nonce, plaintext, aad=aad)
    total_out_bits = (len(ref_ct) + len(ref_tag)) * 8

    # 1. Full 512-Bit Key Avalanche (flip every single bit 0..511)
    key_flip_ratios = []
    for byte_idx in range(64):
        for bit_idx in range(8):
            mod_key = bytearray(base_key)
            mod_key[byte_idx] ^= 1 << bit_idx
            ct, tag = PTRCHardenedCrystalAEAD.encrypt(bytes(mod_key), base_nonce, plaintext, aad=aad)
            diff = hamming_distance(ref_ct + ref_tag, ct + tag)
            key_flip_ratios.append((diff / total_out_bits) * 100.0)

    avg_key_sac = sum(key_flip_ratios) / len(key_flip_ratios)

    # 2. Full 128-Bit Nonce Avalanche (flip every single bit 0..127)
    nonce_flip_ratios = []
    for byte_idx in range(16):
        for bit_idx in range(8):
            mod_nonce = bytearray(base_nonce)
            mod_nonce[byte_idx] ^= 1 << bit_idx
            ct, tag = PTRCHardenedCrystalAEAD.encrypt(base_key, bytes(mod_nonce), plaintext, aad=aad)
            diff = hamming_distance(ref_ct + ref_tag, ct + tag)
            nonce_flip_ratios.append((diff / total_out_bits) * 100.0)

    avg_nonce_sac = sum(nonce_flip_ratios) / len(nonce_flip_ratios)

    # 3. 192-Bit SLIP-MAC Tag Avalanche under 1-Bit Plaintext Perturbations
    tag_bits = len(ref_tag) * 8
    tag_flip_ratios = []
    for byte_idx in range(len(plaintext)):
        for bit_idx in range(8):
            mod_pt = bytearray(plaintext)
            mod_pt[byte_idx] ^= 1 << bit_idx
            _, tag = PTRCHardenedCrystalAEAD.encrypt(base_key, base_nonce, bytes(mod_pt), aad=aad)
            diff = hamming_distance(ref_tag, tag)
            tag_flip_ratios.append((diff / tag_bits) * 100.0)

    avg_tag_sac = sum(tag_flip_ratios) / len(tag_flip_ratios)

    # 4. Shannon Entropy over 16 KB zero-input stream
    zero_stream = b"\x00" * 16384
    stream_ct, _ = PTRCHardenedCrystalAEAD.encrypt(base_key, base_nonce, zero_stream, aad=aad)
    ent = shannon_entropy(stream_ct)

    print(f" -> 512-Bit Key SAC Diffusion   : {avg_key_sac:.4f}% (Target: 50.00% +/- 2.0%)")
    print(f" -> 128-Bit Nonce SAC Diffusion : {avg_nonce_sac:.4f}% (Target: 50.00% +/- 2.0%)")
    print(f" -> 192-Bit SLIP-MAC Tag SAC    : {avg_tag_sac:.4f}% (Target: 50.00% +/- 2.0%)")
    print(f" -> 16 KB Ciphertext Entropy    : {ent:.6f} bits/byte (Ideal: 8.000000)")

    passed = (
        48.0 <= avg_key_sac <= 52.0
        and 48.0 <= avg_nonce_sac <= 52.0
        and 48.0 <= avg_tag_sac <= 52.0
        and ent >= 7.985
    )

    print("==========================================================================")
    if passed:
        print("  STATUS: CRYPTOGRAPHIC METRICS VERIFIED (STRICT AVALANCHE PASSED)")
        return True
    print("  STATUS: CRYPTOGRAPHIC METRICS OUTSIDE TOLERANCE")
    return False


if __name__ == "__main__":
    sys.exit(0 if run_sac_audit() else 1)
