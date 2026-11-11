/# ==============================================================================
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

# -*- coding: utf-8 -*-/

#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* --- pTRC CRYSTALLINE HARDWARE MATRIX ARCHITECTURE (144-FACET EQUILIBRIUM) --- */
#define MOD_BASE        210     /* P4 Primorial Ring (2 * 3 * 5 * 7) */
#define CONTROL_TAKT    24      /* 24 Physical Contact Junctions (1+12 Ur-Cells) */
#define FREE_FACETS     120     /* 120 Free Outer Facets (Active Feedback Sponge) */
#define KEY_SHIFT       48      /* Euler-Phi Constant: phi(210) = 48 */
#define INVARIANT_LIMIT 156     /* Wirminghaus Invariant Limit: 3 * 48 + 12 */

/* --- MULTI-RING P-ADIC CRT EXTENSION RINGS --- */
#define CRT_RING_1      11
#define CRT_RING_2      13
#define CRT_RING_3      17

typedef struct {
    uint8_t junctions[CONTROL_TAKT];    /* 24 Contact Junction Registers */
    uint8_t outer_facets[FREE_FACETS];  /* 120 Outer Facet Feedback Registers */
    uint32_t takt_counter;              /* Monotonic Takt Counter */
    uint8_t crt_phase_1;                /* Ring Z/11Z State */
    uint8_t crt_phase_2;                /* Ring Z/13Z State */
    uint8_t crt_phase_3;                /* Ring Z/17Z State */
} ptrc_crystal_ctx_t;

/* Branchless 8-bit Left Rotation (Constant-Time on ARM Cortex-M & x86) */
static inline uint8_t rotl8(uint8_t value, uint8_t shift) {
    shift &= 7;
    return (uint8_t)((value << shift) | (value >> ((8 - shift) & 7)));
}

/* Single Crystalline Lattice Diffusion Takt (Mixes 24 Junctions & 120 Facets) */
static void ptrc_lattice_takt_step(ptrc_crystal_ctx_t *ctx) {
    uint32_t t = ctx->takt_counter;
    uint8_t j_idx = (uint8_t)(t % CONTROL_TAKT);
    uint8_t f_idx_a = (uint8_t)((t * 7) % FREE_FACETS);
    uint8_t f_idx_b = (uint8_t)((t * 13 + 5) % FREE_FACETS);

    /* Advance coprime CRT rings in parallel */
    ctx->crt_phase_1 = (uint8_t)((ctx->crt_phase_1 + 5) % CRT_RING_1);
    ctx->crt_phase_2 = (uint8_t)((ctx->crt_phase_2 + 7) % CRT_RING_2);
    ctx->crt_phase_3 = (uint8_t)((ctx->crt_phase_3 + 11) % CRT_RING_3);

    uint8_t crt_mix = (uint8_t)((ctx->crt_phase_1 * 19) + (ctx->crt_phase_2 * 17) + (ctx->crt_phase_3 * 13));
    uint8_t base_takt = (uint8_t)(((t * CONTROL_TAKT) + KEY_SHIFT) % MOD_BASE);

    /* Non-linear odd-prime mixing inside Z/256Z (100% bijective & branchless) */
    uint8_t j_val = ctx->junctions[j_idx];
    uint8_t f_a = ctx->outer_facets[f_idx_a];
    uint8_t f_b = ctx->outer_facets[f_idx_b];

    uint8_t mixed = (uint8_t)((j_val ^ base_takt) * 11 + f_a + crt_mix);
    mixed = rotl8(mixed, 3) ^ f_b;

    /* Update both the 24 inner junctions and the 120 outer facets */
    ctx->junctions[j_idx] = (uint8_t)((j_val + mixed) * 7 + 1);
    ctx->outer_facets[f_idx_a] = (uint8_t)(f_a ^ rotl8(mixed, 5));
    ctx->outer_facets[f_idx_b] = (uint8_t)((f_b + ctx->junctions[j_idx]) ^ crt_mix);

    ctx->takt_counter++;
}

/**
 * @brief Initializes the 144-Facet Crystal with a 256-bit Key and 96-bit Nonce.
 * Executes 24 full warmup cycles (24 * 24 = 576 steps) to achieve full avalanche diffusion.
 */
void ptrc_crystal_init(ptrc_crystal_ctx_t *ctx, const uint8_t key[32], const uint8_t nonce[12]) {
    memset(ctx, 0, sizeof(ptrc_crystal_ctx_t));

    /* 1. Seed the 24 Junctions with Key + Wirminghaus Invariant */
    for (size_t i = 0; i < CONTROL_TAKT; i++) {
        ctx->junctions[i] = (uint8_t)(key[i] ^ key[(i + 8) & 31] ^ INVARIANT_LIMIT);
    }

    /* 2. Seed the 120 Outer Facets across coprime prime-ray strides */
    for (size_t i = 0; i < FREE_FACETS; i++) {
        uint8_t k_byte = key[(i * 7) & 31];
        uint8_t n_byte = nonce[(i * 5) % 12];
        ctx->outer_facets[i] = (uint8_t)((k_byte * 13 + n_byte * 17 + (uint8_t)i) ^ 0xFF);
    }

    /* 3. Seed CRT Rings from Nonce & Key */
    ctx->crt_phase_1 = (uint8_t)((key[0] ^ nonce[0]) % CRT_RING_1);
    ctx->crt_phase_2 = (uint8_t)((key[1] ^ nonce[1]) % CRT_RING_2);
    ctx->crt_phase_3 = (uint8_t)((key[2] ^ nonce[2]) % CRT_RING_3);

    /* 4. 24-Takt Crystalline Warmup Cascade (Full 144-Facet Diffusion) */
    for (size_t w = 0; w < (CONTROL_TAKT * CONTROL_TAKT); w++) {
        ptrc_lattice_takt_step(ctx);
    }
}

