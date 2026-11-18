/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.5.0
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program (see the LICENSE file in the root directory).
 * If not, see <https://gnu.org>.
 * ============================================================================== */

/* File: embedded/crypto/ptrc_pq_kem.c (Part 1 of 3 - FO-CCA2 + comp5 v4.5.0) */

#include "ptrc_pq_kem.h"
#include "ptrc_crystal.h"

typedef struct {
    int32_t coeffs[PTRC_KEM_N];
} ptrc_poly_t;

static inline uint8_t ptrc_kem_byte_no_zero(uint8_t b) {
    uint32_t u = (uint32_t)b;
    uint32_t is_zero = ((u | (0U - u)) >> 31U) ^ 1U;
    return (uint8_t)(u | (0U - is_zero));
}

/* Constant-time Z \ {0} zero-guard for 32-bit signed integers: maps 0 -> -1 */
static inline int32_t ptrc_kem_z_no_zero(uint32_t u) {
    uint32_t is_zero = ((u | (0U - u)) >> 31U) ^ 1U;
    return (int32_t)(u | (0U - is_zero));
}

/* Constant-time canonical reduction into {1 .. q-1} (strictly zero-free in Z_q \ {0}) */
static inline int32_t ptrc_kem_mod_q_nz(int64_t x) {
    int64_t r = x % (int64_t)PTRC_KEM_Q;
    uint64_t is_neg = ((uint64_t)r) >> 63U;
    r += (int64_t)((uint64_t)PTRC_KEM_Q & (0ULL - is_neg));
    uint32_t u = (uint32_t)r;
    uint32_t is_zero = ((u | (0U - u)) >> 31U) ^ 1U;
    u += (PTRC_KEM_Q - 1U) & (0U - is_zero);
    return (int32_t)u;
}

/* Constant-time standard residue in {0 .. q-1} for algebraic ring arithmetic */
static inline int32_t ptrc_kem_mod_q_std(int64_t x) {
    int64_t r = x % (int64_t)PTRC_KEM_Q;
    uint64_t is_neg = ((uint64_t)r) >> 63U;
    r += (int64_t)((uint64_t)PTRC_KEM_Q & (0ULL - is_neg));
    return (int32_t)r;
}

/* Constant-time centered residue in {-(q-1)/2 .. +(q-1)/2} */
static inline int32_t ptrc_kem_center_q(int32_t a_std) {
    int32_t half = (int32_t)(PTRC_KEM_Q / 2U);
    uint32_t gt = (uint32_t)(half - a_std) >> 31U;
    return a_std - (int32_t)((uint32_t)PTRC_KEM_Q & (0U - gt));
}

void ptrc_kem_wipe(void *buf, size_t len) {
    if (!buf) {
        return;
    }
    volatile uint8_t *p = (volatile uint8_t *)buf;
    for (size_t i = 0U; i < len; i++) {
        *(p + i) = 0xFFU;
    }
}

static int ptrc_kem_valid_k(uint32_t k) {
    return (k == PTRC_KEM_K_LIGHT || k == PTRC_KEM_K_STD) ? 1 : 0;
}

