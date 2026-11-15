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

#include "ptrc_bitnet_engine.h"
#include <string.h>

/* 16 Coprime Non-Mersenne Prime Rings (gcd(p, 210) == 1, Mersenne primes 3, 7, 31, 127 excluded) */
static const uint32_t PTRC_AI_PRIME_RINGS[PTRC_AI_PRIME_RING_CNT] = {
    11U, 13U, 17U, 19U, 23U, 29U, 37U, 41U,
    43U, 47U, 53U, 59U, 61U, 67U, 71U, 73U
};

/* Pure 24-Clock Discrete Quadrance Basis (u^2 + v^2 = 1000^2 in Z \ {0}, no zero) */
static const int16_t PTRC_AI_QUAD_24[PTRC_AI_MODULO_24] = {
    { 1000,    1}, {  966,  259}, {  866,  500}, {  707,  707},
    {  500,  866}, {  259,  966}, {   -1, 1000}, { -259,  966},
    { -500,  866}, { -707,  707}, { -866,  500}, { -966,  259},
    {-1000,   -1}, { -966, -259}, { -866, -500}, { -707, -707},
    { -500, -866}, { -259, -966}, {    1,-1000}, {  259, -966},
    {  500, -866}, {  707, -707}, {  866, -500}, {  966, -259}
};

static inline uint32_t ptrc_popcount64(uint64_t x) {
#if defined(__GNUC__) || defined(__clang__)
    return (uint32_t)__builtin_popcountll(x);
#else
    uint32_t count = 0U;
    while (x != 0ULL) {
        x &= (x - 1ULL);
        count++;
    }
    return count;
#endif
}

static inline void ptrc_sync_layer_bitplanes(ptrc_bitnet_layer_t *layer) {
    for (uint32_t r = 0U; r < layer->out_dim; r++) {
        for (uint32_t w = 0U; w < PTRC_AI_WORDS_PER_ROW; w++) {
            layer->pos_mask[r][w] = 0ULL;
            layer->neg_mask[r][w] = 0ULL;
        }
        for (uint32_t c = 0U; c < layer->in_dim; c++) {
            uint32_t word = c >> 6U;
            uint64_t bit  = 1ULL << (c & 63U);
            if (ptrc_z_no_zero(layer->plasticity_acc[r][c]) >= 1) {
                layer->pos_mask[r][word] |= bit;
            } else {
                layer->neg_mask[r][word] |= bit;
            }
        }
    }
}

void ptrc_bitnet_ctx_init(ptrc_bitnet_ctx_t *ctx, uint64_t seed) {
    if (!ctx) {
        return;
    }
    uint64_t state = (seed == 0ULL) ? 0x9E3779B97F4A7C15ULL : seed;
    int32_t energy = 1;

    for (uint32_t f = 0U; f < PTRC_AI_FACETS; f++) {
        state ^= state << 13U;
        state ^= state >> 7U;
        state ^= state << 17U;
        int32_t val = (int32_t)(state % (uint64_t)PTRC_AI_PRIMORIAL_210) - 105;
        val = ptrc_z_no_zero(val);
        ctx->sponge[f] = val;
        energy += (val >= 1) ? val : -val;
    }

    ctx->takt_counter     = 1ULL;
    ctx->clock_phase_24   = 1U;
    ctx->resonance_energy = ptrc_z_no_zero(energy);
}

