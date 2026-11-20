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

#include "ptrc_light_universe.h"
#include <stdlib.h>

static const uint32_t PTRC_GFX_RINGS[PTRC_GFX_PRIME_RINGS] = {
    11U, 13U, 17U, 19U, 23U, 29U, 37U, 41U,
    43U, 47U, 53U, 59U, 61U, 67U, 71U, 73U
};

static const int8_t PTRC_JUNCTION_DIRS_24[PTRC_GFX_JUNCTIONS][3] = {
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

static inline uint32_t ptrc_fcc_slot_hash(int32_t x, int32_t y, int32_t z) {
    uint32_t qx = (uint32_t)((x + 1024) / 3);
    uint32_t qy = (uint32_t)((y + 1024) / 3);
    uint32_t qz = (uint32_t)((z + 1024) / 3);
    uint32_t h = (qx * 73856093U) ^ (qy * 19349663U) ^ (qz * 83492791U);
    return h & (PTRC_OCCUPANCY_SLOTS - 1U);
}

static inline uint8_t ptrc_encode_1byte_cascade(
    uint8_t cascade_anchor,
    uint8_t optics_mode,
    uint8_t wavelength_id
) {
    uint8_t wl = (uint8_t)(((wavelength_id - 1U) & 30U) + 1U);
    uint8_t opt = (uint8_t)(optics_mode & 3U);
    uint8_t anc = (uint8_t)(cascade_anchor & 1U);
    return ptrc_u8_no_zero((uint8_t)((anc << 7U) | (opt << 5U) | wl));
}

static int ptrc_point_in_rotating_pyramid(
    int32_t px,
    int32_t py,
    int32_t pz,
    int32_t rot_u,
    int32_t rot_v
) {
    int32_t dx = px - PTRC_PYRAMID_CENTER_X;
    int32_t dy = py;
    int32_t dz = pz;

    int32_t q_dist = dx * dx + dy * dy + dz * dz;
    if (q_dist > (PTRC_PYRAMID_RADIUS * PTRC_PYRAMID_RADIUS)) {
        return 0;
    }

    int32_t lx = (dx * rot_u + dz * rot_v) >> 10;
    int32_t lz = (-dx * rot_v + dz * rot_u) >> 10;
    int32_t ly = (dy * rot_u + lz * rot_v) >> 10;
    int32_t fz = (-dy * rot_v + lz * rot_u) >> 10;

    int32_t lim = (PTRC_PYRAMID_RADIUS * 333) / 1000;
    if (fz < -lim) return 0;
    if ((943 * lx - 333 * fz) > (PTRC_PYRAMID_RADIUS * 333)) return 0;
    if ((-471 * lx + 816 * ly - 333 * fz) > (PTRC_PYRAMID_RADIUS * 333)) return 0;
    if ((-471 * lx - 816 * ly - 333 * fz) > (PTRC_PYRAMID_RADIUS * 333)) return 0;
    return 1;
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

    uint32_t r = (((wl * 7U + opt * 41U) & 0xFFU) * (uint32_t)depth_shade) >> 8U;
    uint32_t g = ((((32U - wl) * 6U + opt * 37U + 40U) & 0xFFU) * (uint32_t)depth_shade) >> 8U;
    uint32_t b = (((110U + wl * 4U + opt * 23U) & 0xFFU) * (uint32_t)depth_shade) >> 8U;

    *r_out = (r == 0U) ? 1U : (uint8_t)r;
    *g_out = (g == 0U) ? 1U : (uint8_t)g;
    *b_out = (b == 0U) ? 1U : (uint8_t)b;
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
        ctx->cell_state[s] = 1U;
    }

    for (uint32_t a = 0U; a < PTRC_WIND_AGENTS; a++) {
        rng = ptrc_u64_no_zero(rng * 6364136223846793005ULL + 1442695040888963407ULL);
        int32_t rx = (int32_t)(rng % (uint64_t)(PTRC_TUNNEL_HALF_X * 2)) - PTRC_TUNNEL_HALF_X;
        int32_t ry = (int32_t)((rng >> 16U) % (uint64_t)(PTRC_TUNNEL_HALF_Y * 2)) - PTRC_TUNNEL_HALF_Y;
        int32_t rz = (int32_t)((rng >> 32U) % (uint64_t)(PTRC_TUNNEL_HALF_Z * 2)) - PTRC_TUNNEL_HALF_Z;

        int32_t x = ptrc_z_no_zero(rx);
        int32_t y = ptrc_z_no_zero(ry);
        int32_t z = ptrc_z_no_zero(rz);
        if (((x + y + z) & 1) != 0) {
            x = ptrc_plichta_move(x, 1);
        }

        uint8_t wl = (uint8_t)((a % 16U) + 1U);
        uint8_t opt = (uint8_t)((a % 3U) + 1U);

        ctx->agents[a].x = (int16_t)x;
        ctx->agents[a].y = (int16_t)y;
        ctx->agents[a].z = (int16_t)z;
        ctx->agents[a].vx = (int16_t)(6 + (int32_t)(a & 3U));
        ctx->agents[a].vy = ptrc_z_no_zero((int32_t)((rng >> 48U) % 3ULL) - 1);
        ctx->agents[a].vz = ptrc_z_no_zero((int32_t)((rng >> 52U) % 3ULL) - 1);
        ctx->agents[a].impulse = (uint8_t)(40U + (a % 180U));
        ctx->agents[a].state_byte = ptrc_encode_1byte_cascade((uint8_t)(a & 1U), opt, wl);
    }

    ctx->takt_counter = 1ULL;
    ctx->clock_phase_24 = 1U;
    ctx->observer_sub_takt = 1U;
    ctx->pyramid_angle_idx = 0U;
    ctx->active_load = 1024U;
    ctx->render_interval_takts = PTRC_GFX_TAKT_137;
    ctx->last_render_takt = 1U;
    ctx->deflection_count = 1U;
    ctx->mirror_pulses = 1U;
    ctx->render_status = PTRC_RENDER_READY;
    return PTRC_GFX_OK;
}

