/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.0
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

/* File: embedded/crypto/ptrc_crystal.c (Part 1 of 2) */

#include "ptrc_crystal.h"
#include <string.h>

/* 8 Pairwise Coprime 1-Byte Non-Mersenne Primes (CRT period > 1.09 * 10^19 takts) */
static const uint8_t PTRC_KEYGEN_PRIMES[PTRC_KEYGEN_PRIME_RINGS] = {
    251U, 241U, 239U, 233U, 229U, 227U, 223U, 211U
};

static inline int32_t ptrc_crypt_z_no_zero(int32_t v) {
    return (v == 0) ? -1 : v;
}

static inline uint64_t ptrc_u64_no_zero(uint64_t v) {
    return (v == 0ULL) ? 1ULL : v;
}

static uint64_t ptrc_gcd_u64(uint64_t a, uint64_t b) {
    while (b != 0ULL) {
        uint64_t t = a % b;
        a = b;
        b = t;
    }
    return a;
}

static uint64_t ptrc_read_le64(const uint8_t *p) {
    return ((uint64_t)(*(p + 0U)))
         | ((uint64_t)(*(p + 1U)) << 8U)
         | ((uint64_t)(*(p + 2U)) << 16U)
         | ((uint64_t)(*(p + 3U)) << 24U)
         | ((uint64_t)(*(p + 4U)) << 32U)
         | ((uint64_t)(*(p + 5U)) << 40U)
         | ((uint64_t)(*(p + 6U)) << 48U)
         | ((uint64_t)(*(p + 7U)) << 56U);
}

static void ptrc_write_le64(uint8_t *p, uint64_t v) {
    *(p + 0U) = (uint8_t)(v & 0xFFULL);
    *(p + 1U) = (uint8_t)((v >> 8U) & 0xFFULL);
    *(p + 2U) = (uint8_t)((v >> 16U) & 0xFFULL);
    *(p + 3U) = (uint8_t)((v >> 24U) & 0xFFULL);
    *(p + 4U) = (uint8_t)((v >> 32U) & 0xFFULL);
    *(p + 5U) = (uint8_t)((v >> 40U) & 0xFFULL);
    *(p + 6U) = (uint8_t)((v >> 48U) & 0xFFULL);
    *(p + 7U) = (uint8_t)((v >> 56U) & 0xFFULL);
}

/* Holographic Crossed Plichta-Mirror reflection across -1 in Z \ {0} */
static inline uint8_t plichta_crossed_mirror(uint8_t x, uint32_t quadrant) {
    uint8_t q = quadrant & 3U;
    uint8_t v = (uint8_t)(~x);
    if (q == 1U) {
        v = (uint8_t)((v << 3U) | (v >> 5U));
    } else if (q == 2U) {
        v = (uint8_t)((v << 5U) | (v >> 3U));
    } else if (q == 3U) {
        v = (uint8_t)(((v & 0x0FU) << 4U) | ((v & 0xF0U) >> 4U));
    }
    return (v == 0U) ? 0xFFU : v;
}

/* Table-free 64-bit Primorial Macro-Cascade Step (gcd(mod, 210) == 1) */
static uint64_t ptrc_macro_cascade_step(ptrc_crystal_ctx_t *ctx, uint64_t step_stride) {
    uint64_t acc = PTRC_PRIMORIAL_P15 ^ ctx->takt_counter;
    uint64_t stride = ptrc_u64_no_zero(step_stride);

    for (uint32_t s = 0U; s < PTRC_MACRO_CASCADE_STAGES; s++) {
        uint64_t mod_s = *(ctx->macro_mod + s);
        uint64_t st    = (*(ctx->macro_state + s) + stride + (uint64_t)(s + 1U)) % mod_s;
        st = ptrc_u64_no_zero(st);
        *(ctx->macro_state + s) = st;
        acc ^= (st * (211ULL + (uint64_t)(s * 12U)));
        acc = (acc << 13U) | (acc >> 51U);
    }
    return ptrc_u64_no_zero(acc);
}

