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

#define _GNU_SOURCE
#include "ptrc_light_universe.h"
#include <dlfcn.h>
#include <pthread.h>
#include <stdlib.h>

typedef struct {
    int8_t dx;
    int8_t dy;
    int8_t dz;
} ptrc_dir3_t;

#define PTRC_MAX_ZBUF_PIXELS (3840U * 2160U)
static int16_t PTRC_STATIC_ZBUF[PTRC_MAX_ZBUF_PIXELS];

static const uint32_t PTRC_GFX_RINGS[PTRC_GFX_PRIME_RINGS] = {
    11U, 13U, 17U, 19U, 23U, 29U, 37U, 41U,
    43U, 47U, 53U, 59U, 61U, 67U, 71U, 73U
};

static const ptrc_dir3_t PTRC_SHELL_12_DIRS[PTRC_GFX_SHELL_12] = {
    { 1,  1, -1}, { 1, -1, -1}, {-1,  1, -1}, {-1, -1, -1},
    { 1,  1,  1}, { 1, -1,  1}, {-1,  1,  1}, {-1, -1,  1},
    { 2,  1, -1}, {-2, -1,  1}, {-1,  2,  1}, { 1, -2, -1}
};

static const ptrc_dir3_t PTRC_JUNCTION_DIRS_24[PTRC_GFX_JUNCTIONS] = {
    { 1,  1, -1}, { 1, -1, -1}, {-1,  1, -1}, {-1, -1, -1},
    { 1,  1,  1}, { 1, -1,  1}, {-1,  1,  1}, {-1, -1,  1},
    { 2,  1, -1}, { 2, -1, -1}, {-2,  1, -1}, {-2, -1, -1},
    {-1,  2,  1}, {-1,  2, -1}, {-1, -2,  1}, {-1, -2, -1},
    { 1, -1,  2}, {-1, -1,  2}, { 1, -1, -2}, {-1, -1, -2},
    { 2,  1,  1}, {-2, -1,  1}, { 1,  2,  1}, {-1, -2, -1}
};

static const int32_t PTRC_CLOCK24_U[PTRC_GFX_JUNCTIONS] = {
    1000,  966,  866,  707,  500,  259,
      -1, -259, -500, -707, -866, -966,
   -1000, -966, -866, -707, -500, -259,
       1,  259,  500,  707,  866,  966
};

static const int32_t PTRC_CLOCK24_V[PTRC_GFX_JUNCTIONS] = {
       1,  259,  500,  707,  866,  966,
    1000,  966,  866,  707,  500,  259,
      -1, -259, -500, -707, -866, -966,
   -1000, -966, -866, -707, -500, -259
};

static inline int32_t ptrc_z_no_zero(int32_t v) {
    return (v == 0) ? -1 : v;
}

static inline int32_t ptrc_z_sym_no_zero(int32_t v, uint32_t parity) {
    if (v != 0) return v;
    return ((parity & 1U) == 0U) ? 1 : -1;
}

static inline uint8_t ptrc_u8_no_zero(uint8_t v) {
    return (v == 0U) ? 0xFFU : v;
}

static inline uint64_t ptrc_u64_no_zero(uint64_t v) {
    return (v == 0ULL) ? 1ULL : v;
}

static inline int32_t ptrc_abs32(int32_t x) {
    return (x < 0) ? -x : x;
}

static inline int32_t ptrc_plichta_move(int32_t pos, int32_t delta) {
    int32_t nxt = pos + delta;
    if (nxt == 0) {
        nxt = (delta >= 0) ? 1 : -1;
    }
    return nxt;
}

/* Prueft zur Laufzeit, ob OpenCL int32-GPU-ALUs auf dem System vorhanden sind (0 Floats) */
static uint32_t ptrc_probe_integer_gpu_hardware(void) {
    void *ocl_handle = dlopen("libOpenCL.so.1", RTLD_LAZY | RTLD_LOCAL);
    if (!ocl_handle) {
        ocl_handle = dlopen("libOpenCL.so", RTLD_LAZY | RTLD_LOCAL);
    }
    if (!ocl_handle) {
        return 0U;
    }
    typedef int32_t (*clGetPlatformIDs_fn)(uint32_t, void **, uint32_t *);
    clGetPlatformIDs_fn get_platforms = NULL;
    *(void **)(&get_platforms) = dlsym(ocl_handle, "clGetPlatformIDs");
    uint32_t num_platforms = 0U;
    uint32_t found = 0U;
    if (get_platforms && get_platforms(0U, NULL, &num_platforms) == 0 && num_platforms > 0U) {
        found = 1U;
    }
    dlclose(ocl_handle);
    return found;
}

static inline void ptrc_get_smooth_rotation(uint32_t angle_step, int32_t *rot_u, int32_t *rot_v) {
    uint32_t step = angle_step % PTRC_PYRAMID_ROT_CYCLE;
    uint32_t phase = (step / PTRC_GFX_TAKT_137) % PTRC_GFX_JUNCTIONS;
    uint32_t next_phase = (phase + 1U) % PTRC_GFX_JUNCTIONS;
    int32_t sub = (int32_t)(step % PTRC_GFX_TAKT_137);
    int32_t inv_sub = (int32_t)PTRC_GFX_TAKT_137 - sub;

    *rot_u = (PTRC_CLOCK24_U[phase] * inv_sub + PTRC_CLOCK24_U[next_phase] * sub) / (int32_t)PTRC_GFX_TAKT_137;
    *rot_v = (PTRC_CLOCK24_V[phase] * inv_sub + PTRC_CLOCK24_V[next_phase] * sub) / (int32_t)PTRC_GFX_TAKT_137;
}

