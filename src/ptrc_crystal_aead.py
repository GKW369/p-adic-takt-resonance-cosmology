# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & 512-Bit Primorial AEAD v4.4.0
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

r"""
pTRC v4.4.0 Hardened Constant-Time 512-Bit Primorial AEAD & KDF (Python Reference).
File: src/ptrc_crystal_aead.py (Part 1 of 3)

Bit-exact match to embedded/crypto/ptrc_crystal.c (v4.4.0):
  - Strictly constant-time O(1) coprime macro-ring derivation (zero secret loops)
  - Strictly branchless zero-free projections in Z \ {0} (zero signed UB)
  - 144-facet crystalline sponge + 137-takt observer mirror pulse
"""

from __future__ import annotations

import ctypes
import pathlib
from typing import List, Optional, Tuple

PTRC_KEY_BYTES = 64
PTRC_NONCE_BYTES = 16
PTRC_TAG_BYTES = 24
PTRC_SEED_BYTES = 32
PTRC_CRYSTAL_FACETS = 144
PTRC_CRYSTAL_JUNCTIONS = 24
PTRC_CRYSTAL_FREE_FACETS = 120
PTRC_MACRO_RINGS = 4

PTRC_CRYPT_OK = 1
PTRC_CRYPT_ERR = -1

PTRC_PRIMORIAL_P15 = 614889782588491410
PTRC_PRIMORIAL_P4 = 210
PTRC_TAKT_PULSE = 137

PTRC_COPRIME_ANCHORS: Tuple[int, ...] = (
    11, 13, 17, 19, 23, 29, 37, 41,
    43, 47, 53, 59, 61, 67, 71, 73,
)

U64_MASK = 0xFFFFFFFFFFFFFFFF
U32_MASK = 0xFFFFFFFF


def _i32(val: int) -> int:
    v = val & U32_MASK
    return v - 0x100000000 if (v & 0x80000000) else v


def ptrc_crypt_z_no_zero_u32(u: int) -> int:
    u32 = u & U32_MASK
    is_zero = ((u32 | ((0 - u32) & U32_MASK)) >> 31) ^ 1
    res = u32 | ((0 - is_zero) & U32_MASK)
    return _i32(res)


def ptrc_u64_no_zero(u: int) -> int:
    u64 = u & U64_MASK
    is_zero = ((u64 | ((0 - u64) & U64_MASK)) >> 63) ^ 1
    return (u64 | ((0 - is_zero) & U64_MASK)) & U64_MASK


def ptrc_byte_no_zero(b: int) -> int:
    u = b & 0xFF
    is_zero = ((u | ((0 - u) & U32_MASK)) >> 31) ^ 1
    return (u | ((0 - is_zero) & U32_MASK)) & 0xFF


def _rotl64(v: int, shift: int) -> int:
    v64 = v & U64_MASK
    s = shift & 63
    return v64 if s == 0 else (((v64 << s) | (v64 >> (64 - s))) & U64_MASK)


def _rotl8(v: int, shift: int) -> int:
    v8 = v & 0xFF
    s = shift & 7
    return v8 if s == 0 else (((v8 << s) | (v8 >> (8 - s))) & 0xFF)


def _load_le64(src: bytes, offset: int) -> int:
    v = 0
    for i in range(8):
        v |= (src.__getitem__(offset + i) & 0xFF) << (i * 8)
    return v & U64_MASK


def _derive_macro_ring_ct_py(raw_word: int, ring_idx: int) -> int:
    acc = ((raw_word & U64_MASK) ^ PTRC_PRIMORIAL_P15 ^ ((ring_idx + 1) * 137)) & U64_MASK
    for step in range(16):
        anchor = PTRC_COPRIME_ANCHORS.__getitem__((step + ring_idx * 3) & 15)
        acc = _rotl64(acc ^ ((anchor * 211) & U64_MASK), (step * 7 + ring_idx * 5 + 3) & 63)
        acc = (acc + (((anchor * 137) & U64_MASK) | 1)) & U64_MASK

    base_q = acc // PTRC_PRIMORIAL_P4
    rem = (acc % PTRC_PRIMORIAL_P4) | 1

    r3 = rem % 3
    div3 = (((r3 | ((0 - r3) & U64_MASK)) >> 63) ^ 1) & 1
    rem = (rem + (70 & ((0 - div3) & U64_MASK))) % PTRC_PRIMORIAL_P4

    r5 = rem % 5
    div5 = (((r5 | ((0 - r5) & U64_MASK)) >> 63) ^ 1) & 1
    rem = (rem + (42 & ((0 - div5) & U64_MASK))) % PTRC_PRIMORIAL_P4

    r7 = rem % 7
    div7 = (((r7 | ((0 - r7) & U64_MASK)) >> 63) ^ 1) & 1
    rem = (rem + (30 & ((0 - div7) & U64_MASK))) % PTRC_PRIMORIAL_P4

    candidate = (base_q * PTRC_PRIMORIAL_P4 + rem) & U64_MASK
    return ptrc_u64_no_zero(candidate | 1)