/**
 * @brief Processes data stream in Encrypt (mode = 0) or Decrypt (mode = 1).
 * Uses active feedback from the 120 outer facets into the keystream.
 */
void ptrc_crystalline_crypt_process(ptrc_crystal_ctx_t *ctx, const uint8_t *input, uint8_t *output, size_t length, int mode) {
    for (size_t i = 0; i < length; i++) {
        /* Advance lattice state and extract dynamic keystream byte from all 144 facets */
        ptrc_lattice_takt_step(ctx);

        uint8_t j_idx = (uint8_t)(ctx->takt_counter % CONTROL_TAKT);
        uint8_t f_idx = (uint8_t)((ctx->takt_counter * 11) % FREE_FACETS);
        uint8_t keystream = (uint8_t)(rotl8(ctx->junctions[j_idx], 2) ^ ctx->outer_facets[f_idx]);

        uint8_t cipher_byte;
        if (mode == 0) {
            /* ENCRYPT: Lossless Plichta-Mirror (^ 0xFF) + Keystream Shift */
            uint8_t mirrored = (uint8_t)(input[i] ^ 0xFF);
            cipher_byte = (uint8_t)(mirrored + keystream);
            output[i] = cipher_byte;
        } else {
            /* DECRYPT: Exact Time-Symmetric Inversion */
            cipher_byte = input[i];
            uint8_t mirrored = (uint8_t)(cipher_byte - keystream);
            output[i] = (uint8_t)(mirrored ^ 0xFF);
        }

        /* ACTIVE FEEDBACK: Ciphertext mutates the 120 outer facets for subsequent bytes */
        uint8_t fb_idx = (uint8_t)((j_idx * 5 + ctx->crt_phase_2) % FREE_FACETS);
        ctx->outer_facets[fb_idx] = (uint8_t)((ctx->outer_facets[fb_idx] + cipher_byte) ^ keystream);
    }
}

/* --- TECHNICAL TELEMETRY & VERIFICATION OUTPUT --- */
int main(void) {
    const char *plaintext = "MINT-Matrix-Core-Initialized: True. 144-Facet Active Feedback Locked.";
    size_t len = strlen(plaintext);

    /* Example 256-bit Secret Key & 96-bit Nonce */
    const uint8_t secret_key[32] = {
        0x18, 0x36, 0x21, 0x00, 0x15, 0x60, 0x24, 0x48,
        0x01, 0x05, 0x07, 0x11, 0x13, 0x17, 0x19, 0x23,
        0x99, 0x88, 0x77, 0x66, 0x55, 0x44, 0x33, 0x22,
        0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x12, 0x34
    };
    const uint8_t nonce[12] = {
        0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C
    };

    uint8_t encrypted[256] = {0};
    uint8_t decrypted[256] = {0};
    ptrc_crystal_ctx_t ctx_enc, ctx_dec;

    printf("\n===========================================================================\n");
    printf("  pTRC FRAMEWORK // HARDENED 144-FACET CRYSTALLINE CRYPT ENGINE v3.0       \n");
    printf("  Active Sponge Feedback + CRT Multi-Ring Cascade (Z/210 x 11 x 13 x 17)   \n");
    printf("===========================================================================\n\n");

    /* Encrypt */
    ptrc_crystal_init(&ctx_enc, secret_key, nonce);
    ptrc_crystalline_crypt_process(&ctx_enc, (const uint8_t *)plaintext, encrypted, len, 0);

    printf("INPUT PLAINTEXT :\n  '%s'\n\n", plaintext);
    printf("ENCRYPTED STREAM (Hex):\n  ");
    for (size_t i = 0; i < len; i++) {
        printf("%02x", encrypted[i]);
    }
    printf("\n\n");

    /* Decrypt */
    ptrc_crystal_init(&ctx_dec, secret_key, nonce);
    ptrc_crystalline_crypt_process(&ctx_dec, encrypted, decrypted, len, 1);
    decrypted[len] = '\0';

    printf("RESTORED OUTPUT :\n  '%s'\n\n", (char *)decrypted);
    printf("VERIFICATION    : %s\n", (strcmp(plaintext, (char *)decrypted) == 0) ? "[ MATCH - 100% BIT-EXACT ]" : "[ MISMATCH ]");
    printf("===========================================================================\n\n");

    return 0;
}
