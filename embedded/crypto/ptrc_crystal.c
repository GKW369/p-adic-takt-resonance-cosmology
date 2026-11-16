/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & 512-Bit Primorial AEAD v4.4.0
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

/* File: embedded/crypto/ptrc_crystal.c (Part 1 of 3 - Hardened Constant-Time v4.4.0) */

#include "ptrc_crystal.h"

/* Primorial P15 = 2 * 3 * 5 * 7 * 11 * 13 * 17 * 19 * 23 * 29 * 31 * 37 * 41 * 43 * 47 */
#define PTRC_PRIMORIAL_P15 614889782588491410ULL
#define PTRC_PRIMORIAL_P4  210ULL
#define PTRC_TAKT_PULSE    137ULL

/* Fixed coprime non-Mersenne ring anchors (gcd(r, 210) == 1) for O(1) initialization */
static const uint64_t PTRC_COPRIME_ANCHORS[16] = {
    11ULL, 13ULL, 17ULL, 19ULL, 23ULL, 29ULL, 37ULL, 41ULL,
    43ULL, 47ULL, 53ULL, 59ULL, 61ULL, 67ULL, 71ULL, 73ULL
};

/* Constant-time zero-free projection: maps 0 -> -1 without branches or signed UB */
static inline int32_t ptrc_crypt_z_no_zero_u32(uint32_t u) {
    uint32_t is_zero = ((u | (0U - u)) >> 31U) ^ 1U;
    uint32_t res = u | (0U - is_zero);
    return (int32_t)res;
}

static inline uint64_t ptrc_u64_no_zero(uint64_t u) {
    uint64_t is_zero = ((u | (0ULL - u)) >> 63U) ^ 1ULL;
    return u | (0ULL - is_zero);
}

static inline uint8_t ptrc_byte_no_zero(uint8_t b) {
    uint32_t u = (uint32_t)b;
    uint32_t is_zero = ((u | (0U - u)) >> 31U) ^ 1U;
    return (uint8_t)(u | (0U - is_zero));
}

static inline uint64_t ptrc_rotl64(uint64_t v, uint32_t shift) {
    uint32_t s = shift & 63U;
    return (s == 0U) ? v : ((v << s) | (v >> (64U - s)));
}

static inline uint8_t ptrc_rotl8(uint8_t v, uint8_t shift) {
    uint8_t s = shift & 7U;
    return (s == 0U) ? v : (uint8_t)((v << s) | (v >> (8U - s)));
}

static uint64_t ptrc_load_le64(const uint8_t *src) {
    uint64_t v = 0ULL;
    for (uint32_t i = 0U; i < 8U; i++) {
        v |= ((uint64_t)(*(src + i))) << (i * 8U);
    }
    return v;
}

/* Constant-time O(1) coprime 64-bit macro-ring derivation without data-dependent loops */
static uint64_t ptrc_derive_macro_ring_ct(uint64_t raw_word, uint32_t ring_idx) {
    uint64_t acc = raw_word ^ PTRC_PRIMORIAL_P15 ^ ((uint64_t)(ring_idx + 1U) * 137ULL);
    for (uint32_t step = 0U; step < 16U; step++) {
        uint64_t anchor = *(PTRC_COPRIME_ANCHORS + ((step + ring_idx * 3U) & 15U));
        acc = ptrc_rotl64(acc ^ (anchor * 211ULL), (step * 7U + ring_idx * 5U + 3U) & 63U);
        acc += (anchor * 137ULL) | 1ULL;
    }

    uint64_t base_q = acc / PTRC_PRIMORIAL_P4;
    uint64_t rem = acc % PTRC_PRIMORIAL_P4;
    rem |= 1ULL;

    uint64_t div3 = (((rem % 3ULL) | (0ULL - (rem % 3ULL))) >> 63U) ^ 1ULL;
    rem = (rem + (70ULL & (0ULL - div3))) % PTRC_PRIMORIAL_P4;

    uint64_t div5 = (((rem % 5ULL) | (0ULL - (rem % 5ULL))) >> 63U) ^ 1ULL;
    rem = (rem + (42ULL & (0ULL - div5))) % PTRC_PRIMORIAL_P4;

    uint64_t div7 = (((rem % 7ULL) | (0ULL - (rem % 7ULL))) >> 63U) ^ 1ULL;
    rem = (rem + (30ULL & (0ULL - div7))) % PTRC_PRIMORIAL_P4;

    uint64_t candidate = base_q * PTRC_PRIMORIAL_P4 + rem;
    return ptrc_u64_no_zero(candidate | 1ULL);
}

