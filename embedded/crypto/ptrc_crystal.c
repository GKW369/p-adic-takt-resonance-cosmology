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

#include "ptrc_crystal.h"

static void ptrc_secure_wipe(void *ptr, size_t len) {
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = PTRC_ZERO_GUARD_U8;
    }
}

static uint64_t ptrc_load_le64(const uint8_t *p) {
    return ((uint64_t)p[0])       | ((uint64_t)p[1] << 8)  |
           ((uint64_t)p[2] << 16) | ((uint64_t)p[3] << 24) |
           ((uint64_t)p[4] << 32) | ((uint64_t)p[5] << 40) |
           ((uint64_t)p[6] << 48) | ((uint64_t)p[7] << 56);
}

static void ptrc_store_le64(uint8_t *p, uint64_t v) {
    p[0] = (uint8_t)(v & 0xFFu);
    p[1] = (uint8_t)((v >> 8)  & 0xFFu);
    p[2] = (uint8_t)((v >> 16) & 0xFFu);
    p[3] = (uint8_t)((v >> 24) & 0xFFu);
    p[4] = (uint8_t)((v >> 32) & 0xFFu);
    p[5] = (uint8_t)((v >> 40) & 0xFFu);
    p[6] = (uint8_t)((v >> 48) & 0xFFu);
    p[7] = (uint8_t)((v >> 56) & 0xFFu);
}

static uint64_t ptrc_rotl64(uint64_t x, unsigned int r) {
    r &= 63u;
    return (x << r) | (x >> ((64u - r) & 63u));
}

static uint8_t ptrc_rotl8(uint8_t x, unsigned int r) {
    r &= 7u;
    return (uint8_t)(((x << r) | (x >> ((8u - r) & 7u))) & 0xFFu);
}

static uint8_t ptrc_byte_no_zero(uint8_t b) {
    uint8_t z = (uint8_t)(((uint32_t)(b | (uint8_t)(-(int8_t)b)) >> 7) ^ 1u);
    return (uint8_t)(b | (uint8_t)(0u - z));
}

static uint64_t ptrc_u64_no_zero(uint64_t v) {
    uint64_t z = ((v | (0ULL - v)) >> 63) ^ 1ULL;
    return v | (0ULL - z);
}

static uint32_t ptrc_u32_no_zero(uint32_t v) {
    uint32_t z = ((v | (0U - v)) >> 31) ^ 1U;
    return v | (0U - z);
}

/* Constant-time O(1) coprime derivation to 210 = 2*3*5*7 (64-bit) */
static uint64_t ptrc_derive_coprime_mod64_ct(uint64_t raw) {
    static const uint64_t cands[8] = {
        UINT64_C(0xF5A3C9178B4D2E61),
        UINT64_C(0xE9B7421D6C8A53F1),
        UINT64_C(0xD3C89147A26F5B11),
        UINT64_C(0xC7E158394D9B2A71),
        UINT64_C(0xB9D47281E35C6F11),
        UINT64_C(0xADF28643197E4C31),
        UINT64_C(0x9E85371B624D9A51),
        UINT64_C(0x8F61942D753B8E71)
    };
    uint64_t base = (raw | UINT64_C(0x8000000000000001));
    uint64_t result = UINT64_C(0xFFFFFFFFFFFFFFFB);
    uint32_t found = 0u;

    for (uint32_t i = 0u; i < 8u; ++i) {
        uint64_t cand = (base ^ (cands[i] & UINT64_C(0x7FFFFFFFFFFFFFFE))) | 1ULL;
        uint32_t r3 = (uint32_t)(cand % 3ULL);
        uint32_t r5 = (uint32_t)(cand % 5ULL);
        uint32_t r7 = (uint32_t)(cand % 7ULL);

        uint32_t nz3 = ((r3 | (0u - r3)) >> 31) & 1u;
        uint32_t nz5 = ((r5 | (0u - r5)) >> 31) & 1u;
        uint32_t nz7 = ((r7 | (0u - r7)) >> 31) & 1u;
        uint32_t ok = nz3 & nz5 & nz7;

        uint32_t pick = ok & (found ^ 1u);
        uint64_t mask = 0ULL - (uint64_t)pick;
        result = (result & ~mask) | (cand & mask);
        found |= ok;
    }
    return result;
}

