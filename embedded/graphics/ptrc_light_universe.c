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

/* File: embedded/graphics/ptrc_light_universe.c (Part 1 of 2) */

#include "ptrc_light_universe.h"

static const uint32_t PTRC_GFX_RINGS[PTRC_GFX_PRIME_RINGS] = {
    11U, 13U, 17U, 19U, 23U, 29U, 37U, 41U,
    43U, 47U, 53U, 59U, 61U, 67U, 71U, 73U
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

static inline int32_t ptrc_gfx_z_no_zero(int32_t v) {
    return (v == 0) ? -1 : v;
}

static inline uint64_t ptrc_gfx_u64_no_zero(uint64_t v) {
    return (v == 0ULL) ? 1ULL : v;
}

static inline int32_t ptrc_gfx_abs32(int32_t x) {
    return (x < 0) ? -x : x;
}

int ptrc_gfx_init(ptrc_gfx_ctx_t *ctx, uint64_t seed) {
    if (!ctx) {
        return PTRC_GFX_ERR;
    }

    uint64_t state = ptrc_gfx_u64_no_zero(seed ^ 614889782588491410ULL);

    for (uint32_t r = 0U; r < PTRC_GFX_PRIME_RINGS; r++) {
        *(ctx->prime_rings + r) = *(PTRC_GFX_RINGS + r);
    }

    for (uint32_t f = 0U; f < PTRC_GFX_FACETS; f++) {
        state = (state * 137ULL + (uint64_t)(f + 1U) * 211ULL) ^ (state >> 13U);
        state = ptrc_gfx_u64_no_zero(state);
        int32_t raw = (int32_t)(state % PTRC_GFX_PRIMORIAL_210) - 105;
        *(ctx->sponge + f) = ptrc_gfx_z_no_zero(raw);
    }

    ctx->takt_counter   = 1ULL;
    ctx->clock_phase_24 = 1U;
    ctx->cam_x          = ptrc_gfx_z_no_zero((*(PTRC_CLOCK24_U + 0U)) * 920);
    ctx->cam_y          = ptrc_gfx_z_no_zero(110000);
    ctx->cam_z          = ptrc_gfx_z_no_zero((*(PTRC_CLOCK24_V + 0U)) * 920);
    ctx->active_hits    = 1U;
    ctx->mirror_pulses  = 1U;

    return PTRC_GFX_OK;
}

int ptrc_gfx_step_takt(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) {
        return PTRC_GFX_ERR;
    }

    uint32_t phase_idx = (ctx->clock_phase_24 - 1U) % PTRC_GFX_JUNCTIONS;
    int32_t u = *(PTRC_CLOCK24_U + phase_idx);
    int32_t v = *(PTRC_CLOCK24_V + phase_idx);

    ctx->cam_x = ptrc_gfx_z_no_zero(u * 920);
    ctx->cam_y = ptrc_gfx_z_no_zero(110000 + v * 16);
    ctx->cam_z = ptrc_gfx_z_no_zero(v * 920);

    if ((ctx->takt_counter % PTRC_GFX_TAKT_137) == 0ULL) {
        for (uint32_t f = 0U; f < PTRC_GFX_FACETS; f++) {
            *(ctx->sponge + f) = ptrc_gfx_z_no_zero(~(*(ctx->sponge + f)));
        }
        ctx->mirror_pulses++;
    } else {
        uint32_t f0 = (uint32_t)((ctx->takt_counter * 37ULL) % PTRC_GFX_FACETS);
        uint32_t f1 = (f0 + 73U) % PTRC_GFX_FACETS;
        int32_t p_val = (int32_t)(*(ctx->prime_rings + (phase_idx & 15U)));
        *(ctx->sponge + f0) = ptrc_gfx_z_no_zero((*(ctx->sponge + f0)) + p_val);
        *(ctx->sponge + f1) = ptrc_gfx_z_no_zero((*(ctx->sponge + f1)) ^ p_val);
    }

    ctx->takt_counter++;
    ctx->clock_phase_24 = (ctx->clock_phase_24 % PTRC_GFX_JUNCTIONS) + 1U;
    return PTRC_GFX_OK;
}

/* File: embedded/graphics/ptrc_light_universe.c (Part 2 of 2) */