static inline uint32_t ptrc_fcc_slot_hash(int32_t x, int32_t y, int32_t z) {
    uint32_t qx = (uint32_t)((x + 1024) / 4);
    uint32_t qy = (uint32_t)((y + 1024) / 4);
    uint32_t qz = (uint32_t)((z + 1024) / 4);
    uint32_t h = (qx * 73856093U) ^ (qy * 19349663U) ^ (qz * 83492791U);
    return h & (PTRC_OCCUPANCY_SLOTS - 1U);
}

static inline uint8_t ptrc_encode_1byte_cascade(
    uint8_t cohesion_anchor,
    uint8_t optics_mode,
    uint8_t wavelength_id
) {
    uint8_t wl = (uint8_t)(((wavelength_id - 1U) & 30U) + 1U);
    uint8_t opt = (uint8_t)(optics_mode & 3U);
    uint8_t anc = (uint8_t)(cohesion_anchor & 1U);
    return ptrc_u8_no_zero((uint8_t)((anc << 7U) | (opt << 5U) | wl));
}

static void ptrc_get_pyramid_dual_axes(uint32_t angle_idx, int32_t *rot_u, int32_t *rot_v, int32_t *tilt_u, int32_t *tilt_v) {
    uint32_t norm_idx = angle_idx % PTRC_PYRAMID_ROT_CYCLE;
    uint32_t rev_idx = (PTRC_PYRAMID_ROT_CYCLE - norm_idx) % PTRC_PYRAMID_ROT_CYCLE;

    /* 1. Propeller-Hauptachse nahe der Waagerechten (volle 360-Grad-Rotor-Drehung) */
    ptrc_get_smooth_rotation(rev_idx, tilt_u, tilt_v);

    /* 2. Sanfter, formtreuer Anstellwinkel der Rotorachse (~18 Grad +/- 6 Grad, 0 Sprung) */
    uint32_t pitch_idx = (norm_idx + (PTRC_PYRAMID_ROT_CYCLE >> 2U)) % PTRC_PYRAMID_ROT_CYCLE;
    int32_t raw_pu = 1024, raw_pv = 0;
    ptrc_get_smooth_rotation(pitch_idx, &raw_pu, &raw_pv);
    int32_t mod_u = 1018 + ((raw_pu - 1024) >> 7);
    int32_t mod_v = raw_pv >> 3;
    *rot_u = (316 * mod_u - 974 * mod_v) >> 10;
    *rot_v = (316 * mod_v + 974 * mod_u) >> 10;
}

static int ptrc_point_in_square_pyramid(
    int32_t px,
    int32_t py,
    int32_t pz,
    int32_t rot_u,
    int32_t rot_v,
    int32_t tilt_u,
    int32_t tilt_v
) {
    int32_t dx = px - PTRC_PYRAMID_CENTER_X;
    int32_t dy = py;
    int32_t dz = pz - PTRC_PYRAMID_CENTER_Z;

    if (ptrc_abs32(dx) > 350 || ptrc_abs32(dy) > 350 || ptrc_abs32(dz) > 350) {
        return 0;
    }

    int32_t ty = (dy * tilt_u - dz * tilt_v) >> 10;
    int32_t tz = (dy * tilt_v + dz * tilt_u) >> 10;
    int32_t lx = (dx * rot_u - tz * rot_v) >> 10;
    int32_t lz = (dx * rot_v + tz * rot_u) >> 10;

    int32_t half_h = PTRC_PYRAMID_HEIGHT >> 1;
    if (ty < -half_h || ty > half_h) {
        return 0;
    }

    int32_t allowed_half_width = ((ty + half_h) * PTRC_PYRAMID_HALF_BASE) / PTRC_PYRAMID_HEIGHT;
    return (ptrc_abs32(lx) <= allowed_half_width && ptrc_abs32(lz) <= allowed_half_width) ? 1 : 0;
}

static inline int ptrc_point_in_crystal_sphere(int32_t px, int32_t py, int32_t pz) {
    int32_t dx = px - PTRC_SPHERE_CENTER_X;
    int32_t dy = py - PTRC_SPHERE_CENTER_Y;
    int32_t dz = pz - PTRC_SPHERE_CENTER_Z;
    if (ptrc_abs32(dx) > PTRC_SPHERE_RADIUS ||
        ptrc_abs32(dy) > PTRC_SPHERE_RADIUS ||
        ptrc_abs32(dz) > PTRC_SPHERE_RADIUS) {
        return 0;
    }
    int32_t q = dx * dx + dy * dy + dz * dz;
    return (q <= (PTRC_SPHERE_RADIUS * PTRC_SPHERE_RADIUS)) ? 1 : 0;
}

