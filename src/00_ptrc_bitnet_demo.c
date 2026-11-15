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

/* File: src/00_ptrc_bitnet_demo.c */

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "ptrc_bitnet_engine.h"

#define DEMO_SAMPLES    4U
#define DEMO_IN_DIM     5U
#define DEMO_HIDDEN_DIM 4U
#define DEMO_OUT_DIM    2U

int main(void) {
    ptrc_bitnet_ctx_t ctx;
    ptrc_bitnet_ctx_init(&ctx, 137210144ULL);

    /* 4 pattern bits + 1 Z \ {0} phase anchor (+1) */
    const int8_t patterns[DEMO_SAMPLES * DEMO_IN_DIM] = {
        -1, -1, -1, -1,  1,
        -1,  1, -1,  1,  1,
         1, -1,  1, -1,  1,
         1,  1,  1,  1,  1
    };
    const int8_t targets[DEMO_SAMPLES * DEMO_OUT_DIM] = {
        -1,  1,
         1, -1,
         1, -1,
        -1,  1
    };

    /* 4 resonant crystal detectors coupled to coprime non-Mersenne prime rings */
    int8_t hidden_weights[DEMO_HIDDEN_DIM * DEMO_IN_DIM];
    for (uint32_t i = 0U; i < DEMO_HIDDEN_DIM * DEMO_IN_DIM; i++) {
        *(hidden_weights + i) = *(patterns + i);
    }

    int8_t out_weights[DEMO_OUT_DIM * DEMO_HIDDEN_DIM] = {
         1, -1,  1, -1,
        -1,  1, -1,  1
    };

    ptrc_bitnet_layer_t hidden_layer;
    ptrc_bitnet_layer_t out_layer;

    /* Thresholds strictly in Z \ {0}: +3 for crystal detector layer, -1 for output layer */
    if (ptrc_bitnet_layer_init(&hidden_layer, DEMO_IN_DIM, DEMO_HIDDEN_DIM, hidden_weights, 3) != PTRC_AI_OK ||
        ptrc_bitnet_layer_init(&out_layer, DEMO_HIDDEN_DIM, DEMO_OUT_DIM, out_weights, PTRC_AI_DEFAULT_THRESH) != PTRC_AI_OK) {
        printf("ERROR: Layer initialization failed.\n");
        return 1;
    }

    printf("===============================================================================\n");
    printf("  pTRC BITNET AI ENGINE v2.0 — BARE-METAL C11 1-BIT CRYSTALLINE INFERENCE\n");
    printf("  Topology     : (4+1) -> 4 -> 2 (Prime-Ring Resonance | Pure Integer Z \\ {0})\n");
    printf("  Context RAM  : %zu bytes static stack | 144 Facets | 137-Takt Sync\n", sizeof(ctx));
    printf("===============================================================================\n");

    for (uint32_t epoch = 1U; epoch <= 16U; epoch++) {
        int32_t locked_count = 0;
        for (uint32_t p = 0U; p < DEMO_SAMPLES; p++) {
            int8_t hidden_act[DEMO_HIDDEN_DIM];
            const int8_t *pat_ptr = patterns + (p * DEMO_IN_DIM);
            const int8_t *tgt_ptr = targets + (p * DEMO_OUT_DIM);

            ptrc_bitnet_forward(&ctx, &hidden_layer, pat_ptr, hidden_act, NULL);
            if (ptrc_bitnet_hebbian_step(&ctx, &out_layer, hidden_act, tgt_ptr, 16) == PTRC_AI_OK) {
                locked_count++;
            }
        }
        if (locked_count == (int32_t)DEMO_SAMPLES) {
            printf(" + Prime-Ring Phase-Lock achieved at Epoch %u (4/4 locked across 144 facets)\n", epoch);
            break;
        }
    }

    int32_t passed = 0;
    for (uint32_t p = 0U; p < DEMO_SAMPLES; p++) {
        int8_t  hidden_act[DEMO_HIDDEN_DIM];
        int8_t  out[DEMO_OUT_DIM]    = { -1, -1 };
        int32_t scores[DEMO_OUT_DIM] = { -1, -1 };

        const int8_t *pat_ptr = patterns + (p * DEMO_IN_DIM);
        const int8_t *tgt_ptr = targets + (p * DEMO_OUT_DIM);

        ptrc_bitnet_forward(&ctx, &hidden_layer, pat_ptr, hidden_act, NULL);
        ptrc_bitnet_forward(&ctx, &out_layer, hidden_act, out, scores);

        int ok = (*(out + 0) == *(tgt_ptr + 0) && *(out + 1) == *(tgt_ptr + 1)) ? PTRC_AI_OK : PTRC_AI_ERR;
        if (ok == PTRC_AI_OK) {
            passed++;
        }
        printf(" + Pattern (%+d,%+d,%+d,%+d) -> Out (%+d,%+d) | Expected (%+d,%+d) | %s\n",
               *(pat_ptr + 0), *(pat_ptr + 1), *(pat_ptr + 2), *(pat_ptr + 3),
               *(out + 0), *(out + 1),
               *(tgt_ptr + 0), *(tgt_ptr + 1),
               (ok == PTRC_AI_OK) ? "PASS" : "FAIL");
    }

    ptrc_bitnet_wipe(&ctx);
    printf("-------------------------------------------------------------------------------\n");
    printf("  VERIFICATION RESULT: %d / 4 Patterns Verified | SRAM Restored to -1\n", passed);
    printf("===============================================================================\n");
    return (passed == 4) ? 0 : 1;
}
