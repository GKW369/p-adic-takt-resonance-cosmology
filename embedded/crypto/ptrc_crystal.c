/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.4.0
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

static inline uint32_t ptrc_u32_no_zero(uint32_t u) {
    uint32_t is_zero = ((u | (0U - u)) >> 31U) ^ 1U;
    return u | (0U - is_zero);
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

/* Constant-time O(1) coprime 64-bit modulus derivation (gcd(mod, 210) == 1 without loops) */
static uint64_t ptrc_derive_coprime_mod64_ct(uint64_t raw_word, uint32_t idx) {
    uint64_t acc = raw_word ^ PTRC_PRIMORIAL_P15 ^ ((uint64_t)(idx + 1U) * 137ULL);
    for (uint32_t step = 0U; step < 16U; step++) {
        uint64_t anchor = *(PTRC_COPRIME_ANCHORS + ((step + idx * 3U) & 15U));
        acc = ptrc_rotl64(acc ^ (anchor * 211ULL), (step * 7U + idx * 5U + 3U) & 63U);
        acc += (anchor * 137ULL) | 1ULL;
    }

    /* Keep magnitude in upper 62-bit prime-ring range [2^61 .. 2^62] */
    uint64_t mag = (acc & 0x1FFFFFFFFFFFFFFFULL) | 0x2000000000000000ULL;
    uint64_t base_q = mag / PTRC_PRIMORIAL_210;
    uint64_t rem = (mag % PTRC_PRIMORIAL_210) | 1ULL;

    /* Branchless coprimality nudges for 3, 5, 7 (gcd(70,3)=1, gcd(42,5)=1, gcd(30,7)=1) */
    uint64_t r3 = rem % 3ULL;
    uint64_t div3 = ((r3 | (0ULL - r3)) >> 63U) ^ 1ULL;
    rem = (rem + (70ULL & (0ULL - div3))) % PTRC_PRIMORIAL_210;

    uint64_t r5 = rem % 5ULL;
    uint64_t div5 = ((r5 | (0ULL - r5)) >> 63U) ^ 1ULL;
    rem = (rem + (42ULL & (0ULL - div5))) % PTRC_PRIMORIAL_210;

    uint64_t r7 = rem % 7ULL;
    uint64_t div7 = ((r7 | (0ULL - r7)) >> 63U) ^ 1ULL;
    rem = (rem + (30ULL & (0ULL - div7))) % PTRC_PRIMORIAL_210;

    return ptrc_u64_no_zero((base_q * PTRC_PRIMORIAL_210 + rem) | 1ULL);
}

/* Constant-time O(1) coprime 32-bit inner CRT ring modulus (gcd(mod, 210) == 1) */
static uint32_t ptrc_derive_inner_mod32_ct(uint64_t seed_word, uint32_t idx) {
    uint64_t acc = ptrc_rotl64(seed_word ^ PTRC_PRIMORIAL_P15, (idx * 17U + 9U) & 63U) + 137ULL;
    uint32_t base_q = (uint32_t)((acc % 65536ULL) + 4096ULL);
    uint32_t rem = (uint32_t)(acc % 210ULL) | 1U;

    uint32_t r3 = rem % 3U;
    uint32_t div3 = ((r3 | (0U - r3)) >> 31U) ^ 1U;
    rem = (rem + (70U & (0U - div3))) % 210U;

    uint32_t r5 = rem % 5U;
    uint32_t div5 = ((r5 | (0U - r5)) >> 31U) ^ 1U;
    rem = (rem + (42U & (0U - div5))) % 210U;

    uint32_t r7 = rem % 7U;
    uint32_t div7 = ((r7 | (0U - r7)) >> 31U) ^ 1U;
    rem = (rem + (30U & (0U - div7))) % 210U;

    return ptrc_u32_no_zero((base_q * 210U + rem) | 1U);
}

static int32_t ptrc_plichta_crossed_mirror(int32_t val, uint32_t clock24, uint32_t ring_mod) {
    uint32_t u = (uint32_t)ptrc_crypt_z_no_zero_u32((uint32_t)val);
    uint32_t inv = ~u;
    uint32_t sh = (clock24 & 7U) + 1U;
    uint32_t rot = (inv << sh) | (inv >> (32U - sh));
    uint32_t mixed = rot ^ (ring_mod * 211U) ^ (clock24 * 137U);
    return ptrc_crypt_z_no_zero_u32(mixed);
}

static void ptrc_sponge_step_ct(ptrc_crystal_ctx_t *ctx) {
    uint32_t phase = (uint32_t)(ctx->takt_counter % PTRC_CRYPT_FACETS);
    uint32_t c24 = ctx->clock_phase_24;
    uint32_t inner_m = *(ctx->inner_mod + (c24 % PTRC_CRYPT_INNER_RINGS));
    uint32_t free_facets = PTRC_CRYPT_FACETS - PTRC_CRYPT_JUNCTIONS; /* 120 */

    /* 24-Clock Control Ring couples into 120 outer triangular facets */
    for (uint32_t j = 0U; j < PTRC_CRYPT_JUNCTIONS; j++) {
        uint32_t jf = free_facets + j;
        uint32_t mf = (j * 5U + phase) % free_facets;

        uint32_t uj = (uint32_t)(*(ctx->sponge + jf));
        uint32_t um = (uint32_t)(*(ctx->sponge + mf));
        uint32_t coupled = (uj ^ um) + (inner_m * (j + 1U));

        *(ctx->sponge + jf) = ptrc_plichta_crossed_mirror((int32_t)coupled, c24 + j, inner_m);
        *(ctx->sponge + mf) = ptrc_crypt_z_no_zero_u32(um ^ (coupled >> 3U) ^ (c24 * 17U));
    }

    /* Constant-time 137-Takt Fine-Structure Observer Mirror Pulse */
    uint64_t rem137 = ctx->takt_counter % PTRC_TAKT_137;
    uint32_t is_pulse = (uint32_t)(((rem137 | (0ULL - rem137)) >> 63U) ^ 1ULL);
    uint32_t pulse_mask = 0U - is_pulse;

    for (uint32_t f = 0U; f < PTRC_CRYPT_FACETS; f++) {
        uint32_t uf = (uint32_t)(*(ctx->sponge + f));
        *(ctx->sponge + f) = ptrc_crypt_z_no_zero_u32(uf ^ pulse_mask);
    }

    /* Advance 4-Stage Primorial Macro-Cascade in O(1) */
    for (uint32_t m = 0U; m < PTRC_MACRO_CASCADE_STAGES; m++) {
        uint64_t ms = *(ctx->macro_state + m);
        uint64_t mm = *(ctx->macro_mod + m);
        uint32_t sp_val = (uint32_t)(*(ctx->sponge + ((m * 31U + phase) % PTRC_CRYPT_FACETS)));
        ms = ptrc_rotl64(ms ^ (uint64_t)sp_val ^ (uint64_t)ctx->session_salt, (m * 11U + 7U) & 63U);
        ms = (ms + ((uint64_t)inner_m * 137ULL)) % mm;
        *(ctx->macro_state + m) = ptrc_u64_no_zero(ms);
    }

    ctx->takt_counter++;
    ctx->clock_phase_24 = (ctx->clock_phase_24 % 24U) + 1U;
}

int ptrc_crystal_init(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t key[PTRC_CRYPT_KEY_BYTES],
    const uint8_t nonce[PTRC_CRYPT_NONCE_BYTES]
) {
    if (!ctx || !key || !nonce) {
        return PTRC_CRYPT_ERR;
    }

    uint64_t n0 = ptrc_load_le64(nonce);
    uint64_t n1 = ptrc_load_le64(nonce + 8U);
    ctx->session_salt = ptrc_u32_no_zero((uint32_t)(n0 ^ (n1 >> 17U) ^ 0x9E3779B9U));

    for (uint32_t m = 0U; m < PTRC_MACRO_CASCADE_STAGES; m++) {
        uint64_t w0 = ptrc_load_le64(key + (m * 16U));
        uint64_t w1 = ptrc_load_le64(key + (m * 16U + 8U));
        uint64_t nw = ((m & 1U) == 0U) ? n0 : n1;
        uint64_t mixed_w = ptrc_rotl64(w0 ^ nw, (m * 13U + 5U) & 63U) + (w1 | 1ULL);
        uint64_t mod_m = ptrc_derive_coprime_mod64_ct(mixed_w, m);
        *(ctx->macro_mod + m) = mod_m;
        *(ctx->macro_state + m) = ptrc_u64_no_zero((mixed_w ^ PTRC_PRIMORIAL_P15) % mod_m);
    }

    for (uint32_t r = 0U; r < PTRC_CRYPT_INNER_RINGS; r++) {
        uint64_t rw = *(ctx->macro_state + r) ^ *(ctx->macro_state + (r + 1U));
        *(ctx->inner_mod + r) = ptrc_derive_inner_mod32_ct(rw, r);
    }

    uint64_t acc = PTRC_PRIMORIAL_P15 ^ *(ctx->macro_state + 0U);
    for (uint32_t f = 0U; f < PTRC_CRYPT_FACETS; f++) {
        uint8_t kb = *(key + (f & 63U));
        uint8_t nb = *(nonce + (f & 15U));
        uint8_t odd_in = (uint8_t)(((kb ^ nb) << 1U) | 1U);
        acc = ptrc_rotl64(acc ^ ((uint64_t)odd_in * (uint64_t)(f + 19U)), (f * 5U + 3U) & 63U) + 137ULL;
        int32_t raw = (int32_t)(acc % PTRC_PRIMORIAL_210) - 105;
        *(ctx->sponge + f) = ptrc_crypt_z_no_zero_u32((uint32_t)raw);
    }

    ctx->takt_counter = 1ULL;
    ctx->clock_phase_24 = 1U;

    for (uint32_t step = 0U; step < 72U; step++) {
        ptrc_sponge_step_ct(ctx);
    }

    return PTRC_CRYPT_OK;
}

/* File: embedded/crypto/ptrc_crystal.c (Part 2 of 3 - Hardened Constant-Time v4.4.0) */

static uint8_t ptrc_next_keystream_byte_ct(ptrc_crystal_ctx_t *ctx) {
    ptrc_sponge_step_ct(ctx);

    uint32_t idx = (uint32_t)((ctx->takt_counter * 17ULL) % PTRC_CRYPT_FACETS);
    uint32_t opp = (idx + 72U) % PTRC_CRYPT_FACETS;

    uint32_t s_a = (uint32_t)(*(ctx->sponge + idx));
    uint32_t s_b = (uint32_t)(*(ctx->sponge + opp));
    uint64_t m_a = *(ctx->macro_state + (idx & 3U));
    uint64_t m_b = *(ctx->macro_state + ((idx + 1U) & 3U));
    uint32_t inner = *(ctx->inner_mod + (idx % PTRC_CRYPT_INNER_RINGS));

    uint32_t combined = s_a ^ (s_b >> 5U) ^ (uint32_t)(m_a ^ (m_b >> 13U)) ^ (inner * 137U) ^ ctx->session_salt;
    uint8_t raw_byte = (uint8_t)((combined ^ (combined >> 8U) ^ (combined >> 16U) ^ (combined >> 24U)) & 0xFFU);

    /* Branchless bipolar nudge (+1 or -1) without secret branches */
    uint32_t bit0 = combined & 1U;
    uint32_t nudge = (bit0 << 1U) - 1U;
    uint8_t rot_amt = (uint8_t)((ctx->session_salt >> (idx & 15U)) & 7U);
    uint8_t b = (uint8_t)((uint32_t)ptrc_rotl8(raw_byte, rot_amt) + nudge);

    return ptrc_byte_no_zero(b);
}

int ptrc_crystal_xor_stream(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t *input,
    uint8_t *output,
    size_t len
) {
    if (!ctx || (!input && len > 0U) || (!output && len > 0U)) {
        return PTRC_CRYPT_ERR;
    }
    for (size_t i = 0U; i < len; i++) {
        uint8_t ks = ptrc_next_keystream_byte_ct(ctx);
        *(output + i) = (uint8_t)(*(input + i) ^ ks);
    }
    return PTRC_CRYPT_OK;
}

static void ptrc_compute_slip_mac_ct(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t *aad,
    size_t aad_len,
    const uint8_t *ciphertext,
    size_t ct_len,
    uint8_t tag_out[PTRC_CRYPT_TAG_BYTES]
) {
    uint64_t len_mix = ((uint64_t)aad_len << 32U) ^ (uint64_t)ct_len ^ PTRC_PRIMORIAL_P15;
    for (uint32_t m = 0U; m < PTRC_MACRO_CASCADE_STAGES; m++) {
        uint64_t mm = *(ctx->macro_mod + m);
        uint64_t st = ptrc_rotl64(*(ctx->macro_state + m) ^ len_mix, (m * 9U + 3U) & 63U) % mm;
        *(ctx->macro_state + m) = ptrc_u64_no_zero(st);
    }

    if (aad && aad_len > 0U) {
        for (size_t i = 0U; i < aad_len; i++) {
            uint8_t odd_b = (uint8_t)(((*(aad + i)) << 1U) | 1U);
            uint32_t f_idx = (uint32_t)(i % PTRC_CRYPT_FACETS);
            uint32_t cur = (uint32_t)(*(ctx->sponge + f_idx));
            *(ctx->sponge + f_idx) = ptrc_crypt_z_no_zero_u32(cur ^ ((uint32_t)odd_b * (uint32_t)((i & 31U) + 1U)));
            if ((i & 7U) == 7U) {
                ptrc_sponge_step_ct(ctx);
            }
        }
    }

    if (ciphertext && ct_len > 0U) {
        for (size_t i = 0U; i < ct_len; i++) {
            uint8_t odd_b = (uint8_t)(((*(ciphertext + i)) << 1U) | 1U);
            uint32_t f_idx = (uint32_t)((i + 37U) % PTRC_CRYPT_FACETS);
            uint32_t cur = (uint32_t)(*(ctx->sponge + f_idx));
            *(ctx->sponge + f_idx) = ptrc_crypt_z_no_zero_u32(cur ^ ((uint32_t)odd_b * (uint32_t)((i & 31U) + 3U)));
            if ((i & 7U) == 7U) {
                ptrc_sponge_step_ct(ctx);
            }
        }
    }

    for (uint32_t final_step = 0U; final_step < 48U; final_step++) {
        ptrc_sponge_step_ct(ctx);
    }

    for (uint32_t t = 0U; t < PTRC_CRYPT_TAG_BYTES; t++) {
        *(tag_out + t) = ptrc_next_keystream_byte_ct(ctx);
    }
}

int ptrc_ct_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    if (!a || !b) {
        return PTRC_CRYPT_ERR;
    }
    uint32_t diff = 0U;
    for (size_t i = 0U; i < len; i++) {
        diff |= (uint32_t)(*(a + i) ^ *(b + i));
    }
    uint32_t is_neq = (diff | (0U - diff)) >> 31U;
    uint32_t mask = 0U - is_neq;
    int32_t res = (int32_t)((1U & (~mask)) | ((uint32_t)PTRC_CRYPT_ERR & mask));
    return res;
}