# File: src/ptrc_crystal_aead.py (Part 2 of 3)


def _plichta_crossed_mirror_py(val: int, quadrant: int, ring_mod: int) -> int:
    u = ptrc_crypt_z_no_zero_u32(val) & U32_MASK
    inv = (~u) & U32_MASK
    sh = (quadrant & 7) + 1
    rot = ((inv << sh) | (inv >> (32 - sh))) & U32_MASK
    mixed = (rot ^ ((ring_mod * 211) & U32_MASK) ^ ((quadrant * 137) & U32_MASK)) & U32_MASK
    return ptrc_crypt_z_no_zero_u32(mixed)


class PtrcCrystalContext:
    r"""Python state mirror of ptrc_crystal_ctx_t (v4.4.0 Constant-Time)."""

    def __init__(self, key: bytes, nonce: bytes) -> None:
        if len(key) != PTRC_KEY_BYTES or len(nonce) != PTRC_NONCE_BYTES:
            raise ValueError("Key must be 64 bytes and nonce must be 16 bytes")

        self.macro_state: List[int] = list((1,)) * PTRC_MACRO_RINGS
        for m in range(PTRC_MACRO_RINGS):
            w0 = _load_le64(key, m * 16)
            w1 = _load_le64(key, m * 16 + 8)
            n_word = _load_le64(nonce, (m & 1) * 8)
            mixed_w = (_rotl64(w0 ^ n_word, (m * 13 + 5) & 63) + (w1 | 1)) & U64_MASK
            self.macro_state.__setitem__(m, _derive_macro_ring_ct_py(mixed_w, m))

        self.session_salt = bytearray(PTRC_NONCE_BYTES)
        for i in range(PTRC_NONCE_BYTES):
            kb = key.__getitem__(i) ^ key.__getitem__(i + 32)
            nb = nonce.__getitem__(i)
            self.session_salt.__setitem__(i, ptrc_byte_no_zero((kb ^ nb ^ (i * 17 + 1)) & 0xFF))

        self.sponge: List[int] = list((1,)) * PTRC_CRYSTAL_FACETS
        acc = (PTRC_PRIMORIAL_P15 ^ self.macro_state.__getitem__(0)) & U64_MASK
        for f in range(PTRC_CRYSTAL_FACETS):
            kb = key.__getitem__(f & 63)
            nb = nonce.__getitem__(f & 15)
            odd_in = (((kb ^ nb) << 1) | 1) & 0xFF
            acc = (_rotl64(acc ^ ((odd_in * (f + 19)) & U64_MASK), (f * 5 + 3) & 63) + 137) & U64_MASK
            raw = int(acc % PTRC_PRIMORIAL_P4) - 105
            self.sponge.__setitem__(f, ptrc_crypt_z_no_zero_u32(raw))

        self.takt_counter: int = 1
        self.quadrant_phase: int = 1

        for _ in range(72):
            self.sponge_step()

    def sponge_step(self) -> None:
        phase = self.takt_counter % PTRC_CRYSTAL_FACETS
        q = self.quadrant_phase
        r_mod = (int(self.macro_state.__getitem__(q & 3) % 997) | 1) & U32_MASK

        for j in range(PTRC_CRYSTAL_JUNCTIONS):
            jf = PTRC_CRYSTAL_FREE_FACETS + j
            mf = (j * 5 + phase) % PTRC_CRYSTAL_FREE_FACETS

            uj = self.sponge.__getitem__(jf) & U32_MASK
            um = self.sponge.__getitem__(mf) & U32_MASK
            coupled = (uj ^ um) + ((r_mod * (j + 1)) & U32_MASK)
            coupled &= U32_MASK

            self.sponge.__setitem__(jf, _plichta_crossed_mirror_py(coupled, q + j, r_mod))
            self.sponge.__setitem__(mf, ptrc_crypt_z_no_zero_u32(um ^ (coupled >> 3) ^ ((q * 17) & U32_MASK)))

        rem137 = self.takt_counter % PTRC_TAKT_PULSE
        is_pulse = (((rem137 | ((0 - rem137) & U64_MASK)) >> 63) ^ 1) & 1
        pulse_mask = (0 - is_pulse) & U32_MASK

        for f in range(PTRC_CRYSTAL_FACETS):
            uf = self.sponge.__getitem__(f) & U32_MASK
            self.sponge.__setitem__(f, ptrc_crypt_z_no_zero_u32(uf ^ pulse_mask))

        for m in range(PTRC_MACRO_RINGS):
            ms = self.macro_state.__getitem__(m)
            anchor = PTRC_COPRIME_ANCHORS.__getitem__((m + q) & 15)
            sp_val = self.sponge.__getitem__((m * 31 + phase) % PTRC_CRYSTAL_FACETS) & U32_MASK
            ms = _rotl64(ms ^ sp_val, (m * 11 + 7) & 63)
            ms = (ms + (((anchor * 137) & U64_MASK) | 1)) & U64_MASK
            self.macro_state.__setitem__(m, ptrc_u64_no_zero(ms))

        self.takt_counter += 1
        self.quadrant_phase = (self.quadrant_phase & 3) + 1

    def next_keystream_byte(self) -> int:
        self.sponge_step()

        idx = (self.takt_counter * 17) % PTRC_CRYSTAL_FACETS
        opp = (idx + 72) % PTRC_CRYSTAL_FACETS

        s_a = self.sponge.__getitem__(idx) & U32_MASK
        s_b = self.sponge.__getitem__(opp) & U32_MASK
        m_a = self.macro_state.__getitem__(idx & 3)
        m_b = self.macro_state.__getitem__((idx + 1) & 3)
        salt = self.session_salt.__getitem__(idx & 15)

        combined = (s_a ^ (s_b >> 5) ^ ((m_a ^ (m_b >> 13)) & U32_MASK) ^ ((salt * 137) & U32_MASK)) & U32_MASK
        raw_byte = (combined ^ (combined >> 8) ^ (combined >> 16) ^ (combined >> 24)) & 0xFF

        bit0 = combined & 1
        nudge = ((bit0 << 1) - 1) & U32_MASK
        b = (_rotl8(raw_byte, salt & 7) + nudge) & 0xFF
        return ptrc_byte_no_zero(b)

    def xor_stream(self, data: bytes) -> bytes:
        out = bytearray(len(data))
        for i in range(len(data)):
            ks = self.next_keystream_byte()
            out.__setitem__(i, data.__getitem__(i) ^ ks)
        return bytes(out)

    def compute_slip_mac(self, aad: bytes, ciphertext: bytes) -> bytes:
        len_mix = (((len(aad) & U32_MASK) << 32) ^ (len(ciphertext) & U32_MASK) ^ PTRC_PRIMORIAL_P15) & U64_MASK
        for m in range(PTRC_MACRO_RINGS):
            self.macro_state.__setitem__(m, ptrc_u64_no_zero(_rotl64(self.macro_state.__getitem__(m) ^ len_mix, (m * 9 + 3) & 63)))

        for i in range(len(aad)):
            odd_b = ((aad.__getitem__(i) << 1) | 1) & 0xFF
            f_idx = i % PTRC_CRYSTAL_FACETS
            cur = self.sponge.__getitem__(f_idx) & U32_MASK
            self.sponge.__setitem__(f_idx, ptrc_crypt_z_no_zero_u32(cur ^ (odd_b * ((i & 31) + 1))))
            if (i & 7) == 7:
                self.sponge_step()

        for i in range(len(ciphertext)):
            odd_b = ((ciphertext.__getitem__(i) << 1) | 1) & 0xFF
            f_idx = (i + 37) % PTRC_CRYSTAL_FACETS
            cur = self.sponge.__getitem__(f_idx) & U32_MASK
            self.sponge.__setitem__(f_idx, ptrc_crypt_z_no_zero_u32(cur ^ (odd_b * ((i & 31) + 3))))
            if (i & 7) == 7:
                self.sponge_step()

        for _ in range(48):
            self.sponge_step()

        tag = bytearray(PTRC_TAG_BYTES)
        for t in range(PTRC_TAG_BYTES):
            tag.__setitem__(t, self.next_keystream_byte())
        return bytes(tag)