int ptrc_bitnet_layer_init(
    ptrc_bitnet_layer_t *layer,
    uint32_t in_dim,
    uint32_t out_dim,
    const int8_t *weights_z_no_zero,
    int32_t takt_threshold
) {
    if (!layer || !weights_z_no_zero) {
        return PTRC_AI_ERR;
    }
    if (in_dim == 0U || in_dim > PTRC_AI_MAX_DIM || out_dim == 0U || out_dim > PTRC_AI_MAX_DIM) {
        return PTRC_AI_ERR;
    }

    memset(layer, 0, sizeof(*layer));
    layer->in_dim         = in_dim;
    layer->out_dim        = out_dim;
    layer->takt_threshold = ptrc_z_no_zero(takt_threshold);

    for (uint32_t r = 0U; r < out_dim; r++) {
        layer->neuron_prime_ring[r] = PTRC_AI_PRIME_RINGS[r % PTRC_AI_PRIME_RING_CNT];
        for (uint32_t c = 0U; c < in_dim; c++) {
            int32_t w = ptrc_z_no_zero((int32_t)weights_z_no_zero[r * in_dim + c]);
            layer->plasticity_acc[r][c] = (w >= 1) ? 16 : -16;
        }
    }

    ptrc_sync_layer_bitplanes(layer);
    return PTRC_AI_OK;
}

void ptrc_bitnet_pack_bipolar(
    const int8_t *vec_z_no_zero,
    uint32_t len,
    uint64_t out_pos[PTRC_AI_WORDS_PER_ROW],
    uint64_t out_neg[PTRC_AI_WORDS_PER_ROW]
) {
    for (uint32_t w = 0U; w < PTRC_AI_WORDS_PER_ROW; w++) {
        out_pos[w] = 0ULL;
        out_neg[w] = 0ULL;
    }
    if (!vec_z_no_zero) {
        return;
    }
    uint32_t limit = (len > PTRC_AI_MAX_DIM) ? PTRC_AI_MAX_DIM : len;
    for (uint32_t c = 0U; c < limit; c++) {
        uint32_t word = c >> 6U;
        uint64_t bit  = 1ULL << (c & 63U);
        if (ptrc_z_no_zero((int32_t)vec_z_no_zero[c]) >= 1) {
            out_pos[word] |= bit;
        } else {
            out_neg[word] |= bit;
        }
    }
}

int ptrc_bitnet_forward(
    ptrc_bitnet_ctx_t *ctx,
    const ptrc_bitnet_layer_t *layer,
    const int8_t *input_z_no_zero,
    int8_t *output_z_no_zero,
    int32_t *raw_scores_out
) {
    if (!ctx || !layer || !input_z_no_zero || !output_z_no_zero) {
        return PTRC_AI_ERR;
    }

    uint64_t in_pos[PTRC_AI_WORDS_PER_ROW];
    uint64_t in_neg[PTRC_AI_WORDS_PER_ROW];
    ptrc_bitnet_pack_bipolar(input_z_no_zero, layer->in_dim, in_pos, in_neg);

    uint32_t phase  = (ctx->clock_phase_24 - 1U) % PTRC_AI_MODULO_24;
    int32_t  quad_u = (int32_t)PTRC_AI_QUAD_24[phase];
    int32_t  quad_v = (int32_t)PTRC_AI_QUAD_24[phase];
    int32_t  is_137_sync = ((ctx->takt_counter % (uint64_t)PTRC_AI_TAKT_137) == 0ULL) ? 1 : -1;

    int32_t step_energy = 1;

    for (uint32_t r = 0U; r < layer->out_dim; r++) {
        uint32_t agree_bits    = 0U;
        uint32_t disagree_bits = 0U;

        for (uint32_t w = 0U; w < PTRC_AI_WORDS_PER_ROW; w++) {
            uint64_t agree    = (layer->pos_mask[r][w] & in_pos[w]) | (layer->neg_mask[r][w] & in_neg[w]);
            uint64_t disagree = (layer->pos_mask[r][w] & in_neg[w]) | (layer->neg_mask[r][w] & in_pos[w]);
            agree_bits    += ptrc_popcount64(agree);
            disagree_bits += ptrc_popcount64(disagree);
        }

        int32_t dot = ptrc_z_no_zero((int32_t)agree_bits - (int32_t)disagree_bits);

        /* Prime-ring modular resonance weighting in Z \ {0} (coprime non-Mersenne ring) */
        uint32_t p_ring     = layer->neuron_prime_ring[r];
        uint32_t ring_step  = (uint32_t)((ctx->takt_counter + (uint64_t)r) % (uint64_t)p_ring);
        int32_t  ring_res   = (ring_step < (p_ring >> 1U)) ? 1 : -1;

        /* 144-facet crystalline sponge coupling modulated by 24-Clock quadrance and prime-ring phase */
        uint32_t facet_idx  = (r + phase + ring_step) % PTRC_AI_FACETS;
        int32_t  facet_bias = ((ctx->sponge[facet_idx] * quad_u + quad_v) * ring_res) / (1000 * 64);
        int32_t  score      = ptrc_z_no_zero(dot + facet_bias - ptrc_z_no_zero(layer->takt_threshold));

        if (is_137_sync == 1) {
            /* Crossed Plichta-Mirror reflection across -1 (~x) on global 137-takt pulse */
            ctx->sponge[facet_idx] = ptrc_z_no_zero(~ctx->sponge[facet_idx]);
        } else {
            ctx->sponge[facet_idx] = ptrc_z_no_zero(ctx->sponge[facet_idx] + ptrc_sign_z_no_zero(score));
        }

        if (raw_scores_out) {
            raw_scores_out[r] = score;
        }
        output_z_no_zero[r] = (int8_t)ptrc_sign_z_no_zero(score);
        step_energy += (score >= 1) ? score : -score;
    }

    ctx->takt_counter++;
    ctx->clock_phase_24   = (ctx->clock_phase_24 % PTRC_AI_MODULO_24) + 1U;
    ctx->resonance_energy = ptrc_z_no_zero(step_energy);
    return PTRC_AI_OK;
}