/* File: embedded/crypto/ptrc_crystal.c (Part 3 of 3 - Hardened Constant-Time v4.4.0) */

int ptrc_aead_encrypt(
    const uint8_t key[PTRC_CRYPT_KEY_BYTES],
    const uint8_t nonce[PTRC_CRYPT_NONCE_BYTES],
    const uint8_t *aad,
    size_t aad_len,
    const uint8_t *plaintext,
    size_t pt_len,
    uint8_t *ciphertext,
    uint8_t tag[PTRC_CRYPT_TAG_BYTES]
) {
    if (!key || !nonce || !tag || (!plaintext && pt_len > 0U) || (!ciphertext && pt_len > 0U)) {
        return PTRC_CRYPT_ERR;
    }
    ptrc_crystal_ctx_t ctx;
    if (ptrc_crystal_init(&ctx, key, nonce) != PTRC_CRYPT_OK) {
        ptrc_crystal_wipe(&ctx);
        return PTRC_CRYPT_ERR;
    }
    (void)ptrc_crystal_xor_stream(&ctx, plaintext, ciphertext, pt_len);
    ptrc_compute_slip_mac_ct(&ctx, aad, aad_len, ciphertext, pt_len, tag);
    ptrc_crystal_wipe(&ctx);
    return PTRC_CRYPT_OK;
}