int ptrc_gfx_step_takt(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) return PTRC_GFX_ERR;

    uint32_t phase_idx = (ctx->clock_phase_24 - 1U) % PTRC_GFX_JUNCTIONS;
    uint32_t p_ring = ctx->prime_rings[phase_idx & 15U];

    for (uint32_t j = 0U; j < PTRC_GFX_JUNCTIONS; j++) {
        uint32_t jf = PTRC_GFX_MEM_FACETS + j;
        uint32_t mf = (j * 5U + phase_idx) % PTRC_GFX_MEM_FACETS;
        int32_t coupled = ctx->sponge[jf] ^ ctx->sponge[mf];
        ctx->sponge[jf] = ptrc_z_no_zero(coupled + (int32_t)p_ring);
    }

    if ((ctx->takt_counter % PTRC_GFX_TAKT_137) == 0ULL) {
        for (uint32_t f = 0U; f < PTRC_GFX_FACETS; f++) {
            ctx->sponge[f] = ptrc_z_no_zero(~ctx->sponge[f]);
        }
        ctx->mirror_pulses++;
    }

    uint32_t rot_idx = (uint32_t)((ctx->takt_counter / 6ULL) % PTRC_GFX_JUNCTIONS);
    ctx->pyramid_angle_idx = rot_idx;
    int32_t rot_u = PTRC_CLOCK24_U[rot_idx];
    int32_t rot_v = PTRC_CLOCK24_V[rot_idx];

    for (uint32_t s = 0U; s < PTRC_OCCUPANCY_SLOTS; s++) {
        ctx->cell_impulse[s] = 1U;
    }

    uint32_t collisions = 0U;
    uint32_t pyramid_hits = 0U;

    for (uint32_t a = 0U; a < PTRC_WIND_AGENTS; a++) {
        ptrc_wind_agent_t *ag = &ctx->agents[a];

        int32_t nx = ptrc_plichta_move((int32_t)ag->x, (int32_t)ag->vx);
        int32_t ny = ptrc_plichta_move((int32_t)ag->y, (int32_t)ag->vy);
        int32_t nz = ptrc_plichta_move((int32_t)ag->z, (int32_t)ag->vz);

        if (nx > PTRC_TUNNEL_HALF_X) {
            nx = -PTRC_TUNNEL_HALF_X + (int32_t)((a + ctx->takt_counter) & 15ULL);
            if (nx == 0) nx = -1;
            ag->vx = (int16_t)(6 + (int32_t)((a + p_ring) & 3U));
            ag->vy = ptrc_z_no_zero((int32_t)((a % 3U) - 1));
            ag->vz = ptrc_z_no_zero((int32_t)(((a >> 2U) % 3U) - 1));
            ag->state_byte = ptrc_encode_1byte_cascade((uint8_t)(a & 1U), 1U, (uint8_t)((a % 12U) + 1U));
        } else if (nx < -PTRC_TUNNEL_HALF_X) {
            nx = -PTRC_TUNNEL_HALF_X + 1;
            ag->vx = 6;
        }

        if (ny > PTRC_TUNNEL_HALF_Y) {
            ny = PTRC_TUNNEL_HALF_Y - 1;
            ag->vy = (int16_t)-ptrc_abs32((int32_t)ag->vy);
        } else if (ny < -PTRC_TUNNEL_HALF_Y) {
            ny = -PTRC_TUNNEL_HALF_Y + 1;
            ag->vy = (int16_t)ptrc_abs32((int32_t)ag->vy);
        }

        if (nz > PTRC_TUNNEL_HALF_Z) {
            nz = PTRC_TUNNEL_HALF_Z - 1;
            ag->vz = (int16_t)-ptrc_abs32((int32_t)ag->vz);
        } else if (nz < -PTRC_TUNNEL_HALF_Z) {
            nz = -PTRC_TUNNEL_HALF_Z + 1;
            ag->vz = (int16_t)ptrc_abs32((int32_t)ag->vz);
        }

        if (ptrc_point_in_rotating_pyramid(nx, ny, nz, rot_u, rot_v)) {
            pyramid_hits++;
            collisions++;
            uint32_t j_dir = (a + rot_idx + (uint32_t)ctx->takt_counter) % PTRC_GFX_JUNCTIONS;
            int32_t jx = PTRC_JUNCTION_DIRS_24[j_dir][0];
            int32_t jy = PTRC_JUNCTION_DIRS_24[j_dir][1];
            int32_t jz = PTRC_JUNCTION_DIRS_24[j_dir][2];

            ag->vx = ptrc_z_no_zero(3 + ptrc_abs32(jx));
            ag->vy = ptrc_z_no_zero(jy * 3 + ((ny >= 0) ? 2 : -2));
            ag->vz = ptrc_z_no_zero(jz * 3 + ((nz >= 0) ? 2 : -2));
            nx = ptrc_plichta_move((int32_t)ag->x, (int32_t)ag->vx);
            ny = ptrc_plichta_move((int32_t)ag->y, (int32_t)ag->vy);
            nz = ptrc_plichta_move((int32_t)ag->z, (int32_t)ag->vz);
            ag->state_byte = ptrc_encode_1byte_cascade(1U, PTRC_OPTICS_FIELD_COUPLED, (uint8_t)(20U + (a % 11U)));
        } else {
            uint32_t slot = ptrc_fcc_slot_hash(nx, ny, nz);
            uint8_t occ_imp = ctx->cell_impulse[slot];
            if (occ_imp == 1U) {
                ctx->cell_impulse[slot] = ag->impulse;
                ctx->cell_state[slot] = ag->state_byte;
                if ((a & 7U) == (uint32_t)(ctx->takt_counter & 7ULL)) {
                    ag->vx = ptrc_z_no_zero(((int32_t)ag->vx * 3 + 7) >> 2);
                    ag->vy = ptrc_z_no_zero(((int32_t)ag->vy * 3) >> 2);
                    ag->vz = ptrc_z_no_zero(((int32_t)ag->vz * 3) >> 2);
                }
            } else {
                collisions++;
                uint32_t alt_dir = (a + occ_imp + (uint32_t)ctx->takt_counter) % PTRC_GFX_JUNCTIONS;
                ag->vy = ptrc_z_no_zero((int32_t)ag->vy + PTRC_JUNCTION_DIRS_24[alt_dir][1]);
                ag->vz = ptrc_z_no_zero((int32_t)ag->vz + PTRC_JUNCTION_DIRS_24[alt_dir][2]);
                if (ag->vy > 8) ag->vy = 8;
                if (ag->vy < -8) ag->vy = -8;
                if (ag->vz > 8) ag->vz = 8;
                if (ag->vz < -8) ag->vz = -8;
                if (ag->impulse > occ_imp) {
                    ctx->cell_impulse[slot] = ag->impulse;
                    ctx->cell_state[slot] = ag->state_byte;
                }
            }
        }

        ag->x = (int16_t)nx;
        ag->y = (int16_t)ny;
        ag->z = (int16_t)nz;
    }

    ctx->deflection_count += collisions;
    ctx->active_load = (collisions >> 4U) + (pyramid_hits >> 2U) + 600U;
    (void)ptrc_gfx_evaluate_observer_sync(ctx);

    ctx->takt_counter++;
    if (ctx->observer_sub_takt >= PTRC_GFX_TAKT_137) {
        ctx->observer_sub_takt = 1U;
        ctx->clock_phase_24 = (ctx->clock_phase_24 % PTRC_GFX_JUNCTIONS) + 1U;
    } else {
        ctx->observer_sub_takt++;
    }
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

