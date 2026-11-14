# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
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

# -*- coding: utf-8 -*-

#include "ptrc_crystal.h"
#include <string.h>

static const uint16_t PRIME_RING_POOL[16] = {
    11, 13, 17, 19, 23, 29, 31, 37,
    41, 43, 47, 53, 59, 61, 67, 71
};

static inline uint8_t rotl8(uint8_t value, uint8_t shift) {
    shift &= 7;
    return (uint8_t)((value << shift) | (value >> ((8 - shift) & 7)));
}

/* Euclidean GCD Sieve from prime_lattice_determinism.py (Zero-Float) */
static uint64_t ptrc_gcd64(uint64_t a, uint64_t b) {
    while (b > 0ULL) {
        uint64_t tmp = b;
        b = a % b;
        a = tmp;
    }
    return a;
}

/* Generates a 64-bit coprime Primorial-encoded ring modulus on-the-fly (Zero Table RAM) */
static uint64_t ptrc_decode_macro_ring(const uint8_t *k_slice, uint8_t stage) {
    uint64_t raw = 0ULL;
    for (size_t i = 0; i < 8; i++) {
        raw = (raw << 8) | (uint64_t)k_slice[i];
    }
    /* Anchor inside P15 Primorial scale and lock onto a coprime ray (gcd == 1 with 210) */
    uint64_t base = (PRIMORIAL_P15 / (uint64_t)(stage + 2)) + (raw % (PRIMORIAL_P15 / 8ULL));
    uint64_t candidate = (base - (base % MOD_BASE)) + (uint64_t)((raw % 48ULL) * 4ULL + 1ULL);
    while (ptrc_gcd64(candidate, MOD_BASE) != 1ULL) {
        candidate += 2ULL;
    }
    return candidate;
}

/* Crossed Plichta-Mirror in Z \ {0} (Jumps across -1 without 0) */
static inline uint8_t plichta_crossed_mirror(uint8_t b, uint8_t quadrant_phase) {
    int16_t z_val = (int16_t)b - 128;
    int16_t non_zero = (z_val >= 0) ? (z_val + 1) : z_val;
    int16_t reflected = -non_zero;
    uint8_t u_ref = (reflected > 0) ? (uint8_t)(reflected - 1 + 128) : (uint8_t)(reflected + 128);
    uint8_t q_rot = (uint8_t)((quadrant_phase & 3) * 2);
    return rotl8(u_ref, q_rot);
}

static inline uint8_t plichta_crossed_unmirror(uint8_t m, uint8_t quadrant_phase) {
    uint8_t q_rot = (uint8_t)((8 - ((quadrant_phase & 3) * 2)) & 7);
    uint8_t u_ref = rotl8(m, q_rot);
    int16_t z_ref = (int16_t)u_ref - 128;
    int16_t reflected = (z_ref >= 0) ? (z_ref + 1) : z_ref;
    int16_t orig_nz = -reflected;
    return (orig_nz > 0) ? (uint8_t)(orig_nz - 1 + 128) : (uint8_t)(orig_nz + 128);
}

static int ptrc_verify_tag_ct(const uint8_t tag_a[SLIP_TAG_BYTES], const uint8_t tag_b[SLIP_TAG_BYTES]) {
    uint8_t diff = 0;
    for (size_t i = 0; i < SLIP_TAG_BYTES; i++) {
        diff |= (uint8_t)(tag_a[i] ^ tag_b[i]);
    }
    return (diff == 0) ? 1 : 0;
}

void ptrc_crystal_wipe(ptrc_crystal_ctx_t *ctx) {
    volatile uint8_t *p = (volatile uint8_t *)ctx;
    for (size_t i = 0; i < sizeof(ptrc_crystal_ctx_t); i++) {
        p[i] = 0;
    }
}

/* Advances the 4-Stage 64-Bit Primorial Macro-Cascade and returns an 8-bit interference mask */
static uint8_t ptrc_macro_cascade_step(ptrc_crystal_ctx_t *ctx) {
    uint64_t fold = 0ULL;
    for (size_t s = 0; s < 4; s++) {
        uint64_t step_stride = (uint64_t)(1836ULL + (s * 137ULL) + (fold & 0xFFFFULL));
        ctx->macro_state[s] = (ctx->macro_state[s] + step_stride) % ctx->macro_mod[s];
        fold ^= (ctx->macro_state[s] ^ (ctx->macro_state[s] >> 17) ^ (ctx->macro_state[s] >> 33));
    }
    return (uint8_t)((fold ^ (fold >> 8) ^ (fold >> 16) ^ (fold >> 24)) & 0xFFULL);
}