int ptrc_aead_decrypt(
    const uint8_t key[PTRC_CRYPT_KEY_BYTES],
    const uint8_t nonce[PTRC_CRYPT_NONCE_BYTES],
    const uint8_t *aad,
    size_t aad_len,
    const uint8_t *ciphertext,
    size_t ct_len,
    const uint8_t tag[PTRC_CRYPT_TAG_BYTES],
    uint8_t *plaintext
) {
    if (!key || !nonce || !tag || (!ciphertext && ct_len > 0U) || (!plaintext && ct_len > 0U)) {
        return PTRC_CRYPT_ERR;
    }

    ptrc_crystal_ctx_t ctx;
    if (ptrc_crystal_init(&ctx, key, nonce) != PTRC_CRYPT_OK) {
        ptrc_crystal_wipe(&ctx);
        return PTRC_CRYPT_ERR;
    }

    (void)ptrc_crystal_xor_stream(&ctx, ciphertext, plaintext, ct_len);

    uint8_t expected_tag[PTRC_CRYPT_TAG_BYTES];
    ptrc_compute_slip_mac_ct(&ctx, aad, aad_len, ciphertext, ct_len, expected_tag);

    int auth_rc = ptrc_ct_memcmp(expected_tag, tag, PTRC_CRYPT_TAG_BYTES);

    /* Branchless fail-closed wipe of plaintext on auth failure */
    uint32_t is_fail = ((uint32_t)auth_rc) >> 31U;
    uint8_t fail_mask = (uint8_t)(0U - is_fail);
    volatile uint8_t *vp = (volatile uint8_t *)plaintext;
    for (size_t i = 0U; i < ct_len; i++) {
        uint8_t cur = *(vp + i);
        *(vp + i) = (uint8_t)((cur & (uint8_t)(~fail_mask)) | (0xFFU & fail_mask));
    }

    /* Scrub expected_tag and context back to -1 (0xFF) */
    volatile uint8_t *vt = (volatile uint8_t *)expected_tag;
    for (size_t i = 0U; i < PTRC_CRYPT_TAG_BYTES; i++) {
        *(vt + i) = 0xFFU;
    }
    ptrc_crystal_wipe(&ctx);
    return auth_rc;
}

