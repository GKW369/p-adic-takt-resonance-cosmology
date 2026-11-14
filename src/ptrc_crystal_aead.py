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

        self.macro_mod = [ptrc_decode_macro_ring(key[s * 8:(s + 1) * 8], s) for s in range(4)]
        self.macro_state = []
        for s in range(4):
            n_part = (nonce[s * 4] << 24) | (nonce[s * 4 + 1] << 16) | (nonce[s * 4 + 2] << 8) | nonce[s * 4 + 3]
            self.macro_state.append(n_part % self.macro_mod[s])

        self.junctions = np.zeros(CONTROL_TAKT, dtype=np.uint8)
        self.outer_facets = np.zeros(FREE_FACETS, dtype=np.uint8)
        self.takt_counter = 0

        c_key = key[32:64]
        idx1 = (c_key[0] ^ c_key[16]) & 0x0F
        idx2 = (idx1 + 1 + ((c_key[1] ^ c_key[17]) % 15)) & 0x0F
        idx3 = (idx2 + 1 + ((c_key[2] ^ c_key[18]) % 14)) & 0x0F

        self.dyn_ring_1 = PRIME_RING_POOL[idx1]
        self.dyn_ring_2 = PRIME_RING_POOL[idx2]
        self.dyn_ring_3 = PRIME_RING_POOL[idx3]

        for i in range(CONTROL_TAKT):
            self.junctions[i] = (c_key[i] ^ c_key[(i + 8) & 31] ^ INVARIANT_LIMIT) & 0xFF

        for i in range(FREE_FACETS):
            k_byte = c_key[(i * 7) & 31]
            n_byte = nonce[(i * 5) & 15]
            raw_seed = (k_byte * 13 + n_byte * 17 + i) & 0xFF
            self.outer_facets[i] = plichta_crossed_mirror(raw_seed, i)

        self.crt_phase_1 = (c_key[3] ^ nonce[0]) % self.dyn_ring_1
        self.crt_phase_2 = (c_key[4] ^ nonce[1]) % self.dyn_ring_2
        self.crt_phase_3 = (c_key[5] ^ nonce[2]) % self.dyn_ring_3

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

        j_val = int(self.junctions[j_idx])
        f_a = int(self.outer_facets[f_idx_a])
        f_b = int(self.outer_facets[f_idx_b])

        mixed = ((j_val ^ base_takt ^ macro_mask) * 11 + f_a + crt_mix) & 0xFF
        mixed = rotl8(mixed, 3) ^ f_b

        new_j = ((j_val + mixed) * 7 + 1) & 0xFF
        self.junctions[j_idx] = new_j
        self.outer_facets[f_idx_a] = (f_a ^ rotl8(mixed, 5)) & 0xFF
        self.outer_facets[f_idx_b] = ((f_b + new_j) ^ crt_mix) & 0xFF

        if (t % RENDER_TAKT_137) == 0:
            frame_parity = INVARIANT_LIMIT ^ macro_mask
            for k in range(CONTROL_TAKT):
                frame_parity ^= rotl8(int(self.junctions[k]), k & 7)
            for f in range(FREE_FACETS):
                h_mirror = plichta_crossed_mirror(int(self.outer_facets[f]), f & 3)
                self.outer_facets[f] = ((h_mirror + frame_parity) ^ int(self.junctions[f % CONTROL_TAKT])) & 0xFF

        self.takt_counter += 1

    def absorb_aad(self, aad: bytes) -> None:
        for b in aad:
            j_idx = self.takt_counter % CONTROL_TAKT
            f_idx = (self.takt_counter * 13) % FREE_FACETS
            self.junctions[j_idx] ^= b
            self.outer_facets[f_idx] = (int(self.outer_facets[f_idx]) + plichta_crossed_mirror(b, j_idx)) & 0xFF
            self._lattice_takt_step()

    def finalize_slip_tag(self, aad_len: int, payload_len: int) -> bytes:
        len_block = [
            aad_len & 0xFF, (aad_len >> 8) & 0xFF, (aad_len >> 16) & 0xFF, (aad_len >> 24) & 0xFF,
            payload_len & 0xFF, (payload_len >> 8) & 0xFF, (payload_len >> 16) & 0xFF, (payload_len >> 24) & 0xFF,
        ]
        for i, lb in enumerate(len_block):
            self.junctions[i] ^= lb
            idx = (i * 15) % FREE_FACETS
            self.outer_facets[idx] = (int(self.outer_facets[idx]) + lb) & 0xFF

        for _ in range(CONTROL_TAKT * CONTROL_TAKT):
            self._lattice_takt_step()

        tag = bytearray(SLIP_TAG_BYTES)
        for i in range(SLIP_TAG_BYTES):
            outer_fold = 0
            for k in range(5):
                outer_fold ^= rotl8(int(self.outer_facets[i * 5 + k]), k + 1)
            tag[i] = ((int(self.junctions[i]) + outer_fold) ^ INVARIANT_LIMIT) & 0xFF
        return bytes(tag)

    def wipe(self) -> None:
        self.junctions.fill(0)
        self.outer_facets.fill(0)
        self.macro_state = [0, 0, 0, 0]
        self.takt_counter = 0

    @classmethod
    def derive_key_and_nonce(cls, master_seed: bytes, context_info: bytes = b"") -> tuple[bytes, bytes]:
        base_k = bytes((((i + 1) * 19 + INVARIANT_LIMIT) ^ KEY_SHIFT) & 0xFF for i in range(PTRC_KEY_BYTES))
        base_n = bytes((((i + 1) * 23 + RENDER_TAKT_137) & 0xFF) for i in range(PTRC_NONCE_BYTES))

        ctx = cls(base_k, base_n)
        ctx.absorb_aad(master_seed)
        ctx.absorb_aad(context_info)

        for _ in range(CONTROL_TAKT * CONTROL_TAKT):
            ctx._lattice_takt_step()

        out_key = bytearray(PTRC_KEY_BYTES)
        for i in range(PTRC_KEY_BYTES):
            ctx._lattice_takt_step()
            out_key[i] = int(ctx.junctions[i % CONTROL_TAKT]) ^ int(ctx.outer_facets[(i * 7) % FREE_FACETS])

        out_nonce = bytearray(PTRC_NONCE_BYTES)
        for i in range(PTRC_NONCE_BYTES):
            ctx._lattice_takt_step()
            out_nonce[i] = (int(ctx.junctions[(i * 3) % CONTROL_TAKT]) + int(ctx.outer_facets[(i * 11) % FREE_FACETS])) & 0xFF

        ctx.wipe()
        return bytes(out_key), bytes(out_nonce)

    @classmethod
    def encrypt(cls, key: bytes, nonce: bytes, plaintext: bytes, aad: bytes = b"") -> tuple[bytes, bytes]:
        ctx = cls(key, nonce)
        ctx.absorb_aad(aad)
        out = bytearray(len(plaintext))

        for i, b in enumerate(plaintext):
            ctx._lattice_takt_step()
            j_idx = ctx.takt_counter % CONTROL_TAKT
            f_idx = (ctx.takt_counter * 11) % FREE_FACETS
            keystream = rotl8(int(ctx.junctions[j_idx]), 2) ^ int(ctx.outer_facets[f_idx])
            q_phase = int(ctx.junctions[j_idx]) ^ (ctx.crt_phase_1 & 0xFF)

            mirrored = plichta_crossed_mirror(b, q_phase)
            cipher_byte = (mirrored + keystream) & 0xFF
            out[i] = cipher_byte

            fb_idx = (j_idx * 5 + ctx.crt_phase_2) % FREE_FACETS
            ctx.outer_facets[fb_idx] = (int(ctx.outer_facets[fb_idx]) + cipher_byte) ^ keystream

        tag = ctx.finalize_slip_tag(len(aad), len(plaintext))
        ctx.wipe()
        return bytes(out), tag

    @classmethod
    def decrypt(cls, key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, aad: bytes = b"") -> tuple[bool, bytes]:
        ctx = cls(key, nonce)
        ctx.absorb_aad(aad)
        out = bytearray(len(ciphertext))

        for i, cipher_byte in enumerate(ciphertext):
            ctx._lattice_takt_step()
            j_idx = ctx.takt_counter % CONTROL_TAKT
            f_idx = (ctx.takt_counter * 11) % FREE_FACETS
            keystream = rotl8(int(ctx.junctions[j_idx]), 2) ^ int(ctx.outer_facets[f_idx])
            q_phase = int(ctx.junctions[j_idx]) ^ (ctx.crt_phase_1 & 0xFF)

            mirrored = (cipher_byte - keystream) & 0xFF
            out[i] = plichta_crossed_unmirror(mirrored, q_phase)

            fb_idx = (j_idx * 5 + ctx.crt_phase_2) % FREE_FACETS
            ctx.outer_facets[fb_idx] = (int(ctx.outer_facets[fb_idx]) + cipher_byte) ^ keystream

        computed_tag = ctx.finalize_slip_tag(len(aad), len(ciphertext))
        ctx.wipe()

        if not verify_tag_ct(computed_tag, tag):
            return False, bytes(len(ciphertext))
        return True, bytes(out)