/* File: embedded/crypto/ptrc_crystal.c (Part 2 of 3 - Hardened Constant-Time v4.4.0) */

static int32_t ptrc_plichta_crossed_mirror(int32_t val, uint32_t quadrant, uint32_t ring_mod) {
    uint32_t u = (uint32_t)ptrc_crypt_z_no_zero_u32((uint32_t)val);
    uint32_t inv = ~u;
    uint32_t rot = (inv << ((quadrant & 7U) + 1U)) | (inv >> (31U - (quadrant & 7U)));
    uint32_t mixed = rot ^ (ring_mod * 211U) ^ (quadrant * 137U);
    return ptrc_crypt_z_no_zero_u32(mixed);
}

static void ptrc_sponge_step_ct(ptrc_crystal_ctx_t *ctx) {
    uint32_t phase = (uint32_t)(ctx->takt_counter % PTRC_CRYSTAL_FACETS);
    uint32_t q = ctx->quadrant_phase;
    uint32_t r_mod = (uint32_t)(*(ctx->macro_state + (q & 3U)) % 997ULL) | 1U;

    for (uint32_t j = 0U; j < PTRC_CRYSTAL_JUNCTIONS; j++) {
        uint32_t jf = PTRC_CRYSTAL_FREE_FACETS + j;
        uint32_t mf = (j * 5U + phase) % PTRC_CRYSTAL_FREE_FACETS;

        uint32_t uj = (uint32_t)(*(ctx->sponge + jf));
        uint32_t um = (uint32_t)(*(ctx->sponge + mf));
        uint32_t coupled = (uj ^ um) + (r_mod * (j + 1U));

        *(ctx->sponge + jf) = ptrc_plichta_crossed_mirror((int32_t)coupled, q + j, r_mod);
        *(ctx->sponge + mf) = ptrc_crypt_z_no_zero_u32(um ^ (coupled >> 3U) ^ (q * 17U));
    }

    uint64_t rem137 = ctx->takt_counter % PTRC_TAKT_PULSE;
    uint32_t is_pulse = (uint32_t)(((rem137 | (0ULL - rem137)) >> 63U) ^ 1ULL);
    uint32_t pulse_mask = 0U - is_pulse;

    for (uint32_t f = 0U; f < PTRC_CRYSTAL_FACETS; f++) {
        uint32_t uf = (uint32_t)(*(ctx->sponge + f));
        uint32_t flipped = uf ^ pulse_mask;
        *(ctx->sponge + f) = ptrc_crypt_z_no_zero_u32(flipped);
    }

    for (uint32_t m = 0U; m < PTRC_MACRO_RINGS; m++) {
        uint64_t ms = *(ctx->macro_state + m);
        uint64_t anchor = *(PTRC_COPRIME_ANCHORS + ((m + q) & 15U));
        uint32_t sp_val = (uint32_t)(*(ctx->sponge + (m * 31U + phase) % PTRC_CRYSTAL_FACETS));
        ms = ptrc_rotl64(ms ^ (uint64_t)sp_val, (m * 11U + 7U) & 63U);
        ms += (anchor * 137ULL) | 1ULL;
        *(ctx->macro_state + m) = ptrc_u64_no_zero(ms);
    }

    ctx->takt_counter++;
    ctx->quadrant_phase = (ctx->quadrant_phase & 3U) + 1U;
}