int ptrc_gfx_init(ptrc_gfx_ctx_t *ctx, uint64_t seed) {
    if (!ctx) return PTRC_GFX_ERR;

    uint64_t rng = ptrc_u64_no_zero(seed ^ 614889782588491410ULL);

    for (uint32_t r = 0U; r < PTRC_GFX_PRIME_RINGS; r++) {
        ctx->prime_rings[r] = PTRC_GFX_RINGS[r];
    }

    for (uint32_t f = 0U; f < PTRC_GFX_FACETS; f++) {
        rng = ptrc_u64_no_zero((rng * 137ULL + (uint64_t)(f + 1U) * 211ULL) ^ (rng >> 13U));
        int32_t raw = (int32_t)(rng % PTRC_GFX_PRIMORIAL_210) - 105;
        ctx->sponge[f] = ptrc_z_no_zero(raw);
    }

    for (uint32_t s = 0U; s < PTRC_OCCUPANCY_SLOTS; s++) {
        ctx->cell_impulse[s] = 1U;
        ctx->cell_density[s] = 1U;
        ctx->cell_cohesion[s] = 1U;
    }

    for (uint32_t a = 0U; a < PTRC_WIND_AGENTS; a++) {
        rng = ptrc_u64_no_zero(rng * 6364136223846793005ULL + 1442695040888963407ULL);
        int32_t rx = (int32_t)(rng % (uint64_t)(PTRC_TUNNEL_HALF_X * 2)) - PTRC_TUNNEL_HALF_X;
        int32_t ry = (int32_t)((rng >> 16U) % (uint64_t)(PTRC_TUNNEL_HALF_Y * 2)) - PTRC_TUNNEL_HALF_Y;
        int32_t rz = (int32_t)((rng >> 32U) % (uint64_t)(PTRC_TUNNEL_HALF_Z * 2)) - PTRC_TUNNEL_HALF_Z;

        int32_t x = ptrc_z_sym_no_zero(rx, a);
        int32_t y = ptrc_z_sym_no_zero(ry, a >> 1U);
        int32_t z = ptrc_z_sym_no_zero(rz, a >> 2U);
        if (((x + y + z) & 1) != 0) {
            x = ptrc_plichta_move(x, 1);
        }

        uint8_t wl = (uint8_t)((a % 16U) + 1U);
        uint8_t opt = PTRC_OPTICS_TRANSLUCENT; (void)opt;
        uint8_t coh = ((a % 5U) == 0U) ? 1U : 0U;

        ctx->agents[a].x = (int16_t)x;
        ctx->agents[a].y = (int16_t)y;
        ctx->agents[a].z = (int16_t)z;
        ctx->agents[a].vx = 1;
        ctx->agents[a].vy = (int16_t)(((a & 1U) == 0U) ? 1 : -1);
        ctx->agents[a].vz = (int16_t)((((a >> 1U) & 1U) == 0U) ? 1 : -1);
        ctx->agents[a].impulse = (uint8_t)(40U + (a % 180U));
        ctx->agents[a].state_byte = ptrc_encode_1byte_cascade(coh, PTRC_OPTICS_TRANSLUCENT, wl);
    }

    ctx->takt_counter = 1ULL;
    ctx->clock_phase_24 = 1U;
    ctx->observer_sub_takt = 1U;
    ctx->pyramid_angle_idx = 0U;
    ctx->active_load = 1024U;
    ctx->assigned_engines = PTRC_DEFAULT_ENGINES;
    ctx->bound_clusters = 1U;
    ctx->gpu_int32_active = ptrc_probe_integer_gpu_hardware();
    ctx->render_interval_takts = PTRC_GFX_TAKT_137;
    ctx->last_render_takt = 1U;
    ctx->deflection_count = 1U;
    ctx->mirror_pulses = 1U;
    ctx->render_status = PTRC_RENDER_READY;
    return PTRC_GFX_OK;
}

typedef struct {
    ptrc_gfx_ctx_t *ctx;
    uint32_t start_idx;
    uint32_t end_idx;
    int32_t  rot_u;
    int32_t  rot_v;
    int32_t         tilt_u;
    int32_t         tilt_v;
    uint32_t p_ring;
    uint32_t collisions_out;
    uint32_t obstacle_hits_out;
    uint32_t bound_out;
} ptrc_worker_args_t;