static void ptrc_lattice_takt_step(ptrc_crystal_ctx_t *ctx) {
    uint8_t macro_mask = ptrc_macro_cascade_step(ctx);
    uint32_t t = ctx->takt_counter;
    uint8_t j_idx = (uint8_t)(t % CONTROL_TAKT);
    uint8_t f_idx_a = (uint8_t)((t * 7) % FREE_FACETS);
    uint8_t f_idx_b = (uint8_t)((t * 13 + 5) % FREE_FACETS);

    ctx->crt_phase_1 = (uint16_t)((ctx->crt_phase_1 + 5) % ctx->dyn_ring_1);
    ctx->crt_phase_2 = (uint16_t)((ctx->crt_phase_2 + 7) % ctx->dyn_ring_2);
    ctx->crt_phase_3 = (uint16_t)((ctx->crt_phase_3 + 11) % ctx->dyn_ring_3);

    uint8_t crt_mix = (uint8_t)((ctx->crt_phase_1 * 19) + (ctx->crt_phase_2 * 17) + (ctx->crt_phase_3 * 13) + macro_mask);
    uint8_t base_takt = (uint8_t)(((t * CONTROL_TAKT) + KEY_SHIFT) % (uint32_t)MOD_BASE);

    uint8_t j_val = ctx->junctions[j_idx];
    uint8_t f_a = ctx->outer_facets[f_idx_a];
    uint8_t f_b = ctx->outer_facets[f_idx_b];

    uint8_t mixed = (uint8_t)((j_val ^ base_takt ^ macro_mask) * 11 + f_a + crt_mix);
    mixed = rotl8(mixed, 3) ^ f_b;

    ctx->junctions[j_idx] = (uint8_t)((j_val + mixed) * 7 + 1);
    ctx->outer_facets[f_idx_a] = (uint8_t)(f_a ^ rotl8(mixed, 5));
    ctx->outer_facets[f_idx_b] = (uint8_t)((f_b + ctx->junctions[j_idx]) ^ crt_mix);

    if ((t % RENDER_TAKT_137) == 0) {
        uint8_t frame_parity = (uint8_t)(INVARIANT_LIMIT ^ macro_mask);
        for (size_t k = 0; k < CONTROL_TAKT; k++) {
            frame_parity ^= rotl8(ctx->junctions[k], (uint8_t)(k & 7));
        }
        for (size_t f = 0; f < FREE_FACETS; f++) {
            uint8_t h_mirror = plichta_crossed_mirror(ctx->outer_facets[f], (uint8_t)(f & 3));
            ctx->outer_facets[f] = (uint8_t)((h_mirror + frame_parity) ^ ctx->junctions[f % CONTROL_TAKT]);
        }
    }

    ctx->takt_counter++;
}

void ptrc_crystal_init(ptrc_crystal_ctx_t *ctx, const uint8_t key[PTRC_KEY_BYTES], const uint8_t nonce[PTRC_NONCE_BYTES]) {
    memset(ctx, 0, sizeof(ptrc_crystal_ctx_t));

    /* First 256 bits (key[0..31]) decode the 4 Macro-Primorial Rings without lookup tables */
    for (uint8_t s = 0; s < 4; s++) {
        ctx->macro_mod[s] = ptrc_decode_macro_ring(&key[s * 8], s);
        uint64_t n_part = ((uint64_t)nonce[s * 4] << 24) | ((uint64_t)nonce[s * 4 + 1] << 16) |
                          ((uint64_t)nonce[s * 4 + 2] << 8) | (uint64_t)nonce[s * 4 + 3];
        ctx->macro_state[s] = n_part % ctx->macro_mod[s];
    }

    /* Second 256 bits (key[32..63]) configure the 144-Facet Crystal & Dynamic Inner Rings */
    const uint8_t *c_key = &key[32];
    uint8_t idx1 = (uint8_t)((c_key[0] ^ c_key[16]) & 0x0F);
    uint8_t idx2 = (uint8_t)((idx1 + 1 + ((c_key[1] ^ c_key[17]) % 15)) & 0x0F);
    uint8_t idx3 = (uint8_t)((idx2 + 1 + ((c_key[2] ^ c_key[18]) % 14)) & 0x0F);

    ctx->dyn_ring_1 = PRIME_RING_POOL[idx1];
    ctx->dyn_ring_2 = PRIME_RING_POOL[idx2];
    ctx->dyn_ring_3 = PRIME_RING_POOL[idx3];

    for (size_t i = 0; i < CONTROL_TAKT; i++) {
        ctx->junctions[i] = (uint8_t)(c_key[i] ^ c_key[(i + 8) & 31] ^ INVARIANT_LIMIT);
    }
    for (size_t i = 0; i < FREE_FACETS; i++) {
        uint8_t k_byte = c_key[(i * 7) & 31];
        uint8_t n_byte = nonce[(i * 5) & 15];
        ctx->outer_facets[i] = plichta_crossed_mirror((uint8_t)(k_byte * 13 + n_byte * 17 + (uint8_t)i), (uint8_t)i);
    }

    ctx->crt_phase_1 = (uint16_t)((c_key[3] ^ nonce[0]) % ctx->dyn_ring_1);
    ctx->crt_phase_2 = (uint16_t)((c_key[4] ^ nonce[1]) % ctx->dyn_ring_2);
    ctx->crt_phase_3 = (uint16_t)((c_key[5] ^ nonce[2]) % ctx->dyn_ring_3);

    for (size_t w = 0; w < (CONTROL_TAKT * CONTROL_TAKT); w++) {
        ptrc_lattice_takt_step(ctx);
    }
}

