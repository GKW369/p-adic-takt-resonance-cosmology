/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Light Universe Engine v4.0
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

/* File: embedded/graphics/ptrc_light_universe.h */

#ifndef PTRC_LIGHT_UNIVERSE_H
#define PTRC_LIGHT_UNIVERSE_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PTRC_GFX_FACETS         144U
#define PTRC_GFX_JUNCTIONS      24U
#define PTRC_GFX_PRIME_RINGS    16U
#define PTRC_GFX_PRIMORIAL_210  210U
#define PTRC_GFX_TAKT_137       137U
#define PTRC_GFX_LIMIT_156      156
#define PTRC_GFX_VOXEL_SHIFT    16U
#define PTRC_GFX_VOXEL_STEP     65536
#define PTRC_GFX_MAX_STEPS      28U

#define PTRC_GFX_OK             1
#define PTRC_GFX_ERR            (-1)

/* Static stack context for Z \ {0} Light Universe rendering (zero malloc) */
typedef struct {
    int32_t  sponge[PTRC_GFX_FACETS];
    uint32_t prime_rings[PTRC_GFX_PRIME_RINGS];
    uint64_t takt_counter;
    uint32_t clock_phase_24;
    int32_t  cam_x;
    int32_t  cam_y;
    int32_t  cam_z;
    uint32_t active_hits;
    uint32_t mirror_pulses;
} ptrc_gfx_ctx_t;

/* Initialize universe state strictly inside Z \ {0} (no zero point) */
int ptrc_gfx_init(ptrc_gfx_ctx_t *ctx, uint64_t seed);

/* Advance one discrete universe takt (137-takt mirror pulse + 24-clock orbit) */
int ptrc_gfx_step_takt(ptrc_gfx_ctx_t *ctx);

/* Render one RGB24 frame (width * height * 3 bytes) without float or division */
int ptrc_gfx_render_frame_rgb24(
    ptrc_gfx_ctx_t *ctx,
    uint32_t width,
    uint32_t height,
    uint8_t *rgb_out
);

/* Scrub context memory back to Z \ {0} ground state (-1 / 0xFF) */
void ptrc_gfx_wipe(ptrc_gfx_ctx_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* PTRC_LIGHT_UNIVERSE_H */