static void ptrc_process_agent_range(ptrc_worker_args_t *w) {
    ptrc_gfx_ctx_t *ctx = w->ctx;
    uint32_t collisions = 0U;
    uint32_t obstacle_hits = 0U;
    uint32_t bound_cnt = 0U;
    uint32_t phase_24 = ctx->clock_phase_24;
    uint8_t local_impulse[PTRC_OCCUPANCY_SLOTS];
    uint8_t local_density[PTRC_OCCUPANCY_SLOTS];
    uint8_t local_cohesion[PTRC_OCCUPANCY_SLOTS];
    for (uint32_t s = 0U; s < PTRC_OCCUPANCY_SLOTS; s++) {
        local_impulse[s] = 1U;
        local_density[s] = 1U;
        local_cohesion[s] = 1U;
    }

    for (uint32_t a = w->start_idx; a < w->end_idx; a++) {
        ptrc_wind_agent_t *ag = &ctx->agents[a];
        uint32_t sym_bit = a + (uint32_t)ctx->takt_counter;
        uint32_t is_cohesive = (uint32_t)((ag->state_byte >> 7U) & 1U);
        if (is_cohesive != 0U) {
            bound_cnt++;
        }

        int32_t nx = ptrc_plichta_move((int32_t)ag->x, (int32_t)ag->vx);
        int32_t ny = ptrc_plichta_move((int32_t)ag->y, (int32_t)ag->vy);
        int32_t nz = ptrc_plichta_move((int32_t)ag->z, (int32_t)ag->vz);

        if (nx > PTRC_TUNNEL_HALF_X) {
            uint64_t mix = (uint64_t)a * 2654435761ULL + ctx->takt_counter * 137ULL;
            nx = -PTRC_TUNNEL_HALF_X + (int32_t)(mix & 7ULL) + 1;
            ny = ptrc_z_sym_no_zero((int32_t)((mix >> 8U) % (uint64_t)(PTRC_TUNNEL_HALF_Y * 2)) - PTRC_TUNNEL_HALF_Y, a);
            nz = ptrc_z_sym_no_zero((int32_t)((mix >> 24U) % (uint64_t)(PTRC_TUNNEL_HALF_Z * 2)) - PTRC_TUNNEL_HALF_Z, a >> 1U);
            ag->vx = 1;
            ag->vy = (int16_t)(((sym_bit & 1U) == 0U) ? 1 : -1);
            ag->vz = (int16_t)((((sym_bit >> 1U) & 1U) == 0U) ? 1 : -1);
            ag->state_byte = ptrc_encode_1byte_cascade((uint8_t)is_cohesive, 1U, (uint8_t)((a % 12U) + 1U));
        } else if (nx < -PTRC_TUNNEL_HALF_X) {
            nx = -PTRC_TUNNEL_HALF_X + 1;
            ag->vx = 1;
        }

        if (ny > (PTRC_TUNNEL_HALF_Y - 12)) {
            if (ny > PTRC_TUNNEL_HALF_Y) {
                ny = PTRC_TUNNEL_HALF_Y - 1;
                ag->vy = (int16_t)-ptrc_abs32((int32_t)ag->vy);
            }
            if (ag->vx > 3) ag->vx--;
        } else if (ny < (-PTRC_TUNNEL_HALF_Y + 12)) {
            if (ny < -PTRC_TUNNEL_HALF_Y) {
                ny = -PTRC_TUNNEL_HALF_Y + 1;
                ag->vy = (int16_t)ptrc_abs32((int32_t)ag->vy);
            }
            if (ag->vx > 3) ag->vx--;
        }

        if (nz > (PTRC_TUNNEL_HALF_Z - 10)) {
            if (nz > PTRC_TUNNEL_HALF_Z) {
                nz = PTRC_TUNNEL_HALF_Z - 1;
                ag->vz = (int16_t)-ptrc_abs32((int32_t)ag->vz);
            }
            if (ag->vx > 3) ag->vx--;
        } else if (nz < (-PTRC_TUNNEL_HALF_Z + 10)) {
            if (nz < -PTRC_TUNNEL_HALF_Z) {
                nz = -PTRC_TUNNEL_HALF_Z + 1;
                ag->vz = (int16_t)ptrc_abs32((int32_t)ag->vz);
            }
            if (ag->vx > 3) ag->vx--;
        }

        if (ptrc_point_in_square_pyramid(nx, ny, nz, w->rot_u, w->rot_v, w->tilt_u, w->tilt_v)) {
            obstacle_hits++;
            collisions++;
            uint32_t facet_144 = (a + (ctx->pyramid_angle_idx / 137U) * 6U + phase_24) % PTRC_GFX_FACETS;
            int32_t aniso_bias = (ctx->sponge[facet_144] >= 0) ? 1 : -1;
            uint32_t j_dir = (facet_144 + (uint32_t)ctx->takt_counter) % PTRC_GFX_JUNCTIONS;
            int32_t jy = (int32_t)PTRC_JUNCTION_DIRS_24[j_dir].dy;
            int32_t jz = (int32_t)PTRC_JUNCTION_DIRS_24[j_dir].dz;

            ag->vx = 1;
            ag->vy = ptrc_z_sym_no_zero(jy + ((ny >= 0) ? 1 : -1) + aniso_bias, sym_bit);
            ag->vz = ptrc_z_sym_no_zero(jz + ((nz >= 0) ? 1 : -1) - aniso_bias, sym_bit >> 1U);
            nx = ptrc_plichta_move((int32_t)ag->x, -2);
            ny = ptrc_plichta_move((int32_t)ag->y, (int32_t)ag->vy);
            nz = ptrc_plichta_move((int32_t)ag->z, (int32_t)ag->vz);
            ag->state_byte = ptrc_encode_1byte_cascade(1U, PTRC_OPTICS_FIELD_COUPLED, (uint8_t)(22U + (a % 9U)));
        } else if (ptrc_point_in_crystal_sphere(nx, ny, nz)) {
            obstacle_hits++;
            collisions++;
            uint32_t facet_144 = (a * 3U + phase_24) % PTRC_GFX_FACETS;
            int32_t aniso_bias = (ctx->sponge[facet_144] >= 0) ? 1 : -1;
            int32_t sdy = ny - PTRC_SPHERE_CENTER_Y;
            int32_t sdz = nz - PTRC_SPHERE_CENTER_Z;
            ag->vx = 1;
            ag->vy = ptrc_z_sym_no_zero(((sdy >= 0) ? 1 : -1) + aniso_bias, sym_bit);
            ag->vz = ptrc_z_sym_no_zero(((sdz >= 0) ? 1 : -1) - aniso_bias, sym_bit >> 1U);
            nx = ptrc_plichta_move((int32_t)ag->x, -2);
            ny = ptrc_plichta_move((int32_t)ag->y, (int32_t)ag->vy);
            nz = ptrc_plichta_move((int32_t)ag->z, (int32_t)ag->vz);
            ag->state_byte = ptrc_encode_1byte_cascade(1U, PTRC_OPTICS_CRYSTALLINE, (uint8_t)(25U + (a % 6U)));
        } else {
            uint32_t slot = ptrc_fcc_slot_hash(nx, ny, nz);
            uint8_t occ_imp = local_impulse[slot];
            uint8_t dens = local_density[slot];
            uint8_t slot_coh = local_cohesion[slot];
            if (dens < 250U) local_density[slot] = (uint8_t)(dens + 1U);
            if (is_cohesive != 0U && slot_coh < 250U) local_cohesion[slot] = (uint8_t)(slot_coh + 1U);

            if (occ_imp == 1U) {
                local_impulse[slot] = ag->impulse;
                ag->vx = 1;
                ag->vy = (ag->vy > 0) ? -1 : 1;
                ag->vz = (ag->vz > 0) ? -1 : 1;
            } else {
                collisions++;
                /* Kohaesions-Anker ("Liebes-/Bindungsvariable"): gebundene Cluster halten zusammen */
                if ((is_cohesive != 0U || slot_coh >= 2U) && dens >= 3U) {
                    ag->vx = 1;
                    ag->state_byte = ptrc_encode_1byte_cascade(1U, PTRC_OPTICS_TRANSLUCENT, 19U);
                } else {
                    uint32_t facet_144 = (slot + occ_imp + phase_24) % PTRC_GFX_FACETS;
                    uint32_t alt_dir = (facet_144 + (uint32_t)ptrc_abs32(ctx->sponge[facet_144])) % PTRC_GFX_JUNCTIONS;
                    int32_t nvy = (int32_t)ag->vy + (int32_t)PTRC_JUNCTION_DIRS_24[alt_dir].dy;
                    int32_t nvz = (int32_t)ag->vz + (int32_t)PTRC_JUNCTION_DIRS_24[alt_dir].dz;
                    ag->vy = (int16_t)ptrc_z_sym_no_zero(nvy, sym_bit);
                    ag->vz = (int16_t)ptrc_z_sym_no_zero(nvz, sym_bit >> 1U);
                    ag->vy = (ag->vy >= 0) ? 1 : -1;
                    ag->vz = (ag->vz >= 0) ? 1 : -1;
                }
                if (ag->impulse > occ_imp) {
                    local_impulse[slot] = ag->impulse;
                }
            }
        }

        if (nx > PTRC_TUNNEL_HALF_X) nx = PTRC_TUNNEL_HALF_X;
        if (nx < -PTRC_TUNNEL_HALF_X) nx = -PTRC_TUNNEL_HALF_X;
        if (ny > PTRC_TUNNEL_HALF_Y) ny = PTRC_TUNNEL_HALF_Y;
        if (ny < -PTRC_TUNNEL_HALF_Y) ny = -PTRC_TUNNEL_HALF_Y;
        if (nz > PTRC_TUNNEL_HALF_Z) nz = PTRC_TUNNEL_HALF_Z;
        if (nz < -PTRC_TUNNEL_HALF_Z) nz = -PTRC_TUNNEL_HALF_Z;
        ag->vx = 1;
        ag->vy = (ag->vy >= 0) ? 1 : -1;
        ag->vz = (ag->vz >= 0) ? 1 : -1;
        ag->x = (int16_t)ptrc_z_no_zero(nx);
        ag->y = (int16_t)ptrc_z_no_zero(ny);
        ag->z = (int16_t)ptrc_z_no_zero(nz);
    }

    w->collisions_out = collisions;
    w->obstacle_hits_out = obstacle_hits;
    w->bound_out = bound_cnt;
}