int ptrc_crystal_init(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t key[PTRC_CRYPT_KEY_BYTES],
    const uint8_t nonce[PTRC_CRYPT_NONCE_BYTES]
) {
    if (!ctx || !key || !nonce) {
        return PTRC_CRYPT_ERR;
    }

    uint64_t n0 = ptrc_read_le64(nonce);
    uint64_t n1 = ptrc_read_le64(nonce + 8U);

    /* 1. Zero-Table 64-Bit Primorial Modulus Decoding from Key[0..31] */
    for (uint32_t s = 0U; s < PTRC_MACRO_CASCADE_STAGES; s++) {
        uint64_t raw = ptrc_read_le64(key + (s * 8U)) ^ (n0 + (uint64_t)(s * 137U));
        uint64_t mod_s = (raw | (1ULL << 62U) | 1ULL);
        while (ptrc_gcd_u64(mod_s, PTRC_PRIMORIAL_210) != 1ULL) {
            mod_s += 2ULL;
        }
        *(ctx->macro_mod + s) = mod_s;

        uint64_t seed_s = ptrc_read_le64(key + (((s + 4U) & 7U) * 8U)) ^ n1 ^ PTRC_PRIMORIAL_P15;
        *(ctx->macro_state + s) = ptrc_u64_no_zero(seed_s % mod_s);
    }

    /* 2. Dynamic Coprime Inner CRT Ring Selection from Key[32..63] */
    for (uint32_t r = 0U; r < PTRC_CRYPT_INNER_RINGS; r++) {
        uint32_t cand = 257U + (uint32_t)(ptrc_read_le64(key + 32U + (r * 8U)) % 4096ULL) * 2U;
        while (ptrc_gcd_u64((uint64_t)cand, PTRC_PRIMORIAL_210) != 1ULL) {
            cand += 2U;
        }
        *(ctx->inner_mod + r) = cand;
    }

    ctx->takt_counter   = 1ULL;
    ctx->clock_phase_24 = 1U;
    ctx->session_salt   = (uint32_t)(ptrc_u64_no_zero((n0 ^ n1) & 0xFFFFFFFFULL));

    /* 3. Populate 144-Facet Crystalline Sponge strictly in Z \ {0} */
    for (uint32_t f = 0U; f < PTRC_CRYPT_FACETS; f++) {
        uint64_t mix = ptrc_macro_cascade_step(ctx, (uint64_t)(f + 1U) * 137ULL);
        int32_t val = (int32_t)(mix % PTRC_PRIMORIAL_210) - 105;
        *(ctx->sponge + f) = ptrc_crypt_z_no_zero(val);
    }

    /* 4. 576-Step Warm-Up Cascade (4 x 144 Facets) */
    for (uint32_t w = 0U; w < PTRC_CRYPT_FACETS * 4U; w++) {
        uint64_t m = ptrc_macro_cascade_step(ctx, (uint64_t)(w + 1U));
        uint32_t idx = w % PTRC_CRYPT_FACETS;
        int32_t delta = ptrc_crypt_z_no_zero((int32_t)(m % 211ULL) - 105);
        *(ctx->sponge + idx) = ptrc_crypt_z_no_zero((*(ctx->sponge + idx)) ^ delta);
        ctx->takt_counter++;
    }

    return PTRC_CRYPT_OK;
}

/* File: embedded/crypto/ptrc_crystal.c (Part 2 of 2) */