static void ptrc_absorb_aad(ptrc_crystal_ctx_t *ctx, const uint8_t *aad, size_t aad_len) {
    for (size_t i = 0; i < aad_len; i++) {
        uint8_t j_idx = (uint8_t)(ctx->takt_counter % CONTROL_TAKT);
        uint8_t f_idx = (uint8_t)((ctx->takt_counter * 13) % FREE_FACETS);
        ctx->junctions[j_idx] ^= aad[i];
        ctx->outer_facets[f_idx] = (uint8_t)(ctx->outer_facets[f_idx] + plichta_crossed_mirror(aad[i], j_idx));
        ptrc_lattice_takt_step(ctx);
    }
}

static void ptrc_finalize_slip_tag(ptrc_crystal_ctx_t *ctx, size_t aad_len, size_t payload_len, uint8_t tag_out[SLIP_TAG_BYTES]) {
    uint8_t len_block[8] = {
        (uint8_t)(aad_len & 0xFF), (uint8_t)((aad_len >> 8) & 0xFF),
        (uint8_t)((aad_len >> 16) & 0xFF), (uint8_t)((aad_len >> 24) & 0xFF),
        (uint8_t)(payload_len & 0xFF), (uint8_t)((payload_len >> 8) & 0xFF),
        (uint8_t)((payload_len >> 16) & 0xFF), (uint8_t)((payload_len >> 24) & 0xFF)
    };

    for (size_t i = 0; i < 8; i++) {
        ctx->junctions[i] ^= len_block[i];
        ctx->outer_facets[(i * 15) % FREE_FACETS] += len_block[i];
    }
    for (size_t f = 0; f < (CONTROL_TAKT * CONTROL_TAKT); f++) {
        ptrc_lattice_takt_step(ctx);
    }
    for (size_t i = 0; i < SLIP_TAG_BYTES; i++) {
        uint8_t outer_fold = 0;
        for (size_t k = 0; k < 5; k++) {
            outer_fold ^= rotl8(ctx->outer_facets[i * 5 + k], (uint8_t)(k + 1));
        }
        tag_out[i] = (uint8_t)((ctx->junctions[i] + outer_fold) ^ INVARIANT_LIMIT);
    }
}

void ptrc_kdf_derive(
    const uint8_t *master_seed, size_t seed_len,
    const uint8_t *context_info, size_t info_len,
    uint8_t out_key[PTRC_KEY_BYTES], uint8_t out_nonce[PTRC_NONCE_BYTES]
) {
    uint8_t base_k[PTRC_KEY_BYTES];
    uint8_t base_n[PTRC_NONCE_BYTES];
    for (size_t i = 0; i < PTRC_KEY_BYTES; i++) {
        base_k[i] = (uint8_t)(((i + 1) * 19 + INVARIANT_LIMIT) ^ KEY_SHIFT);
    }
    for (size_t i = 0; i < PTRC_NONCE_BYTES; i++) {
        base_n[i] = (uint8_t)(((i + 1) * 23 + RENDER_TAKT_137) & 0xFF);
    }

    ptrc_crystal_ctx_t ctx;
    ptrc_crystal_init(&ctx, base_k, base_n);
    ptrc_absorb_aad(&ctx, master_seed, seed_len);
    ptrc_absorb_aad(&ctx, context_info, info_len);

    for (size_t w = 0; w < (CONTROL_TAKT * CONTROL_TAKT); w++) {
        ptrc_lattice_takt_step(&ctx);
    }
    for (size_t i = 0; i < PTRC_KEY_BYTES; i++) {
        ptrc_lattice_takt_step(&ctx);
        out_key[i] = (uint8_t)(ctx.junctions[i % CONTROL_TAKT] ^ ctx.outer_facets[(i * 7) % FREE_FACETS]);
    }
    for (size_t i = 0; i < PTRC_NONCE_BYTES; i++) {
        ptrc_lattice_takt_step(&ctx);
        out_nonce[i] = (uint8_t)(ctx.junctions[(i * 3) % CONTROL_TAKT] + ctx.outer_facets[(i * 11) % FREE_FACETS]);
    }
    ptrc_crystal_wipe(&ctx);
}