/* Constant-time O(1) coprime derivation to 210 (32-bit inner rings) */
static uint32_t ptrc_derive_inner_mod32_ct(uint32_t raw) {
    static const uint32_t cands[8] = {
        UINT32_C(0xB5A3C911),
        UINT32_C(0xC9B74211),
        UINT32_C(0xD3C89141),
        UINT32_C(0xE7E15831),
        UINT32_C(0x99D47281),
        UINT32_C(0xADF28641),
        UINT32_C(0xBE853711),
        UINT32_C(0xCF619421)
    };
    uint32_t base = (raw | UINT32_C(0x80000001));
    uint32_t result = UINT32_C(0xFFFFFFFB);
    uint32_t found = 0u;

    for (uint32_t i = 0u; i < 8u; ++i) {
        uint32_t cand = (base ^ (cands[i] & UINT32_C(0x7FFFFFFE))) | 1u;
        uint32_t r3 = cand % 3u;
        uint32_t r5 = cand % 5u;
        uint32_t r7 = cand % 7u;

        uint32_t nz3 = ((r3 | (0u - r3)) >> 31) & 1u;
        uint32_t nz5 = ((r5 | (0u - r5)) >> 31) & 1u;
        uint32_t nz7 = ((r7 | (0u - r7)) >> 31) & 1u;
        uint32_t ok = nz3 & nz5 & nz7;

        uint32_t pick = ok & (found ^ 1u);
        uint32_t mask = 0u - pick;
        result = (result & ~mask) | (cand & mask);
        found |= ok;
    }
    return result;
}

static uint64_t ptrc_mulmod64(uint64_t a, uint64_t b, uint64_t m) {
#if defined(__SIZEOF_INT128__)
    return (uint64_t)(((__uint128_t)a * (__uint128_t)b) % (__uint128_t)m);
#else
    uint64_t res = 0ULL;
    a %= m;
    for (int i = 0; i < 64; ++i) {
        uint64_t mask = 0ULL - (b & 1ULL);
        uint64_t sum = res + a;
        if (sum >= m || sum < res) {
            sum -= m;
        }
        res = (res & ~mask) | (sum & mask);
        b >>= 1;
        uint64_t dbl = a + a;
        if (dbl >= m || dbl < a) {
            dbl -= m;
        }
        a = dbl;
    }
    return res;
#endif
}

static void ptrc_crystal_permute_round(ptrc_crystal_ctx_t *ctx) {
    /* 1. 64-bit 4-stage Primorial Macro-Cascade */
    uint64_t prev_out = ptrc_u64_no_zero(ctx->p_state[3] ^ (ctx->counter + 1ULL));
    for (int i = 0; i < 4; ++i) {
        uint64_t m = ctx->p_ring[i];
        uint64_t x = ctx->p_state[i] ^ ptrc_rotl64(prev_out, (unsigned int)(13 * (i + 1)));
        x = (x % (m - 1ULL)) + 1ULL;
        uint64_t y = ptrc_mulmod64(x, ctx->p_mult[i], m);
        y = ptrc_u64_no_zero(y);
        ctx->p_state[i] = y;
        prev_out = y;
    }

    /* 2. Inner 32-bit coprime CRT rings coupled with 137-pulse */
    uint64_t cascade_mix = ctx->p_state[0] ^ ptrc_rotl64(ctx->p_state[1], 17) ^
                           ptrc_rotl64(ctx->p_state[2], 31) ^ ptrc_rotl64(ctx->p_state[3], 47);

    for (int j = 0; j < 3; ++j) {
        uint32_t im = ctx->inner_mod[j];
        uint32_t inj = (uint32_t)((cascade_mix >> (j * 21)) & UINT32_C(0x1FFFFF));
        uint32_t s = ctx->inner_state[j] ^ inj ^ (ctx->pulse_137 * (uint32_t)(j + 3));
        s = (s % (im - 1u)) + 1u;
        uint64_t prod = (uint64_t)s * (uint64_t)(137u + (uint32_t)j * 24u + 1u);
        s = (uint32_t)(prod % (uint64_t)im);
        ctx->inner_state[j] = ptrc_u32_no_zero(s);
    }

    /* 3. 144-Facet Coupled Tri-Facet Sponge */
    uint32_t base_idx = (ctx->takt_24 * 6u) % PTRC_FACET_COUNT;
    uint32_t i0 = base_idx;
    uint32_t i1 = (base_idx + 24u + (ctx->inner_state[0] % 23u)) % PTRC_FACET_COUNT;
    uint32_t i2 = (base_idx + 72u + (ctx->inner_state[1] % 47u)) % PTRC_FACET_COUNT;

    uint8_t f0 = ctx->facets[i0];
    uint8_t f1 = ctx->facets[i1];
    uint8_t f2 = ctx->facets[i2];

    uint8_t k_byte = (uint8_t)((cascade_mix >> ((ctx->takt_24 & 7u) * 8u)) & 0xFFu);
    uint8_t n0 = ptrc_rotl8((uint8_t)(f0 ^ f1 ^ k_byte), 3);
    uint8_t n1 = ptrc_rotl8((uint8_t)(f1 + f2 + (uint8_t)ctx->pulse_137), 5);
    uint8_t n2 = (uint8_t)(~(f2 ^ n0 ^ (uint8_t)(ctx->inner_state[2] & 0xFFu)));

    ctx->facets[i0] = ptrc_byte_no_zero(n0);
    ctx->facets[i1] = ptrc_byte_no_zero(n1);
    ctx->facets[i2] = ptrc_byte_no_zero(n2);

    /* Advance 24-takt & 137-pulse clocks */
    ctx->takt_24 = (ctx->takt_24 + 1u) % 24u;
    ctx->pulse_137 = (ctx->pulse_137 + 1u) % 137u;
    ctx->counter += 1ULL;
}