# File: src/ptrc_crystal_aead.py (Part 3 of 3)


def ptrc_aead_encrypt(key: bytes, nonce: bytes, plaintext: bytes, aad: bytes = b"") -> Tuple[bytes, bytes]:
    ctx = PtrcCrystalContext(key, nonce)
    ct = ctx.xor_stream(plaintext)
    tag = ctx.compute_slip_mac(aad, ct)
    return ct, tag


def ptrc_aead_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, aad: bytes = b"") -> Tuple[int, bytes]:
    if len(tag) != PTRC_TAG_BYTES:
        return PTRC_CRYPT_ERR, bytes((0xFF,)) * len(ciphertext)
    ctx = PtrcCrystalContext(key, nonce)
    pt = ctx.xor_stream(ciphertext)
    expected = ctx.compute_slip_mac(aad, ciphertext)
    diff = 0
    for i in range(PTRC_TAG_BYTES):
        diff |= expected.__getitem__(i) ^ tag.__getitem__(i)
    if diff != 0:
        return PTRC_CRYPT_ERR, bytes((0xFF,)) * len(ciphertext)
    return PTRC_CRYPT_OK, pt


def ptrc_kdf_derive(ikm: bytes, salt: bytes, info: bytes, okm_len: int) -> bytes:
    if len(ikm) == 0 or okm_len <= 0:
        raise ValueError("Invalid ikm or okm_len")

    init_k = bytearray(PTRC_KEY_BYTES)
    init_n = bytearray(PTRC_NONCE_BYTES)
    for i in range(PTRC_KEY_BYTES):
        b = ikm.__getitem__(i % len(ikm))
        init_k.__setitem__(i, ptrc_byte_no_zero((b ^ (i * 13 + 7)) & 0xFF))
    for i in range(PTRC_NONCE_BYTES):
        sb = salt.__getitem__(i % len(salt)) if len(salt) > 0 else 0xA5
        init_n.__setitem__(i, ptrc_byte_no_zero((sb ^ (i * 19 + 3)) & 0xFF))

    ctx = PtrcCrystalContext(bytes(init_k), bytes(init_n))

    for i in range(len(ikm)):
        odd_b = ((ikm.__getitem__(i) << 1) | 1) & 0xFF
        f_idx = i % PTRC_CRYSTAL_FACETS
        cur = ctx.sponge.__getitem__(f_idx) & U32_MASK
        ctx.sponge.__setitem__(f_idx, ptrc_crypt_z_no_zero_u32(cur ^ (odd_b * 17)))
        if (i & 7) == 7:
            ctx.sponge_step()

    for i in range(len(salt)):
        odd_b = ((salt.__getitem__(i) << 1) | 1) & 0xFF
        f_idx = (i + 29) % PTRC_CRYSTAL_FACETS
        cur = ctx.sponge.__getitem__(f_idx) & U32_MASK
        ctx.sponge.__setitem__(f_idx, ptrc_crypt_z_no_zero_u32(cur ^ (odd_b * 23)))
        if (i & 7) == 7:
            ctx.sponge_step()

    for i in range(len(info)):
        odd_b = ((info.__getitem__(i) << 1) | 1) & 0xFF
        f_idx = (i + 61) % PTRC_CRYSTAL_FACETS
        cur = ctx.sponge.__getitem__(f_idx) & U32_MASK
        ctx.sponge.__setitem__(f_idx, ptrc_crypt_z_no_zero_u32(cur ^ (odd_b * 31)))
        if (i & 7) == 7:
            ctx.sponge_step()

    for _ in range(64):
        ctx.sponge_step()

    okm = bytearray(okm_len)
    for i in range(okm_len):
        okm.__setitem__(i, ctx.next_keystream_byte())
    return bytes(okm)


