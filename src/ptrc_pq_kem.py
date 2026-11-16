# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & CCA2 Post-Quantum Ring-KEM v4.3.1
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
pTRC v4.3.1 Discrete 1-Bit Integer Physics & CCA2 Post-Quantum Ring-KEM.
File: src/ptrc_pq_kem.py (Part 1 of 3)

Bit-exact match to embedded/crypto/ptrc_pq_kem.c (v4.3.1):
  - Fujisaki-Okamoto (FO) CCA2 re-encryption check & implicit constant-time rejection
  - Strictly UB-free unsigned mixing projected into Z_{7681} \ {0}
  - Profile A (512-Dim Standard, k=2): PK=1056B, SK=2112B, CT=1152B, SS=64B
  - Profile B (256-Dim Ultra-Light, k=1): PK=544B, SK=1088B, CT=640B, SS=64B
"""

from __future__ import annotations

import ctypes
import pathlib
from typing import List, Optional, Tuple

PTRC_KEM_Q = 7681
PTRC_KEM_HALF_Q = 3840
PTRC_KEM_QUARTER_Q = 1920

PTRC_KEM_N = 256
PTRC_KEM_FACETS = 144
PTRC_KEM_TAKT_137 = 137
PTRC_KEM_PRIMORIAL_210 = 210

PTRC_KEM_SEED_BYTES = 32
PTRC_KEM_MSG_BYTES = 32
PTRC_KEM_SS_BYTES = 64

# Profile A: Standard 512-Dim Module-Lattice (k = 2, FO-CCA2 SK includes PK + z)
PTRC_KEM_K = 2
PTRC_KEM_PK_BYTES = 1056
PTRC_KEM_SK_BYTES = 2112
PTRC_KEM_CT_BYTES = 1152

# Profile B: Ultra-Light 256-Dim IoT Ring-Lattice (k = 1, FO-CCA2 SK includes PK + z)
PTRC_KEM_LIGHT_K = 1
PTRC_KEM_LIGHT_PK_BYTES = 544
PTRC_KEM_LIGHT_SK_BYTES = 1088
PTRC_KEM_LIGHT_CT_BYTES = 640

PTRC_KEM_OK = 1
PTRC_KEM_ERR = -1

U64_MASK = 0xFFFFFFFFFFFFFFFF
U32_MASK = 0xFFFFFFFF


def _i32(val: int) -> int:
    v = val & U32_MASK
    return v - 0x100000000 if (v & 0x80000000) else v


def ptrc_kem_z_no_zero_u32(u: int) -> int:
    u32 = u & U32_MASK
    is_zero = ((u32 | ((0 - u32) & U32_MASK)) >> 31) ^ 1
    res = u32 | ((0 - is_zero) & U32_MASK)
    return _i32(res)


def ptrc_kem_byte_no_zero(b: int) -> int:
    u = b & 0xFF
    is_zero = ((u | ((0 - u) & U32_MASK)) >> 31) ^ 1
    return (u | ((0 - is_zero) & U32_MASK)) & 0xFF


def ptrc_kem_ct_abs32(x: int) -> int:
    ux = x & U32_MASK
    mask = ux >> 31
    neg_mask = (0 - mask) & U32_MASK
    return ((ux ^ neg_mask) + mask) & U32_MASK


def ptrc_kem_mod_q_no_zero(x: int) -> int:
    r"""Centered modular reduction into Z_{7681} \ {0} = {-3840..-1, +1..+3840}."""
    x32 = _i32(x)
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
    r"""Internal 144-facet Z \ {0} sponge matching ptrc_kem_ctx_t in C11 v4.3.1."""

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
            self.sponge.__setitem__(f, ptrc_kem_z_no_zero_u32(raw))
        self.takt_counter: int = 1
        self.quadrant_phase: int = 1

    def next_word(self) -> int:
        idx = (self.takt_counter * 37) % PTRC_KEM_FACETS
        opp = (idx + 73) % PTRC_KEM_FACETS
        jnc = (idx + 24) % PTRC_KEM_FACETS

        ua = self.sponge.__getitem__(idx) & U32_MASK
        ub = self.sponge.__getitem__(opp) & U32_MASK
        uc = self.sponge.__getitem__(jnc) & U32_MASK

        umixed = ((~ua) + (ub ^ uc) + (self.quadrant_phase * 11)) & U32_MASK
        mixed = ptrc_kem_z_no_zero_u32(umixed)
        self.sponge.__setitem__(idx, mixed)

        uopp = (ub + ((mixed & U32_MASK) >> 2)) & U32_MASK
        self.sponge.__setitem__(opp, ptrc_kem_z_no_zero_u32(uopp))

        if (self.takt_counter % PTRC_KEM_TAKT_137) == 0:
            for f in range(PTRC_KEM_FACETS):
                uf = self.sponge.__getitem__(f) & U32_MASK
                self.sponge.__setitem__(f, ptrc_kem_z_no_zero_u32(~uf))

        self.takt_counter += 1
        self.quadrant_phase = (self.quadrant_phase & 3) + 1
        return mixed

    def sample_noise(self) -> int:
        uv = self.next_word() & U32_MASK
        mag = (uv & 1) + 1
        sign_bit = uv >> 31
        sign_mask = (0 - sign_bit) & U32_MASK
        signed_mag = ((mag ^ sign_mask) + sign_bit) & U32_MASK
        return _i32(signed_mag)

# File: src/ptrc_pq_kem.py (Part 2 of 3)


def _expand_a_poly(seed_a: bytes, row: int, col: int) -> List[int]:
    tag = ((((row + 1) * 17) ^ ((col + 1) * 31)) | 1) & 0xFF
    local_ctx = _PtrcKemSponge(seed_a, tag)
    out = list((1,)) * PTRC_KEM_N
    for i in range(PTRC_KEM_N):
        uraw = local_ctx.next_word() & U32_MASK
        uval = (uraw * 53 + (i * 137)) & U32_MASK
        out.__setitem__(i, ptrc_kem_mod_q_no_zero(_i32(uval)))
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
        uval = lo | (hi << 8)
        if uval == 0:
            uval = 0xFFFF
        if uval & 0x8000:
            uval -= 0x10000
        poly.__setitem__(i, uval)
    return poly


def _hash_pair_py(out_len: int, in1: bytes, in2: bytes, domain: int) -> bytes:
    h_ctx = _PtrcKemSponge(in1, domain)
    for i in range(len(in1)):
        odd_b = ((in1.__getitem__(i) << 1) | 1) & 0xFF
        f_idx = i % PTRC_KEM_FACETS
        cur = h_ctx.sponge.__getitem__(f_idx) & U32_MASK
        h_ctx.sponge.__setitem__(f_idx, ptrc_kem_z_no_zero_u32(cur ^ (odd_b * ((i & 31) + 1))))
        if (i & 7) == 7:
            h_ctx.next_word()

    for i in range(len(in2)):
        odd_b = ((in2.__getitem__(i) << 1) | 1) & 0xFF
        f_idx = (i + 19) % PTRC_KEM_FACETS
        cur = h_ctx.sponge.__getitem__(f_idx) & U32_MASK
        h_ctx.sponge.__setitem__(f_idx, ptrc_kem_z_no_zero_u32(cur ^ (odd_b * ((i & 31) + 3))))
        if (i & 7) == 7:
            h_ctx.next_word()

    for _ in range(576):
        h_ctx.next_word()

    out = bytearray(out_len)
    for i in range(out_len):
        uval = h_ctx.next_word() & U32_MASK
        b = (uval ^ (uval >> 8)) & 0xFF
        out.__setitem__(i, ptrc_kem_byte_no_zero(b))
    return bytes(out)


def _keygen_core_py(seed: bytes, k_dim: int) -> Tuple[bytes, bytes]:
    if len(seed) != PTRC_KEM_SEED_BYTES or k_dim not in (1, 2):
        raise ValueError("Invalid seed or k_dim")

    ctx = _PtrcKemSponge(seed, 0x10 | k_dim)
    s_bytes = k_dim * PTRC_KEM_N * 2
    pk_bytes = PTRC_KEM_SEED_BYTES + s_bytes
    pk_out = bytearray(pk_bytes)
    sk_out = bytearray(s_bytes + pk_bytes + PTRC_KEM_SEED_BYTES)

    seed_a = bytearray(PTRC_KEM_SEED_BYTES)
    for i in range(PTRC_KEM_SEED_BYTES):
        b = (ctx.next_word() & U32_MASK) & 0xFF
        val = ptrc_kem_byte_no_zero(b)
        seed_a.__setitem__(i, val)
        pk_out.__setitem__(i, val)

    s_vecs: List[List[int]] = list((list(),)) * k_dim
    e_vecs: List[List[int]] = list((list(),)) * k_dim
    for k in range(k_dim):
        sk_poly = list((1,)) * PTRC_KEM_N
        ek_poly = list((1,)) * PTRC_KEM_N
        for i in range(PTRC_KEM_N):
            sk_poly.__setitem__(i, ctx.sample_noise())
            ek_poly.__setitem__(i, ctx.sample_noise())
        s_vecs.__setitem__(k, sk_poly)
        e_vecs.__setitem__(k, ek_poly)
        _pack_poly(sk_out, k * PTRC_KEM_N * 2, sk_poly)

    seed_a_bytes = bytes(seed_a)
    for row in range(k_dim):
        acc = list(e_vecs.__getitem__(row))
        for col in range(k_dim):
            a_poly = _expand_a_poly(seed_a_bytes, row, col)
            _poly_mul_acc(acc, a_poly, s_vecs.__getitem__(col))
        b_poly = list((1,)) * PTRC_KEM_N
        for i in range(PTRC_KEM_N):
            b_poly.__setitem__(i, ptrc_kem_mod_q_no_zero(acc.__getitem__(i)))
        _pack_poly(pk_out, PTRC_KEM_SEED_BYTES + row * PTRC_KEM_N * 2, b_poly)

    for i in range(pk_bytes):
        sk_out.__setitem__(s_bytes + i, pk_out.__getitem__(i))
    for i in range(PTRC_KEM_SEED_BYTES):
        zb = (ctx.next_word() & U32_MASK) & 0xFF
        sk_out.__setitem__(s_bytes + pk_bytes + i, ptrc_kem_byte_no_zero(zb))

    return bytes(pk_out), bytes(sk_out)

# File: src/ptrc_pq_kem.py (Part 3 of 3)


def _pke_encrypt_det_py(pk: bytes, msg: bytes, coins: bytes, k_dim: int) -> bytes:
    ctx = _PtrcKemSponge(coins, 0x30 | k_dim)
    u_bytes = k_dim * PTRC_KEM_N * 2
    ct_out = bytearray(u_bytes + 128)

    r_vecs: List[List[int]] = list((list(),)) * k_dim
    e1_vecs: List[List[int]] = list((list(),)) * k_dim
    for k in range(k_dim):
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
    for col in range(k_dim):
        acc = list(e1_vecs.__getitem__(col))
        for row in range(k_dim):
            a_poly = _expand_a_poly(seed_a, row, col)
            _poly_mul_acc(acc, a_poly, r_vecs.__getitem__(row))
        u_poly = list((1,)) * PTRC_KEM_N
        for i in range(PTRC_KEM_N):
            u_poly.__setitem__(i, ptrc_kem_mod_q_no_zero(acc.__getitem__(i)))
        _pack_poly(ct_out, col * PTRC_KEM_N * 2, u_poly)

    v_acc = list(e2)
    for k in range(k_dim):
        b_poly = _unpack_poly(pk, PTRC_KEM_SEED_BYTES + k * PTRC_KEM_N * 2)
        _poly_mul_acc(v_acc, b_poly, r_vecs.__getitem__(k))

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
        ct_out.__setitem__(u_bytes + byte_idx, packed_nibbles)

    return bytes(ct_out)


def _encaps_core_py(pk: bytes, msg_seed: bytes, k_dim: int) -> Tuple[bytes, bytes]:
    expected_pk = PTRC_KEM_SEED_BYTES + k_dim * PTRC_KEM_N * 2
    if len(pk) != expected_pk or len(msg_seed) != PTRC_KEM_MSG_BYTES or k_dim not in (1, 2):
        raise ValueError("Invalid pk, msg_seed, or k_dim")

    msg = bytes(ptrc_kem_byte_no_zero(msg_seed.__getitem__(i)) for i in range(PTRC_KEM_MSG_BYTES))
    coins = _hash_pair_py(PTRC_KEM_SEED_BYTES, pk, msg, 0x55)
    ct_bytes = _pke_encrypt_det_py(pk, msg, coins, k_dim)
    ss_bytes = _hash_pair_py(PTRC_KEM_SS_BYTES, msg, ct_bytes, 0x77)
    return ct_bytes, ss_bytes


def _decaps_core_py(ct: bytes, sk: bytes, k_dim: int) -> bytes:
    s_bytes = k_dim * PTRC_KEM_N * 2
    pk_bytes = PTRC_KEM_SEED_BYTES + s_bytes
    ct_bytes = s_bytes + 128
    expected_sk = s_bytes + pk_bytes + PTRC_KEM_SEED_BYTES
    if len(ct) != ct_bytes or len(sk) != expected_sk or k_dim not in (1, 2):
        raise ValueError("Invalid ct, sk, or k_dim")

    pk_embedded = sk[s_bytes : s_bytes + pk_bytes]
    z_reject = sk[s_bytes + pk_bytes : expected_sk]

    su_acc = list((0,)) * PTRC_KEM_N
    for k in range(k_dim):
        s_poly = _unpack_poly(sk, k * PTRC_KEM_N * 2)
        u_poly = _unpack_poly(ct, k * PTRC_KEM_N * 2)
        _poly_mul_acc(su_acc, s_poly, u_poly)

    msg_prime = bytearray(PTRC_KEM_MSG_BYTES)
    for byte_idx in range(128):
        packed_nibbles = ct.__getitem__(s_bytes + byte_idx)
        for nib in range(2):
            coeff_idx = byte_idx * 2 + nib
            comp4 = (packed_nibbles >> (nib * 4)) & 0x0F
            v_approx = ((comp4 * PTRC_KEM_Q + 8) >> 4) - PTRC_KEM_HALF_Q
            diff = ptrc_kem_mod_q_no_zero(v_approx - su_acc.__getitem__(coeff_idx))
            abs_diff = ptrc_kem_ct_abs32(diff)
            bit = (_i32(PTRC_KEM_QUARTER_Q - abs_diff) & U32_MASK) >> 31
            b_idx = coeff_idx >> 3
            msg_prime.__setitem__(b_idx, msg_prime.__getitem__(b_idx) | (bit << (coeff_idx & 7)))

    for i in range(PTRC_KEM_MSG_BYTES):
        msg_prime.__setitem__(i, ptrc_kem_byte_no_zero(msg_prime.__getitem__(i)))

    msg_prime_bytes = bytes(msg_prime)
    coins_prime = _hash_pair_py(PTRC_KEM_SEED_BYTES, pk_embedded, msg_prime_bytes, 0x55)
    ct_prime = _pke_encrypt_det_py(pk_embedded, msg_prime_bytes, coins_prime, k_dim)

    diff_acc = 0
    for i in range(ct_bytes):
        diff_acc |= ct.__getitem__(i) ^ ct_prime.__getitem__(i)
    fail_mask = 0xFF if diff_acc != 0 else 0x00

    ss_real = _hash_pair_py(PTRC_KEM_SS_BYTES, msg_prime_bytes, ct, 0x77)
    ss_reject = _hash_pair_py(PTRC_KEM_SS_BYTES, z_reject, ct, 0x99)

    ss_out = bytearray(PTRC_KEM_SS_BYTES)
    for i in range(PTRC_KEM_SS_BYTES):
        sel = ((ss_real.__getitem__(i) & (~fail_mask)) | (ss_reject.__getitem__(i) & fail_mask)) & 0xFF
        ss_out.__setitem__(i, sel)
    return bytes(ss_out)


def ptrc_kem_keygen_py(seed: bytes) -> Tuple[bytes, bytes]:
    return _keygen_core_py(seed, PTRC_KEM_K)


def ptrc_kem_encaps_py(pk: bytes, msg_seed: bytes) -> Tuple[bytes, bytes]:
    return _encaps_core_py(pk, msg_seed, PTRC_KEM_K)


def ptrc_kem_decaps_py(ct: bytes, sk: bytes) -> bytes:
    return _decaps_core_py(ct, sk, PTRC_KEM_K)


def ptrc_kem_light_keygen_py(seed: bytes) -> Tuple[bytes, bytes]:
    return _keygen_core_py(seed, PTRC_KEM_LIGHT_K)


def ptrc_kem_light_encaps_py(pk: bytes, msg_seed: bytes) -> Tuple[bytes, bytes]:
    return _encaps_core_py(pk, msg_seed, PTRC_KEM_LIGHT_K)


def ptrc_kem_light_decaps_py(ct: bytes, sk: bytes) -> bytes:
    return _decaps_core_py(ct, sk, PTRC_KEM_LIGHT_K)


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
            u8p = ctypes.POINTER(ctypes.c_uint8)
            for fn_kg in (lib.ptrc_kem_keygen, lib.ptrc_kem_light_keygen):
                fn_kg.argtypes = [u8p, u8p, u8p]
                fn_kg.restype = ctypes.c_int
            for fn_en in (lib.ptrc_kem_encaps, lib.ptrc_kem_light_encaps):
                fn_en.argtypes = [u8p, u8p, u8p, u8p]
                fn_en.restype = ctypes.c_int
            for fn_de in (lib.ptrc_kem_decaps, lib.ptrc_kem_light_decaps):
                fn_de.argtypes = [u8p, u8p, u8p]
                fn_de.restype = ctypes.c_int
            lib.ptrc_kem_wipe.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
            lib.ptrc_kem_wipe.restype = None
            return lib
    return None
