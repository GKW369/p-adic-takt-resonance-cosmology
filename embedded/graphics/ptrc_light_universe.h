/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Observer Windtunnel v4.1
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
#define PTRC_GFX_FREE_FACETS    120U
#define PTRC_GFX_JUNCTIONS      24U
#define PTRC_GFX_CRYSTAL_RAD    9
#define PTRC_GFX_PRIME_RINGS    16U
#define PTRC_GFX_PRIMORIAL_210  210U
#define PTRC_GFX_TAKT_137       137U
#define PTRC_GFX_AGENT_COUNT    60000U

#define PTRC_GFX_OK             1
#define PTRC_GFX_ERR            (-1)

/* Static stack context for Z \ {0} Observer Universe & 60,000-Agent Windtunnel */
typedef struct {
    int32_t  sponge[PTRC_GFX_FACETS];
    uint8_t  crystal_state[PTRC_GFX_FACETS];
    uint32_t prime_rings[PTRC_GFX_PRIME_RINGS];
    int32_t  agent_x[PTRC_GFX_AGENT_COUNT];
    int32_t  agent_y[PTRC_GFX_AGENT_COUNT];
    int32_t  agent_vx[PTRC_GFX_AGENT_COUNT];
    int32_t  agent_vy[PTRC_GFX_AGENT_COUNT];
    uint8_t  agent_state[PTRC_GFX_AGENT_COUNT];
    uint64_t takt_counter;
    uint32_t clock_phase_24;
    int32_t  pyramid_cx;
    int32_t  pyramid_cy;
    uint32_t active_hits;
    uint32_t mirror_pulses;
} ptrc_gfx_ctx_t;

/* Initialize 1+12 crystal lattice and 60,000 agents strictly inside Z \ {0} */
int ptrc_gfx_init(ptrc_gfx_ctx_t *ctx, uint64_t seed);

/* Advance one discrete light-speed takt (lattice interaction + agent flow) */
int ptrc_gfx_step_takt(ptrc_gfx_ctx_t *ctx);

/* Advance 137 light-speed takts up to the Observer Render Pulse */
int ptrc_gfx_advance_observer_epoch(ptrc_gfx_ctx_t *ctx);

/* Render Full-HD / arbitrary RGB24 Observer View without float or zero point */
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
