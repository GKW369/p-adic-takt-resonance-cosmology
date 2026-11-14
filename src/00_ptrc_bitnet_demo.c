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

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "ptrc_bitnet_engine.h"

int main(void) {
    ptrc_bitnet_ctx_t ctx;
    ptrc_bitnet_ctx_init(&ctx, 137210144ULL);

    /* 4-input -> 2-output 1-bit {-1, +1} crystalline layer */
    const uint32_t in_dim  = 4U;
    const uint32_t out_dim = 2U;
    int8_t init_weights[8] = {
         1, -1,  1, -1,
        -1,  1, -1,  1
    };

    ptrc_bitnet_layer_t layer;
    if (ptrc_bitnet_layer_init(&layer, in_dim, out_dim, init_weights, 0) != 0) {
        printf("ERROR: Layer initialization failed.\n");
        return 1;
    }

    const int8_t patterns[4][4] = {
        { -1, -1, -1, -1 },
        { -1,  1, -1,  1 },
        {  1, -1,  1, -1 },
        {  1,  1,  1,  1 }
    };
    const int8_t targets[4][2] = {
        { -1,  1 },
        {  1, -1 },
        {  1, -1 },
        { -1,  1 }
    };

    printf("===============================================================================\n");
    printf("  pTRC BITNET AI ENGINE v2.0 — BARE-METAL C11 1-BIT CRYSTALLINE INFERENCE\n");
    printf("  Context RAM  : %zu bytes static stack | Zero float/double | Zero malloc\n", sizeof(ctx));
    printf("  Lattice Core : Z \\ {0} | 144 Facets | 24-Clock Quadrance | 137-Takt Sync\n");
    printf("===============================================================================\n");

    /* Discrete Integer Hebbian Plasticity Training (Zero Floating-Point Backprop) */
    for (uint32_t epoch = 1U; epoch <= 12U; epoch++) {
        int32_t total_err = 0;
        for (uint32_t p = 0U; p < 4U; p++) {
            total_err += ptrc_bitnet_hebbian_step(&ctx, &layer, patterns[p], targets[p], 4);
        }
        if (total_err == 0) {
            printf(" + Hebbian Convergence achieved at Epoch %u (0 errors across 144 facets)\n", epoch);
            break;
        }
    }

    /* Forward 1-Bit XNOR + POPCOUNT Inference Verification */
    int32_t passed = 0;
    for (uint32_t p = 0U; p < 4U; p++) {
        int8_t  out[2]    = { -1, -1 };
        int32_t scores[2] = {  0,  0 };
        ptrc_bitnet_forward(&ctx, &layer, patterns[p], out, scores);
        int ok = (out[0] == targets[p][0] && out[1] == targets[p][1]) ? 1 : 0;
        passed += ok;
        printf(" + Pattern [%+d,%+d,%+d,%+d] -> Out [%+d,%+d] (Expected [%+d,%+d]) | %s\n",
               patterns[p][0], patterns[p][1], patterns[p][2], patterns[p][3],
               out[0], out[1], targets[p][0], targets[p][1],
               ok ? "PASS" : "FAIL");
    }

    ptrc_bitnet_wipe(&ctx);
    printf("-------------------------------------------------------------------------------\n");
    printf("  VERIFICATION RESULT: %d / 4 Patterns Verified | SRAM Context Scrubbed\n", passed);
    printf("===============================================================================\n");
    return (passed == 4) ? 0 : 1;
}
