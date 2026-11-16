# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Post-Quantum Ring-KEM v4.2
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
pTRC v4.2 Discrete 1-Bit Integer Physics & Post-Quantum Ring-KEM (Python Reference).
File: src/ptrc_pq_kem.py

Bit-exact match to embedded/crypto/ptrc_pq_kem.c:
  - Non-Mersenne lattice prime q = 7681 (gcd(7681, 210) == 1)
  - Strict Z_{7681} \ {0} centered ring arithmetic (zero maps to -1)
  - Zero lookup tables, zero floats, deterministic 144-facet sponge expansion
  - Outputs a 512-bit (64-byte) shared secret directly compatible with ptrc_crystal_aead
"""

from __future__ import annotations

import ctypes
import pathlib
from typing import List, Optional, Tuple

PTRC_KEM_Q = 7681
PTRC_KEM_HALF_Q = 3840
PTRC_KEM_QUARTER_Q = 1920

PTRC_KEM_K = 2
PTRC_KEM_N = 256
PTRC_KEM_FACETS = 144
PTRC_KEM_TAKT_137 = 137
PTRC_KEM_PRIMORIAL_210 = 210

PTRC_KEM_SEED_BYTES = 32
PTRC_KEM_MSG_BYTES = 32
PTRC_KEM_SS_BYTES = 64
PTRC_KEM_PK_BYTES = 1056
PTRC_KEM_SK_BYTES = 1024
PTRC_KEM_CT_BYTES = 1152

PTRC_KEM_OK = 1
PTRC_KEM_ERR = -1

U64_MASK = 0xFFFFFFFFFFFFFFFF
U32_MASK = 0xFFFFFFFF


def _i32(val: int) -> int:
    v = val & U32_MASK
    return v - 0x100000000 if (v & 0x80000000) else v


def _c_shr_i32(val: int, shift: int) -> int:
    return _i32(val) >> shift


def ptrc_kem_z_no_zero(v: int) -> int:
    v32 = _i32(v)
    return -1 if v32 == 0 else v32


def ptrc_kem_mod_q_no_zero(x: int) -> int:
    """Centered modular reduction into Z_{7681} \ {0} = {-3840..-1, +1..+3840}."""
    x32 = _i32(x)
    # C11 signed remainder semantics
    r = abs(x32) % PTRC_KEM_Q
    if x32 < 0 and r != 0:
        r = -r
    if r < 0:
        r += PTRC_KEM_Q
    if r > PTRC_KEM_HALF_Q:
        r -= PTRC_KEM_Q
    if r == 0:
        r = -1
    return r


class _PtrcKemSponge:
    """Internal 144-facet Z \ {0} sponge matching ptrc_kem_ctx_t in C11."""

    def __init__(self, seed: bytes, domain: int) -> None:
        acc = (614889782588491410 ^ (((domain | 1) & 0xFF) * 137)) & U64_MASK
        self.sponge: List[int] = list((1,)) * PTRC_KEM_FACETS
        seed_len = len(seed)
        for f in range(PTRC_KEM_FACETS):
            sb = seed.__getitem__(f % seed_len) if seed_len > 0 else 0xFF
            odd_b = ((sb << 1) | 1) & 0xFF
            acc = ((acc * 211) ^ (odd_b * (f + 17))) + 137
            acc &= U64_MASK
            acc ^= (acc >> 13)
            raw = int(acc % PTRC_KEM_PRIMORIAL_210) - 105
            self.sponge.__setitem__(f, ptrc_kem_z_no_zero(raw))
        self.takt_counter: int = 1
        self.quadrant_phase: int = 1

    def next_word(self) -> int:
        idx = (self.takt_counter * 37) % PTRC_KEM_FACETS
        opp = (idx + 73) % PTRC_KEM_FACETS
        jnc = (idx + 24) % PTRC_KEM_FACETS

        a = self.sponge.__getitem__(idx)
        b = self.sponge.__getitem__(opp)
        c = self.sponge.__getitem__(jnc)

        mixed = ptrc_kem_z_no_zero((~a) + (b ^ c) + (self.quadrant_phase * 11))
        self.sponge.__setitem__(idx, mixed)
        self.sponge.__setitem__(opp, ptrc_kem_z_no_zero(b + _c_shr_i32(mixed, 2)))

        if (self.takt_counter % PTRC_KEM_TAKT_137) == 0:
            for f in range(PTRC_KEM_FACETS):
                self.sponge.__setitem__(f, ptrc_kem_z_no_zero(~self.sponge.__getitem__(f)))

        self.takt_counter += 1
        self.quadrant_phase = (self.quadrant_phase & 3) + 1
        return mixed

    def sample_noise(self) -> int:
        v = self.next_word()
        mag = (abs(v) & 1) + 1
        return -mag if v < 0 else mag


def _expand_a_poly(seed_a: bytes, row: int, col: int) -> List[int]:
    tag = (((row + 1) * 17) ^ ((col + 1) * 31) | 1) & 0xFF
    local_ctx = _PtrcKemSponge(seed_a, tag)
    out = list((1,)) * PTRC_KEM_N
    for i in range(PTRC_KEM_N):
        raw = local_ctx.next_word()
        out.__setitem__(i, ptrc_kem_mod_q_no_zero(raw * 53 + i * 137))
    return out


def _poly_mul_acc(acc: List[int], a: List[int], b: List[int]) -> None:
    for i in range(PTRC_KEM_N):
        ai = a.__getitem__(i)
        for j in range(PTRC_KEM_N):
            prod = ai * b.__getitem__(j)
            k = i + j
            if k < PTRC_KEM_N:
                acc.__setitem__(k, _i32(acc.__getitem__(k) + prod))
            else:
                idx = k - PTRC_KEM_N
                acc.__setitem__(idx, _i32(acc.__getitem__(idx) - prod))


def _pack_poly(dst: bytearray, offset: int, poly: List[int]) -> None:
    for i in range(PTRC_KEM_N):
        u = poly.__getitem__(i) & 0xFFFF
        dst.__setitem__(offset + i * 2 + 0, u & 0xFF)
        dst.__setitem__(offset + i * 2 + 1, (u >> 8) & 0xFF)


def _unpack_poly(src: bytes, offset: int) -> List[int]:
    poly = list((1,)) * PTRC_KEM_N
    for i in range(PTRC_KEM_N):
        lo = src.__getitem__(offset + i * 2 + 0)
        hi = src.__getitem__(offset + i * 2 + 1)
        val = lo | (hi << 8)
        if val & 0x8000:
            val -= 0x10000
        poly.__setitem__(i, -1 if val == 0 else val)
    return poly


def ptrc_kem_keygen_py(seed: bytes) -> Tuple[bytes, bytes]:
    if len(seed) != PTRC_KEM_SEED_BYTES:
        raise ValueError("Seed must be 32 bytes")

    ctx = _PtrcKemSponge(seed, 0x11)
    pk_out = bytearray(PTRC_KEM_PK_BYTES)
    sk_out = bytearray(PTRC_KEM_SK_BYTES)

    seed_a = bytearray(PTRC_KEM_SEED_BYTES)
    for i in range(PTRC_KEM_SEED_BYTES):
        b = ctx.next_word() & 0xFF
        val = 0xFF if b == 0 else b
        seed_a.__setitem__(i, val)
        pk_out.__setitem__(i, val)

    s_vecs: List[List[int]] = list((list(), list()))
    e_vecs: List[List[int]] = list((list(), list()))
    for k in range(PTRC_KEM_K):
        sk_poly = list((1,)) * PTRC_KEM_N
        ek_poly = list((1,)) * PTRC_KEM_N
        for i in range(PTRC_KEM_N):
            sk_poly.__setitem__(i, ctx.sample_noise())
            ek_poly.__setitem__(i, ctx.sample_noise())
        s_vecs.__setitem__(k, sk_poly)
        e_vecs.__setitem__(k, ek_poly)
        _pack_poly(sk_out, k * PTRC_KEM_N * 2, sk_poly)

    seed_a_bytes = bytes(seed_a)
    for row in range(PTRC_KEM_K):
        acc = list(e_vecs.__getitem__(row))
        for col in range(PTRC_KEM_K):
            a_poly = _expand_a_poly(seed_a_bytes, row, col)
            _poly_mul_acc(acc, a_poly, s_vecs.__getitem__(col))
        b_poly = list((1,)) * PTRC_KEM_N
        for i in range(PTRC_KEM_N):
            b_poly.__setitem__(i, ptrc_kem_mod_q_no_zero(acc.__getitem__(i)))
        _pack_poly(pk_out, PTRC_KEM_SEED_BYTES + row * PTRC_KEM_N * 2, b_poly)

    return bytes(pk_out), bytes(sk_out)

def _derive_ss_py(msg: bytes, transcript: bytes) -> bytes:
    combined = msg + transcript[:PTRC_KEM_SEED_BYTES]
    kdf_ctx = _PtrcKemSponge(combined, 0x77)
    for _ in range(576):
        kdf_ctx.next_word()
    ss_out = bytearray(PTRC_KEM_SS_BYTES)
    for i in range(PTRC_KEM_SS_BYTES):
        val = kdf_ctx.next_word()
        b = (val ^ _c_shr_i32(val, 8)) & 0xFF
        ss_out.__setitem__(i, 0xFF if b == 0 else b)
    return bytes(ss_out)


def ptrc_kem_encaps_py(pk: bytes, coins: bytes) -> Tuple[bytes, bytes]:
    if len(pk) != PTRC_KEM_PK_BYTES or len(coins) != PTRC_KEM_SEED_BYTES:
        raise ValueError("Invalid pk or coins length")

    ctx = _PtrcKemSponge(coins, 0x33)
    ct_out = bytearray(PTRC_KEM_CT_BYTES)

    msg = bytearray(PTRC_KEM_MSG_BYTES)
    for i in range(PTRC_KEM_MSG_BYTES):
        b = ctx.next_word() & 0xFF
        msg.__setitem__(i, 0xFF if b == 0 else b)

    r_vecs: List[List[int]] = list((list(), list()))
    e1_vecs: List[List[int]] = list((list(), list()))
    for k in range(PTRC_KEM_K):
        rk = list((1,)) * PTRC_KEM_N
        e1k = list((1,)) * PTRC_KEM_N
        for i in range(PTRC_KEM_N):
            rk.__setitem__(i, ctx.sample_noise())
            e1k.__setitem__(i, ctx.sample_noise())
        r_vecs.__setitem__(k, rk)
        e1_vecs.__setitem__(k, e1k)

    e2 = list((1,)) * PTRC_KEM_N
    for i in range(PTRC_KEM_N):
        e2.__setitem__(i, ctx.sample_noise())

    seed_a = pk[:PTRC_KEM_SEED_BYTES]
    for col in range(PTRC_KEM_K):
        acc = list(e1_vecs.__getitem__(col))
        for row in range(PTRC_KEM_K):
            a_poly = _expand_a_poly(seed_a, row, col)
            _poly_mul_acc(acc, a_poly, r_vecs.__getitem__(row))
        u_poly = list((1,)) * PTRC_KEM_N
        for i in range(PTRC_KEM_N):
            u_poly.__setitem__(i, ptrc_kem_mod_q_no_zero(acc.__getitem__(i)))
        _pack_poly(ct_out, col * PTRC_KEM_N * 2, u_poly)

    v_acc = list(e2)
    for k in range(PTRC_KEM_K):
        b_poly = _unpack_poly(pk, PTRC_KEM_SEED_BYTES + k * PTRC_KEM_N * 2)
        _poly_mul_acc(v_acc, b_poly, r_vecs.__getitem__(k))

    v_offset = PTRC_KEM_K * PTRC_KEM_N * 2
    for byte_idx in range(128):
        packed_nibbles = 0
        for nib in range(2):
            coeff_idx = byte_idx * 2 + nib
            m_bit = (msg.__getitem__(coeff_idx >> 3) >> (coeff_idx & 7)) & 1
            m_encode = PTRC_KEM_HALF_Q if m_bit != 0 else 0
            v_centered = ptrc_kem_mod_q_no_zero(v_acc.__getitem__(coeff_idx) + m_encode)
            v_pos = v_centered + PTRC_KEM_HALF_Q
            comp4 = (((v_pos * 16) + PTRC_KEM_HALF_Q) // PTRC_KEM_Q) & 0x0F
            packed_nibbles |= comp4 << (nib * 4)
        ct_out.__setitem__(v_offset + byte_idx, packed_nibbles)

    ct_bytes = bytes(ct_out)
    ss_bytes = _derive_ss_py(bytes(msg), ct_bytes)
    return ct_bytes, ss_bytes


def ptrc_kem_decaps_py(ct: bytes, sk: bytes) -> bytes:
    if len(ct) != PTRC_KEM_CT_BYTES or len(sk) != PTRC_KEM_SK_BYTES:
        raise ValueError("Invalid ct or sk length")

    su_acc = list((0,)) * PTRC_KEM_N
    for k in range(PTRC_KEM_K):
        s_poly = _unpack_poly(sk, k * PTRC_KEM_N * 2)
        u_poly = _unpack_poly(ct, k * PTRC_KEM_N * 2)
        _poly_mul_acc(su_acc, s_poly, u_poly)

    msg = bytearray(PTRC_KEM_MSG_BYTES)
    v_offset = PTRC_KEM_K * PTRC_KEM_N * 2
    for byte_idx in range(128):
        packed_nibbles = ct.__getitem__(v_offset + byte_idx)
        for nib in range(2):
            coeff_idx = byte_idx * 2 + nib
            comp4 = (packed_nibbles >> (nib * 4)) & 0x0F
            v_approx = ((comp4 * PTRC_KEM_Q + 8) >> 4) - PTRC_KEM_HALF_Q
            diff = ptrc_kem_mod_q_no_zero(v_approx - su_acc.__getitem__(coeff_idx))
            if abs(diff) > PTRC_KEM_QUARTER_Q:
                b_idx = coeff_idx >> 3
                msg.__setitem__(b_idx, msg.__getitem__(b_idx) | (1 << (coeff_idx & 7)))

    for i in range(PTRC_KEM_MSG_BYTES):
        if msg.__getitem__(i) == 0:
            msg.__setitem__(i, 0xFF)

    return _derive_ss_py(bytes(msg), ct)


def load_c_kem_library(search_root: Optional[pathlib.Path] = None) -> Optional[ctypes.CDLL]:
    root = search_root or pathlib.Path(__file__).resolve().parent.parent
    candidates = [
        root / "build" / "libptrc_pq_kem.so",
        root / "build" / "libptrc_pq_kem.dylib",
        root / "build" / "ptrc_pq_kem.dll",
        root / "build" / "Release" / "ptrc_pq_kem.dll",
    ]
    for cand in candidates:
        if cand.exists():
            lib = ctypes.CDLL(str(cand))
            lib.ptrc_kem_keygen.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
            ]
            lib.ptrc_kem_keygen.restype = ctypes.c_int

            lib.ptrc_kem_encaps.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
            ]
            lib.ptrc_kem_encaps.restype = ctypes.c_int

            lib.ptrc_kem_decaps.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
            ]
            lib.ptrc_kem_decaps.restype = ctypes.c_int

            lib.ptrc_kem_wipe.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
            lib.ptrc_kem_wipe.restype = None
            return lib
    return None