int ptrc_kdf_derive(
    const uint8_t *master_seed,
    size_t seed_len,
    const uint8_t *context_info,
    size_t info_len,
    uint8_t out_key[PTRC_CRYPT_KEY_BYTES],
    uint8_t out_nonce[PTRC_CRYPT_NONCE_BYTES]
) {
    if (!master_seed || seed_len == 0U || !out_key || !out_nonce) {
        return PTRC_CRYPT_ERR;
    }

    uint8_t init_k[PTRC_CRYPT_KEY_BYTES];
    uint8_t init_n[PTRC_CRYPT_NONCE_BYTES];
    for (uint32_t i = 0U; i < PTRC_CRYPT_KEY_BYTES; i++) {
        uint8_t b = *(master_seed + (i % seed_len));
        *(init_k + i) = ptrc_byte_no_zero((uint8_t)(b ^ (uint8_t)(i * 13U + 7U)));
    }
    for (uint32_t i = 0U; i < PTRC_CRYPT_NONCE_BYTES; i++) {
        uint8_t ib = (context_info && info_len > 0U) ? *(context_info + (i % info_len)) : 0xA5U;
        *(init_n + i) = ptrc_byte_no_zero((uint8_t)(ib ^ (uint8_t)(i * 19U + 3U)));
    }

    ptrc_crystal_ctx_t ctx;
    (void)ptrc_crystal_init(&ctx, init_k, init_n);

    for (size_t i = 0U; i < seed_len; i++) {
        uint8_t odd_b = (uint8_t)(((*(master_seed + i)) << 1U) | 1U);
        uint32_t f_idx = (uint32_t)(i % PTRC_CRYPT_FACETS);
        *(ctx.sponge + f_idx) = ptrc_crypt_z_no_zero_u32((uint32_t)(*(ctx.sponge + f_idx)) ^ ((uint32_t)odd_b * 17U));
        if ((i & 7U) == 7U) {
            ptrc_sponge_step_ct(&ctx);
        }
    }

    if (context_info && info_len > 0U) {
        for (size_t i = 0U; i < info_len; i++) {
            uint8_t odd_b = (uint8_t)(((*(context_info + i)) << 1U) | 1U);
            uint32_t f_idx = (uint32_t)((i + 61U) % PTRC_CRYPT_FACETS);
            *(ctx.sponge + f_idx) = ptrc_crypt_z_no_zero_u32((uint32_t)(*(ctx.sponge + f_idx)) ^ ((uint32_t)odd_b * 31U));
            if ((i & 7U) == 7U) {
                ptrc_sponge_step_ct(&ctx);
            }
        }
    }

    for (uint32_t d = 0U; d < 64U; d++) {
        ptrc_sponge_step_ct(&ctx);
    }

    for (uint32_t i = 0U; i < PTRC_CRYPT_KEY_BYTES; i++) {
        *(out_key + i) = ptrc_next_keystream_byte_ct(&ctx);
    }
    for (uint32_t i = 0U; i < PTRC_CRYPT_NONCE_BYTES; i++) {
        *(out_nonce + i) = ptrc_next_keystream_byte_ct(&ctx);
    }

    volatile uint8_t *vk = (volatile uint8_t *)init_k;
    for (size_t i = 0U; i < PTRC_CRYPT_KEY_BYTES; i++) {
        *(vk + i) = 0xFFU;
    }
    volatile uint8_t *vn = (volatile uint8_t *)init_n;
    for (size_t i = 0U; i < PTRC_CRYPT_NONCE_BYTES; i++) {
        *(vn + i) = 0xFFU;
    }
    ptrc_crystal_wipe(&ctx);
    return PTRC_CRYPT_OK;
}