/* Hash arbitrary transcript into 64-byte pTRC key + 16-byte nonce via 144-facet KDF */
static void ptrc_kem_hash_transcript(
    uint8_t domain_tag,
    const uint8_t *in_a,
    size_t len_a,
    const uint8_t *in_b,
    size_t len_b,
    uint8_t out_64[PTRC_CRYPT_KEY_BYTES],
    uint8_t out_16[PTRC_CRYPT_NONCE_BYTES]
) {
    uint8_t seed_buf[64];
    for (uint32_t i = 0U; i < 64U; i++) {
        *(seed_buf + i) = (uint8_t)(((i * 137U + (uint32_t)domain_tag * 29U + 11U) & 0xFFU) | 1U);
    }
    if (in_a && len_a > 0U) {
        for (size_t i = 0U; i < len_a; i++) {
            uint32_t idx = (uint32_t)(i & 63U);
            uint8_t v = (uint8_t)(*(seed_buf + idx) ^ *(in_a + i) ^ (uint8_t)((i >> 6U) * 19U));
            *(seed_buf + idx) = ptrc_kem_byte_no_zero(v);
        }
    }

    uint8_t info_buf[64];
    for (uint32_t i = 0U; i < 64U; i++) {
        *(info_buf + i) = (uint8_t)(((i * 211U + (uint32_t)domain_tag * 43U + 7U) & 0xFFU) | 1U);
    }
    if (in_b && len_b > 0U) {
        for (size_t i = 0U; i < len_b; i++) {
            uint32_t idx = (uint32_t)(i & 63U);
            uint8_t v = (uint8_t)(*(info_buf + idx) ^ *(in_b + i) ^ (uint8_t)((i >> 6U) * 31U));
            *(info_buf + idx) = ptrc_kem_byte_no_zero(v);
        }
    }
    *(info_buf + 0U) ^= (uint8_t)(len_a & 0xFFU);
    *(info_buf + 1U) ^= (uint8_t)((len_a >> 8U) & 0xFFU);
    *(info_buf + 2U) ^= (uint8_t)(len_b & 0xFFU);
    *(info_buf + 3U) ^= (uint8_t)((len_b >> 8U) & 0xFFU);

    (void)ptrc_kdf_derive(seed_buf, sizeof(seed_buf), info_buf, sizeof(info_buf), out_64, out_16);
    ptrc_kem_wipe(seed_buf, sizeof(seed_buf));
    ptrc_kem_wipe(info_buf, sizeof(info_buf));
}

/* Expand uniform polynomial in Z_q \ {0} on-the-fly from 32-byte seed and matrix indices */
static void ptrc_kem_expand_uniform_poly(
    ptrc_poly_t *out,
    const uint8_t seed[PTRC_KEM_SEED_BYTES],
    uint8_t row,
    uint8_t col
) {
    uint8_t key[PTRC_CRYPT_KEY_BYTES];
    uint8_t nonce[PTRC_CRYPT_NONCE_BYTES];
    for (uint32_t i = 0U; i < PTRC_CRYPT_KEY_BYTES; i++) {
        uint8_t sb = *(seed + (i & 31U));
        uint8_t v = (uint8_t)(sb ^ (uint8_t)(i * 23U + (uint32_t)row * 71U + (uint32_t)col * 137U));
        *(key + i) = ptrc_kem_byte_no_zero(v);
    }
    for (uint32_t i = 0U; i < PTRC_CRYPT_NONCE_BYTES; i++) {
        uint8_t sb = *(seed + ((i + 11U) & 31U));
        uint8_t v = (uint8_t)(sb ^ (uint8_t)(i * 17U + (uint32_t)row * 13U + (uint32_t)col * 41U));
        *(nonce + i) = ptrc_kem_byte_no_zero(v);
    }

    ptrc_crystal_ctx_t ctx;
    (void)ptrc_crystal_init(&ctx, key, nonce);

    uint8_t zeros[PTRC_KEM_N * 2U];
    uint8_t stream[PTRC_KEM_N * 2U];
    for (uint32_t i = 0U; i < sizeof(zeros); i++) {
        *(zeros + i) = 0xFFU;
    }
    (void)ptrc_crystal_xor_stream(&ctx, zeros, stream, sizeof(stream));

    for (uint32_t n = 0U; n < PTRC_KEM_N; n++) {
        uint32_t lo = (uint32_t)(*(stream + n * 2U));
        uint32_t hi = (uint32_t)(*(stream + n * 2U + 1U));
        uint32_t raw16 = lo | (hi << 8U);
        uint32_t val = (raw16 % (PTRC_KEM_Q - 1U)) + 1U;
        *(out->coeffs + n) = (int32_t)val;
    }

    ptrc_crystal_wipe(&ctx);
    ptrc_kem_wipe(key, sizeof(key));
    ptrc_kem_wipe(nonce, sizeof(nonce));
}

/* ==============================================================================
 * File: embedded/crypto/ptrc_pq_kem.c (Part 2 of 3 - FO-CCA2 + comp5 v4.5.0)
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 * ============================================================================== */