void ptrc_aead_encrypt(
    const uint8_t key[PTRC_KEY_BYTES], const uint8_t nonce[PTRC_NONCE_BYTES],
    const uint8_t *aad, size_t aad_len,
    const uint8_t *plaintext, uint8_t *ciphertext, size_t length,
    uint8_t tag_out[SLIP_TAG_BYTES]
) {
    ptrc_crystal_ctx_t ctx;
    ptrc_crystal_init(&ctx, key, nonce);
    ptrc_absorb_aad(&ctx, aad, aad_len);

    for (size_t i = 0; i < length; i++) {
        ptrc_lattice_takt_step(&ctx);
        uint8_t j_idx = (uint8_t)(ctx.takt_counter % CONTROL_TAKT);
        uint8_t f_idx = (uint8_t)((ctx.takt_counter * 11) % FREE_FACETS);
        uint8_t keystream = (uint8_t)(rotl8(ctx.junctions[j_idx], 2) ^ ctx.outer_facets[f_idx]);
        uint8_t q_phase = (uint8_t)(ctx.junctions[j_idx] ^ (uint8_t)ctx.crt_phase_1);

        uint8_t mirrored = plichta_crossed_mirror(plaintext[i], q_phase);
        uint8_t cipher_byte = (uint8_t)(mirrored + keystream);
        ciphertext[i] = cipher_byte;

        uint8_t fb_idx = (uint8_t)((j_idx * 5 + ctx.crt_phase_2) % FREE_FACETS);
        ctx.outer_facets[fb_idx] = (uint8_t)((ctx.outer_facets[fb_idx] + cipher_byte) ^ keystream);
    }

    ptrc_finalize_slip_tag(&ctx, aad_len, length, tag_out);
    ptrc_crystal_wipe(&ctx);
}

int ptrc_aead_decrypt(
    const uint8_t key[PTRC_KEY_BYTES], const uint8_t nonce[PTRC_NONCE_BYTES],
    const uint8_t *aad, size_t aad_len,
    const uint8_t *ciphertext, uint8_t *plaintext, size_t length,
    const uint8_t expected_tag[SLIP_TAG_BYTES]
) {
    ptrc_crystal_ctx_t ctx;
    uint8_t computed_tag[SLIP_TAG_BYTES];

    ptrc_crystal_init(&ctx, key, nonce);
    ptrc_absorb_aad(&ctx, aad, aad_len);

    for (size_t i = 0; i < length; i++) {
        ptrc_lattice_takt_step(&ctx);
        uint8_t j_idx = (uint8_t)(ctx.takt_counter % CONTROL_TAKT);
        uint8_t f_idx = (uint8_t)((ctx.takt_counter * 11) % FREE_FACETS);
        uint8_t keystream = (uint8_t)(rotl8(ctx.junctions[j_idx], 2) ^ ctx.outer_facets[f_idx]);
        uint8_t q_phase = (uint8_t)(ctx.junctions[j_idx] ^ (uint8_t)ctx.crt_phase_1);

        uint8_t cipher_byte = ciphertext[i];
        uint8_t mirrored = (uint8_t)(cipher_byte - keystream);
        plaintext[i] = plichta_crossed_unmirror(mirrored, q_phase);

        uint8_t fb_idx = (uint8_t)((j_idx * 5 + ctx.crt_phase_2) % FREE_FACETS);
        ctx.outer_facets[fb_idx] = (uint8_t)((ctx.outer_facets[fb_idx] + cipher_byte) ^ keystream);
    }

    ptrc_finalize_slip_tag(&ctx, aad_len, length, computed_tag);
    ptrc_crystal_wipe(&ctx);

    int authentic = ptrc_verify_tag_ct(computed_tag, expected_tag);
    if (!authentic) {
        memset(plaintext, 0, length);
    }
    return authentic;
}