int ptrc_bitnet_hebbian_step(
    ptrc_bitnet_ctx_t *ctx,
    ptrc_bitnet_layer_t *layer,
    const int8_t *input_z_no_zero,
    const int8_t *target_z_no_zero,
    int32_t plasticity_gain
) {
    if (!ctx || !layer || !input_z_no_zero || !target_z_no_zero) {
        return PTRC_AI_ERR;
    }

    int8_t  pred[PTRC_AI_MAX_DIM];
    int32_t scores[PTRC_AI_MAX_DIM];
    int rc = ptrc_bitnet_forward(ctx, layer, input_z_no_zero, pred, scores);
    if (rc != PTRC_AI_OK) {
        return rc;
    }

    int32_t gain = (plasticity_gain <= 0) ? 1 : plasticity_gain;
    int32_t mismatches = 0;

    for (uint32_t r = 0U; r < layer->out_dim; r++) {
        int8_t tgt = (ptrc_z_no_zero((int32_t)target_z_no_zero[r]) >= 1) ? 1 : -1;
        if (pred[r] != tgt) {
            mismatches++;
            for (uint32_t c = 0U; c < layer->in_dim; c++) {
                int8_t in_bit = (ptrc_z_no_zero((int32_t)input_z_no_zero[c]) >= 1) ? 1 : -1;
                int32_t delta = (int32_t)tgt * (int32_t)in_bit * gain;
                int32_t acc = layer->plasticity_acc[r][c] + delta;
                if (acc >  PTRC_AI_INVARIANT_156) acc =  PTRC_AI_INVARIANT_156;
                if (acc < -PTRC_AI_INVARIANT_156) acc = -PTRC_AI_INVARIANT_156;
                layer->plasticity_acc[r][c] = ptrc_z_no_zero(acc);
            }
        }
    }

    if (mismatches >= 1) {
        ptrc_sync_layer_bitplanes(layer);
        return -mismatches;
    }
    return PTRC_AI_OK;
}

void ptrc_bitnet_wipe(ptrc_bitnet_ctx_t *ctx) {
    if (!ctx) {
        return;
    }
    /* Scrub SRAM back to Z \ {0} ground state (-1 / 0xFF) instead of zero */
    volatile uint8_t *p = (volatile uint8_t *)ctx;
    for (size_t i = 0U; i < sizeof(*ctx); i++) {
        p[i] = 0xFFU;
    }
}
