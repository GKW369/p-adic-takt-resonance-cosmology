/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Post-Quantum Ring-KEM v4.2
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

/* File: embedded/crypto/ptrc_pq_kem.c (Part 1 of 2) */

#include "ptrc_pq_kem.h"

static inline int32_t ptrc_kem_z_no_zero(int32_t v) {
    return (v == 0) ? -1 : v;
}

static inline int32_t ptrc_kem_abs32(int32_t x) {
    return (x < 0) ? -x : x;
}

/* Centered modular reduction into Z_{7681} \ {0} = {-3840..-1, +1..+3840} */
static inline int16_t ptrc_kem_mod_q_no_zero(int32_t x) {
    int32_t r = x % PTRC_KEM_Q;
    if (r < 0) {
        r += PTRC_KEM_Q;
    }
    if (r > PTRC_KEM_HALF_Q) {
        r -= PTRC_KEM_Q;
    }
    if (r == 0) {
        r = -1;
    }
    return (int16_t)r;
}

static inline uint8_t ptrc_kem_rotl8(uint8_t v, uint8_t shift) {
    uint8_t s = shift & 7U;
    return (s == 0U) ? v : (uint8_t)((v << s) | (v >> (8U - s)));
}

static void ptrc_kem_sponge_init(ptrc_kem_ctx_t *ctx, const uint8_t *seed, size_t seed_len, uint8_t domain) {
    uint64_t acc = 614889782588491410ULL ^ ((uint64_t)(domain | 1U) * 137ULL);
    for (uint32_t f = 0U; f < PTRC_KEM_FACETS; f++) {
        uint8_t sb = (seed && seed_len > 0U) ? *(seed + (f % seed_len)) : 0xFFU;
        uint8_t odd_b = (uint8_t)((sb << 1U) | 1U);
        acc = ((acc * 211ULL) ^ ((uint64_t)odd_b * (uint64_t)(f + 17U))) + 137ULL;
        acc ^= (acc >> 13U);
        int32_t raw = (int32_t)(acc % PTRC_KEM_PRIMORIAL_210) - 105;
        *(ctx->sponge + f) = ptrc_kem_z_no_zero(raw);
    }
    ctx->takt_counter = 1ULL;
    ctx->quadrant_phase = 1U;
}

static int32_t ptrc_kem_sponge_next(ptrc_kem_ctx_t *ctx) {
    uint32_t idx = (uint32_t)((ctx->takt_counter * 37ULL) % PTRC_KEM_FACETS);
    uint32_t opp = (idx + 73U) % PTRC_KEM_FACETS;
    uint32_t jnc = (idx + 24U) % PTRC_KEM_FACETS;

    int32_t a = *(ctx->sponge + idx);
    int32_t b = *(ctx->sponge + opp);
    int32_t c = *(ctx->sponge + jnc);

    /* Crossed Plichta-Mirror over -1 inside Z \ {0} */
    int32_t mixed = ptrc_kem_z_no_zero((~a) + (b ^ c) + (int32_t)(ctx->quadrant_phase * 11U));
    *(ctx->sponge + idx) = mixed;
    *(ctx->sponge + opp) = ptrc_kem_z_no_zero(b + (mixed >> 2));

    if ((ctx->takt_counter % PTRC_KEM_TAKT_137) == 0ULL) {
        for (uint32_t f = 0U; f < PTRC_KEM_FACETS; f++) {
            *(ctx->sponge + f) = ptrc_kem_z_no_zero(~(*(ctx->sponge + f)));
        }
    }

    ctx->takt_counter++;
    ctx->quadrant_phase = (ctx->quadrant_phase & 3U) + 1U;
    return mixed;
}

/* Sample small centered bipolar noise in {-2, -1, +1, +2} (strictly zero-free) */
static int16_t ptrc_kem_sample_noise(ptrc_kem_ctx_t *ctx) {
    int32_t v = ptrc_kem_sponge_next(ctx);
    int32_t mag = (ptrc_kem_abs32(v) & 1) + 1; /* 1 or 2 */
    return (v < 0) ? (int16_t)(-mag) : (int16_t)mag;
}