static uint8_t ptrc_next_keystream_byte(ptrc_crystal_ctx_t *ctx) {
    uint32_t phase = (ctx->clock_phase_24 - 1U) % PTRC_CRYPT_JUNCTIONS;
    uint64_t macro_out = ptrc_macro_cascade_step(ctx, (uint64_t)(phase + 1U) * 156ULL);

    uint32_t f0 = (uint32_t)((macro_out + phase) % PTRC_CRYPT_FACETS);
    uint32_t f1 = (f0 + 37U) % PTRC_CRYPT_FACETS;
    uint32_t f2 = (f0 + 73U) % PTRC_CRYPT_FACETS;

    uint32_t m0 = *(ctx->inner_mod + 0U);
    uint32_t m1 = *(ctx->inner_mod + 1U);
    uint32_t m2 = *(ctx->inner_mod + 2U);

    uint32_t r0 = (uint32_t)((uint32_t)(*(ctx->sponge + f0)) ^ (uint32_t)macro_out) % m0;
    uint32_t r1 = (uint32_t)((uint32_t)(*(ctx->sponge + f1)) ^ (uint32_t)(macro_out >> 16U)) % m1;
    uint32_t r2 = (uint32_t)((uint32_t)(*(ctx->sponge + f2)) ^ (uint32_t)(macro_out >> 32U)) % m2;

    int32_t combined = ptrc_crypt_z_no_zero((int32_t)((r0 ^ (r1 << 5U) ^ (r2 << 11U) ^ ctx->session_salt) & 0x7FFFFFFFU));

    if ((ctx->takt_counter % PTRC_TAKT_137) == 0ULL) {
        *(ctx->sponge + f0) = ptrc_crypt_z_no_zero(~(*(ctx->sponge + f0)));
        *(ctx->sponge + f1) = ptrc_crypt_z_no_zero(~(*(ctx->sponge + f1)));
    } else {
        *(ctx->sponge + f0) = ptrc_crypt_z_no_zero((*(ctx->sponge + f0)) + ((combined & 1) ? 1 : -1));
        *(ctx->sponge + f2) = ptrc_crypt_z_no_zero((*(ctx->sponge + f2)) ^ combined);
    }

    uint8_t raw_byte = (uint8_t)((combined ^ (combined >> 8U) ^ (combined >> 16U) ^ (uint32_t)(macro_out >> 48U)) & 0xFFU);
    uint8_t out_byte = plichta_crossed_mirror(raw_byte, phase);

    ctx->takt_counter++;
    ctx->clock_phase_24 = (ctx->clock_phase_24 % PTRC_CRYPT_JUNCTIONS) + 1U;
    return out_byte;
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
        uint8_t ks = ptrc_next_keystream_byte(ctx);
        *(output + i) = (uint8_t)((*(input + i)) ^ ks);
    }
    return PTRC_CRYPT_OK;
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
    for (size_t i = 0U; i < PTRC_CRYPT_KEY_BYTES; i++) {
        uint8_t sb = *(master_seed + (i % seed_len));
        uint8_t ib = (context_info && info_len > 0U) ? (*(context_info + (i % info_len))) : (uint8_t)(i + 1U);
        *(init_k + i) = plichta_crossed_mirror((uint8_t)(sb ^ ib ^ (uint8_t)(i * 137U + 1U)), (uint32_t)i);
    }
    for (size_t i = 0U; i < PTRC_CRYPT_NONCE_BYTES; i++) {
        uint8_t sb = *(master_seed + ((i * 7U) % seed_len));
        *(init_n + i) = plichta_crossed_mirror((uint8_t)(sb ^ (uint8_t)(i * 211U + 1U)), (uint32_t)(i + 1U));
    }

    ptrc_crystal_ctx_t ctx;
    ptrc_crystal_init(&ctx, init_k, init_n);

    for (size_t i = 0U; i < seed_len; i++) {
        uint8_t b = *(master_seed + i);
        uint32_t idx = (uint32_t)(i % PTRC_CRYPT_FACETS);
        *(ctx.sponge + idx) = ptrc_crypt_z_no_zero((*(ctx.sponge + idx)) ^ (int32_t)(b | 1U));
        ptrc_next_keystream_byte(&ctx);
    }
    if (context_info && info_len > 0U) {
        for (size_t i = 0U; i < info_len; i++) {
            uint8_t b = *(context_info + i);
            uint32_t idx = (uint32_t)((i + 37U) % PTRC_CRYPT_FACETS);
            *(ctx.sponge + idx) = ptrc_crypt_z_no_zero((*(ctx.sponge + idx)) ^ (int32_t)(b | 1U));
            ptrc_next_keystream_byte(&ctx);
        }
    }

    for (size_t i = 0U; i < PTRC_CRYPT_KEY_BYTES; i++) {
        *(out_key + i) = ptrc_next_keystream_byte(&ctx);
    }
    for (size_t i = 0U; i < PTRC_CRYPT_NONCE_BYTES; i++) {
        *(out_nonce + i) = ptrc_next_keystream_byte(&ctx);
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

    uint64_t takt = ptrc_u64_no_zero(session_takt);
    uint8_t ring_state[PTRC_KEYGEN_PRIME_RINGS];
    uint8_t takt_buf[PTRC_KEYGEN_PRIME_RINGS];

    for (uint32_t r = 0U; r < PTRC_KEYGEN_PRIME_RINGS; r++) {
        uint8_t prime_r = *(PTRC_KEYGEN_PRIMES + r);
        uint8_t res = (uint8_t)((takt + (uint64_t)(r * 137U)) % (uint64_t)prime_r);
        if (res == 0U) {
            res = 1U;
        }
        *(ring_state + r) = plichta_crossed_mirror(res, r);
        *(takt_buf + r)   = (uint8_t)((takt >> (r * 8U)) & 0xFFULL);
    }

    ptrc_kdf_derive(ring_state, PTRC_KEYGEN_PRIME_RINGS, domain_seed, seed_len, out_key, out_nonce);

    for (size_t i = 0U; i < PTRC_CRYPT_NONCE_BYTES; i++) {
        size_t idx = i & 7U;
        *(out_nonce + i) = (uint8_t)((*(out_nonce + i)) ^ (*(ring_state + idx)) ^ (*(takt_buf + idx)));
    }
    return PTRC_CRYPT_OK;
}