int ptrc_crystal_init(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t key[PTRC_KEY_BYTES],
    const uint8_t nonce[PTRC_NONCE_BYTES]
) {
    if (!ctx || !key || !nonce) {
        return PTRC_CRYPT_ERR;
    }

    for (uint32_t m = 0U; m < PTRC_MACRO_RINGS; m++) {
        uint64_t w0 = ptrc_load_le64(key + (m * 16U));
        uint64_t w1 = ptrc_load_le64(key + (m * 16U + 8U));
        uint64_t n_word = ptrc_load_le64(nonce + ((m & 1U) * 8U));
        uint64_t mixed_w = ptrc_rotl64(w0 ^ n_word, (m * 13U + 5U) & 63U) + (w1 | 1ULL);
        *(ctx->macro_state + m) = ptrc_derive_macro_ring_ct(mixed_w, m);
    }

    for (uint32_t i = 0U; i < PTRC_NONCE_BYTES; i++) {
        uint8_t kb = *(key + i) ^ *(key + i + 32U);
        uint8_t nb = *(nonce + i);
        *(ctx->session_salt + i) = ptrc_byte_no_zero((uint8_t)(kb ^ nb ^ (uint8_t)(i * 17U + 1U)));
    }

    uint64_t acc = PTRC_PRIMORIAL_P15 ^ *(ctx->macro_state + 0U);
    for (uint32_t f = 0U; f < PTRC_CRYSTAL_FACETS; f++) {
        uint8_t kb = *(key + (f & 63U));
        uint8_t nb = *(nonce + (f & 15U));
        uint8_t odd_in = (uint8_t)(((kb ^ nb) << 1U) | 1U);
        acc = ptrc_rotl64(acc ^ ((uint64_t)odd_in * (uint64_t)(f + 19U)), (f * 5U + 3U) & 63U) + 137ULL;
        int32_t raw = (int32_t)(acc % PTRC_PRIMORIAL_P4) - 105;
        *(ctx->sponge + f) = ptrc_crypt_z_no_zero_u32((uint32_t)raw);
    }

    ctx->takt_counter = 1ULL;
    ctx->quadrant_phase = 1U;

    for (uint32_t step = 0U; step < 72U; step++) {
        ptrc_sponge_step_ct(ctx);
    }

    return PTRC_CRYPT_OK;
}

static uint8_t ptrc_next_keystream_byte_ct(ptrc_crystal_ctx_t *ctx) {
    ptrc_sponge_step_ct(ctx);

    uint32_t idx = (uint32_t)((ctx->takt_counter * 17ULL) % PTRC_CRYSTAL_FACETS);
    uint32_t opp = (idx + 72U) % PTRC_CRYSTAL_FACETS;

    uint32_t s_a = (uint32_t)(*(ctx->sponge + idx));
    uint32_t s_b = (uint32_t)(*(ctx->sponge + opp));
    uint64_t m_a = *(ctx->macro_state + (idx & 3U));
    uint64_t m_b = *(ctx->macro_state + ((idx + 1U) & 3U));
    uint8_t salt = *(ctx->session_salt + (idx & 15U));

    uint32_t combined = s_a ^ (s_b >> 5U) ^ (uint32_t)(m_a ^ (m_b >> 13U)) ^ ((uint32_t)salt * 137U);
    uint8_t raw_byte = (uint8_t)((combined ^ (combined >> 8U) ^ (combined >> 16U) ^ (combined >> 24U)) & 0xFFU);

    uint32_t bit0 = combined & 1U;
    uint32_t nudge = (bit0 << 1U) - 1U;
    uint8_t b = (uint8_t)((uint32_t)ptrc_rotl8(raw_byte, (uint8_t)(salt & 7U)) + nudge);

    return ptrc_byte_no_zero(b);
}

int ptrc_crystal_xor_stream(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t *in,
    uint8_t *out,
    size_t len
) {
    if (!ctx || (!in && len > 0U) || (!out && len > 0U)) {
        return PTRC_CRYPT_ERR;
    }
    for (size_t i = 0U; i < len; i++) {
        uint8_t ks = ptrc_next_keystream_byte_ct(ctx);
        *(out + i) = (uint8_t)(*(in + i) ^ ks);
    }
    return PTRC_CRYPT_OK;
}