/* Expand public ring polynomial A[row][col] on-the-fly from 32-byte seed_a (zero RAM table) */
static void ptrc_kem_expand_a_poly(
    int16_t poly_out[PTRC_KEM_N],
    const uint8_t seed_a[PTRC_KEM_SEED_BYTES],
    uint8_t row,
    uint8_t col
) {
    ptrc_kem_ctx_t local_ctx;
    uint8_t tag = (uint8_t)((((row + 1U) * 17U) ^ ((col + 1U) * 31U)) | 1U);
    ptrc_kem_sponge_init(&local_ctx, seed_a, PTRC_KEM_SEED_BYTES, tag);
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        int32_t raw = ptrc_kem_sponge_next(&local_ctx);
        *(poly_out + i) = ptrc_kem_mod_q_no_zero(raw * 53 + (int32_t)(i * 137U));
    }
    ptrc_kem_wipe(&local_ctx, sizeof(local_ctx));
}

/* Negacyclic polynomial multiplication in Z_q[X]/(X^256 + 1) \ {0} */
static void ptrc_kem_poly_mul_acc(
    int32_t acc[PTRC_KEM_N],
    const int16_t a[PTRC_KEM_N],
    const int16_t b[PTRC_KEM_N]
) {
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        int32_t ai = (int32_t)(*(a + i));
        for (uint32_t j = 0U; j < PTRC_KEM_N; j++) {
            int32_t prod = ai * (int32_t)(*(b + j));
            uint32_t k = i + j;
            if (k < PTRC_KEM_N) {
                *(acc + k) += prod;
            } else {
                *(acc + (k - PTRC_KEM_N)) -= prod;
            }
        }
    }
}

static void ptrc_kem_pack_poly(uint8_t *dst, const int16_t poly[PTRC_KEM_N]) {
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        uint16_t u = (uint16_t)(*(poly + i));
        *(dst + (i * 2U) + 0U) = (uint8_t)(u & 0xFFU);
        *(dst + (i * 2U) + 1U) = (uint8_t)((u >> 8U) & 0xFFU);
    }
}

static void ptrc_kem_unpack_poly(int16_t poly[PTRC_KEM_N], const uint8_t *src) {
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        uint16_t lo = (uint16_t)(*(src + (i * 2U) + 0U));
        uint16_t hi = (uint16_t)(*(src + (i * 2U) + 1U));
        int16_t val = (int16_t)(lo | (hi << 8U));
        *(poly + i) = (val == 0) ? -1 : val;
    }
}

int ptrc_kem_keygen(
    uint8_t pk_out[PTRC_KEM_PK_BYTES],
    uint8_t sk_out[PTRC_KEM_SK_BYTES],
    const uint8_t seed[PTRC_KEM_SEED_BYTES]
) {
    if (!pk_out || !sk_out || !seed) {
        return PTRC_KEM_ERR;
    }

    ptrc_kem_ctx_t ctx;
    ptrc_kem_sponge_init(&ctx, seed, PTRC_KEM_SEED_BYTES, 0x11U);

    /* Derive 32-byte public matrix seed_a in Z \ {0} */
    uint8_t seed_a[PTRC_KEM_SEED_BYTES];
    for (uint32_t i = 0U; i < PTRC_KEM_SEED_BYTES; i++) {
        uint8_t b = (uint8_t)(ptrc_kem_sponge_next(&ctx) & 0xFF);
        *(seed_a + i) = (b == 0U) ? 0xFFU : b;
        *(pk_out + i) = *(seed_a + i);
    }

    /* Sample secret vector s[k][n] and error vector e[k][n] */
    int16_t s[PTRC_KEM_K][PTRC_KEM_N];
    int16_t e[PTRC_KEM_K][PTRC_KEM_N];
    for (uint32_t k = 0U; k < PTRC_KEM_K; k++) {
        for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
            s[k][i] = ptrc_kem_sample_noise(&ctx);
            e[k][i] = ptrc_kem_sample_noise(&ctx);
        }
        ptrc_kem_pack_poly(sk_out + (k * PTRC_KEM_N * 2U), s[k]);
    }

    /* Compute public lattice vector b = A * s + e (mod q) in Z \ {0} */
    int16_t a_poly[PTRC_KEM_N];
    for (uint32_t row = 0U; row < PTRC_KEM_K; row++) {
        int32_t acc[PTRC_KEM_N];
        for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
            acc[i] = (int32_t)e[row][i];
        }
        for (uint32_t col = 0U; col < PTRC_KEM_K; col++) {
            ptrc_kem_expand_a_poly(a_poly, seed_a, (uint8_t)row, (uint8_t)col);
            ptrc_kem_poly_mul_acc(acc, a_poly, s[col]);
        }
        int16_t b_poly[PTRC_KEM_N];
        for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
            b_poly[i] = ptrc_kem_mod_q_no_zero(acc[i]);
        }
        ptrc_kem_pack_poly(pk_out + PTRC_KEM_SEED_BYTES + (row * PTRC_KEM_N * 2U), b_poly);
    }

    ptrc_kem_wipe(&ctx, sizeof(ctx));
    ptrc_kem_wipe(s, sizeof(s));
    ptrc_kem_wipe(e, sizeof(e));
    ptrc_kem_wipe(a_poly, sizeof(a_poly));
    return PTRC_KEM_OK;
}