static void *ptrc_worker_thread_entry(void *arg) {
    ptrc_process_agent_range((ptrc_worker_args_t *)arg);
    return NULL;
}

static uint32_t ptrc_compute_required_engines(uint32_t load, uint32_t bound_clusters) {
    uint32_t effective = load + (bound_clusters >> 7U);
    if (effective >= 1900U) return 8U;
    if (effective >= 1350U) return 4U;
    if (effective >= 950U)  return 2U;
    return 1U;
}

static void ptrc_advance_takt_metadata(
    ptrc_gfx_ctx_t *ctx,
    uint32_t collisions,
    uint32_t obstacle_hits,
    uint32_t bound_clusters
) {
    ctx->deflection_count += collisions;
    ctx->bound_clusters = bound_clusters;
    ctx->active_load = (collisions >> 4U) + (obstacle_hits >> 2U) + (bound_clusters >> 8U) + 600U;
    ctx->assigned_engines = ptrc_compute_required_engines(ctx->active_load, bound_clusters);
    (void)ptrc_gfx_evaluate_observer_sync(ctx);

    ctx->takt_counter++;
    if (ctx->observer_sub_takt >= PTRC_GFX_TAKT_137) {
        ctx->observer_sub_takt = 1U;
        ctx->clock_phase_24 = (ctx->clock_phase_24 % PTRC_GFX_JUNCTIONS) + 1U;
    } else {
        ctx->observer_sub_takt++;
    }
}

static void ptrc_prepare_takt_fields(ptrc_gfx_ctx_t *ctx, int32_t *rot_u, int32_t *rot_v, int32_t *tilt_u, int32_t *tilt_v, uint32_t *p_ring) {
    uint32_t phase_idx = (ctx->clock_phase_24 - 1U) % PTRC_GFX_JUNCTIONS;
    *p_ring = ctx->prime_rings[phase_idx & 15U];

    for (uint32_t j = 0U; j < PTRC_GFX_JUNCTIONS; j++) {
        uint32_t jf = PTRC_GFX_MEM_FACETS + j;
        uint32_t mf = (j * 5U + phase_idx) % PTRC_GFX_MEM_FACETS;
        int32_t coupled = ctx->sponge[jf] ^ ctx->sponge[mf];
        ctx->sponge[jf] = ptrc_z_no_zero(coupled + (int32_t)(*p_ring));
    }

    if ((ctx->takt_counter % PTRC_GFX_TAKT_137) == 0ULL) {
        for (uint32_t f = 0U; f < PTRC_GFX_FACETS; f++) {
            ctx->sponge[f] = ptrc_z_no_zero(~ctx->sponge[f]);
        }
        ctx->mirror_pulses++;
    }

    ctx->pyramid_angle_idx = (uint32_t)((ctx->takt_counter * 3ULL) % PTRC_PYRAMID_ROT_CYCLE);
    ptrc_get_pyramid_dual_axes(ctx->pyramid_angle_idx, rot_u, rot_v, tilt_u, tilt_v);

    for (uint32_t s = 0U; s < PTRC_OCCUPANCY_SLOTS; s++) {
        ctx->cell_impulse[s] = 1U;
        ctx->cell_density[s] = 1U;
        ctx->cell_cohesion[s] = 1U;
    }
}

int ptrc_gfx_step_takt(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) return PTRC_GFX_ERR;
    int32_t rot_u, rot_v, tilt_u, tilt_v;
    uint32_t p_ring;
    ptrc_prepare_takt_fields(ctx, &rot_u, &rot_v, &tilt_u, &tilt_v, &p_ring);

    ptrc_worker_args_t single = {ctx, 0U, PTRC_WIND_AGENTS, rot_u, rot_v, tilt_u, tilt_v, p_ring, 0U, 0U, 0U};
    ptrc_process_agent_range(&single);
    ptrc_advance_takt_metadata(ctx, single.collisions_out, single.obstacle_hits_out, single.bound_out);
    return PTRC_GFX_OK;
}

