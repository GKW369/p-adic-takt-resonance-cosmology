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

static inline int32_t ptrc_plichta_step_axis(int32_t pos, int32_t delta) {
    int32_t next = pos + delta;
    if (next == 0) {
        next = (delta >= 0) ? 1 : -1;
    }
    if (next > 8) {
        next = -8 + ((next - 9) & 7);
        if (next == 0) next = -1;
    } else if (next < -8) {
        next = 8 - ((-next - 9) & 7);
        if (next == 0) next = 1;
    }
    return next;
}

static inline uint32_t ptrc_coord_to_idx(int32_t c) {
    return (c < 0) ? (uint32_t)(c + 8) : (uint32_t)(c + 7);
}

static inline uint32_t ptrc_cell_linear_idx(int32_t x, int32_t y, int32_t z) {
    uint32_t ix = ptrc_coord_to_idx(x) & 15U;
    uint32_t iy = ptrc_coord_to_idx(y) & 15U;
    uint32_t iz = ptrc_coord_to_idx(z) & 15U;
    return (iz * PTRC_LATTICE_DIM + iy) * PTRC_LATTICE_DIM + ix;
}

static inline uint8_t ptrc_encode_1byte_state(uint8_t element_id, uint8_t wavelength_id) {
    uint8_t wl = (uint8_t)(((wavelength_id - 1U) & 30U) + 1U);
    uint8_t el_band = (uint8_t)((element_id % 7U) + 1U);
    return ptrc_u8_no_zero((uint8_t)((el_band << 5U) | (wl & 0x1FU)));
}