/* Squeeze a 512-bit (64-byte) shared secret in Z \ {0} from message m and context transcript */

static void ptrc_kem_derive_ss(
    uint8_t ss_out[PTRC_KEM_SS_BYTES],
    const uint8_t msg[PTRC_KEM_MSG_BYTES],
    const uint8_t ct[PTRC_KEM_CT_BYTES]
) {
    ptrc_kem_ctx_t kdf_ctx;
    ptrc_kem_sponge_init(&kdf_ctx, msg, PTRC_KEM_MSG_BYTES, 0x77U);

    /* Absorb all 1152 bytes of the ciphertext into the 144-facet sponge (bit-0 sensitive) */
    for (uint32_t i = 0U; i < PTRC_KEM_CT_BYTES; i++) {
        uint8_t cb = *(ct + i);
        uint8_t odd_cb = (uint8_t)((cb << 1U) | 1U);
        uint32_t f_idx = i % PTRC_KEM_FACETS;
        *(kdf_ctx.sponge + f_idx) = ptrc_kem_z_no_zero(
            (*(kdf_ctx.sponge + f_idx)) ^ ((int32_t)odd_cb * (int32_t)((i & 31U) + 1U))
        );
        if ((i & 7U) == 7U) {
            (void)ptrc_kem_sponge_next(&kdf_ctx);
        }
    }

    /* Diffuse across all 144 facets over 576 steps (24 x 24) */
    for (uint32_t step = 0U; step < 576U; step++) {
        (void)ptrc_kem_sponge_next(&kdf_ctx);
    }

    for (uint32_t i = 0U; i < PTRC_KEM_SS_BYTES; i++) {
        int32_t val = ptrc_kem_sponge_next(&kdf_ctx);
        uint8_t b = (uint8_t)((val ^ (val >> 8)) & 0xFF);
        *(ss_out + i) = (b == 0U) ? 0xFFU : b;
    }

    ptrc_kem_wipe(&kdf_ctx, sizeof(kdf_ctx));
}