static void ptrc_compute_slip_mac_ct(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t *aad,
    size_t aad_len,
    const uint8_t *ciphertext,
    size_t ct_len,
    uint8_t tag_out[PTRC_TAG_BYTES]
) {
    uint64_t len_mix = ((uint64_t)aad_len << 32U) ^ (uint64_t)ct_len ^ PTRC_PRIMORIAL_P15;
    for (uint32_t m = 0U; m < PTRC_MACRO_RINGS; m++) {
        *(ctx->macro_state + m) = ptrc_u64_no_zero(ptrc_rotl64(*(ctx->macro_state + m) ^ len_mix, (m * 9U + 3U) & 63U));
    }

    for (size_t i = 0U; i < aad_len; i++) {
        uint8_t odd_b = (uint8_t)(((*(aad + i)) << 1U) | 1U);
        uint32_t f_idx = (uint32_t)(i % PTRC_CRYSTAL_FACETS);
        uint32_t cur = (uint32_t)(*(ctx->sponge + f_idx));
        *(ctx->sponge + f_idx) = ptrc_crypt_z_no_zero_u32(cur ^ ((uint32_t)odd_b * (uint32_t)((i & 31U) + 1U)));
        if ((i & 7U) == 7U) {
            ptrc_sponge_step_ct(ctx);
        }
    }

    for (size_t i = 0U; i < ct_len; i++) {
        uint8_t odd_b = (uint8_t)(((*(ciphertext + i)) << 1U) | 1U);
        uint32_t f_idx = (uint32_t)((i + 37U) % PTRC_CRYSTAL_FACETS);
        uint32_t cur = (uint32_t)(*(ctx->sponge + f_idx));
        *(ctx->sponge + f_idx) = ptrc_crypt_z_no_zero_u32(cur ^ ((uint32_t)odd_b * (uint32_t)((i & 31U) + 3U)));
        if ((i & 7U) == 7U) {
            ptrc_sponge_step_ct(ctx);
        }
    }

    for (uint32_t final_step = 0U; final_step < 48U; final_step++) {
        ptrc_sponge_step_ct(ctx);
    }

    for (uint32_t t = 0U; t < PTRC_TAG_BYTES; t++) {
        *(tag_out + t) = ptrc_next_keystream_byte_ct(ctx);
    }
}

/* File: embedded/crypto/ptrc_crystal.c (Part 3 of 3 - Hardened Constant-Time v4.4.0) */

int ptrc_verify_tag_ct(
    const uint8_t tag_a[PTRC_TAG_BYTES],
    const uint8_t tag_b[PTRC_TAG_BYTES]
) {
    if (!tag_a || !tag_b) {
        return PTRC_CRYPT_ERR;
    }
    uint32_t diff = 0U;
    for (uint32_t i = 0U; i < PTRC_TAG_BYTES; i++) {
        diff |= (uint32_t)(*(tag_a + i) ^ *(tag_b + i));
    }
    uint32_t is_neq = (diff | (0U - diff)) >> 31U;
    uint32_t mask = 0U - is_neq;
    int32_t res = (int32_t)((1U & (~mask)) | ((uint32_t)PTRC_CRYPT_ERR & mask));
    return res;
}

int ptrc_aead_encrypt(
    const uint8_t key[PTRC_KEY_BYTES],
    const uint8_t nonce[PTRC_NONCE_BYTES],
    const uint8_t *aad,
    size_t aad_len,
    const uint8_t *plaintext,
    uint8_t *ciphertext,
    size_t len,
    uint8_t tag_out[PTRC_TAG_BYTES]
) {
    if (!key || !nonce || !tag_out || (!plaintext && len > 0U) || (!ciphertext && len > 0U)) {
        return PTRC_CRYPT_ERR;
    }
    ptrc_crystal_ctx_t ctx;
    if (ptrc_crystal_init(&ctx, key, nonce) != PTRC_CRYPT_OK) {
        ptrc_crystal_wipe(&ctx);
        return PTRC_CRYPT_ERR;
    }
    (void)ptrc_crystal_xor_stream(&ctx, plaintext, ciphertext, len);
    ptrc_compute_slip_mac_ct(&ctx, aad, aad_len, ciphertext, len, tag_out);
    ptrc_crystal_wipe(&ctx);
    return PTRC_CRYPT_OK;
}