/* Weist jedem Beobachtercluster dynamisch 1..8 parallele pTRC-Engines zu */
int ptrc_gfx_step_takt_adaptive(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) return PTRC_GFX_ERR;
    int32_t rot_u, rot_v, tilt_u, tilt_v;
    uint32_t p_ring;
    ptrc_prepare_takt_fields(ctx, &rot_u, &rot_v, &tilt_u, &tilt_v, &p_ring);

    uint32_t n_eng = ctx->assigned_engines;
    if (n_eng < PTRC_MIN_ENGINES) n_eng = PTRC_MIN_ENGINES;
    if (n_eng > PTRC_MAX_ENGINES) n_eng = PTRC_MAX_ENGINES;

    if (n_eng == 1U) {
        ptrc_worker_args_t single = {ctx, 0U, PTRC_WIND_AGENTS, rot_u, rot_v, tilt_u, tilt_v, p_ring, 0U, 0U, 0U};
        ptrc_process_agent_range(&single);
        ptrc_advance_takt_metadata(ctx, single.collisions_out, single.obstacle_hits_out, single.bound_out);
        return PTRC_GFX_OK;
    }

    pthread_t threads[PTRC_MAX_ENGINES];
    ptrc_worker_args_t args[PTRC_MAX_ENGINES];
    uint32_t chunk = PTRC_WIND_AGENTS / n_eng;

    for (uint32_t t = 0U; t < n_eng; t++) {
        args[t].ctx = ctx;
        args[t].start_idx = t * chunk;
        args[t].end_idx = (t == (n_eng - 1U)) ? PTRC_WIND_AGENTS : ((t + 1U) * chunk);
        args[t].rot_u = rot_u;
        args[t].rot_v = rot_v;
        args[t].tilt_u = tilt_u;
        args[t].tilt_v = tilt_v;
        args[t].p_ring = p_ring;
        args[t].collisions_out = 0U;
        args[t].obstacle_hits_out = 0U;
        args[t].bound_out = 0U;
        (void)pthread_create(&threads[t], NULL, ptrc_worker_thread_entry, &args[t]);
    }

    uint32_t tot_col = 0U, tot_hits = 0U, tot_bound = 0U;
    for (uint32_t t = 0U; t < n_eng; t++) {
        (void)pthread_join(threads[t], NULL);
        tot_col += args[t].collisions_out;
        tot_hits += args[t].obstacle_hits_out;
        tot_bound += args[t].bound_out;
    }

    ptrc_advance_takt_metadata(ctx, tot_col, tot_hits, tot_bound);
    return PTRC_GFX_OK;
}

int ptrc_gfx_evaluate_observer_sync(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) return PTRC_GFX_ERR;

    if (ctx->active_load >= 2600U) {
        ctx->render_interval_takts = 0U;
        ctx->render_status = PTRC_RENDER_STALL;
        return PTRC_RENDER_STALL;
    } else if (ctx->active_load >= 1900U) {
        ctx->render_interval_takts = PTRC_GFX_TAKT_137 * 4U;
    } else if (ctx->active_load >= 1350U) {
        ctx->render_interval_takts = PTRC_GFX_TAKT_137 * 2U;
    } else {
        ctx->render_interval_takts = PTRC_GFX_TAKT_137;
    }

    if ((ctx->takt_counter % (uint64_t)ctx->render_interval_takts) == 0ULL) {
        ctx->last_render_takt = (uint32_t)ctx->takt_counter;
        ctx->render_status = PTRC_RENDER_READY;
    } else {
        ctx->render_status = PTRC_RENDER_WAIT;
    }
    return ctx->render_status;
}

static void ptrc_transpose_wavelength_to_rgb(
    uint8_t state_byte,
    int32_t depth_shade,
    uint8_t *r_out,
    uint8_t *g_out,
    uint8_t *b_out
) {
    uint32_t wl = (uint32_t)(state_byte & 0x1FU);
    uint32_t opt = (uint32_t)((state_byte >> 5U) & 3U);
    uint32_t br, bg, bb;

    if (opt == PTRC_OPTICS_CRYSTALLINE || opt == PTRC_OPTICS_FIELD_COUPLED) {
        br = 255U;
        bg = 65U + (wl & 31U);
        bb = 195U + (wl & 31U);
    } else {
        br = 68U + (wl & 15U);
        bg = 152U + (wl & 31U);
        bb = 235U + (wl & 15U);
    }

    uint32_t r = (br * (uint32_t)depth_shade) >> 8U;
    uint32_t g = (bg * (uint32_t)depth_shade) >> 8U;
    uint32_t b = (bb * (uint32_t)depth_shade) >> 8U;

    *r_out = (r == 0U) ? 1U : (uint8_t)r;
    *g_out = (g == 0U) ? 1U : (uint8_t)g;
    *b_out = (b == 0U) ? 1U : (uint8_t)b;
}

