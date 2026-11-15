# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.0
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

"""
pTRC v4.0 512-Bit Zero-Table Primorial Macro-Cascade & 144-Facet AEAD (Python Reference).
File: src/ptrc_crystal_aead.py

Strictly pure integer (-1 adjacent to +1, no zero point), zero-trigonometry,
and bit-identical to embedded/crypto/ptrc_crystal.c.
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

# 8 Pairwise Coprime 1-Byte Non-Mersenne Primes (CRT period > 1.09 * 10^19 takts)
PTRC_KEYGEN_PRIMES: Tuple[int, ...] = (251, 241, 239, 233, 229, 227, 223, 211)

U64_MASK = 0xFFFFFFFFFFFFFFFF
U32_MASK = 0xFFFFFFFF


def ptrc_crypt_z_no_zero(v: int) -> int:
    """Maps signed 32-bit integer into Z \\ {0}: 0 resolves directly to -1."""
    v32 = v & U32_MASK
    if v32 & 0x80000000:
        v32 -= 0x100000000
    return -1 if v32 == 0 else v32


def ptrc_u64_no_zero(v: int) -> int:
    """Maps unsigned 64-bit integer away from zero: 0 resolves to 1."""
    v64 = v & U64_MASK
    return 1 if v64 == 0 else v64


def _gcd_u64(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a


def _read_le64(buf: bytes, offset: int) -> int:
    return int.from_bytes(buf[offset : offset + 8], "little", signed=False)


def _write_le64(v: int) -> bytes:
    return (v & U64_MASK).to_bytes(8, "little", signed=False)


def _rotl64(v: int, shift: int) -> int:
    v &= U64_MASK
    return ((v << shift) | (v >> (64 - shift))) & U64_MASK


def plichta_crossed_mirror(x: int, quadrant: int) -> int:
    """Holographic Crossed Plichta-Mirror reflection across -1 in Z \\ {0}."""
    q = quadrant & 3
    v = (~x) & 0xFF
    if q == 1:
        v = ((v << 3) | (v >> 5)) & 0xFF
    elif q == 2:
        v = ((v << 5) | (v >> 3)) & 0xFF
    elif q == 3:
        v = (((v & 0x0F) << 4) | ((v & 0xF0) >> 4)) & 0xFF
    return 0xFF if v == 0 else v


class PtrcCrystalContext:
    """Pure Python reference matching ptrc_crystal_ctx_t in embedded/crypto/ptrc_crystal.c."""

    def __init__(self, key: bytes, nonce: bytes) -> None:
        if len(key) != PTRC_CRYPT_KEY_BYTES:
            raise ValueError("Key must be 64 bytes (512 bits)")
        if len(nonce) != PTRC_CRYPT_NONCE_BYTES:
            raise ValueError("Nonce must be 16 bytes (128 bits)")

        n0 = _read_le64(nonce, 0)
        n1 = _read_le64(nonce, 8)

        self.macro_mod: List[int] = list((1,)) * PTRC_MACRO_CASCADE_STAGES
        self.macro_state: List[int] = list((1,)) * PTRC_MACRO_CASCADE_STAGES
        self.inner_mod: List[int] = list((1,)) * PTRC_CRYPT_INNER_RINGS
        self.sponge: List[int] = list((1,)) * PTRC_CRYPT_FACETS

        for s in range(PTRC_MACRO_CASCADE_STAGES):
            raw = (_read_le64(key, s * 8) ^ ((n0 + s * 137) & U64_MASK)) & U64_MASK
            mod_s = raw | (1 << 62) | 1
            while _gcd_u64(mod_s, PTRC_PRIMORIAL_210) != 1:
                mod_s += 2
            self.macro_mod[s] = mod_s

            seed_s = (_read_le64(key, ((s + 4) & 7) * 8) ^ n1 ^ PTRC_PRIMORIAL_P15) & U64_MASK
            self.macro_state[s] = ptrc_u64_no_zero(seed_s % mod_s)

        for r in range(PTRC_CRYPT_INNER_RINGS):
            cand = 257 + int((_read_le64(key, 32 + r * 8) % 4096) * 2)
            while _gcd_u64(cand, PTRC_PRIMORIAL_210) != 1:
                cand += 2
            self.inner_mod[r] = cand

        self.takt_counter: int = 1
        self.clock_phase_24: int = 1
        self.session_salt: int = ptrc_u64_no_zero((n0 ^ n1) & U32_MASK) & U32_MASK

        for f in range(PTRC_CRYPT_FACETS):
            mix = self._macro_cascade_step((f + 1) * 137)
            val = int(mix % PTRC_PRIMORIAL_210) - 105
            self.sponge[f] = ptrc_crypt_z_no_zero(val)

        for w in range(PTRC_CRYPT_FACETS * 4):
            m = self._macro_cascade_step((w + 1) * 137)
            idx0 = w % PTRC_CRYPT_FACETS
            idx1 = (idx0 + 37) % PTRC_CRYPT_FACETS
            idx2 = (idx0 + 73) % PTRC_CRYPT_FACETS
            d0 = ptrc_crypt_z_no_zero(m & 0x7FFFFFFF)
            d1 = ptrc_crypt_z_no_zero((m >> 17) & 0x7FFFFFFF)
            d2 = ptrc_crypt_z_no_zero((m >> 33) & 0x7FFFFFFF)
            self.sponge[idx0] = ptrc_crypt_z_no_zero(self.sponge[idx0] ^ d0)
            self.sponge[idx1] = ptrc_crypt_z_no_zero(self.sponge[idx1] + (1 if (d1 & 1) else -1))
            self.sponge[idx2] = ptrc_crypt_z_no_zero(self.sponge[idx2] ^ d2)
            self.takt_counter += 1

    def _macro_cascade_step(self, step_stride: int) -> int:
        acc = (PTRC_PRIMORIAL_P15 ^ self.takt_counter) & U64_MASK
        stride = ptrc_u64_no_zero(step_stride)
        for s in range(PTRC_MACRO_CASCADE_STAGES):
            mod_s = self.macro_mod[s]
            st = (self.macro_state[s] + stride + (acc & U32_MASK) + (s + 1)) % mod_s
            st = ptrc_u64_no_zero(st)
            self.macro_state[s] = st
            acc = (acc ^ ((st * (211 + s * 12)) & U64_MASK)) & U64_MASK
            acc = _rotl64(acc, 13)
        return ptrc_u64_no_zero(acc)

    def next_keystream_byte(self) -> int:
        phase = (self.clock_phase_24 - 1) % PTRC_CRYPT_JUNCTIONS
        macro_out = self._macro_cascade_step((phase + 1) * 156)

        f0 = (macro_out + phase) % PTRC_CRYPT_FACETS
        f1 = (f0 + 37) % PTRC_CRYPT_FACETS
        f2 = (f0 + 73) % PTRC_CRYPT_FACETS

        m0, m1, m2 = self.inner_mod
        r0 = ((self.sponge[f0] & U32_MASK) ^ (macro_out & U32_MASK)) % m0
        r1 = ((self.sponge[f1] & U32_MASK) ^ ((macro_out >> 16) & U32_MASK)) % m1
        r2 = ((self.sponge[f2] & U32_MASK) ^ ((macro_out >> 32) & U32_MASK)) % m2

        combined = ptrc_crypt_z_no_zero((r0 ^ (r1 << 5) ^ (r2 << 11) ^ self.session_salt) & 0x7FFFFFFF)

        if (self.takt_counter % PTRC_TAKT_137) == 0:
            self.sponge[f0] = ptrc_crypt_z_no_zero(~self.sponge[f0])
            self.sponge[f1] = ptrc_crypt_z_no_zero(~self.sponge[f1])
        else:
            step_dir = 1 if (combined & 1) else -1
            self.sponge[f0] = ptrc_crypt_z_no_zero(self.sponge[f0] + step_dir)
            self.sponge[f2] = ptrc_crypt_z_no_zero(self.sponge[f2] ^ combined)

        comb_u32 = combined & U32_MASK
        raw_byte = (comb_u32 ^ (comb_u32 >> 8) ^ (comb_u32 >> 16) ^ ((macro_out >> 48) & 0xFF)) & 0xFF
        out_byte = plichta_crossed_mirror(raw_byte, phase)

        self.takt_counter += 1
        self.clock_phase_24 = (self.clock_phase_24 % PTRC_CRYPT_JUNCTIONS) + 1
        return out_byte

    def xor_stream(self, data: bytes) -> bytes:
        out = bytearray(len(data))
        for i, b in enumerate(data):
            out[i] = b ^ self.next_keystream_byte()
        return bytes(out)


def ptrc_kdf_derive(master_seed: bytes, context_info: bytes = b"") -> Tuple[bytes, bytes]:
    if not master_seed:
        raise ValueError("Master seed must not be empty")

    init_k = bytearray(PTRC_CRYPT_KEY_BYTES)
    init_n = bytearray(PTRC_CRYPT_NONCE_BYTES)
    seed_len = len(master_seed)
    info_len = len(context_info)

    for i in range(PTRC_CRYPT_KEY_BYTES):
        sb = master_seed[i % seed_len]
        ib = context_info[i % info_len] if info_len >= 1 else ((i + 1) & 0xFF)
        init_k[i] = plichta_crossed_mirror((sb ^ ib ^ (i * 137 + 1)) & 0xFF, i)

    for i in range(PTRC_CRYPT_NONCE_BYTES):
        sb = master_seed[(i * 7) % seed_len]
        init_n[i] = plichta_crossed_mirror((sb ^ (i * 211 + 1)) & 0xFF, i + 1)

    ctx = PtrcCrystalContext(bytes(init_k), bytes(init_n))

    for i, b in enumerate(master_seed):
        idx = i % PTRC_CRYPT_FACETS
        ctx.sponge[idx] = ptrc_crypt_z_no_zero(ctx.sponge[idx] ^ ((b << 1) | 1))
        ctx.next_keystream_byte()

    for i, b in enumerate(context_info):
        idx = (i + 37) % PTRC_CRYPT_FACETS
        ctx.sponge[idx] = ptrc_crypt_z_no_zero(ctx.sponge[idx] ^ ((b << 1) | 1))
        ctx.next_keystream_byte()

    out_key = bytes(ctx.next_keystream_byte() for _ in range(PTRC_CRYPT_KEY_BYTES))
    out_nonce = bytes(ctx.next_keystream_byte() for _ in range(PTRC_CRYPT_NONCE_BYTES))
    return out_key, out_nonce


def ptrc_primorial_keygen(session_takt: int, domain_seed: bytes) -> Tuple[bytes, bytes]:
    if not domain_seed:
        raise ValueError("Domain seed must not be empty")

    takt = ptrc_u64_no_zero(session_takt)
    ring_state = bytearray(PTRC_KEYGEN_PRIME_RINGS)
    takt_buf = bytearray(PTRC_KEYGEN_PRIME_RINGS)

    for r in range(PTRC_KEYGEN_PRIME_RINGS):
        prime_r = PTRC_KEYGEN_PRIMES[r]
        res = (takt + r * 137) % prime_r
        if res == 0:
            res = 1
        ring_state[r] = plichta_crossed_mirror(res, r)
        takt_buf[r] = (takt >> (r * 8)) & 0xFF

    out_key, raw_nonce = ptrc_kdf_derive(bytes(ring_state), domain_seed)
    out_nonce = bytearray(raw_nonce)
    for i in range(PTRC_CRYPT_NONCE_BYTES):
        idx = i & 7
        out_nonce[i] ^= ring_state[idx] ^ takt_buf[idx]
    return out_key, bytes(out_nonce)


def _compute_slip_mac(key: bytes, nonce: bytes, aad: bytes, ciphertext: bytes) -> bytes:
    mac_ctx = PtrcCrystalContext(key, nonce)

    for i, b in enumerate(aad):
        v = (b << 1) | 1
        f = i % PTRC_CRYPT_FACETS
        s = (((mac_ctx.session_salt << 7) | (mac_ctx.session_salt >> 25)) ^ v) & U32_MASK
        mac_ctx.session_salt = 1 if s == 0 else s
        mac_ctx.sponge[f] = ptrc_crypt_z_no_zero(mac_ctx.sponge[f] ^ v)
        mac_ctx.next_keystream_byte()

    for i, b in enumerate(ciphertext):
        v = (b << 1) | 1
        f = (i + 73) % PTRC_CRYPT_FACETS
        s = (((mac_ctx.session_salt << 7) | (mac_ctx.session_salt >> 25)) ^ v) & U32_MASK
        mac_ctx.session_salt = 1 if s == 0 else s
        mac_ctx.sponge[f] = ptrc_crypt_z_no_zero(mac_ctx.sponge[f] ^ v)
        mac_ctx.next_keystream_byte()

    len_block = _write_le64(ptrc_u64_no_zero(len(aad))) + _write_le64(ptrc_u64_no_zero(len(ciphertext)))
    for i, b in enumerate(len_block):
        v = (b << 1) | 1
        f = (i + 137) % PTRC_CRYPT_FACETS
        s = (((mac_ctx.session_salt << 7) | (mac_ctx.session_salt >> 25)) ^ v) & U32_MASK
        mac_ctx.session_salt = 1 if s == 0 else s
        mac_ctx.sponge[f] = ptrc_crypt_z_no_zero(mac_ctx.sponge[f] ^ v)
        mac_ctx.next_keystream_byte()

    return bytes(mac_ctx.next_keystream_byte() for _ in range(PTRC_CRYPT_TAG_BYTES))


def ptrc_ct_memcmp(a: bytes, b: bytes) -> int:
    if len(a) != len(b):
        return PTRC_CRYPT_ERR
    diff = 0
    for x, y in zip(a, b):
        diff |= x ^ y
    return PTRC_CRYPT_OK if diff == 0 else PTRC_CRYPT_ERR


def ptrc_aead_encrypt(key: bytes, nonce: bytes, plaintext: bytes, aad: bytes = b"") -> Tuple[bytes, bytes]:
    ctx = PtrcCrystalContext(key, nonce)
    ciphertext = ctx.xor_stream(plaintext)
    tag = _compute_slip_mac(key, nonce, aad, ciphertext)
    return ciphertext, tag


def ptrc_aead_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, aad: bytes = b"") -> Tuple[int, bytes]:
    if len(tag) != PTRC_CRYPT_TAG_BYTES:
        return PTRC_CRYPT_ERR, b""
    expected_tag = _compute_slip_mac(key, nonce, aad, ciphertext)
    if ptrc_ct_memcmp(expected_tag, tag) != PTRC_CRYPT_OK:
        return PTRC_CRYPT_ERR, b""
    ctx = PtrcCrystalContext(key, nonce)
    plaintext = ctx.xor_stream(ciphertext)
    return PTRC_CRYPT_OK, plaintext


class _CCrystalCtx(ctypes.Structure):
    _fields_ = [
        ("macro_mod", ctypes.c_uint64 * PTRC_MACRO_CASCADE_STAGES),
        ("macro_state", ctypes.c_uint64 * PTRC_MACRO_CASCADE_STAGES),
        ("inner_mod", ctypes.c_uint32 * PTRC_CRYPT_INNER_RINGS),
        ("sponge", ctypes.c_int32 * PTRC_CRYPT_FACETS),
        ("takt_counter", ctypes.c_uint64),
        ("clock_phase_24", ctypes.c_uint32),
        ("session_salt", ctypes.c_uint32),
    ]


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
            lib = ctypes.CDLL(str(cand))
            lib.ptrc_crystal_init.argtypes = [
                ctypes.POINTER(_CCrystalCtx),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
            ]
            lib.ptrc_crystal_init.restype = ctypes.c_int

            lib.ptrc_primorial_keygen.argtypes = [
                ctypes.c_uint64,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
            ]
            lib.ptrc_primorial_keygen.restype = ctypes.c_int

            lib.ptrc_kdf_derive.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
            ]
            lib.ptrc_kdf_derive.restype = ctypes.c_int

            lib.ptrc_aead_encrypt.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
            ]
            lib.ptrc_aead_encrypt.restype = ctypes.c_int

            lib.ptrc_aead_decrypt.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
            ]
            lib.ptrc_aead_decrypt.restype = ctypes.c_int

            lib.ptrc_crystal_wipe.argtypes = [ctypes.POINTER(_CCrystalCtx)]
            lib.ptrc_crystal_wipe.restype = None
            return lib
    return None