int ptrc_primorial_keygen(
    uint64_t session_takt,
    const uint8_t *domain_seed,
    size_t seed_len,
    uint8_t out_key[PTRC_CRYPT_KEY_BYTES],
    uint8_t out_nonce[PTRC_CRYPT_NONCE_BYTES]
) {
    if (!domain_seed || seed_len == 0U || !out_key || !out_nonce) {
        return PTRC_CRYPT_ERR;
    }
    static const uint8_t crt_moduli[PTRC_KEYGEN_PRIME_RINGS] = { 251U, 241U, 239U, 233U, 229U, 227U, 223U, 211U };
    uint8_t ctx_info[16];
    uint64_t t_nz = ptrc_u64_no_zero(session_takt);
    for (uint32_t i = 0U; i < 8U; i++) {
        uint8_t m = *(crt_moduli + i);
        uint8_t sb = *(domain_seed + (i % seed_len));
        uint8_t res = (uint8_t)(((t_nz + (uint64_t)sb) % (uint64_t)m) + 1U);
        *(ctx_info + i) = ptrc_byte_no_zero(res);
        *(ctx_info + i + 8U) = ptrc_byte_no_zero((uint8_t)(res ^ *(domain_seed + ((i + 8U) % seed_len))));
    }

    int rc = ptrc_kdf_derive(domain_seed, seed_len, ctx_info, sizeof(ctx_info), out_key, out_nonce);

    volatile uint8_t *vc = (volatile uint8_t *)ctx_info;
    for (size_t i = 0U; i < sizeof(ctx_info); i++) {
        *(vc + i) = 0xFFU;
    }
    return rc;
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