/* Sample centered binomial noise polynomial in Z \ {0}: {-2, -1, +1, +2} */
static void ptrc_kem_sample_noise_poly(
    ptrc_poly_t *out,
    const uint8_t coins[PTRC_KEM_SEED_BYTES],
    uint8_t nonce_tag
) {
    uint8_t key[PTRC_CRYPT_KEY_BYTES];
    uint8_t nonce[PTRC_CRYPT_NONCE_BYTES];
    for (uint32_t i = 0U; i < PTRC_CRYPT_KEY_BYTES; i++) {
        uint8_t cb = *(coins + (i & 31U));
        uint8_t v = (uint8_t)(cb ^ (uint8_t)(i * 37U + (uint32_t)nonce_tag * 97U));
        *(key + i) = ptrc_kem_byte_no_zero(v);
    }
    for (uint32_t i = 0U; i < PTRC_CRYPT_NONCE_BYTES; i++) {
        uint8_t cb = *(coins + ((i + 7U) & 31U));
        uint8_t v = (uint8_t)(cb ^ (uint8_t)(i * 29U + (uint32_t)nonce_tag * 53U));
        *(nonce + i) = ptrc_kem_byte_no_zero(v);
    }

    ptrc_crystal_ctx_t ctx;
    (void)ptrc_crystal_init(&ctx, key, nonce);

    uint8_t mask_in[PTRC_KEM_N];
    uint8_t rnd[PTRC_KEM_N];
    for (uint32_t i = 0U; i < sizeof(mask_in); i++) {
        *(mask_in + i) = 0xAAU;
    }
    (void)ptrc_crystal_xor_stream(&ctx, mask_in, rnd, sizeof(rnd));

    for (uint32_t n = 0U; n < PTRC_KEM_N; n++) {
        uint8_t rb = *(rnd + n);
        int32_t a = (int32_t)((rb & 1U) + ((rb >> 1U) & 1U));
        int32_t b = (int32_t)(((rb >> 2U) & 1U) + ((rb >> 3U) & 1U));
        int32_t diff = a - b; /* in {-2, -1, 0, +1, +2} */
        uint32_t udiff = (uint32_t)diff;
        uint32_t is_zero = ((udiff | (0U - udiff)) >> 31U) ^ 1U;
        int32_t sign_bit = (int32_t)((rb >> 4U) & 1U);
        int32_t nz_fallback = (sign_bit << 1) - 1; /* -1 or +1 */
        uint32_t zmask = 0U - is_zero;
        uint32_t chosen = (udiff & (~zmask)) | ((uint32_t)nz_fallback & zmask);
        *(out->coeffs + n) = ptrc_kem_z_no_zero(chosen);
    }

    ptrc_crystal_wipe(&ctx);
    ptrc_kem_wipe(key, sizeof(key));
    ptrc_kem_wipe(nonce, sizeof(nonce));
}

/* Negacyclic polynomial multiplication in Z_q[X]/(X^256 + 1), zero-free result in {1..q-1} */
static void ptrc_kem_poly_mul_acc(
    ptrc_poly_t *acc,
    const ptrc_poly_t *a,
    const ptrc_poly_t *b
) {
    int64_t tmp[PTRC_KEM_N];
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        *(tmp + i) = (int64_t)ptrc_kem_mod_q_std((int64_t)(*(acc->coeffs + i)));
    }
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        int64_t ai = (int64_t)(*(a->coeffs + i));
        for (uint32_t j = 0U; j < PTRC_KEM_N; j++) {
            int64_t bj = (int64_t)(*(b->coeffs + j));
            uint32_t idx = i + j;
            if (idx < PTRC_KEM_N) {
                *(tmp + idx) += ai * bj;
            } else {
                *(tmp + (idx - PTRC_KEM_N)) -= ai * bj;
            }
        }
    }
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        *(acc->coeffs + i) = ptrc_kem_mod_q_nz(*(tmp + i));
    }
}

static void ptrc_kem_poly_add_nz(ptrc_poly_t *r, const ptrc_poly_t *a, const ptrc_poly_t *b) {
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        int64_t s = (int64_t)ptrc_kem_mod_q_std((int64_t)(*(a->coeffs + i)))
                  + (int64_t)ptrc_kem_mod_q_std((int64_t)(*(b->coeffs + i)));
        *(r->coeffs + i) = ptrc_kem_mod_q_nz(s);
    }
}