int ptrc_kem_encaps(
    uint8_t ct_out[PTRC_KEM_CT_BYTES],
    uint8_t ss_out[PTRC_KEM_SS_BYTES],
    const uint8_t pk[PTRC_KEM_PK_BYTES],
    const uint8_t coins[PTRC_KEM_SEED_BYTES]
) {
    if (!ct_out || !ss_out || !pk || !coins) {
        return PTRC_KEM_ERR;
    }

    ptrc_kem_ctx_t ctx;
    ptrc_kem_sponge_init(&ctx, coins, PTRC_KEM_SEED_BYTES, 0x33U);

    /* 1. Derive 256-bit ephemeral secret message m in Z \ {0} */
    uint8_t msg[PTRC_KEM_MSG_BYTES];
    for (uint32_t i = 0U; i < PTRC_KEM_MSG_BYTES; i++) {
        uint8_t b = (uint8_t)(ptrc_kem_sponge_next(&ctx) & 0xFF);
        *(msg + i) = (b == 0U) ? 0xFFU : b;
    }

    /* 2. Sample ephemeral secret vector r[k][n], error e1[k][n], and scalar error poly e2[n] */
    int16_t r[PTRC_KEM_K][PTRC_KEM_N];
    int16_t e1[PTRC_KEM_K][PTRC_KEM_N];
    int16_t e2[PTRC_KEM_N];
    for (uint32_t k = 0U; k < PTRC_KEM_K; k++) {
        for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
            r[k][i] = ptrc_kem_sample_noise(&ctx);
            e1[k][i] = ptrc_kem_sample_noise(&ctx);
        }
    }
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        e2[i] = ptrc_kem_sample_noise(&ctx);
    }

    /* 3. Compute u = A^T * r + e1 (mod q) and pack into first 1024 bytes of ct_out */
    int16_t a_poly[PTRC_KEM_N];
    for (uint32_t col = 0U; col < PTRC_KEM_K; col++) {
        int32_t acc[PTRC_KEM_N];
        for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
            acc[i] = (int32_t)e1[col][i];
        }
        for (uint32_t row = 0U; row < PTRC_KEM_K; row++) {
            ptrc_kem_expand_a_poly(a_poly, pk, (uint8_t)row, (uint8_t)col);
            ptrc_kem_poly_mul_acc(acc, a_poly, r[row]);
        }
        int16_t u_poly[PTRC_KEM_N];
        for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
            u_poly[i] = ptrc_kem_mod_q_no_zero(acc[i]);
        }
        ptrc_kem_pack_poly(ct_out + (col * PTRC_KEM_N * 2U), u_poly);
    }

    /* 4. Compute v = b^T * r + e2 + round(q/2) * m_bit (mod q) and compress 4-bit nibbles */
    int32_t v_acc[PTRC_KEM_N];
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        v_acc[i] = (int32_t)e2[i];
    }

    int16_t b_poly[PTRC_KEM_N];
    for (uint32_t k = 0U; k < PTRC_KEM_K; k++) {
        ptrc_kem_unpack_poly(b_poly, pk + PTRC_KEM_SEED_BYTES + (k * PTRC_KEM_N * 2U));
        ptrc_kem_poly_mul_acc(v_acc, b_poly, r[k]);
    }

    uint8_t *v_bytes = ct_out + (PTRC_KEM_K * PTRC_KEM_N * 2U);
    for (uint32_t byte_idx = 0U; byte_idx < 128U; byte_idx++) {
        uint8_t packed_nibbles = 0U;
        for (uint32_t nib = 0U; nib < 2U; nib++) {
            uint32_t coeff_idx = byte_idx * 2U + nib;
            uint8_t m_bit = (uint8_t)((*(msg + (coeff_idx >> 3U)) >> (coeff_idx & 7U)) & 1U);
            int32_t m_encode = (m_bit != 0U) ? PTRC_KEM_HALF_Q : 0;
            int32_t v_centered = (int32_t)ptrc_kem_mod_q_no_zero(v_acc[coeff_idx] + m_encode);

            /* Map [-3840..+3840] to [0..7680], then compress cleanly into 4-bit nibble [0..15] */
            uint32_t v_pos = (uint32_t)(v_centered + PTRC_KEM_HALF_Q);
            uint8_t comp4 = (uint8_t)(((v_pos * 16U) + (uint32_t)PTRC_KEM_HALF_Q) / (uint32_t)PTRC_KEM_Q) & 0x0FU;
            packed_nibbles |= (uint8_t)(comp4 << (nib * 4U));
        }
        *(v_bytes + byte_idx) = packed_nibbles;
    }

    /* 5. Derive 512-bit shared secret bound to ciphertext transcript */
    ptrc_kem_derive_ss(ss_out, msg, ct_out);

    ptrc_kem_wipe(&ctx, sizeof(ctx));
    ptrc_kem_wipe(msg, sizeof(msg));
    ptrc_kem_wipe(r, sizeof(r));
    ptrc_kem_wipe(e1, sizeof(e1));
    ptrc_kem_wipe(e2, sizeof(e2));
    ptrc_kem_wipe(a_poly, sizeof(a_poly));
    ptrc_kem_wipe(b_poly, sizeof(b_poly));
    return PTRC_KEM_OK;
}