static inline void ptrc_project_single_crystal(
    uint8_t *rgb_out,
    int16_t *z_buf,
    uint32_t width,
    uint32_t height,
    int32_t wx,
    int32_t wy,
    int32_t wz,
    uint8_t r,
    uint8_t g,
    uint8_t b,
    int32_t blend_mode
) {
    int32_t persp = 1414 + wz;
    if (persp <= 100) return;

    int32_t sx = (wx * 1414) / persp;
    int32_t sy = (wy * 1414) / persp;

    int32_t px = ((sx + PTRC_TUNNEL_HALF_X) * (int32_t)width) / (PTRC_TUNNEL_HALF_X * 2);
    int32_t py = ((sy + PTRC_TUNNEL_HALF_Y) * (int32_t)height) / (PTRC_TUNNEL_HALF_Y * 2);

    if (px < 0 || px >= (int32_t)width || py < 0 || py >= (int32_t)height) {
        return;
    }

    size_t p_flat = (size_t)py * (size_t)width + (size_t)px;
    if (wz <= (int32_t)z_buf[p_flat]) {
        z_buf[p_flat] = (int16_t)wz;
        size_t pix = p_flat * 3U;
        if (blend_mode == 0 || (rgb_out[pix + 0U] == 1U && rgb_out[pix + 1U] == 2U)) {
            rgb_out[pix + 0U] = r;
            rgb_out[pix + 1U] = g;
            rgb_out[pix + 2U] = b;
        } else {
            uint8_t mr = (uint8_t)((rgb_out[pix + 0U] + r) >> 1U);
            uint8_t mg = (uint8_t)((rgb_out[pix + 1U] + g) >> 1U);
            uint8_t mb = (uint8_t)((rgb_out[pix + 2U] + b) >> 1U);
            rgb_out[pix + 0U] = (mr == 0U) ? 1U : mr;
            rgb_out[pix + 1U] = (mg == 0U) ? 1U : mg;
            rgb_out[pix + 2U] = (mb == 0U) ? 1U : mb;
        }
    }
}

static inline void ptrc_splat_cluster_1_plus_12(
    uint8_t *rgb_out,
    int16_t *z_buf,
    uint32_t width,
    uint32_t height,
    int32_t wx,
    int32_t wy,
    int32_t wz,
    uint8_t r,
    uint8_t g,
    uint8_t b,
    int32_t blend_mode
) {
    ptrc_project_single_crystal(rgb_out, z_buf, width, height, wx, wy, wz, r, g, b, blend_mode);

    int32_t obs_dist = PTRC_GFX_DEPTH_1414 + wz;
    if (obs_dist <= 100) return;

    /* Kontinuierliche Strahlensatz-Quantelung der 1+12 Huelle nach Beobachterdistanz */
    int32_t shell_span = (blend_mode == 0) ? 1 : ((PTRC_GFX_DEPTH_1414 * 5) / (obs_dist * 3));
    uint32_t shell_limit = (blend_mode == 0) ? 6U : PTRC_GFX_SHELL_12;
    if (shell_span > 0) {
        uint8_t sr = (uint8_t)((r * 7U) >> 3U);
        uint8_t sg = (uint8_t)((g * 7U) >> 3U);
        uint8_t sb = (uint8_t)((b * 7U) >> 3U);
        if (sr == 0U) sr = 1U;
        if (sg == 0U) sg = 1U;
        if (sb == 0U) sb = 1U;

        for (int32_t ring = 1; ring <= shell_span; ring++) {
            for (uint32_t s = 0U; s < shell_limit; s++) {
                ptrc_project_single_crystal(
                    rgb_out, z_buf, width, height,
                    wx + (((int32_t)PTRC_SHELL_12_DIRS[s].dx * ring + 1) >> 1),
                    wy + (((int32_t)PTRC_SHELL_12_DIRS[s].dy * ring + 1) >> 1),
                    wz + (((int32_t)PTRC_SHELL_12_DIRS[s].dz * ring + 1) >> 1),
                    sr, sg, sb, blend_mode
                );
            }
        }
    }
}

static void ptrc_render_crystal_pyramid(
    uint8_t *rgb_out,
    int16_t *z_buf,
    uint32_t width,
    uint32_t height,
    int32_t rot_u,
    int32_t rot_v,
    int32_t tilt_u,
    int32_t tilt_v
) {
    int32_t half_h = PTRC_PYRAMID_HEIGHT >> 1;
    const int32_t step = 2;

    for (int32_t ty = -half_h; ty <= half_h; ty += step) {
        int32_t ny = ptrc_z_no_zero(ty);
        int32_t hw = ((ty + half_h) * PTRC_PYRAMID_HALF_BASE) / PTRC_PYRAMID_HEIGHT;
        if (hw < 1) hw = 1;
        int32_t fcc_shift = ((ty >> 1) & 1);

        for (int32_t s = -hw + fcc_shift; s <= hw; s += step) {
            int32_t ns = ptrc_z_no_zero(s);
            int32_t is_edge = (ptrc_abs32(ptrc_abs32(s) - hw) <= step || ty <= (-half_h + step) || ty >= (half_h - step));

            for (int32_t wall = 0; wall < 4; wall++) {
                int32_t lx, lz;
                uint8_t wr, wg, wb;
                if (wall == 0) {
                    lx = ns; lz = -hw; wr = 215U; wg = 165U; wb = 55U;
                } else if (wall == 1) {
                    lx = hw; lz = ns; wr = 185U; wg = 138U; wb = 45U;
                } else if (wall == 2) {
                    lx = ns; lz = hw; wr = 145U; wg = 105U; wb = 35U;
                } else {
                    lx = -hw; lz = ns; wr = 175U; wg = 130U; wb = 42U;
                }
                if (is_edge) {
                    wr = 252U; wg = 220U; wb = 115U;
                }

                int32_t rx = (lx * rot_u + lz * rot_v) >> 10;
                int32_t rz = (-lx * rot_v + lz * rot_u) >> 10;
                int32_t wy = (ny * tilt_u + rz * tilt_v) >> 10;
                int32_t wz = ((-ny * tilt_v + rz * tilt_u) >> 10) + PTRC_PYRAMID_CENTER_Z;
                int32_t wx = rx + PTRC_PYRAMID_CENTER_X;

                ptrc_splat_cluster_1_plus_12(rgb_out, z_buf, width, height, wx, wy, wz, wr, wg, wb, 0);
            }
        }
    }

    int32_t base_hw = PTRC_PYRAMID_HALF_BASE;
    for (int32_t bz = -base_hw; bz <= base_hw; bz += step) {
        int32_t nbz = ptrc_z_no_zero(bz);
        int32_t fcc_shift = ((bz >> 1) & 1);
        for (int32_t bx = -base_hw + fcc_shift; bx <= base_hw; bx += step) {
            int32_t nbx = ptrc_z_no_zero(bx);
            int32_t is_border = (ptrc_abs32(ptrc_abs32(bx) - base_hw) <= step ||
                                 ptrc_abs32(ptrc_abs32(bz) - base_hw) <= step);
            uint8_t br = is_border ? 252U : 115U;
            uint8_t bg = is_border ? 220U : 84U;
            uint8_t bb = is_border ? 115U : 30U;

            int32_t rx = (nbx * rot_u + nbz * rot_v) >> 10;
            int32_t rz = (-nbx * rot_v + nbz * rot_u) >> 10;
            int32_t wy = (half_h * tilt_u + rz * tilt_v) >> 10;
            int32_t wz = ((-half_h * tilt_v + rz * tilt_u) >> 10) + PTRC_PYRAMID_CENTER_Z;
            int32_t wx = rx + PTRC_PYRAMID_CENTER_X;

            ptrc_splat_cluster_1_plus_12(rgb_out, z_buf, width, height, wx, wy, wz, br, bg, bb, 0);
        }
    }
}

