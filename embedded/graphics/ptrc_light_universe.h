/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Observer Windtunnel v4.6.0
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
#define PTRC_GFX_SHELL_12           12U
#define PTRC_GFX_CLUSTER_13         13U
#define PTRC_GFX_STABLE_ELEMENTS    81U
#define PTRC_GFX_PRIME_RINGS        16U
#define PTRC_GFX_PRIMORIAL_210      210U
#define PTRC_GFX_TAKT_137           137U
#define PTRC_GFX_INVARIANT_156      156
#define PTRC_GFX_DEPTH_1414         1414

#define PTRC_MIN_ENGINES            1U
#define PTRC_DEFAULT_ENGINES        4U
#define PTRC_MAX_ENGINES            8U

#define PTRC_TUNNEL_HALF_X          960
#define PTRC_TUNNEL_HALF_Y          540
#define PTRC_TUNNEL_HALF_Z          240

#define PTRC_PYRAMID_CENTER_X       (-320)
#define PTRC_PYRAMID_CENTER_Z       55
#define PTRC_PYRAMID_HALF_BASE      192
#define PTRC_PYRAMID_HEIGHT         540
#define PTRC_PYRAMID_ROT_CYCLE      3288U

#define PTRC_SPHERE_CENTER_X        320
#define PTRC_SPHERE_CENTER_Y        (-140)
#define PTRC_SPHERE_CENTER_Z        75
#define PTRC_SPHERE_RADIUS          175

#define PTRC_WIND_AGENTS            60000U
#define PTRC_OCCUPANCY_SLOTS        65536U

#define PTRC_GFX_OK                 1
#define PTRC_GFX_ERR                (-1)
#define PTRC_RENDER_READY           1
#define PTRC_RENDER_WAIT            2
#define PTRC_RENDER_STALL           (-2)

#define PTRC_OPTICS_OPAQUE          0U
#define PTRC_OPTICS_TRANSLUCENT     1U
#define PTRC_OPTICS_CRYSTALLINE     2U
#define PTRC_OPTICS_FIELD_COUPLED   3U

#define PTRC_BACKEND_CPU_INT        1U
#define PTRC_BACKEND_GPU_INT32      2U

typedef struct {
    int16_t  x, y, z;
    int16_t  vx, vy, vz;
    uint8_t  state_byte;
    uint8_t  impulse;
} ptrc_wind_agent_t;

typedef struct {
    ptrc_wind_agent_t agents[PTRC_WIND_AGENTS];
    uint8_t           cell_impulse[PTRC_OCCUPANCY_SLOTS];
    uint8_t           cell_density[PTRC_OCCUPANCY_SLOTS];
    uint8_t           cell_cohesion[PTRC_OCCUPANCY_SLOTS];
    int32_t           sponge[PTRC_GFX_FACETS];
    uint32_t          prime_rings[PTRC_GFX_PRIME_RINGS];
    uint64_t          takt_counter;
    uint32_t          clock_phase_24;
    uint32_t          observer_sub_takt;
    uint32_t          pyramid_angle_idx;
    uint32_t          active_load;
    uint32_t          assigned_engines;
    uint32_t          bound_clusters;
    uint32_t          gpu_int32_active;
    uint32_t          render_interval_takts;
    uint32_t          last_render_takt;
    uint32_t          deflection_count;
    uint32_t          mirror_pulses;
    int32_t           render_status;
} ptrc_gfx_ctx_t;

int  ptrc_gfx_init(ptrc_gfx_ctx_t *ctx, uint64_t seed);
int  ptrc_gfx_step_takt(ptrc_gfx_ctx_t *ctx);
int  ptrc_gfx_step_takt_adaptive(ptrc_gfx_ctx_t *ctx);
int  ptrc_gfx_evaluate_observer_sync(ptrc_gfx_ctx_t *ctx);
int  ptrc_gfx_render_observer_rgb24(ptrc_gfx_ctx_t *ctx, uint32_t width, uint32_t height, uint8_t *rgb_out);
void ptrc_gfx_wipe(ptrc_gfx_ctx_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* PTRC_LIGHT_UNIVERSE_H */