int ptrc_kem_decaps(
    uint8_t ss_out[PTRC_KEM_SS_BYTES],
    const uint8_t ct[PTRC_KEM_CT_BYTES],
    const uint8_t sk[PTRC_KEM_SK_BYTES]
) {
    if (!ss_out || !ct || !sk) {
        return PTRC_KEM_ERR;
    }

    /* 1. Compute s^T * u in Z_q \ {0} */
    int32_t su_acc[PTRC_KEM_N];
    for (uint32_t i = 0U; i < PTRC_KEM_N; i++) {
        su_acc[i] = 0;
    }

    int16_t s_poly[PTRC_KEM_N];
    int16_t u_poly[PTRC_KEM_N];
    for (uint32_t k = 0U; k < PTRC_KEM_K; k++) {
        ptrc_kem_unpack_poly(s_poly, sk + (k * PTRC_KEM_N * 2U));
        ptrc_kem_unpack_poly(u_poly, ct + (k * PTRC_KEM_N * 2U));
        ptrc_kem_poly_mul_acc(su_acc, s_poly, u_poly);
    }

    /* 2. Decompress v and recover 256-bit message m via centered threshold without floats */
    uint8_t msg[PTRC_KEM_MSG_BYTES];
    for (uint32_t i = 0U; i < PTRC_KEM_MSG_BYTES; i++) {
        *(msg + i) = 0U;
    }

    const uint8_t *v_bytes = ct + (PTRC_KEM_K * PTRC_KEM_N * 2U);
    for (uint32_t byte_idx = 0U; byte_idx < 128U; byte_idx++) {
        uint8_t packed_nibbles = *(v_bytes + byte_idx);
        for (uint32_t nib = 0U; nib < 2U; nib++) {
            uint32_t coeff_idx = byte_idx * 2U + nib;
            uint8_t comp4 = (uint8_t)((packed_nibbles >> (nib * 4U)) & 0x0FU);
            int32_t v_approx = (int32_t)(((uint32_t)comp4 * (uint32_t)PTRC_KEM_Q + 8U) >> 4U) - PTRC_KEM_HALF_Q;

            int32_t diff = (int32_t)ptrc_kem_mod_q_no_zero(v_approx - su_acc[coeff_idx]);
            /* If |diff| > q/4 (1920), bit is 1; otherwise bit is 0 */
            if (ptrc_kem_abs32(diff) > PTRC_KEM_QUARTER_Q) {
                *(msg + (coeff_idx >> 3U)) |= (uint8_t)(1U << (coeff_idx & 7U));
            }
        }
    }

    /* Map any zero byte back into Z \ {0} (0xFF) matching encaps invariant */
    for (uint32_t i = 0U; i < PTRC_KEM_MSG_BYTES; i++) {
        if (*(msg + i) == 0U) {
            *(msg + i) = 0xFFU;
        }
    }

    /* 3. Derive identical 512-bit shared secret (bound to ct[0..31] transcript) */
    ptrc_kem_derive_ss(ss_out, msg, ct);

    ptrc_kem_wipe(s_poly, sizeof(s_poly));
    ptrc_kem_wipe(u_poly, sizeof(u_poly));
    ptrc_kem_wipe(msg, sizeof(msg));
    return PTRC_KEM_OK;
}

void ptrc_kem_wipe(void *ptr, size_t len) {
    if (!ptr || len == 0U) {
        return;
    }
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    for (size_t i = 0U; i < len; i++) {
        *(p + i) = 0xFFU;
    }
}