static void ptrc_kem_poly_sub_std(ptrc_poly_t *r, const ptrc_poly_t *a, const ptrc_poly_t *b) {
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        int64_t d = (int64_t)ptrc_kem_mod_q_std((int64_t)(*(a->coeffs + i)))
                  - (int64_t)ptrc_kem_mod_q_std((int64_t)(*(b->coeffs + i)));
        *(r->coeffs + i) = ptrc_kem_mod_q_std(d);
    }
}

static void ptrc_kem_poly_pack(uint8_t out[PTRC_KEM_POLY_BYTES], const ptrc_poly_t *p) {
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        uint32_t v = (uint32_t)ptrc_kem_mod_q_nz((int64_t)(*(p->coeffs + i)));
        *(out + i * 2U)      = (uint8_t)(v & 0xFFU);
        *(out + i * 2U + 1U) = (uint8_t)((v >> 8U) & 0xFFU);
    }
}

static void ptrc_kem_poly_unpack(ptrc_poly_t *p, const uint8_t in[PTRC_KEM_POLY_BYTES]) {
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        uint32_t lo = (uint32_t)(*(in + i * 2U));
        uint32_t hi = (uint32_t)(*(in + i * 2U + 1U));
        uint32_t v = lo | (hi << 8U);
        *(p->coeffs + i) = ptrc_kem_mod_q_nz((int64_t)v);
    }
}

/* v4.5.0: 5-bit ciphertext compression (256 * 5 / 8 = 160 bytes) -> max rounding noise +-120 */
static void ptrc_kem_poly_compress5(uint8_t out[PTRC_KEM_V_COMP_BYTES], const ptrc_poly_t *v) {
    for (uint32_t b = 0U; b < PTRC_KEM_V_COMP_BYTES; b++) {
        *(out + b) = 0U;
    }
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        uint32_t x = (uint32_t)ptrc_kem_mod_q_std((int64_t)(*(v->coeffs + i)));
        uint32_t c5 = ((x * 32U + (PTRC_KEM_Q / 2U)) / PTRC_KEM_Q) & 0x1FU;
        uint32_t bit_pos = i * 5U;
        uint32_t byte_idx = bit_pos >> 3U;
        uint32_t shift = bit_pos & 7U;
        *(out + byte_idx) |= (uint8_t)((c5 << shift) & 0xFFU);
        if (shift > 3U) {
            *(out + byte_idx + 1U) |= (uint8_t)((c5 >> (8U - shift)) & 0xFFU);
        }
    }
}

static void ptrc_kem_poly_decompress5(ptrc_poly_t *v, const uint8_t in[PTRC_KEM_V_COMP_BYTES]) {
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        uint32_t bit_pos = i * 5U;
        uint32_t byte_idx = bit_pos >> 3U;
        uint32_t shift = bit_pos & 7U;
        uint32_t lo = (uint32_t)(*(in + byte_idx)) >> shift;
        uint32_t hi = (shift > 3U) ? ((uint32_t)(*(in + byte_idx + 1U)) << (8U - shift)) : 0U;
        uint32_t c5 = (lo | hi) & 0x1FU;
        uint32_t val = (c5 * PTRC_KEM_Q + 16U) / 32U;
        *(v->coeffs + i) = (int32_t)val;
    }
}

