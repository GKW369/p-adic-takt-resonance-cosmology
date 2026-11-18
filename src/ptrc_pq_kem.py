# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.5.0
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
pTRC Post-Quantum Ring-KEM (Zero-Float Cyclotomic Lattice over q = 7681) - v4.5.0.
File: src/ptrc_pq_kem.py (Part 1 of 2)

Bit-exact Python reference implementation matching embedded/crypto/ptrc_pq_kem.c (v4.5.0):
  - Fujisaki-Okamoto (FO) CCA2 re-encryption & constant-time implicit rejection
  - 5-bit ciphertext compression (comp5, 160 bytes) halving rounding noise to +-120
  - Dual-profile support: Profile A (k=2, 512-Dim) & Profile B (k=1, 256-Dim Ultra-Light IoT)
"""

from __future__ import annotations

import ctypes
import pathlib
from typing import List, Optional, Tuple

from ptrc_crystal_aead import (
    PTRC_CRYPT_KEY_BYTES,
    PTRC_CRYPT_NONCE_BYTES,
    PtrcCrystalContext,
    ptrc_kdf_derive,
)

PTRC_KEM_N = 256
PTRC_KEM_Q = 7681
PTRC_KEM_ETA = 2
PTRC_KEM_SEED_BYTES = 32
PTRC_KEM_POLY_BYTES = 512
PTRC_KEM_SS_BYTES = 64
PTRC_KEM_MSG_BYTES = 32

PTRC_KEM_V_COMP_BITS = 5
PTRC_KEM_V_COMP_BYTES = 160

PTRC_KEM_K_STD = 2
PTRC_KEM_PK_BYTES_STD = PTRC_KEM_SEED_BYTES + PTRC_KEM_K_STD * PTRC_KEM_POLY_BYTES          # 1056
PTRC_KEM_SK_BYTES_STD = PTRC_KEM_K_STD * PTRC_KEM_POLY_BYTES + PTRC_KEM_PK_BYTES_STD + 32  # 2112
PTRC_KEM_CT_BYTES_STD = PTRC_KEM_K_STD * PTRC_KEM_POLY_BYTES + PTRC_KEM_V_COMP_BYTES       # 1184

PTRC_KEM_K_LIGHT = 1
PTRC_KEM_PK_BYTES_LIGHT = PTRC_KEM_SEED_BYTES + PTRC_KEM_K_LIGHT * PTRC_KEM_POLY_BYTES          # 544
PTRC_KEM_SK_BYTES_LIGHT = PTRC_KEM_K_LIGHT * PTRC_KEM_POLY_BYTES + PTRC_KEM_PK_BYTES_LIGHT + 32  # 1088
PTRC_KEM_CT_BYTES_LIGHT = PTRC_KEM_K_LIGHT * PTRC_KEM_POLY_BYTES + PTRC_KEM_V_COMP_BYTES       # 672

PTRC_KEM_K = PTRC_KEM_K_STD
PTRC_KEM_PK_BYTES = PTRC_KEM_PK_BYTES_STD
PTRC_KEM_SK_BYTES = PTRC_KEM_SK_BYTES_STD
PTRC_KEM_CT_BYTES = PTRC_KEM_CT_BYTES_STD

PTRC_KEM_OK = 1
PTRC_KEM_ERR = -1


def _mod_q_nz(x: int) -> int:
    r = x % PTRC_KEM_Q
    return (PTRC_KEM_Q - 1) if r == 0 else r


def _mod_q_std(x: int) -> int:
    return x % PTRC_KEM_Q


def _center_q(a_std: int) -> int:
    half = PTRC_KEM_Q // 2
    return a_std - PTRC_KEM_Q if a_std > half else a_std


def _hash_transcript_py(domain_tag: int, in_a: bytes, in_b: bytes = b"") -> Tuple[bytes, bytes]:
    seed_buf = bytearray(((i * 137 + domain_tag * 29 + 11) & 0xFF) | 1 for i in range(64))
    for i, b in enumerate(in_a):
        idx = i & 63
        v = (seed_buf[idx] ^ b ^ ((i >> 6) * 19)) & 0xFF
        seed_buf[idx] = 0xFF if v == 0 else v

    info_buf = bytearray(((i * 211 + domain_tag * 43 + 7) & 0xFF) | 1 for i in range(64))
    for i, b in enumerate(in_b):
        idx = i & 63
        v = (info_buf[idx] ^ b ^ ((i >> 6) * 31)) & 0xFF
        info_buf[idx] = 0xFF if v == 0 else v

    info_buf ^= len(in_a) & 0xFF
    info_buf ^= (len(in_a) >> 8) & 0xFF
    info_buf ^= len(in_b) & 0xFF
    info_buf ^= (len(in_b) >> 8) & 0xFF

    return ptrc_kdf_derive(bytes(seed_buf), bytes(info_buf))


def _expand_uniform_poly_py(seed: bytes, row: int, col: int) -> List[int]:
    key = bytearray(PTRC_CRYPT_KEY_BYTES)
    nonce = bytearray(PTRC_CRYPT_NONCE_BYTES)
    for i in range(PTRC_CRYPT_KEY_BYTES):
        sb = seed[i & 31]
        v = (sb ^ ((i * 23 + row * 71 + col * 137) & 0xFF)) & 0xFF
        key[i] = 0xFF if v == 0 else v
    for i in range(PTRC_CRYPT_NONCE_BYTES):
        sb = seed[(i + 11) & 31]
        v = (sb ^ ((i * 17 + row * 13 + col * 41) & 0xFF)) & 0xFF
        nonce[i] = 0xFF if v == 0 else v

    ctx = PtrcCrystalContext(bytes(key), bytes(nonce))
    stream = ctx.xor_stream(bytes([0xFF] * (PTRC_KEM_N * 2)))
    out = [0] * PTRC_KEM_N
    for n in range(PTRC_KEM_N):
        raw16 = stream[n * 2] | (stream[n * 2 + 1] << 8)
        out[n] = (raw16 % (PTRC_KEM_Q - 1)) + 1
    return out


def _sample_noise_poly_py(coins: bytes, nonce_tag: int) -> List[int]:
    key = bytearray(PTRC_CRYPT_KEY_BYTES)
    nonce = bytearray(PTRC_CRYPT_NONCE_BYTES)
    for i in range(PTRC_CRYPT_KEY_BYTES):
        cb = coins[i & 31]
        v = (cb ^ ((i * 37 + nonce_tag * 97) & 0xFF)) & 0xFF
        key[i] = 0xFF if v == 0 else v
    for i in range(PTRC_CRYPT_NONCE_BYTES):
        cb = coins[(i + 7) & 31]
        v = (cb ^ ((i * 29 + nonce_tag * 53) & 0xFF)) & 0xFF
        nonce[i] = 0xFF if v == 0 else v

    ctx = PtrcCrystalContext(bytes(key), bytes(nonce))
    rnd = ctx.xor_stream(bytes([0xAA] * PTRC_KEM_N))
    out = [0] * PTRC_KEM_N
    for n in range(PTRC_KEM_N):
        rb = rnd[n]
        a = (rb & 1) + ((rb >> 1) & 1)
        b = ((rb >> 2) & 1) + ((rb >> 3) & 1)
        diff = a - b
        if diff == 0:
            sign_bit = (rb >> 4) & 1
            diff = (sign_bit << 1) - 1
        out[n] = diff
    return out


def _poly_mul_acc_py(acc: List[int], a: List[int], b: List[int]) -> None:
    tmp = [_mod_q_std(x) for x in acc]
    for i in range(PTRC_KEM_N):
        ai = a[i]
        for j in range(PTRC_KEM_N):
            bj = b[j]
            idx = i + j
            if idx < PTRC_KEM_N:
                tmp[idx] += ai * bj
            else:
                tmp[idx - PTRC_KEM_N] -= ai * bj
    for i in range(PTRC_KEM_N):
        acc[i] = _mod_q_nz(tmp[i])


def _poly_add_nz_py(a: List[int], b: List[int]) -> List[int]:
    return [_mod_q_nz(_mod_q_std(x) + _mod_q_std(y)) for x, y in zip(a, b)]


def _poly_sub_std_py(a: List[int], b: List[int]) -> List[int]:
    return [_mod_q_std(_mod_q_std(x) - _mod_q_std(y)) for x, y in zip(a, b)]


def _poly_pack_py(p: List[int]) -> bytes:
    out = bytearray(PTRC_KEM_POLY_BYTES)
    for i in range(PTRC_KEM_N):
        v = _mod_q_nz(p[i])
        out[i * 2] = v & 0xFF
        out[i * 2 + 1] = (v >> 8) & 0xFF
    return bytes(out)


def _poly_unpack_py(buf: bytes, offset: int = 0) -> List[int]:
    out = [0] * PTRC_KEM_N
    for i in range(PTRC_KEM_N):
        v = buf[offset + i * 2] | (buf[offset + i * 2 + 1] << 8)
        out[i] = _mod_q_nz(v)
    return out


def _poly_compress5_py(v: List[int]) -> bytes:
    out = bytearray(PTRC_KEM_V_COMP_BYTES)
    for i in range(PTRC_KEM_N):
        x = _mod_q_std(v[i])
        c5 = ((x * 32 + (PTRC_KEM_Q // 2)) // PTRC_KEM_Q) & 0x1F
        bit_pos = i * 5
        byte_idx = bit_pos >> 3
        shift = bit_pos & 7
        out[byte_idx] |= (c5 << shift) & 0xFF
        if shift > 3:
            out[byte_idx + 1] |= (c5 >> (8 - shift)) & 0xFF
    return bytes(out)


def _poly_decompress5_py(buf: bytes, offset: int = 0) -> List[int]:
    out = [0] * PTRC_KEM_N
    for i in range(PTRC_KEM_N):
        bit_pos = i * 5
        byte_idx = bit_pos >> 3
        shift = bit_pos & 7
        lo = buf[offset + byte_idx] >> shift
        hi = (buf[offset + byte_idx + 1] << (8 - shift)) if shift > 3 else 0
        c5 = (lo | hi) & 0x1F
        out[i] = (c5 * PTRC_KEM_Q + 16) // 32
    return out

# ==============================================================================
# File: src/ptrc_pq_kem.py (Part 2 of 2)
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
# ==============================================================================

def _indcpa_enc_py(k: int, pk: bytes, msg: bytes, r_coins: bytes) -> bytes:
    seed_a = pk[:PTRC_KEM_SEED_BYTES]
    t_vec = [_poly_unpack_py(pk, PTRC_KEM_SEED_BYTES + i * PTRC_KEM_POLY_BYTES) for i in range(k)]
    r_vec = [_sample_noise_poly_py(r_coins, 0x10 + i) for i in range(k)]
    e1_vec = [_sample_noise_poly_py(r_coins, 0x20 + i) for i in range(k)]
    e2 = _sample_noise_poly_py(r_coins, 0x30)

    ct_parts = bytearray()
    for i in range(k):
        u_i = [0] * PTRC_KEM_N
        for j in range(k):
            a_ji = _expand_uniform_poly_py(seed_a, j, i)
            _poly_mul_acc_py(u_i, a_ji, r_vec[j])
        u_i = _poly_add_nz_py(u_i, e1_vec[i])
        ct_parts.extend(_poly_pack_py(u_i))

    v_poly = [0] * PTRC_KEM_N
    for i in range(k):
        _poly_mul_acc_py(v_poly, t_vec[i], r_vec[i])
    v_poly = _poly_add_nz_py(v_poly, e2)

    half_q = (PTRC_KEM_Q + 1) // 2
    for n in range(PTRC_KEM_N):
        bit = (msg[n >> 3] >> (n & 7)) & 1
        cur = _mod_q_std(v_poly[n])
        if bit:
            cur += half_q
        v_poly[n] = _mod_q_nz(cur)

    ct_parts.extend(_poly_compress5_py(v_poly))
    return bytes(ct_parts)


def ptrc_kem_keygen_ex(k: int, seed: bytes) -> Tuple[bytes, bytes]:
    if k not in (PTRC_KEM_K_LIGHT, PTRC_KEM_K_STD) or len(seed) != PTRC_KEM_SEED_BYTES:
        raise ValueError("Invalid profile k or seed length")

    domain_tag = b"pTRC_KEM_FO_4.5" + bytes([k])
    expanded_k, expanded_n = ptrc_kdf_derive(seed, domain_tag)

    seed_a = expanded_k[:32]
    coins_s = expanded_k[32:64]
    z_reject = bytearray(PTRC_KEM_SEED_BYTES)
    for i in range(16):
        z_reject[i] = expanded_n[i]
        z_reject[i + 16] = expanded_k[i] ^ expanded_k[i + 32]

    s_vec = [_sample_noise_poly_py(coins_s, 0x01 + i) for i in range(k)]
    e_vec = [_sample_noise_poly_py(coins_s, 0x81 + i) for i in range(k)]

    sk_s_bytes = bytearray()
    pk_t_bytes = bytearray()
    for i in range(k):
        sk_s_bytes.extend(_poly_pack_py(s_vec[i]))
        t_i = [0] * PTRC_KEM_N
        for j in range(k):
            a_ij = _expand_uniform_poly_py(seed_a, i, j)
            _poly_mul_acc_py(t_i, a_ij, s_vec[j])
        t_i = _poly_add_nz_py(t_i, e_vec[i])
        pk_t_bytes.extend(_poly_pack_py(t_i))

    pk = bytes(seed_a) + bytes(pk_t_bytes)
    sk = bytes(sk_s_bytes) + pk + bytes(z_reject)
    return pk, sk


def ptrc_kem_encaps_ex(k: int, pk: bytes, coins: bytes) -> Tuple[bytes, bytes]:
    pk_bytes = PTRC_KEM_SEED_BYTES + k * PTRC_KEM_POLY_BYTES
    if k not in (PTRC_KEM_K_LIGHT, PTRC_KEM_K_STD) or len(pk) != pk_bytes or len(coins) != PTRC_KEM_MSG_BYTES:
        raise ValueError("Invalid pk or coins length")

    pk_hash_64, _ = _hash_transcript_py(0xA1, pk)
    g_64, _ = _hash_transcript_py(0xB2, coins, pk_hash_64[:32])
    k_bar = g_64[:32]
    r_coins = g_64[32:64]

    ct = _indcpa_enc_py(k, pk, coins, r_coins)
    ss, _ = _hash_transcript_py(0xC3, k_bar, ct)
    return ct, ss


def ptrc_kem_decaps_ex(k: int, sk: bytes, ct: bytes) -> bytes:
    s_bytes = k * PTRC_KEM_POLY_BYTES
    pk_bytes = PTRC_KEM_SEED_BYTES + s_bytes
    sk_bytes = s_bytes + pk_bytes + PTRC_KEM_SEED_BYTES
    ct_bytes = s_bytes + PTRC_KEM_V_COMP_BYTES
    if k not in (PTRC_KEM_K_LIGHT, PTRC_KEM_K_STD) or len(sk) != sk_bytes or len(ct) != ct_bytes:
        raise ValueError("Invalid sk or ct length")

    pk = sk[s_bytes:s_bytes + pk_bytes]
    z_reject = sk[s_bytes + pk_bytes:]

    s_vec = [_poly_unpack_py(sk, i * PTRC_KEM_POLY_BYTES) for i in range(k)]
    u_vec = [_poly_unpack_py(ct, i * PTRC_KEM_POLY_BYTES) for i in range(k)]
    v_poly = _poly_decompress5_py(ct, s_bytes)

    su_acc = [0] * PTRC_KEM_N
    for i in range(k):
        _poly_mul_acc_py(su_acc, s_vec[i], u_vec[i])
    diff = _poly_sub_std_py(v_poly, su_acc)

    m_prime = bytearray(PTRC_KEM_MSG_BYTES)
    q_quarter = PTRC_KEM_Q // 4
    for n in range(PTRC_KEM_N):
        c = _center_q(diff[n])
        if abs(c) > q_quarter:
            m_prime[n >> 3] |= 1 << (n & 7)

    pk_hash_64, _ = _hash_transcript_py(0xA1, pk)
    g_64, _ = _hash_transcript_py(0xB2, bytes(m_prime), pk_hash_64[:32])
    k_bar_prime = g_64[:32]
    r_coins_prime = g_64[32:64]

    ct_prime = _indcpa_enc_py(k, pk, bytes(m_prime), r_coins_prime)
    ss_valid, _ = _hash_transcript_py(0xC3, k_bar_prime, ct)
    ss_reject, _ = _hash_transcript_py(0xD4, z_reject, ct)

    ct_diff = 0
    for a, b in zip(ct, ct_prime):
        ct_diff |= a ^ b
    return ss_valid if ct_diff == 0 else ss_reject


def ptrc_kem_keygen(seed: bytes) -> Tuple[bytes, bytes]:
    return ptrc_kem_keygen_ex(PTRC_KEM_K_STD, seed)


def ptrc_kem_encaps(pk: bytes, coins: bytes) -> Tuple[bytes, bytes]:
    return ptrc_kem_encaps_ex(PTRC_KEM_K_STD, pk, coins)


def ptrc_kem_decaps(sk: bytes, ct: bytes) -> bytes:
    return ptrc_kem_decaps_ex(PTRC_KEM_K_STD, sk, ct)


def ptrc_kem_keygen_light(seed: bytes) -> Tuple[bytes, bytes]:
    return ptrc_kem_keygen_ex(PTRC_KEM_K_LIGHT, seed)


def ptrc_kem_encaps_light(pk: bytes, coins: bytes) -> Tuple[bytes, bytes]:
    return ptrc_kem_encaps_ex(PTRC_KEM_K_LIGHT, pk, coins)


def ptrc_kem_decaps_light(sk: bytes, ct: bytes) -> bytes:
    return ptrc_kem_decaps_ex(PTRC_KEM_K_LIGHT, sk, ct)


def load_c_pq_kem_library(search_root: Optional[pathlib.Path] = None) -> Optional[ctypes.CDLL]:
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

            lib.ptrc_kem_keygen_ex.argtypes = [ctypes.c_uint32, u8p, u8p, u8p]
            lib.ptrc_kem_keygen_ex.restype = ctypes.c_int
            lib.ptrc_kem_encaps_ex.argtypes = [ctypes.c_uint32, u8p, u8p, u8p, u8p]
            lib.ptrc_kem_encaps_ex.restype = ctypes.c_int
            lib.ptrc_kem_decaps_ex.argtypes = [ctypes.c_uint32, u8p, u8p, u8p]
            lib.ptrc_kem_decaps_ex.restype = ctypes.c_int

            lib.ptrc_kem_keygen.argtypes = [u8p, u8p, u8p]
            lib.ptrc_kem_keygen.restype = ctypes.c_int
            lib.ptrc_kem_encaps.argtypes = [u8p, u8p, u8p, u8p]
            lib.ptrc_kem_encaps.restype = ctypes.c_int
            lib.ptrc_kem_decaps.argtypes = [u8p, u8p, u8p]
            lib.ptrc_kem_decaps.restype = ctypes.c_int

            lib.ptrc_kem_keygen_light.argtypes = [u8p, u8p, u8p]
            lib.ptrc_kem_keygen_light.restype = ctypes.c_int
            lib.ptrc_kem_encaps_light.argtypes = [u8p, u8p, u8p, u8p]
            lib.ptrc_kem_encaps_light.restype = ctypes.c_int
            lib.ptrc_kem_decaps_light.argtypes = [u8p, u8p, u8p]
            lib.ptrc_kem_decaps_light.restype = ctypes.c_int
            return lib
    return None