int ptrc_gfx_render_observer_rgb24(
    ptrc_gfx_ctx_t *ctx,
    uint32_t width,
    uint32_t height,
    uint8_t *rgb_out
) {
    if (!ctx || !rgb_out || width < 2U || height < 2U) return PTRC_GFX_ERR;

    size_t total_pixels = (size_t)width * (size_t)height;
    int16_t *z_buf = (int16_t *)malloc(total_pixels * sizeof(int16_t));
    if (!z_buf) return PTRC_GFX_ERR;

    for (size_t p = 0U; p < total_pixels; p++) {
        z_buf[p] = 1000;
        size_t idx = p * 3U;
        rgb_out[idx + 0U] = 1U;
        rgb_out[idx + 1U] = 2U;
        rgb_out[idx + 2U] = 6U;
    }

    if (ctx->render_status == PTRC_RENDER_STALL) {
        free(z_buf);
        return PTRC_RENDER_STALL;
    }

    uint32_t rot_idx = ctx->pyramid_angle_idx % PTRC_GFX_JUNCTIONS;
    int32_t rot_u = PTRC_CLOCK24_U[rot_idx];
    int32_t rot_v = PTRC_CLOCK24_V[rot_idx];

    /* 1. Solide rotierende 3D-Pyramide im linken Drittel rendern (Z-Occlusion) */
    int32_t pyr_cx = ((PTRC_PYRAMID_CENTER_X + PTRC_TUNNEL_HALF_X) * (int32_t)width) / (PTRC_TUNNEL_HALF_X * 2);
    int32_t pyr_cy = (int32_t)(height >> 1U);
    int32_t pyr_r_px = (PTRC_PYRAMID_RADIUS * (int32_t)width) / (PTRC_TUNNEL_HALF_X * 2);

    for (int32_t dy = -pyr_r_px; dy <= pyr_r_px; dy++) {
        int32_t py = pyr_cy + dy;
        if (py < 0 || py >= (int32_t)height) continue;
        int32_t wy = ((py - (int32_t)(height >> 1U)) * (PTRC_TUNNEL_HALF_Y * 2)) / (int32_t)height;

        for (int32_t dx = -pyr_r_px; dx <= pyr_r_px; dx++) {
            int32_t px = pyr_cx + dx;
            if (px < 0 || px >= (int32_t)width) continue;
            int32_t wx = ((px - (int32_t)(width >> 1U)) * (PTRC_TUNNEL_HALF_X * 2)) / (int32_t)width;

            for (int32_t wz = -PTRC_PYRAMID_RADIUS; wz <= PTRC_PYRAMID_RADIUS; wz += 4) {
                if (ptrc_point_in_rotating_pyramid(wx, wy, wz, rot_u, rot_v)) {
                    size_t p_flat = (size_t)py * (size_t)width + (size_t)px;
                    z_buf[p_flat] = (int16_t)wz;
                    int32_t shade = 230 - ((wz + PTRC_PYRAMID_RADIUS) >> 1);
                    if (shade < 60) shade = 60;
                    if (shade > 250) shade = 250;
                    size_t pix = p_flat * 3U;
                    rgb_out[pix + 0U] = (uint8_t)shade;
                    rgb_out[pix + 1U] = (uint8_t)((shade * 3) >> 2);
                    rgb_out[pix + 2U] = (uint8_t)((shade >> 2) + 20);
                    break;
                }
            }
        }
    }

    /* 2. Alle 60.000 Luftmolekuel-Cluster (1+12) mit Z-Occlusion & Transparenz projizieren */
    for (uint32_t a = 0U; a < PTRC_WIND_AGENTS; a++) {
        const ptrc_wind_agent_t *ag = &ctx->agents[a];

        int32_t z_depth = (int32_t)ag->z;
        int32_t persp = 1414 + z_depth;
        int32_t sx = ((int32_t)ag->x * 1414) / persp;
        int32_t sy = ((int32_t)ag->y * 1414) / persp;

        int32_t px = ((sx + PTRC_TUNNEL_HALF_X) * (int32_t)width) / (PTRC_TUNNEL_HALF_X * 2);
        int32_t py = ((sy + PTRC_TUNNEL_HALF_Y) * (int32_t)height) / (PTRC_TUNNEL_HALF_Y * 2);

        if (px >= 0 && px < (int32_t)width && py >= 0 && py < (int32_t)height) {
            size_t p_flat = (size_t)py * (size_t)width + (size_t)px;

            if (z_depth <= (int32_t)z_buf[p_flat]) {
                z_buf[p_flat] = (int16_t)z_depth;
                int32_t depth_shade = 240 - ((z_depth + PTRC_TUNNEL_HALF_Z) >> 2);
                if (depth_shade < 55) depth_shade = 55;
                if (depth_shade > 255) depth_shade = 255;

                uint8_t r, g, b;
                ptrc_transpose_wavelength_to_rgb(ag->state_byte, depth_shade, &r, &g, &b);

                size_t pix = p_flat * 3U;
                if (rgb_out[pix + 0U] == 1U && rgb_out[pix + 1U] == 2U) {
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
    }

    free(z_buf);
    return PTRC_GFX_OK;
}

void ptrc_gfx_wipe(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) return;
    volatile uint8_t *p = (volatile uint8_t *)ctx;
    for (size_t i = 0U; i < sizeof(*ctx); i++) {
        p[i] = 0xFFU;
    }
}