static void ptrc_transpose_wavelength_to_rgb(
    uint8_t state_byte,
    int32_t depth_shade,
    uint8_t *r_out,
    uint8_t *g_out,
    uint8_t *b_out
) {
    uint32_t wl = (uint32_t)(state_byte & 0x1FU);
    uint32_t band = (uint32_t)((state_byte >> 5U) & 7U);

    uint32_t r = (((wl * 8U + band * 19U) & 0xFFU) * (uint32_t)depth_shade) >> 8U;
    uint32_t g = ((((32U - wl) * 7U + band * 29U) & 0xFFU) * (uint32_t)depth_shade) >> 8U;
    uint32_t b = ((((wl * 13U) ^ (band * 41U)) & 0xFFU) * (uint32_t)depth_shade) >> 8U;

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

    uint32_t idx = 0U;
    for (int32_t iz = 0; iz < (int32_t)PTRC_LATTICE_DIM; iz++) {
        int8_t cz = (int8_t)((iz < 8) ? (iz - 8) : (iz - 7));
        for (int32_t iy = 0; iy < (int32_t)PTRC_LATTICE_DIM; iy++) {
            int8_t cy = (int8_t)((iy < 8) ? (iy - 8) : (iy - 7));
            for (int32_t ix = 0; ix < (int32_t)PTRC_LATTICE_DIM; ix++) {
                int8_t cx = (int8_t)((ix < 8) ? (ix - 8) : (ix - 7));
                ptrc_crystal_cell_t *cell = &ctx->cells[idx++];
                cell->cx = cx;
                cell->cy = cy;
                cell->cz = cz;
                cell->state_byte = 1U;
                cell->impulse = 1U;
                cell->observer_cluster = (uint8_t)(((ix + iy + iz) % 24) + 1);
                for (uint32_t m = 0U; m < PTRC_GFX_MEM_FACETS; m++) {
                    cell->facet_mem[m] = 1U;
                }
            }
        }
    }

    for (uint32_t p = 0U; p < PTRC_MAX_IMPULSE_PACKETS; p++) {
        rng = ptrc_u64_no_zero(rng * 6364136223846793005ULL + 1442695040888963407ULL);
        int32_t sx = (int32_t)(rng % 16ULL) - 8;
        int32_t sy = (int32_t)((rng >> 8U) % 16ULL) - 8;
        int32_t sz = (int32_t)((rng >> 16U) % 16ULL) - 8;
        ctx->packets[p].x = ptrc_z_no_zero(sx);
        ctx->packets[p].y = ptrc_z_no_zero(sy);
        ctx->packets[p].z = ptrc_z_no_zero(sz);
        ctx->packets[p].dir_idx = (uint8_t)(p % PTRC_GFX_JUNCTIONS);
        ctx->packets[p].impulse = (uint8_t)((p % 240U) + 10U);
        ctx->packets[p].wavelength_id = (uint8_t)((p % 31U) + 1U);
        ctx->packets[p].element_id = (uint8_t)((p % PTRC_GFX_STABLE_ELEMENTS) + 1U);
    }

    ctx->takt_counter = 1ULL;
    ctx->clock_phase_24 = 1U;
    ctx->active_load = PTRC_MAX_IMPULSE_PACKETS;
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

    for (uint32_t c = 0U; c < PTRC_LATTICE_CELLS; c++) {
        ctx->cells[c].impulse = 1U;
    }

    uint32_t collisions = 0U;
    uint32_t occupied_cells = 0U;

    for (uint32_t p = 0U; p < PTRC_MAX_IMPULSE_PACKETS; p++) {
        ptrc_impulse_packet_t *pkt = &ctx->packets[p];
        uint8_t d_idx = pkt->dir_idx % PTRC_GFX_JUNCTIONS;

        int32_t nx = ptrc_plichta_step_axis(pkt->x, PTRC_JUNCTION_DIRS_24[d_idx][0]);
        int32_t ny = ptrc_plichta_step_axis(pkt->y, PTRC_JUNCTION_DIRS_24[d_idx][1]);
        int32_t nz = ptrc_plichta_step_axis(pkt->z, PTRC_JUNCTION_DIRS_24[d_idx][2]);

        uint32_t target_cell_idx = ptrc_cell_linear_idx(nx, ny, nz);
        ptrc_crystal_cell_t *cell = &ctx->cells[target_cell_idx];

        if (cell->impulse == 1U) {
            cell->impulse = pkt->impulse;
            cell->state_byte = ptrc_encode_1byte_state(pkt->element_id, pkt->wavelength_id);
            cell->facet_mem[(ctx->takt_counter + p) % PTRC_GFX_MEM_FACETS] = pkt->element_id;
            pkt->x = nx;
            pkt->y = ny;
            pkt->z = nz;
            occupied_cells++;
        } else {
            collisions++;
            uint8_t weaker_impulse = pkt->impulse;
            uint8_t weaker_wl = pkt->wavelength_id;
            uint8_t weaker_el = pkt->element_id;

            if (pkt->impulse > cell->impulse) {
                weaker_impulse = cell->impulse;
                cell->impulse = pkt->impulse;
                cell->state_byte = ptrc_encode_1byte_state(pkt->element_id, pkt->wavelength_id);
                pkt->x = nx;
                pkt->y = ny;
                pkt->z = nz;
            }

            uint8_t alt_dir = (uint8_t)((d_idx + (weaker_impulse % 11U) + 1U) % PTRC_GFX_JUNCTIONS);
            int32_t ax = ptrc_plichta_step_axis(nx, PTRC_JUNCTION_DIRS_24[alt_dir][0]);
            int32_t ay = ptrc_plichta_step_axis(ny, PTRC_JUNCTION_DIRS_24[alt_dir][1]);
            int32_t az = ptrc_plichta_step_axis(nz, PTRC_JUNCTION_DIRS_24[alt_dir][2]);

            uint32_t alt_idx = ptrc_cell_linear_idx(ax, ay, az);
            if (ctx->cells[alt_idx].impulse == 1U) {
                ctx->cells[alt_idx].impulse = ptrc_u8_no_zero(weaker_impulse);
                ctx->cells[alt_idx].state_byte = ptrc_encode_1byte_state(weaker_el, weaker_wl);
                occupied_cells++;
            }
            pkt->x = ax;
            pkt->y = ay;
            pkt->z = az;
            pkt->dir_idx = alt_dir;
        }
    }

    ctx->deflection_count += collisions;
    ctx->active_load = occupied_cells + (collisions * 2U);
    (void)ptrc_gfx_evaluate_observer_sync(ctx);

    ctx->takt_counter++;
    ctx->clock_phase_24 = (ctx->clock_phase_24 % PTRC_GFX_JUNCTIONS) + 1U;
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
    for (size_t p = 0U; p < total_pixels; p++) {
        size_t idx = p * 3U;
        rgb_out[idx + 0U] = 1U;
        rgb_out[idx + 1U] = 2U;
        rgb_out[idx + 2U] = 6U;
    }

    if (ctx->render_status == PTRC_RENDER_STALL) {
        return PTRC_RENDER_STALL;
    }

    uint32_t phase_idx = (ctx->clock_phase_24 - 1U) % PTRC_GFX_JUNCTIONS;
    int32_t rot_u = PTRC_CLOCK24_U[phase_idx];
    int32_t rot_v = PTRC_CLOCK24_V[phase_idx];

    for (uint32_t c = 0U; c < PTRC_LATTICE_CELLS; c++) {
        const ptrc_crystal_cell_t *cell = &ctx->cells[c];
        if (cell->impulse == 1U) continue;

        int32_t x = (int32_t)cell->cx * 28;
        int32_t y = (int32_t)cell->cy * 28;
        int32_t z = (int32_t)cell->cz * 28;

        int32_t rx = (x * rot_u - z * rot_v) >> 10;
        int32_t rz = ((x * rot_v + z * rot_u) >> 10) + 320;
        if (rz <= 20) continue;

        int32_t denom = ((rz * 1000) / PTRC_GFX_DEPTH_1414) + PTRC_GFX_INVARIANT_156;
        int32_t px = ((rx * (int32_t)width) / denom) + (int32_t)(width >> 1U);
        int32_t py = ((y * (int32_t)height) / denom) + (int32_t)(height >> 1U);

        if (px >= 0 && px < (int32_t)width && py >= 0 && py < (int32_t)height) {
            int32_t depth_shade = 255 - ((rz - 100) >> 1);
            if (depth_shade < 48) depth_shade = 48;
            if (depth_shade > 255) depth_shade = 255;

            uint8_t r, g, b;
            ptrc_transpose_wavelength_to_rgb(cell->state_byte, depth_shade, &r, &g, &b);

            size_t pix = ((size_t)py * (size_t)width + (size_t)px) * 3U;
            rgb_out[pix + 0U] = r;
            rgb_out[pix + 1U] = g;
            rgb_out[pix + 2U] = b;
        }
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