int ptrc_gfx_render_frame_rgb24(
    ptrc_gfx_ctx_t *ctx,
    uint32_t width,
    uint32_t height,
    uint8_t *rgb_out
) {
    if (!ctx || !rgb_out || width < 2U || height < 2U) {
        return PTRC_GFX_ERR;
    }

    int32_t half_w = (int32_t)(width >> 1U);
    int32_t half_h = (int32_t)(height >> 1U);
    uint32_t phase_idx = (ctx->clock_phase_24 - 1U) % PTRC_GFX_JUNCTIONS;
    int32_t rot_u = *(PTRC_CLOCK24_U + phase_idx);
    int32_t rot_v = *(PTRC_CLOCK24_V + phase_idx);
    uint32_t hit_counter = 1U;

    int32_t scale_x = (1024 / half_w) >= 1 ? (1024 / half_w) : 1;
    int32_t scale_y = (576 / half_h) >= 1 ? (576 / half_h) : 1;

    for (uint32_t py = 0U; py < height; py++) {
        int32_t dy = ptrc_gfx_z_no_zero(((int32_t)py - half_h) * scale_y);
        size_t row_offset = (size_t)py * (size_t)width * 3U;

        for (uint32_t px = 0U; px < width; px++) {
            int32_t dx = ptrc_gfx_z_no_zero(((int32_t)px - half_w) * scale_x);

            int32_t dir_x = ptrc_gfx_z_no_zero(((-1024 * rot_u + dx * rot_v) >> 10) * 64);
            int32_t dir_y = ptrc_gfx_z_no_zero((-115 - dy) * 64);
            int32_t dir_z = ptrc_gfx_z_no_zero(((-1024 * rot_v - dx * rot_u) >> 10) * 64);

            int32_t ray_x = ctx->cam_x;
            int32_t ray_y = ctx->cam_y;
            int32_t ray_z = ctx->cam_z;

            uint8_t out_r = 1U;
            uint8_t out_g = 1U;
            uint8_t out_b = 3U;

            for (uint32_t step = 1U; step <= PTRC_GFX_MAX_STEPS; step++) {
                ray_x += dir_x;
                ray_y += dir_y;
                ray_z += dir_z;

                int32_t vx = ptrc_gfx_z_no_zero(ray_x >> PTRC_GFX_VOXEL_SHIFT);
                int32_t vy = ptrc_gfx_z_no_zero(ray_y >> PTRC_GFX_VOXEL_SHIFT);
                int32_t vz = ptrc_gfx_z_no_zero(ray_z >> PTRC_GFX_VOXEL_SHIFT);

                int32_t manhattan = ptrc_gfx_abs32(vx) + ptrc_gfx_abs32(vy) + ptrc_gfx_abs32(vz);
                uint32_t facet_idx = (uint32_t)((ptrc_gfx_abs32(vx * 3 + vy * 5 + vz * 7)) % PTRC_GFX_FACETS);
                int32_t facet_val = *(ctx->sponge + facet_idx);

                /* 1. Central Golden 1+12 Octahedral Crystal Pyramid (manhattan <= 16) */
                if (manhattan <= 16 && (vy & 1) != 0 && ((ptrc_gfx_abs32(vx + vz + (facet_val & 7)) % 3U) != 0U)) {
                    uint32_t shade = 250U - (step * 5U);
                    if (shade < 64U) {
                        shade = 64U;
                    }
                    out_r = (uint8_t)shade;
                    out_g = (uint8_t)((shade * 195U) >> 8U);
                    out_b = (uint8_t)((shade * 52U) >> 8U);
                    if (out_b == 0U) {
                        out_b = 1U;
                    }
                    hit_counter++;
                    break;
                }

                /* 2. Outer Cyan & Violet Coprime Prime-Ring Resonance Starfield */
                uint32_t sig = (uint32_t)ptrc_gfx_abs32(vx * 137 + vy * 211 + vz * 157 + facet_val);
                if ((sig % 11U) == 1U && (sig % 23U) == 1U) {
                    uint32_t ring_sel = sig % PTRC_GFX_PRIME_RINGS;
                    uint32_t lum = 240U - (step * 4U);
                    if (lum < 72U) {
                        lum = 72U;
                    }
                    if ((ring_sel & 1U) == 0U) {
                        out_r = 24U;
                        out_g = (uint8_t)((lum * 220U) >> 8U);
                        out_b = (uint8_t)lum;
                    } else {
                        out_r = (uint8_t)((lum * 210U) >> 8U);
                        out_g = 42U;
                        out_b = (uint8_t)lum;
                    }
                    hit_counter++;
                    break;
                }
            }

            size_t pix = row_offset + (size_t)px * 3U;
            *(rgb_out + pix + 0U) = (out_r == 0U) ? 1U : out_r;
            *(rgb_out + pix + 1U) = (out_g == 0U) ? 1U : out_g;
            *(rgb_out + pix + 2U) = (out_b == 0U) ? 1U : out_b;
        }
    }

    ctx->active_hits = hit_counter;
    return PTRC_GFX_OK;
}

void ptrc_gfx_wipe(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) {
        return;
    }
    volatile uint8_t *p = (volatile uint8_t *)ctx;
    for (size_t i = 0U; i < sizeof(*ctx); i++) {
        *(p + i) = 0xFFU;
    }
}
