/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics Engine
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 * Licensed under the GNU Affero General Public License v3 (AGPLv3).
 * ============================================================================== */

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