/* Deterministic CPA-PKE encryption core used by both Encaps and FO Re-Encryption */
static void ptrc_kem_indcpa_enc(
    uint32_t k,
    const uint8_t *pk,
    const uint8_t msg[PTRC_KEM_MSG_BYTES],
    const uint8_t r_coins[PTRC_KEM_SEED_BYTES],
    uint8_t *ct_out
) {
    const uint8_t *seed_a = pk;
    ptrc_poly_t t_vec[PTRC_KEM_MAX_K];
    ptrc_poly_t r_vec[PTRC_KEM_MAX_K];
    ptrc_poly_t e1_vec[PTRC_KEM_MAX_K];
    ptrc_poly_t u_vec[PTRC_KEM_MAX_K];
    ptrc_poly_t a_ij;
    ptrc_poly_t e2;
    ptrc_poly_t v_poly;

    for (uint32_t i = 0U; i < k; i++) {
        ptrc_kem_poly_unpack(&t_vec[i], pk + PTRC_KEM_SEED_BYTES + i * PTRC_KEM_POLY_BYTES);
        ptrc_kem_sample_noise_poly(&r_vec[i], r_coins, (uint8_t)(0x10U + i));
        ptrc_kem_sample_noise_poly(&e1_vec[i], r_coins, (uint8_t)(0x20U + i));
        for (uint32_t n = 0U; n < PTRC_KEM_N; n++) {
            *(u_vec[i].coeffs + n) = 0;
        }
    }
    ptrc_kem_sample_noise_poly(&e2, r_coins, 0x30U);

    for (uint32_t i = 0U; i < k; i++) {
        for (uint32_t j = 0U; j < k; j++) {
            ptrc_kem_expand_uniform_poly(&a_ij, seed_a, (uint8_t)j, (uint8_t)i);
            ptrc_kem_poly_mul_acc(&u_vec[i], &a_ij, &r_vec[j]);
        }
        ptrc_kem_poly_add_nz(&u_vec[i], &u_vec[i], &e1_vec[i]);
        ptrc_kem_poly_pack(ct_out + i * PTRC_KEM_POLY_BYTES, &u_vec[i]);
    }

    for (uint32_t n = 0U; n < PTRC_KEM_N; n++) {
        *(v_poly.coeffs + n) = 0;
    }
    for (uint32_t i = 0U; i < k; i++) {
        ptrc_kem_poly_mul_acc(&v_poly, &t_vec[i], &r_vec[i]);
    }
    ptrc_kem_poly_add_nz(&v_poly, &v_poly, &e2);

    int32_t half_q = (int32_t)((PTRC_KEM_Q + 1U) / 2U); /* 3841 */
    for (uint32_t n = 0U; n < PTRC_KEM_N; n++) {
        uint32_t bit = ((uint32_t)(*(msg + (n >> 3U))) >> (n & 7U)) & 1U;
        int64_t cur = (int64_t)ptrc_kem_mod_q_std((int64_t)(*(v_poly.coeffs + n)));
        cur += (int64_t)(half_q & (int32_t)(0U - bit));
        *(v_poly.coeffs + n) = ptrc_kem_mod_q_nz(cur);
    }

    ptrc_kem_poly_compress5(ct_out + k * PTRC_KEM_POLY_BYTES, &v_poly);

    ptrc_kem_wipe(r_vec, sizeof(r_vec));
    ptrc_kem_wipe(e1_vec, sizeof(e1_vec));
    ptrc_kem_wipe(&e2, sizeof(e2));
    ptrc_kem_wipe(&v_poly, sizeof(v_poly));
}

/* ==============================================================================
 * File: embedded/crypto/ptrc_pq_kem.c (Part 3 of 3 - FO-CCA2 + comp5 v4.5.0)
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 * ============================================================================== */