static void ptrc_render_crystal_sphere(
    uint8_t *rgb_out,
    int16_t *z_buf,
    uint32_t width,
    uint32_t height,
    int32_t rot_u,
    int32_t rot_v
) {
    const int32_t r_sph = PTRC_SPHERE_RADIUS;
    const int32_t r_sq = r_sph * r_sph;
    const int32_t r_inner_sq = (r_sph - 4) * (r_sph - 4);
    const int32_t step = 2;

    for (int32_t ly = -r_sph; ly <= r_sph; ly += step) {
        int32_t ny = ptrc_z_no_zero(ly);
        int32_t fcc_y = ((ly >> 1) & 1);
        for (int32_t lz = -r_sph + fcc_y; lz <= r_sph; lz += step) {
            int32_t nz = ptrc_z_no_zero(lz);
            int32_t yz_sq = ny * ny + nz * nz;
            if (yz_sq > r_sq) continue;

            for (int32_t lx = -r_sph; lx <= r_sph; lx += step) {
                int32_t nx = ptrc_z_no_zero(lx);
                int32_t q = yz_sq + nx * nx;
                if (q > r_sq || q < r_inner_sq) continue;

                int32_t rx = (nx * rot_u - nz * rot_v) >> 10;
                int32_t rz = (nx * rot_v + nz * rot_u) >> 10;

                int32_t light = 155 - ((rx + ny - rz) >> 3);
                if (light < 55) light = 55;
                if (light > 250) light = 250;

                int32_t is_ring = (ptrc_abs32(ny) <= 4 || ptrc_abs32(nx) <= 4) ? 1 : 0;
                uint8_t cr = is_ring ? 140U : (uint8_t)((light * 3) >> 3);
                uint8_t cg = is_ring ? 245U : (uint8_t)((light * 7) >> 3);
                uint8_t cb = is_ring ? 255U : (uint8_t)light;

                ptrc_splat_cluster_1_plus_12(
                    rgb_out, z_buf, width, height,
                    rx + PTRC_SPHERE_CENTER_X,
                    ny + PTRC_SPHERE_CENTER_Y,
                    rz + PTRC_SPHERE_CENTER_Z,
                    cr, cg, cb, 0
                );
            }
        }
    }
}

int ptrc_gfx_render_observer_rgb24(
    ptrc_gfx_ctx_t *ctx,
    uint32_t width,
    uint32_t height,
    uint8_t *rgb_out
) {
    if (!ctx || !rgb_out || width < 2U || height < 2U) return PTRC_GFX_ERR;

    size_t total_pixels = (size_t)width * (size_t)height;
    if (total_pixels > PTRC_MAX_ZBUF_PIXELS) return PTRC_GFX_ERR;

    int16_t *z_buf = PTRC_STATIC_ZBUF;
    for (size_t p = 0U; p < total_pixels; p++) {
        z_buf[p] = 1000;
        size_t idx = p * 3U;
        rgb_out[idx + 0U] = 1U;
        rgb_out[idx + 1U] = 2U;
        rgb_out[idx + 2U] = 6U;
    }

    if (ctx->render_status == PTRC_RENDER_STALL) {
        return PTRC_RENDER_STALL;
    }

    int32_t rot_u, rot_v, tilt_u, tilt_v;
    ptrc_get_pyramid_dual_axes(ctx->pyramid_angle_idx, &rot_u, &rot_v, &tilt_u, &tilt_v);

    ptrc_render_crystal_pyramid(rgb_out, z_buf, width, height, rot_u, rot_v, tilt_u, tilt_v);
    ptrc_render_crystal_sphere(rgb_out, z_buf, width, height, rot_u, rot_v);

    for (uint32_t a = 0U; a < PTRC_WIND_AGENTS; a++) {
        const ptrc_wind_agent_t *ag = &ctx->agents[a];
        int32_t z_depth = (int32_t)ag->z;

        int32_t depth_shade = 245 - ((z_depth + PTRC_TUNNEL_HALF_Z) >> 2);
        if (depth_shade < 50) depth_shade = 50;
        if (depth_shade > 255) depth_shade = 255;

        uint8_t r, g, b;
        ptrc_transpose_wavelength_to_rgb(ag->state_byte, depth_shade, &r, &g, &b);

        ptrc_splat_cluster_1_plus_12(
            rgb_out, z_buf, width, height,
            (int32_t)ag->x, (int32_t)ag->y, z_depth,
            r, g, b, 1
        );
    }

    return PTRC_GFX_OK;
}

void ptrc_gfx_wipe(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) return;
    volatile uint8_t *p = (volatile uint8_t *)ctx;
    for (size_t i = 0U; i < sizeof(*ctx); i++) {
        p[i] = 0xFFU;
    }
}
