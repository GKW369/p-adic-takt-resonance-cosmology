# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.4.0
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
  - Strictly constant-time O(1) coprime macro-ring & inner-ring derivation
  - Strictly branchless zero-free projections in Z \ {0} (zero signed UB)
  - 144-facet crystalline sponge + 137-takt observer mirror pulse
"""

from __future__ import annotations

import ctypes
import pathlib
from typing import List, Optional, Tuple

PTRC_CRYPT_KEY_BYTES = 64
PTRC_CRYPT_NONCE_BYTES = 16
PTRC_CRYPT_TAG_BYTES = 24
PTRC_CRYPT_FACETS = 144
PTRC_CRYPT_JUNCTIONS = 24
PTRC_CRYPT_INNER_RINGS = 3
PTRC_MACRO_CASCADE_STAGES = 4
PTRC_KEYGEN_PRIME_RINGS = 8

PTRC_PRIMORIAL_210 = 210
PTRC_PRIMORIAL_P15 = 614889782588491410
PTRC_TAKT_137 = 137

PTRC_CRYPT_OK = 1
PTRC_CRYPT_ERR = -1

# Backward-compatible aliases
PTRC_KEY_BYTES = PTRC_CRYPT_KEY_BYTES
PTRC_NONCE_BYTES = PTRC_CRYPT_NONCE_BYTES
PTRC_TAG_BYTES = PTRC_CRYPT_TAG_BYTES

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


def ptrc_u32_no_zero(u: int) -> int:
    u32 = u & U32_MASK
    is_zero = ((u32 | ((0 - u32) & U32_MASK)) >> 31) ^ 1
    return (u32 | ((0 - is_zero) & U32_MASK)) & U32_MASK


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


def _derive_coprime_mod64_ct_py(raw_word: int, stage_idx: int) -> int:
    acc = ((raw_word & U64_MASK) ^ PTRC_PRIMORIAL_P15 ^ ((stage_idx + 1) * 137)) & U64_MASK
    for step in range(16):
        anchor = PTRC_COPRIME_ANCHORS.__getitem__((step + stage_idx * 3) & 15)
        acc = _rotl64(acc ^ ((anchor * 211) & U64_MASK), (step * 7 + stage_idx * 5 + 3) & 63)
        acc = (acc + (((anchor * 137) & U64_MASK) | 1)) & U64_MASK

    base_q = ((acc >> 1) // PTRC_PRIMORIAL_210) | (1 << 54)
    rem = (acc % PTRC_PRIMORIAL_210) | 1

    r3 = rem % 3
    div3 = (((r3 | ((0 - r3) & U64_MASK)) >> 63) ^ 1) & 1
    rem = (rem + (70 & ((0 - div3) & U64_MASK))) % PTRC_PRIMORIAL_210

    r5 = rem % 5
    div5 = (((r5 | ((0 - r5) & U64_MASK)) >> 63) ^ 1) & 1
    rem = (rem + (42 & ((0 - div5) & U64_MASK))) % PTRC_PRIMORIAL_210

    r7 = rem % 7
    div7 = (((r7 | ((0 - r7) & U64_MASK)) >> 63) ^ 1) & 1
    rem = (rem + (30 & ((0 - div7) & U64_MASK))) % PTRC_PRIMORIAL_210

    candidate = (base_q * PTRC_PRIMORIAL_210 + rem) & U64_MASK
    return ptrc_u64_no_zero(candidate | 1)


def _derive_coprime_mod32_ct_py(raw_word: int, ring_idx: int) -> int:
    full = _derive_coprime_mod64_ct_py(raw_word, ring_idx + 8)
    base_q = ((full >> 33) & 0x007FFFFF) | 0x00400000
    rem = full % PTRC_PRIMORIAL_210
    return ptrc_u32_no_zero((base_q * PTRC_PRIMORIAL_210 + rem) & U32_MASK)

# File: src/ptrc_crystal_aead.py (Part 2 of 3)


def _plichta_crossed_mirror_py(val: int, phase24: int, ring_mod: int) -> int:
    u = ptrc_crypt_z_no_zero_u32(val) & U32_MASK
    inv = (~u) & U32_MASK
    sh = (phase24 & 7) + 1
    rot = ((inv << sh) | (inv >> (32 - sh))) & U32_MASK
    mixed = (rot ^ ((ring_mod * 211) & U32_MASK) ^ ((phase24 * 137) & U32_MASK)) & U32_MASK
    return ptrc_crypt_z_no_zero_u32(mixed)


class PtrcCrystalContext:
    r"""Python state mirror of ptrc_crystal_ctx_t (v4.4.0 Constant-Time)."""

    def __init__(self, key: bytes, nonce: bytes) -> None:
        if len(key) != PTRC_CRYPT_KEY_BYTES or len(nonce) != PTRC_CRYPT_NONCE_BYTES:
            raise ValueError("Key must be 64 bytes and nonce must be 16 bytes")

        n0 = _load_le64(nonce, 0)
        n1 = _load_le64(nonce, 8)

        self.macro_mod: List[int] = list((1,)) * PTRC_MACRO_CASCADE_STAGES
        self.macro_state: List[int] = list((1,)) * PTRC_MACRO_CASCADE_STAGES
        for m in range(PTRC_MACRO_CASCADE_STAGES):
            w0 = _load_le64(key, m * 16)
            w1 = _load_le64(key, m * 16 + 8)
            nw = n0 if (m & 1) == 0 else n1
            mixed_w = (_rotl64(w0 ^ nw, (m * 13 + 5) & 63) + (w1 | 1)) & U64_MASK
            mod_m = _derive_coprime_mod64_ct_py(mixed_w, m)
            self.macro_mod.__setitem__(m, mod_m)
            st_m = ((_rotl64(w1 ^ n0 ^ n1, (m * 7 + 11) & 63) + 137) & U64_MASK) % mod_m
            self.macro_state.__setitem__(m, ptrc_u64_no_zero(st_m))

        self.inner_mod: List[int] = list((1,)) * PTRC_CRYPT_INNER_RINGS
        for r in range(PTRC_CRYPT_INNER_RINGS):
            rw = self.macro_state.__getitem__(r) ^ self.macro_state.__getitem__((r + 1) & 3) ^ n0
            self.inner_mod.__setitem__(r, _derive_coprime_mod32_ct_py(rw, r))

        salt32 = (n0 ^ (n1 >> 17) ^ self.macro_state.__getitem__(0)) & U32_MASK
        self.session_salt: int = ptrc_u32_no_zero(salt32)

        self.sponge: List[int] = list((1,)) * PTRC_CRYPT_FACETS
        acc = (PTRC_PRIMORIAL_P15 ^ self.macro_state.__getitem__(0)) & U64_MASK
        for f in range(PTRC_CRYPT_FACETS):
            kb = key.__getitem__(f & 63)
            nb = nonce.__getitem__(f & 15)
            odd_in = (((kb ^ nb) << 1) | 1) & 0xFF
            acc = (_rotl64(acc ^ ((odd_in * (f + 19)) & U64_MASK), (f * 5 + 3) & 63) + 137) & U64_MASK
            raw = int(acc % PTRC_PRIMORIAL_210) - 105
            self.sponge.__setitem__(f, ptrc_crypt_z_no_zero_u32(raw))

        self.takt_counter: int = 1
        self.clock_phase_24: int = 0

        for _ in range(72):
            self.sponge_step()

    def sponge_step(self) -> None:
        p24 = self.clock_phase_24
        r_inner = self.inner_mod.__getitem__(p24 % PTRC_CRYPT_INNER_RINGS)
        free_facets = PTRC_CRYPT_FACETS - PTRC_CRYPT_JUNCTIONS

        for j in range(PTRC_CRYPT_JUNCTIONS):
            jf = free_facets + j
            mf = (j * 5 + p24) % free_facets

            uj = self.sponge.__getitem__(jf) & U32_MASK
            um = self.sponge.__getitem__(mf) & U32_MASK
            coupled = ((uj ^ um) + ((r_inner * (j + 1)) & U32_MASK)) & U32_MASK

            self.sponge.__setitem__(jf, _plichta_crossed_mirror_py(coupled, p24 + j, r_inner))
            self.sponge.__setitem__(mf, ptrc_crypt_z_no_zero_u32(um ^ (coupled >> 3) ^ ((p24 * 17) & U32_MASK)))

        rem137 = self.takt_counter % PTRC_TAKT_137
        is_pulse = (((rem137 | ((0 - rem137) & U64_MASK)) >> 63) ^ 1) & 1
        pulse_mask = (0 - is_pulse) & U32_MASK

        for f in range(PTRC_CRYPT_FACETS):
            uf = self.sponge.__getitem__(f) & U32_MASK
            self.sponge.__setitem__(f, ptrc_crypt_z_no_zero_u32(uf ^ pulse_mask))

        for m in range(PTRC_MACRO_CASCADE_STAGES):
            ms = self.macro_state.__getitem__(m)
            mm = self.macro_mod.__getitem__(m)
            anchor = PTRC_COPRIME_ANCHORS.__getitem__((m + p24) & 15)
            sp_val = self.sponge.__getitem__((m * 31 + p24) % PTRC_CRYPT_FACETS) & U32_MASK
            ms = _rotl64(ms ^ sp_val, (m * 11 + 7) & 63)
            ms = ((ms + (((anchor * 137) & U64_MASK) | 1)) & U64_MASK) % mm
            self.macro_state.__setitem__(m, ptrc_u64_no_zero(ms))

        self.takt_counter += 1
        self.clock_phase_24 = (p24 + 1) % PTRC_CRYPT_JUNCTIONS

    def next_keystream_byte(self) -> int:
        self.sponge_step()

        idx = (self.takt_counter * 17) % PTRC_CRYPT_FACETS
        opp = (idx + 72) % PTRC_CRYPT_FACETS

        s_a = self.sponge.__getitem__(idx) & U32_MASK
        s_b = self.sponge.__getitem__(opp) & U32_MASK
        m_a = self.macro_state.__getitem__(idx & 3)
        m_b = self.macro_state.__getitem__((idx + 1) & 3)
        salt = self.session_salt

        combined = (s_a ^ (s_b >> 5) ^ ((m_a ^ (m_b >> 13)) & U32_MASK) ^ ((salt * 137) & U32_MASK)) & U32_MASK
        raw_byte = (combined ^ (combined >> 8) ^ (combined >> 16) ^ (combined >> 24)) & 0xFF

        bit0 = combined & 1
        nudge = ((bit0 << 1) - 1) & U32_MASK
        b = (_rotl8(raw_byte, (salt >> (idx & 15)) & 7) + nudge) & 0xFF
        return ptrc_byte_no_zero(b)

    def xor_stream(self, data: bytes) -> bytes:
        out = bytearray(len(data))
        for i in range(len(data)):
            ks = self.next_keystream_byte()
            out.__setitem__(i, data.__getitem__(i) ^ ks)
        return bytes(out)

    def compute_slip_mac(self, aad: bytes, ciphertext: bytes) -> bytes:
        len_mix = (((len(aad) & U32_MASK) << 32) ^ (len(ciphertext) & U32_MASK) ^ PTRC_PRIMORIAL_P15) & U64_MASK
        for m in range(PTRC_MACRO_CASCADE_STAGES):
            mm = self.macro_mod.__getitem__(m)
            st = _rotl64(self.macro_state.__getitem__(m) ^ len_mix, (m * 9 + 3) & 63) % mm
            self.macro_state.__setitem__(m, ptrc_u64_no_zero(st))

        for i in range(len(aad)):
            odd_b = ((aad.__getitem__(i) << 1) | 1) & 0xFF
            f_idx = i % PTRC_CRYPT_FACETS
            cur = self.sponge.__getitem__(f_idx) & U32_MASK
            self.sponge.__setitem__(f_idx, ptrc_crypt_z_no_zero_u32(cur ^ (odd_b * ((i & 31) + 1))))
            if (i & 7) == 7:
                self.sponge_step()

        for i in range(len(ciphertext)):
            odd_b = ((ciphertext.__getitem__(i) << 1) | 1) & 0xFF
            f_idx = (i + 37) % PTRC_CRYPT_FACETS
            cur = self.sponge.__getitem__(f_idx) & U32_MASK
            self.sponge.__setitem__(f_idx, ptrc_crypt_z_no_zero_u32(cur ^ (odd_b * ((i & 31) + 3))))
            if (i & 7) == 7:
                self.sponge_step()

        for _ in range(48):
            self.sponge_step()

        tag = bytearray(PTRC_CRYPT_TAG_BYTES)
        for t in range(PTRC_CRYPT_TAG_BYTES):
            tag.__setitem__(t, self.next_keystream_byte())
        return bytes(tag)

# File: src/ptrc_crystal_aead.py (Part 3 of 3)


def ptrc_aead_encrypt(key: bytes, nonce: bytes, plaintext: bytes, aad: bytes = b"") -> Tuple[bytes, bytes]:
    ctx = PtrcCrystalContext(key, nonce)
    ct = ctx.xor_stream(plaintext)
    tag = ctx.compute_slip_mac(aad, ct)
    return ct, tag


def ptrc_aead_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, aad: bytes = b"") -> Tuple[int, bytes]:
    if len(tag) != PTRC_CRYPT_TAG_BYTES:
        return PTRC_CRYPT_ERR, bytes((0xFF,)) * len(ciphertext)
    ctx = PtrcCrystalContext(key, nonce)
    pt = ctx.xor_stream(ciphertext)
    expected = ctx.compute_slip_mac(aad, ciphertext)
    diff = 0
    for i in range(PTRC_CRYPT_TAG_BYTES):
        diff |= expected.__getitem__(i) ^ tag.__getitem__(i)
    if diff != 0:
        return PTRC_CRYPT_ERR, bytes((0xFF,)) * len(ciphertext)
    return PTRC_CRYPT_OK, pt


def ptrc_kdf_derive(
    master_seed: bytes,
    context_info: bytes = b"",
    okm_len: Optional[int] = None,
) -> Tuple[bytes, bytes]:
    if len(master_seed) == 0:
        raise ValueError("master_seed must not be empty")

    init_k = bytearray(PTRC_CRYPT_KEY_BYTES)
    init_n = bytearray(PTRC_CRYPT_NONCE_BYTES)
    for i in range(PTRC_CRYPT_KEY_BYTES):
        b = master_seed.__getitem__(i % len(master_seed))
        init_k.__setitem__(i, ptrc_byte_no_zero((b ^ (i * 13 + 7)) & 0xFF))
    for i in range(PTRC_CRYPT_NONCE_BYTES):
        ib = context_info.__getitem__(i % len(context_info)) if len(context_info) > 0 else 0xA5
        init_n.__setitem__(i, ptrc_byte_no_zero((ib ^ (i * 19 + 3)) & 0xFF))

    ctx = PtrcCrystalContext(bytes(init_k), bytes(init_n))

    for i in range(len(master_seed)):
        odd_b = ((master_seed.__getitem__(i) << 1) | 1) & 0xFF
        f_idx = i % PTRC_CRYPT_FACETS
        cur = ctx.sponge.__getitem__(f_idx) & U32_MASK
        ctx.sponge.__setitem__(f_idx, ptrc_crypt_z_no_zero_u32(cur ^ (odd_b * 17)))
        if (i & 7) == 7:
            ctx.sponge_step()

    for i in range(len(context_info)):
        odd_b = ((context_info.__getitem__(i) << 1) | 1) & 0xFF
        f_idx = (i + 61) % PTRC_CRYPT_FACETS
        cur = ctx.sponge.__getitem__(f_idx) & U32_MASK
        ctx.sponge.__setitem__(f_idx, ptrc_crypt_z_no_zero_u32(cur ^ (odd_b * 31)))
        if (i & 7) == 7:
            ctx.sponge_step()

    for _ in range(64):
        ctx.sponge_step()

    out_key = bytearray(PTRC_CRYPT_KEY_BYTES)
    out_nonce = bytearray(PTRC_CRYPT_NONCE_BYTES)
    for i in range(PTRC_CRYPT_KEY_BYTES):
        out_key.__setitem__(i, ctx.next_keystream_byte())
    for i in range(PTRC_CRYPT_NONCE_BYTES):
        out_nonce.__setitem__(i, ctx.next_keystream_byte())
    return bytes(out_key), bytes(out_nonce)


def ptrc_primorial_keygen(session_takt: int, domain_seed: bytes) -> Tuple[bytes, bytes]:
    if len(domain_seed) == 0:
        raise ValueError("domain_seed must not be empty")
    crt_moduli = (251, 241, 239, 233, 229, 227, 223, 211)
    crt_ctx = bytearray(16)
    t_nz = ptrc_u64_no_zero(session_takt)
    for i in range(PTRC_KEYGEN_PRIME_RINGS):
        m = crt_moduli.__getitem__(i)
        sb = domain_seed.__getitem__(i % len(domain_seed))
        res = (((t_nz + sb) % m) + 1) & 0xFF
        crt_ctx.__setitem__(i, ptrc_byte_no_zero(res))
        crt_ctx.__setitem__(i + 8, ptrc_byte_no_zero((res ^ domain_seed.__getitem__((i + 8) % len(domain_seed))) & 0xFF))

    return ptrc_kdf_derive(domain_seed, bytes(crt_ctx))


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