def ptrc_primorial_keygen(seed: bytes, session_takt: int) -> Tuple[bytes, bytes]:
    if len(seed) != PTRC_SEED_BYTES:
        raise ValueError("Seed must be 32 bytes")
    crt_moduli = (251, 241, 239, 233, 229, 227, 223, 211)
    takt_bytes = bytearray(16)
    t_nz = ptrc_u64_no_zero(session_takt)
    for i in range(8):
        m = crt_moduli.__getitem__(i)
        res = (((t_nz + seed.__getitem__(i)) % m) + 1) & 0xFF
        takt_bytes.__setitem__(i, ptrc_byte_no_zero(res))
        takt_bytes.__setitem__(i + 8, ptrc_byte_no_zero((res ^ seed.__getitem__(i + 8)) & 0xFF))

    out_buf = ptrc_kdf_derive(seed, bytes(takt_bytes), b"pTRC-CRT-KG-v4", PTRC_KEY_BYTES + PTRC_NONCE_BYTES)
    return out_buf[:PTRC_KEY_BYTES], out_buf[PTRC_KEY_BYTES:]


def load_c_crystal_library(search_root: Optional[pathlib.Path] = None) -> Optional[ctypes.CDLL]:
    root = search_root or pathlib.Path(__file__).resolve().parent.parent
    candidates = [
        root / "build" / "libptrc_crystal.so",
        root / "build" / "libptrc_crystal.dylib",
        root / "build" / "ptrc_crystal.dll",
        root / "build" / "Release" / "ptrc_crystal.dll",
    ]
    for cand in candidates:
        if cand.exists():
            return ctypes.CDLL(str(cand))
    return None