int ptrc_kem_keygen_ex(
    uint32_t k,
    const uint8_t seed[PTRC_KEM_SEED_BYTES],
    uint8_t *pk,
    uint8_t *sk
) {
    if (!ptrc_kem_valid_k(k) || !seed || !pk || !sk) {
        return PTRC_KEM_ERR;
    }

    uint8_t expanded_k[PTRC_CRYPT_KEY_BYTES];
    uint8_t expanded_n[PTRC_CRYPT_NONCE_BYTES];
    uint8_t domain_tag[16] = {
        'p','T','R','C','_','K','E','M','_','F','O','_','4','.','5', (uint8_t)k
    };
    (void)ptrc_kdf_derive(seed, PTRC_KEM_SEED_BYTES, domain_tag, sizeof(domain_tag), expanded_k, expanded_n);

    const uint8_t *seed_a = expanded_k;
    const uint8_t *coins_s = expanded_k + 32U;
    uint8_t z_reject[PTRC_KEM_SEED_BYTES];
    for (uint32_t i = 0U; i < 16U; i++) {
        *(z_reject + i) = *(expanded_n + i);
        *(z_reject + i + 16U) = (uint8_t)(*(expanded_k + i) ^ *(expanded_k + i + 32U));
    }

    for (uint32_t i = 0U; i < PTRC_KEM_SEED_BYTES; i++) {
        *(pk + i) = *(seed_a + i);
    }

    ptrc_poly_t s_vec[PTRC_KEM_MAX_K];
    ptrc_poly_t e_vec[PTRC_KEM_MAX_K];
    ptrc_poly_t t_vec[PTRC_KEM_MAX_K];
    ptrc_poly_t a_ij;

    size_t s_bytes = (size_t)k * PTRC_KEM_POLY_BYTES;
    size_t pk_bytes = PTRC_KEM_SEED_BYTES + s_bytes;

    for (uint32_t i = 0U; i < k; i++) {
        ptrc_kem_sample_noise_poly(&s_vec[i], coins_s, (uint8_t)(0x01U + i));
        ptrc_kem_sample_noise_poly(&e_vec[i], coins_s, (uint8_t)(0x81U + i));
        ptrc_kem_poly_pack(sk + i * PTRC_KEM_POLY_BYTES, &s_vec[i]);
        for (uint32_t n = 0U; n < PTRC_KEM_N; n++) {
            *(t_vec[i].coeffs + n) = 0;
        }
    }

    for (uint32_t i = 0U; i < k; i++) {
        for (uint32_t j = 0U; j < k; j++) {
            ptrc_kem_expand_uniform_poly(&a_ij, seed_a, (uint8_t)i, (uint8_t)j);
            ptrc_kem_poly_mul_acc(&t_vec[i], &a_ij, &s_vec[j]);
        }
        ptrc_kem_poly_add_nz(&t_vec[i], &t_vec[i], &e_vec[i]);
        ptrc_kem_poly_pack(pk + PTRC_KEM_SEED_BYTES + i * PTRC_KEM_POLY_BYTES, &t_vec[i]);
    }

    /* FO secret key layout: sk = s_packed || pk || z_reject */
    for (size_t i = 0U; i < pk_bytes; i++) {
        *(sk + s_bytes + i) = *(pk + i);
    }
    for (uint32_t i = 0U; i < PTRC_KEM_SEED_BYTES; i++) {
        *(sk + s_bytes + pk_bytes + i) = *(z_reject + i);
    }

    ptrc_kem_wipe(s_vec, sizeof(s_vec));
    ptrc_kem_wipe(e_vec, sizeof(e_vec));
    ptrc_kem_wipe(expanded_k, sizeof(expanded_k));
    ptrc_kem_wipe(expanded_n, sizeof(expanded_n));
    ptrc_kem_wipe(z_reject, sizeof(z_reject));
    return PTRC_KEM_OK;
}

int ptrc_kem_encaps_ex(
    uint32_t k,
    const uint8_t *pk,
    const uint8_t coins[PTRC_KEM_SEED_BYTES],
    uint8_t *ct,
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
) {
    if (!ptrc_kem_valid_k(k) || !pk || !coins || !ct || !shared_secret) {
        return PTRC_KEM_ERR;
    }

    size_t pk_bytes = PTRC_KEM_SEED_BYTES + (size_t)k * PTRC_KEM_POLY_BYTES;
    size_t ct_bytes = (size_t)k * PTRC_KEM_POLY_BYTES + PTRC_KEM_V_COMP_BYTES;

    uint8_t pk_hash_64[PTRC_CRYPT_KEY_BYTES];
    uint8_t pk_hash_16[PTRC_CRYPT_NONCE_BYTES];
    ptrc_kem_hash_transcript(0xA1U, pk, pk_bytes, NULL, 0U, pk_hash_64, pk_hash_16);

    uint8_t g_64[PTRC_CRYPT_KEY_BYTES];
    uint8_t g_16[PTRC_CRYPT_NONCE_BYTES];
    ptrc_kem_hash_transcript(0xB2U, coins, PTRC_KEM_MSG_BYTES, pk_hash_64, 32U, g_64, g_16);

    const uint8_t *k_bar = g_64;
    const uint8_t *r_coins = g_64 + 32U;

    ptrc_kem_indcpa_enc(k, pk, coins, r_coins, ct);

    uint8_t dummy_nonce[PTRC_CRYPT_NONCE_BYTES];
    ptrc_kem_hash_transcript(0xC3U, k_bar, 32U, ct, ct_bytes, shared_secret, dummy_nonce);

    ptrc_kem_wipe(pk_hash_64, sizeof(pk_hash_64));
    ptrc_kem_wipe(pk_hash_16, sizeof(pk_hash_16));
    ptrc_kem_wipe(g_64, sizeof(g_64));
    ptrc_kem_wipe(g_16, sizeof(g_16));
    ptrc_kem_wipe(dummy_nonce, sizeof(dummy_nonce));
    return PTRC_KEM_OK;
}

