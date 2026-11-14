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

import numpy as np

MOD_BASE = 210
PRIMORIAL_P15 = 614889782588491410
CONTROL_TAKT = 24
FREE_FACETS = 120
KEY_SHIFT = 48
INVARIANT_LIMIT = 156
RENDER_TAKT_137 = 137
SLIP_TAG_BYTES = 24
PTRC_KEY_BYTES = 64
PTRC_NONCE_BYTES = 16

PRIME_RING_POOL = (11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71)
KEYGEN_PRIME_RINGS = (251, 241, 239, 233, 229, 227, 223, 211)


def rotl8(value: int, shift: int) -> int:
    shift &= 7
    value &= 0xFF
    return ((value << shift) | (value >> ((8 - shift) & 7))) & 0xFF


def ptrc_gcd(a: int, b: int) -> int:
    while b > 0:
        a, b = b, a % b
    return a


def ptrc_decode_macro_ring(k_slice: bytes, stage: int) -> int:
    """Decodes a 64-bit coprime Primorial-anchored ring modulus on-the-fly."""
    raw = 0
    for b in k_slice:
        raw = (raw << 8) | b
    base = (PRIMORIAL_P15 // (stage + 2)) + (raw % (PRIMORIAL_P15 // 8))
    candidate = (base - (base % MOD_BASE)) + ((raw % 48) * 4 + 1)
    while ptrc_gcd(candidate, MOD_BASE) != 1:
        candidate += 2
    return candidate


def plichta_crossed_mirror(b: int, quadrant_phase: int) -> int:
    z_val = (b & 0xFF) - 128
    non_zero = (z_val + 1) if z_val >= 0 else z_val
    reflected = -non_zero
    u_ref = (reflected - 1 + 128) if reflected > 0 else (reflected + 128)
    q_rot = (quadrant_phase & 3) * 2
    return rotl8(u_ref, q_rot)


def plichta_crossed_unmirror(m: int, quadrant_phase: int) -> int:
    q_rot = (8 - ((quadrant_phase & 3) * 2)) & 7
    u_ref = rotl8(m, q_rot)
    z_ref = u_ref - 128
    reflected = (z_ref + 1) if z_ref >= 0 else z_ref
    orig_nz = -reflected
    return ((orig_nz - 1 + 128) if orig_nz > 0 else (orig_nz + 128)) & 0xFF


def verify_tag_ct(tag_a: bytes, tag_b: bytes) -> bool:
    if len(tag_a) != SLIP_TAG_BYTES or len(tag_b) != SLIP_TAG_BYTES:
        return False
    diff = 0
    for a, b in zip(tag_a, tag_b):
        diff |= (a ^ b)
    return diff == 0


class PTRCHardenedCrystalAEAD:
    def __init__(self, key: bytes, nonce: bytes):
        if len(key) != PTRC_KEY_BYTES or len(nonce) != PTRC_NONCE_BYTES:
            raise ValueError("Key must be 64 bytes (512-bit) and Nonce 16 bytes (128-bit).")

        self.macro_mod = list()
        self.macro_state = list()
        for s in range(4):
            mod_s = ptrc_decode_macro_ring(key[s * 8:(s + 1) * 8], s)
            self.macro_mod.append(mod_s)
            k_word = 0
            for b in range(8):
                k_word = (k_word << 8) | key[s * 8 + b]
            n_part = (nonce[s * 4] << 24) | (nonce[s * 4 + 1] << 16) | (nonce[s * 4 + 2] << 8) | nonce[s * 4 + 3]
            mixed_seed = (
                ((k_word ^ ((n_part * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF)) * 6364136223846793005
                 + 1442695040888963407)
                & 0xFFFFFFFFFFFFFFFF
            )
            self.macro_state.append(mixed_seed % mod_s)

        self.junctions = np.zeros(CONTROL_TAKT, dtype=np.uint8)
        self.outer_facets = np.zeros(FREE_FACETS, dtype=np.uint8)
        self.takt_counter = 0

        c_key = key[32:64]
        idx1 = (c_key[0] ^ c_key[16] ^ key[0]) & 0x0F
        idx2 = (idx1 + 1 + ((c_key[1] ^ c_key[17] ^ key[1]) % 15)) & 0x0F
        idx3 = (idx2 + 1 + ((c_key[2] ^ c_key[18] ^ key[2]) % 14)) & 0x0F

        self.dyn_ring_1 = PRIME_RING_POOL[idx1]
        self.dyn_ring_2 = PRIME_RING_POOL[idx2]
        self.dyn_ring_3 = PRIME_RING_POOL[idx3]

        for i in range(CONTROL_TAKT):
            self.junctions[i] = (c_key[i] ^ c_key[(i + 8) & 31] ^ key[i] ^ key[(i + 8) & 31] ^ INVARIANT_LIMIT) & 0xFF

        for i in range(FREE_FACETS):
            k_byte = (c_key[(i * 7) & 31] ^ key[(i * 11) & 31]) & 0xFF
            n_byte = nonce[(i * 5) & 15]
            raw_seed = (k_byte * 13 + n_byte * 17 + i) & 0xFF
            self.outer_facets[i] = plichta_crossed_mirror(raw_seed, i)

        self.crt_phase_1 = (c_key[3] ^ key[3] ^ nonce[0]) % self.dyn_ring_1
        self.crt_phase_2 = (c_key[4] ^ key[4] ^ nonce[1]) % self.dyn_ring_2
        self.crt_phase_3 = (c_key[5] ^ key[5] ^ nonce[2]) % self.dyn_ring_3

        for _ in range(CONTROL_TAKT * CONTROL_TAKT):
            self._lattice_takt_step()

    def _macro_cascade_step(self) -> int:
        fold = 0
        for s in range(4):
            stride = 1836 + (s * 137) + (fold & 0xFFFF)
            st = (self.macro_state[s] + stride) % self.macro_mod[s]
            self.macro_state[s] = st
            fold ^= (st ^ (st >> 17) ^ (st >> 33))
        return (fold ^ (fold >> 8) ^ (fold >> 16) ^ (fold >> 24)) & 0xFF

    def _lattice_takt_step(self) -> None:
        macro_mask = self._macro_cascade_step()
        t = self.takt_counter
        j_idx = t % CONTROL_TAKT
        f_idx_a = (t * 7) % FREE_FACETS
        f_idx_b = (t * 13 + 5) % FREE_FACETS

        self.crt_phase_1 = (self.crt_phase_1 + 5) % self.dyn_ring_1
        self.crt_phase_2 = (self.crt_phase_2 + 7) % self.dyn_ring_2
        self.crt_phase_3 = (self.crt_phase_3 + 11) % self.dyn_ring_3

        crt_mix = ((self.crt_phase_1 * 19) + (self.crt_phase_2 * 17) + (self.crt_phase_3 * 13) + macro_mask) & 0xFF
        base_takt = ((t * CONTROL_TAKT) + KEY_SHIFT) % MOD_BASE

bash record_crypto_demo.sh