int ptrc_aead_decrypt(
    const uint8_t key[PTRC_KEY_BYTES],
    const uint8_t nonce[PTRC_NONCE_BYTES],
    const uint8_t *aad,
    size_t aad_len,
    const uint8_t *ciphertext,
    uint8_t *plaintext,
    size_t len,
    const uint8_t tag[PTRC_TAG_BYTES]
) {
    if (!key || !nonce || !tag || (!ciphertext && len > 0U) || (!plaintext && len > 0U)) {
        return PTRC_CRYPT_ERR;
    }

    ptrc_crystal_ctx_t ctx;
    if (ptrc_crystal_init(&ctx, key, nonce) != PTRC_CRYPT_OK) {
        ptrc_crystal_wipe(&ctx);
        return PTRC_CRYPT_ERR;
    }

    (void)ptrc_crystal_xor_stream(&ctx, ciphertext, plaintext, len);

    uint8_t expected_tag[PTRC_TAG_BYTES];
    ptrc_compute_slip_mac_ct(&ctx, aad, aad_len, ciphertext, len, expected_tag);

    int auth_rc = ptrc_verify_tag_ct(expected_tag, tag);

    uint32_t is_fail = ((uint32_t)auth_rc) >> 31U;
    uint8_t fail_mask = (uint8_t)(0U - is_fail);
    volatile uint8_t *vp = (volatile uint8_t *)plaintext;
    for (size_t i = 0U; i < len; i++) {
        uint8_t cur = *(vp + i);
        *(vp + i) = (uint8_t)((cur & (uint8_t)(~fail_mask)) | (0xFFU & fail_mask));
    }

    volatile uint8_t *vt = (volatile uint8_t *)expected_tag;
    for (size_t i = 0U; i < PTRC_TAG_BYTES; i++) {
        *(vt + i) = 0xFFU;
    }
    ptrc_crystal_wipe(&ctx);
    return auth_rc;
}

int ptrc_kdf_derive(
    const uint8_t *ikm,
    size_t ikm_len,
    const uint8_t *salt,
    size_t salt_len,
    const uint8_t *info,
    size_t info_len,
    uint8_t *okm,
    size_t okm_len
) {
    if (!ikm || !okm || okm_len == 0U) {
        return PTRC_CRYPT_ERR;
    }

    uint8_t init_k[PTRC_KEY_BYTES];
    uint8_t init_n[PTRC_NONCE_BYTES];
    for (uint32_t i = 0U; i < PTRC_KEY_BYTES; i++) {
        uint8_t b = (ikm_len > 0U) ? *(ikm + (i % ikm_len)) : 0xFFU;
        *(init_k + i) = ptrc_byte_no_zero((uint8_t)(b ^ (uint8_t)(i * 13U + 7U)));
    }
    for (uint32_t i = 0U; i < PTRC_NONCE_BYTES; i++) {
        uint8_t sb = (salt && salt_len > 0U) ? *(salt + (i % salt_len)) : 0xA5U;
        *(init_n + i) = ptrc_byte_no_zero((uint8_t)(sb ^ (uint8_t)(i * 19U + 3U)));
    }

    ptrc_crystal_ctx_t ctx;
    (void)ptrc_crystal_init(&ctx, init_k, init_n);

    for (size_t i = 0U; i < ikm_len; i++) {
        uint8_t odd_b = (uint8_t)(((*(ikm + i)) << 1U) | 1U);
        uint32_t f_idx = (uint32_t)(i % PTRC_CRYSTAL_FACETS);
        *(ctx.sponge + f_idx) = ptrc_crypt_z_no_zero_u32((uint32_t)(*(ctx.sponge + f_idx)) ^ ((uint32_t)odd_b * 17U));
        if ((i & 7U) == 7U) ptrc_sponge_step_ct(&ctx);
    }
    if (salt && salt_len > 0U) {
        for (size_t i = 0U; i < salt_len; i++) {
            uint8_t odd_b = (uint8_t)(((*(salt + i)) << 1U) | 1U);
            uint32_t f_idx = (uint32_t)((i + 29U) % PTRC_CRYSTAL_FACETS);
            *(ctx.sponge + f_idx) = ptrc_crypt_z_no_zero_u32((uint32_t)(*(ctx.sponge + f_idx)) ^ ((uint32_t)odd_b * 23U));
            if ((i & 7U) == 7U) ptrc_sponge_step_ct(&ctx);
        }
    }
    if (info && info_len > 0U) {
        for (size_t i = 0U; i < info_len; i++) {
            uint8_t odd_b = (uint8_t)(((*(info + i)) << 1U) | 1U);
            uint32_t f_idx = (uint32_t)((i + 61U) % PTRC_CRYSTAL_FACETS);
            *(ctx.sponge + f_idx) = ptrc_crypt_z_no_zero_u32((uint32_t)(*(ctx.sponge + f_idx)) ^ ((uint32_t)odd_b * 31U));
            if ((i & 7U) == 7U) ptrc_sponge_step_ct(&ctx);
        }
    }

    for (uint32_t d = 0U; d < 64U; d++) {
        ptrc_sponge_step_ct(&ctx);
    }

    for (size_t i = 0U; i < okm_len; i++) {
        *(okm + i) = ptrc_next_keystream_byte_ct(&ctx);
    }

    volatile uint8_t *vk = (volatile uint8_t *)init_k;
    for (size_t i = 0U; i < PTRC_KEY_BYTES; i++) *(vk + i) = 0xFFU;
    volatile uint8_t *vn = (volatile uint8_t *)init_n;
    for (size_t i = 0U; i < PTRC_NONCE_BYTES; i++) *(vn + i) = 0xFFU;
    ptrc_crystal_wipe(&ctx);
    return PTRC_CRYPT_OK;
}