int ptrc_kem_decaps_ex(
    uint32_t k,
    const uint8_t *sk,
    const uint8_t *ct,
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
) {
    if (!ptrc_kem_valid_k(k) || !sk || !ct || !shared_secret) {
        return PTRC_KEM_ERR;
    }

    size_t s_bytes = (size_t)k * PTRC_KEM_POLY_BYTES;
    size_t pk_bytes = PTRC_KEM_SEED_BYTES + s_bytes;
    size_t ct_bytes = s_bytes + PTRC_KEM_V_COMP_BYTES;

    const uint8_t *pk = sk + s_bytes;
    const uint8_t *z_reject = sk + s_bytes + pk_bytes;

    ptrc_poly_t s_vec[PTRC_KEM_MAX_K];
    ptrc_poly_t u_vec[PTRC_KEM_MAX_K];
    ptrc_poly_t v_poly;
    ptrc_poly_t su_acc;
    ptrc_poly_t diff;

    for (uint32_t i = 0U; i < k; i++) {
        ptrc_kem_poly_unpack(&s_vec[i], sk + i * PTRC_KEM_POLY_BYTES);
        ptrc_kem_poly_unpack(&u_vec[i], ct + i * PTRC_KEM_POLY_BYTES);
    }
    ptrc_kem_poly_decompress5(&v_poly, ct + s_bytes);

    for (uint32_t n = 0U; n < PTRC_KEM_N; n++) {
        *(su_acc.coeffs + n) = 0;
    }
    for (uint32_t i = 0U; i < k; i++) {
        ptrc_kem_poly_mul_acc(&su_acc, &s_vec[i], &u_vec[i]);
    }
    ptrc_kem_poly_sub_std(&diff, &v_poly, &su_acc);

    uint8_t m_prime[PTRC_KEM_MSG_BYTES];
    for (uint32_t b = 0U; b < PTRC_KEM_MSG_BYTES; b++) {
        *(m_prime + b) = 0U;
    }

    int32_t q_quarter = (int32_t)(PTRC_KEM_Q / 4U);
    for (uint32_t n = 0U; n < PTRC_KEM_N; n++) {
        int32_t c = ptrc_kem_center_q(*(diff.coeffs + n));
        uint32_t sign_m = ((uint32_t)c) >> 31U;
        int32_t abs_c = (int32_t)(((uint32_t)c ^ (0U - sign_m)) + sign_m);
        uint32_t bit = ((uint32_t)(q_quarter - abs_c)) >> 31U;
        *(m_prime + (n >> 3U)) |= (uint8_t)(bit << (n & 7U));
    }

    uint8_t pk_hash_64[PTRC_CRYPT_KEY_BYTES];
    uint8_t pk_hash_16[PTRC_CRYPT_NONCE_BYTES];
    ptrc_kem_hash_transcript(0xA1U, pk, pk_bytes, NULL, 0U, pk_hash_64, pk_hash_16);

    uint8_t g_64[PTRC_CRYPT_KEY_BYTES];
    uint8_t g_16[PTRC_CRYPT_NONCE_BYTES];
    ptrc_kem_hash_transcript(0xB2U, m_prime, PTRC_KEM_MSG_BYTES, pk_hash_64, 32U, g_64, g_16);

    const uint8_t *k_bar_prime = g_64;
    const uint8_t *r_coins_prime = g_64 + 32U;

    uint8_t ct_prime[PTRC_KEM_MAX_CT_BYTES];
    ptrc_kem_indcpa_enc(k, pk, m_prime, r_coins_prime, ct_prime);

    uint32_t ct_diff = 0U;
    for (size_t i = 0U; i < ct_bytes; i++) {
        ct_diff |= (uint32_t)(*(ct + i) ^ *(ct_prime + i));
    }
    uint32_t is_invalid = (ct_diff | (0U - ct_diff)) >> 31U;
    uint8_t fail_mask = (uint8_t)(0U - is_invalid);

    uint8_t ss_valid[PTRC_KEM_SS_BYTES];
    uint8_t ss_reject[PTRC_KEM_SS_BYTES];
    uint8_t dummy_nonce[PTRC_CRYPT_NONCE_BYTES];

    ptrc_kem_hash_transcript(0xC3U, k_bar_prime, 32U, ct, ct_bytes, ss_valid, dummy_nonce);
    ptrc_kem_hash_transcript(0xD4U, z_reject, PTRC_KEM_SEED_BYTES, ct, ct_bytes, ss_reject, dummy_nonce);

    for (uint32_t i = 0U; i < PTRC_KEM_SS_BYTES; i++) {
        *(shared_secret + i) = (uint8_t)((*(ss_valid + i) & (uint8_t)(~fail_mask)) | (*(ss_reject + i) & fail_mask));
    }

    ptrc_kem_wipe(s_vec, sizeof(s_vec));
    ptrc_kem_wipe(&v_poly, sizeof(v_poly));
    ptrc_kem_wipe(&su_acc, sizeof(su_acc));
    ptrc_kem_wipe(&diff, sizeof(diff));
    ptrc_kem_wipe(m_prime, sizeof(m_prime));
    ptrc_kem_wipe(pk_hash_64, sizeof(pk_hash_64));
    ptrc_kem_wipe(pk_hash_16, sizeof(pk_hash_16));
    ptrc_kem_wipe(g_64, sizeof(g_64));
    ptrc_kem_wipe(g_16, sizeof(g_16));
    ptrc_kem_wipe(ct_prime, sizeof(ct_prime));
    ptrc_kem_wipe(ss_valid, sizeof(ss_valid));
    ptrc_kem_wipe(ss_reject, sizeof(ss_reject));
    ptrc_kem_wipe(dummy_nonce, sizeof(dummy_nonce));
    return PTRC_KEM_OK;
}

