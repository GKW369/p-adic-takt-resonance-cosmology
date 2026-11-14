/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & AI Inference Engine
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

#ifndef PTRC_BITNET_ENGINE_H
#define PTRC_BITNET_ENGINE_H

#include <stddef.h>
#include <stdint.h>
#include <stdalign.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ==============================================================================
 * FUNDAMENTAL pTRC AI CONSTANTS (STRICTLY Z \ {0}, ZERO-FLOAT, ZERO-TRIG)
 * ============================================================================== */
#define PTRC_AI_FACETS          144U
#define PTRC_AI_JUNCTIONS       24U
#define PTRC_AI_MODULO_24       24U
#define PTRC_AI_PRIMORIAL_210   210
#define PTRC_AI_TAKT_137        137U
#define PTRC_AI_INVARIANT_156   156
#define PTRC_AI_MAX_DIM         144U
#define PTRC_AI_WORDS_PER_ROW   3U      /* 3 x 64-bit = 192 bits (>= 144 facets) */

/* ==============================================================================
 * BARE-METAL 1-BIT CRYSTALLINE LAYER & RESONANCE CONTEXT (ZERO MALLOC)
 * ============================================================================== */
typedef struct {
    alignas(16) uint64_t pos_mask[PTRC_AI_MAX_DIM][PTRC_AI_WORDS_PER_ROW];
    alignas(16) uint64_t neg_mask[PTRC_AI_MAX_DIM][PTRC_AI_WORDS_PER_ROW];
    int32_t  plasticity_acc[PTRC_AI_MAX_DIM][PTRC_AI_MAX_DIM];
    uint32_t in_dim;
    uint32_t out_dim;
    int32_t  takt_threshold;
} ptrc_bitnet_layer_t;

typedef struct {
    alignas(16) int32_t sponge[PTRC_AI_FACETS];
    uint64_t takt_counter;
    uint32_t clock_phase_24;
    int32_t  resonance_energy;
} ptrc_bitnet_ctx_t;

/* ==============================================================================
 * CORE Z \ {0} ARITHMETIC & BIT-INFERENCE API
 * ============================================================================== */

/* Maps any integer into Z \ {0} (0 resolves strictly to -1) */
static inline int32_t ptrc_z_no_zero(int32_t v) {
    return (v == 0) ? -1 : v;
}

/* Sign activation in Z \ {0}: >= 0 -> +1, < 0 -> -1 */
static inline int32_t ptrc_sign_z_no_zero(int32_t v) {
    return (v >= 0) ? 1 : -1;
}

/* Initializes the 144-facet crystalline resonance context in Z \ {0} */
void ptrc_bitnet_ctx_init(ptrc_bitnet_ctx_t *ctx, uint64_t seed);

/* Initializes a 1-bit {-1, +1} layer from deterministic integer weights */
int ptrc_bitnet_layer_init(
    ptrc_bitnet_layer_t *layer,
    uint32_t in_dim,
    uint32_t out_dim,
    const int8_t *weights_z_no_zero,
    int32_t takt_threshold
);

/* Packs a Z \ {0} bipolar vector ({-1, +1}) into 64-bit bitplanes */
void ptrc_bitnet_pack_bipolar(
    const int8_t *vec_z_no_zero,
    uint32_t len,
    uint64_t out_pos[PTRC_AI_WORDS_PER_ROW],
    uint64_t out_neg[PTRC_AI_WORDS_PER_ROW]
);

/* Pure XNOR + POPCOUNT 1-Bit Matrix-Vector Inference with 24-Clock & 137-Takt Modulation */
int ptrc_bitnet_forward(
    ptrc_bitnet_ctx_t *ctx,
    const ptrc_bitnet_layer_t *layer,
    const int8_t *input_z_no_zero,
    int8_t *output_z_no_zero,
    int32_t *raw_scores_out
);

/* Discrete Integer Hebbian Plasticity Update in Z \ {0} (Zero Floating-Point Backprop) */
int ptrc_bitnet_hebbian_step(
    ptrc_bitnet_ctx_t *ctx,
    ptrc_bitnet_layer_t *layer,
    const int8_t *input_z_no_zero,
    const int8_t *target_z_no_zero,
    int32_t plasticity_gain
);

/* Volatile SRAM scrubbing for bare-metal targets */
void ptrc_bitnet_wipe(ptrc_bitnet_ctx_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* PTRC_BITNET_ENGINE_H */