static void ptrc_compute_slip_mac(
    const uint8_t key[PTRC_CRYPT_KEY_BYTES],
    const uint8_t nonce[PTRC_CRYPT_NONCE_BYTES],
    const uint8_t *aad,
    size_t aad_len,
    const uint8_t *ciphertext,
    size_t ct_len,
    uint8_t out_tag[PTRC_CRYPT_TAG_BYTES]
) {
    ptrc_crystal_ctx_t mac_ctx;
    ptrc_crystal_init(&mac_ctx, key, nonce);

    for (size_t i = 0U; i < aad_len; i++) {
        uint32_t f = (uint32_t)(i % PTRC_CRYPT_FACETS);
        *(mac_ctx.sponge + f) = ptrc_crypt_z_no_zero((*(mac_ctx.sponge + f)) ^ (int32_t)((*(aad + i)) | 1U));
        ptrc_next_keystream_byte(&mac_ctx);
    }
    for (size_t i = 0U; i < ct_len; i++) {
        uint32_t f = (uint32_t)((i + 73U) % PTRC_CRYPT_FACETS);
        *(mac_ctx.sponge + f) = ptrc_crypt_z_no_zero((*(mac_ctx.sponge + f)) ^ (int32_t)((*(ciphertext + i)) | 1U));
        ptrc_next_keystream_byte(&mac_ctx);
    }

    uint8_t len_block[PTRC_CRYPT_NONCE_BYTES];
    ptrc_write_le64(len_block, ptrc_u64_no_zero((uint64_t)aad_len));
    ptrc_write_le64(len_block + 8U, ptrc_u64_no_zero((uint64_t)ct_len));
    for (size_t i = 0U; i < PTRC_CRYPT_NONCE_BYTES; i++) {
        uint32_t f = (uint32_t)((i + 137U) % PTRC_CRYPT_FACETS);
        *(mac_ctx.sponge + f) = ptrc_crypt_z_no_zero((*(mac_ctx.sponge + f)) ^ (int32_t)((*(len_block + i)) | 1U));
        ptrc_next_keystream_byte(&mac_ctx);
    }

    for (size_t t = 0U; t < PTRC_CRYPT_TAG_BYTES; t++) {
        *(out_tag + t) = ptrc_next_keystream_byte(&mac_ctx);
    }
    ptrc_crystal_wipe(&mac_ctx);
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
    ptrc_crystal_init(&ctx, key, nonce);
    ptrc_crystal_xor_stream(&ctx, plaintext, ciphertext, pt_len);
    ptrc_crystal_wipe(&ctx);

    ptrc_compute_slip_mac(key, nonce, aad, aad_len, ciphertext, pt_len, tag);
    return PTRC_CRYPT_OK;
}

int ptrc_ct_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    if (!a || !b) {
        return PTRC_CRYPT_ERR;
    }
    uint8_t diff = 0U;
    for (size_t i = 0U; i < len; i++) {
        diff |= (uint8_t)((*(a + i)) ^ (*(b + i)));
    }
    return (diff == 0U) ? PTRC_CRYPT_OK : PTRC_CRYPT_ERR;
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

    uint8_t expected_tag[PTRC_CRYPT_TAG_BYTES];
    ptrc_compute_slip_mac(key, nonce, aad, aad_len, ciphertext, ct_len, expected_tag);

    if (ptrc_ct_memcmp(expected_tag, tag, PTRC_CRYPT_TAG_BYTES) != PTRC_CRYPT_OK) {
        if (plaintext && ct_len > 0U) {
            volatile uint8_t *vp = (volatile uint8_t *)plaintext;
            for (size_t i = 0U; i < ct_len; i++) {
                *(vp + i) = 0xFFU;
            }
        }
        return PTRC_CRYPT_ERR;
    }

    ptrc_crystal_ctx_t ctx;
    ptrc_crystal_init(&ctx, key, nonce);
    ptrc_crystal_xor_stream(&ctx, ciphertext, plaintext, ct_len);
    ptrc_crystal_wipe(&ctx);
    return PTRC_CRYPT_OK;
}

void ptrc_crystal_wipe(ptrc_crystal_ctx_t *ctx) {
    if (!ctx) {
        return;
    }
    /* Scrub SRAM back to Z \ {0} ground state (-1 / 0xFF) instead of zero */
    volatile uint8_t *p = (volatile uint8_t *)ctx;
    for (size_t i = 0U; i < sizeof(*ctx); i++) {
        *(p + i) = 0xFFU;
    }
}