int ptrc_kem_keygen(
    const uint8_t seed[PTRC_KEM_SEED_BYTES],
    uint8_t pk[PTRC_KEM_PK_BYTES_STD],
    uint8_t sk[PTRC_KEM_SK_BYTES_STD]
) {
    return ptrc_kem_keygen_ex(PTRC_KEM_K_STD, seed, pk, sk);
}

int ptrc_kem_encaps(
    const uint8_t pk[PTRC_KEM_PK_BYTES_STD],
    const uint8_t coins[PTRC_KEM_SEED_BYTES],
    uint8_t ct[PTRC_KEM_CT_BYTES_STD],
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
) {
    return ptrc_kem_encaps_ex(PTRC_KEM_K_STD, pk, coins, ct, shared_secret);
}

int ptrc_kem_decaps(
    const uint8_t sk[PTRC_KEM_SK_BYTES_STD],
    const uint8_t ct[PTRC_KEM_CT_BYTES_STD],
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
) {
    return ptrc_kem_decaps_ex(PTRC_KEM_K_STD, sk, ct, shared_secret);
}

int ptrc_kem_keygen_light(
    const uint8_t seed[PTRC_KEM_SEED_BYTES],
    uint8_t pk[PTRC_KEM_PK_BYTES_LIGHT],
    uint8_t sk[PTRC_KEM_SK_BYTES_LIGHT]
) {
    return ptrc_kem_keygen_ex(PTRC_KEM_K_LIGHT, seed, pk, sk);
}

int ptrc_kem_encaps_light(
    const uint8_t pk[PTRC_KEM_PK_BYTES_LIGHT],
    const uint8_t coins[PTRC_KEM_SEED_BYTES],
    uint8_t ct[PTRC_KEM_CT_BYTES_LIGHT],
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
) {
    return ptrc_kem_encaps_ex(PTRC_KEM_K_LIGHT, pk, coins, ct, shared_secret);
}

int ptrc_kem_decaps_light(
    const uint8_t sk[PTRC_KEM_SK_BYTES_LIGHT],
    const uint8_t ct[PTRC_KEM_CT_BYTES_LIGHT],
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
) {
    return ptrc_kem_decaps_ex(PTRC_KEM_K_LIGHT, sk, ct, shared_secret);
}