int ptrc_primorial_keygen(
    const uint8_t seed[PTRC_SEED_BYTES],
    uint64_t session_takt,
    uint8_t key_out[PTRC_KEY_BYTES],
    uint8_t nonce_out[PTRC_NONCE_BYTES]
) {
    if (!seed || !key_out || !nonce_out) {
        return PTRC_CRYPT_ERR;
    }
    static const uint8_t crt_moduli[8] = { 251U, 241U, 239U, 233U, 229U, 227U, 223U, 211U };
    uint8_t takt_bytes[16];
    uint64_t t_nz = ptrc_u64_no_zero(session_takt);
    for (uint32_t i = 0U; i < 8U; i++) {
        uint8_t m = *(crt_moduli + i);
        uint8_t res = (uint8_t)(((t_nz + (uint64_t)(*(seed + i))) % (uint64_t)m) + 1U);
        *(takt_bytes + i) = ptrc_byte_no_zero(res);
        *(takt_bytes + i + 8U) = ptrc_byte_no_zero((uint8_t)(res ^ *(seed + i + 8U)));
    }

    uint8_t out_buf[PTRC_KEY_BYTES + PTRC_NONCE_BYTES];
    static const uint8_t domain_info[14] = { 'p','T','R','C','-','C','R','T','-','K','G','-','v','4' };
    (void)ptrc_kdf_derive(seed, PTRC_SEED_BYTES, takt_bytes, sizeof(takt_bytes), domain_info, sizeof(domain_info), out_buf, sizeof(out_buf));

    for (uint32_t i = 0U; i < PTRC_KEY_BYTES; i++) *(key_out + i) = *(out_buf + i);
    for (uint32_t i = 0U; i < PTRC_NONCE_BYTES; i++) *(nonce_out + i) = *(out_buf + PTRC_KEY_BYTES + i);

    volatile uint8_t *vo = (volatile uint8_t *)out_buf;
    for (size_t i = 0U; i < sizeof(out_buf); i++) *(vo + i) = 0xFFU;
    volatile uint8_t *vt = (volatile uint8_t *)takt_bytes;
    for (size_t i = 0U; i < sizeof(takt_bytes); i++) *(vt + i) = 0xFFU;
    return PTRC_CRYPT_OK;
}

void ptrc_crystal_wipe(ptrc_crystal_ctx_t *ctx) {
    if (!ctx) {
        return;
    }
    volatile uint8_t *p = (volatile uint8_t *)ctx;
    for (size_t i = 0U; i < sizeof(*ctx); i++) {
        *(p + i) = 0xFFU;
    }
}