/* ==============================================================================
 * File: embedded/crypto/ptrc_crystal.c (Part 2 of 3 - Hardened Constant-Time v4.5.0)
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 * ============================================================================== */

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

/* Internal crystal keystream state strictly in Z \ {0}: {1 .. 256} (never 0) */
static uint16_t ptrc_next_keystream_state_ct(ptrc_crystal_ctx_t *ctx) {
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

    return (uint16_t)((uint16_t)b + 1U);
}

/* Unbiased 8-bit XOR mask in {0..255} projected from {1..256} without 0xFF duplication */
static uint8_t ptrc_next_keystream_byte_ct(ptrc_crystal_ctx_t *ctx) {
    uint16_t nz_state = ptrc_next_keystream_state_ct(ctx);
    return (uint8_t)((nz_state - 1U) & 0xFFU);
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

/* ==============================================================================
 * File: embedded/crypto/ptrc_crystal.c (Part 3 of 3 - Hardened Constant-Time v4.5.0)
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 * ============================================================================== */

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
    uint8_t folded_seed[16];
    for (size_t j = 0U; j < 16U; j++) {
        *(folded_seed + j) = (uint8_t)(((j * 137U) + 211U) & 0xFFU);
    }
    for (size_t j = 0U; j < seed_len; j++) {
        size_t slot = j & 15U;
        *(folded_seed + slot) = ptrc_rotl8((uint8_t)(*(folded_seed + slot) ^ *(domain_seed + j)), 3U);
    }

    uint8_t ctx_info[16];
    uint64_t t_nz = ptrc_u64_no_zero(session_takt);
    for (uint32_t i = 0U; i < 8U; i++) {
        uint8_t m = *(crt_moduli + i);
        uint8_t sb = *(folded_seed + i);
        uint8_t res = (uint8_t)(((t_nz + (uint64_t)sb) % (uint64_t)m) + 1U);
        *(ctx_info + i) = ptrc_byte_no_zero(res);
        *(ctx_info + i + 8U) = ptrc_byte_no_zero((uint8_t)(res ^ *(folded_seed + i + 8U)));
    }

    int rc = ptrc_kdf_derive(domain_seed, seed_len, ctx_info, sizeof(ctx_info), out_key, out_nonce);

    volatile uint8_t *vf = (volatile uint8_t *)folded_seed;
    for (size_t i = 0U; i < sizeof(folded_seed); i++) {
        *(vf + i) = 0xFFU;
    }
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
