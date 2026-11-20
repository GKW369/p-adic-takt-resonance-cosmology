/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Observer Windtunnel v4.5.0
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


#ifndef PTRC_LIGHT_UNIVERSE_H
#define PTRC_LIGHT_UNIVERSE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PTRC_GFX_FACETS             144U
#define PTRC_GFX_JUNCTIONS          24U
#define PTRC_GFX_MEM_FACETS         120U
#define PTRC_GFX_STABLE_ELEMENTS    81U
#define PTRC_GFX_PRIME_RINGS        16U
#define PTRC_GFX_PRIMORIAL_210      210U
#define PTRC_GFX_TAKT_137           137U
#define PTRC_GFX_INVARIANT_156      156
#define PTRC_GFX_DEPTH_1414         1414

#define PTRC_LATTICE_DIM            16U
#define PTRC_LATTICE_CELLS          (PTRC_LATTICE_DIM * PTRC_LATTICE_DIM * PTRC_LATTICE_DIM)
#define PTRC_MAX_IMPULSE_PACKETS    1024U

#define PTRC_GFX_OK                 1
#define PTRC_GFX_ERR                (-1)
#define PTRC_RENDER_READY           1
#define PTRC_RENDER_WAIT            2
#define PTRC_RENDER_STALL           (-2)

typedef struct {
    int8_t   cx, cy, cz;
    uint8_t  state_byte;
    uint8_t  impulse;
    uint8_t  observer_cluster;
    uint8_t  facet_mem[PTRC_GFX_MEM_FACETS];
} ptrc_crystal_cell_t;

typedef struct {
    int32_t  x, y, z;
    uint8_t  dir_idx;
    uint8_t  impulse;
    uint8_t  wavelength_id;
    uint8_t  element_id;
} ptrc_impulse_packet_t;

typedef struct {
    ptrc_crystal_cell_t   cells[PTRC_LATTICE_CELLS];
    ptrc_impulse_packet_t packets[PTRC_MAX_IMPULSE_PACKETS];
    int32_t               sponge[PTRC_GFX_FACETS];
    uint32_t              prime_rings[PTRC_GFX_PRIME_RINGS];
    uint64_t              takt_counter;
    uint32_t              clock_phase_24;
    uint32_t              active_load;
    uint32_t              render_interval_takts;
    uint32_t              last_render_takt;
    uint32_t              deflection_count;
    uint32_t              mirror_pulses;
    int32_t               render_status;
} ptrc_gfx_ctx_t;

int  ptrc_gfx_init(ptrc_gfx_ctx_t *ctx, uint64_t seed);
int  ptrc_gfx_step_takt(ptrc_gfx_ctx_t *ctx);
int  ptrc_gfx_evaluate_observer_sync(ptrc_gfx_ctx_t *ctx);
int  ptrc_gfx_render_observer_rgb24(ptrc_gfx_ctx_t *ctx, uint32_t width, uint32_t height, uint8_t *rgb_out);
void ptrc_gfx_wipe(ptrc_gfx_ctx_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* PTRC_LIGHT_UNIVERSE_H */
