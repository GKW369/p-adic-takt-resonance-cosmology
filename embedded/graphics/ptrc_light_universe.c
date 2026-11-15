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

/* File: embedded/graphics/ptrc_light_universe.c (Part 1 of 2) */

#include "ptrc_light_universe.h"

/* Virtual 16.384 x 9.216 integer lattice space (16:9 exact ratio, zero-free) */
#define VIRT_W 16384
#define VIRT_H 9216

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
        uint8_t st8 = (uint8_t)(state & 0xFFULL);
        *(ctx->crystal_state + f) = (st8 == 0U) ? 0xFFU : st8;
    }

    /* Seed 60,000 freely distributed 1-bit information agents across Z \ {0} */
    for (uint32_t i = 0U; i < PTRC_GFX_AGENT_COUNT; i++) {
        state = (state * 6364136223846793005ULL + 1442695040888963407ULL);
        state = ptrc_gfx_u64_no_zero(state);
        int32_t ax = (int32_t)(state % (uint64_t)VIRT_W) + 1;
        state = (state ^ (state >> 17U)) * 211ULL + 137ULL;
        state = ptrc_gfx_u64_no_zero(state);
        int32_t ay = (int32_t)(state % (uint64_t)VIRT_H) + 1;

        *(ctx->agent_x + i) = ptrc_gfx_z_no_zero(ax);
        *(ctx->agent_y + i) = ptrc_gfx_z_no_zero(ay);
        *(ctx->agent_vx + i) = ptrc_gfx_z_no_zero(44 + (int32_t)(i % 19U));
        *(ctx->agent_vy + i) = ptrc_gfx_z_no_zero((int32_t)(i % 5U) - 2);
        uint8_t ast = (uint8_t)((state >> 8U) & 0xFFULL);
        *(ctx->agent_state + i) = (ast == 0U) ? 0xFFU : ast;
    }

    ctx->takt_counter   = 1ULL;
    ctx->clock_phase_24 = 1U;
    /* Floating rotating pyramid in the front third (~1/5 of screen width = ~3276) */
    ctx->pyramid_cx     = ptrc_gfx_z_no_zero(4600);
    ctx->pyramid_cy     = ptrc_gfx_z_no_zero(VIRT_H >> 1);
    ctx->active_hits    = 1U;
    ctx->mirror_pulses  = 1U;

    return PTRC_GFX_OK;
}

int ptrc_gfx_step_takt(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) {
        return PTRC_GFX_ERR;
    }

    uint32_t phase_idx = (ctx->clock_phase_24 - 1U) % PTRC_GFX_JUNCTIONS;
    int32_t rot_u = *(PTRC_CLOCK24_U + phase_idx);
    int32_t rot_v = *(PTRC_CLOCK24_V + phase_idx);
    int32_t p_ring = (int32_t)(*(ctx->prime_rings + (phase_idx & 15U)));

    /* 1. 24 Contact Junctions exchange state with 120 free isotropy facets */
    for (uint32_t j = 0U; j < PTRC_GFX_JUNCTIONS; j++) {
        uint32_t jf = PTRC_GFX_FREE_FACETS + j;
        uint32_t mf = (j * 5U + phase_idx) % PTRC_GFX_FREE_FACETS;
        int32_t coupled = (*(ctx->sponge + jf)) ^ (*(ctx->sponge + mf));
        *(ctx->sponge + jf) = ptrc_gfx_z_no_zero(coupled + p_ring);
        uint8_t sn = (uint8_t)(((*(ctx->crystal_state + mf)) ^ (uint8_t)(coupled & 0xFF)) + (uint8_t)p_ring);
        *(ctx->crystal_state + mf) = (sn == 0U) ? 0xFFU : sn;
    }

    /* 2. Global 137-Takt Observer Mirror Pulse */
    if ((ctx->takt_counter % PTRC_GFX_TAKT_137) == 0ULL) {
        for (uint32_t f = 0U; f < PTRC_GFX_FACETS; f++) {
            *(ctx->sponge + f) = ptrc_gfx_z_no_zero(~(*(ctx->sponge + f)));
            uint8_t inv = (uint8_t)(~(*(ctx->crystal_state + f)));
            *(ctx->crystal_state + f) = (inv == 0U) ? 0xFFU : inv;
        }
        ctx->mirror_pulses++;
    }

    /* 3. Pyramid bobs gently up & down in the front third (24-Clock Quadrance) */
    int32_t py_center = (VIRT_H >> 1) + ((rot_v * 680) >> 10);
    ctx->pyramid_cx = ptrc_gfx_z_no_zero(4600 + ((rot_u * 180) >> 10));
    ctx->pyramid_cy = ptrc_gfx_z_no_zero(py_center);

    /* Pyramid half-width ~ 1638 (total width ~ 3276 = 1/5 of 16384 screen width) */
    const int32_t pyr_rad = 1638;

    /* 4. Advance all 60,000 agents flowing from left -> right around the rotating pyramid */
    for (uint32_t i = 0U; i < PTRC_GFX_AGENT_COUNT; i++) {
        int32_t ax = *(ctx->agent_x + i) + *(ctx->agent_vx + i);
        int32_t ay = *(ctx->agent_y + i) + *(ctx->agent_vy + i);

        /* Respawn fresh particles on the left boundary when exiting right */
        if (ax > VIRT_W) {
            ax = ptrc_gfx_z_no_zero((ax % 64) + 1);
            ay = ptrc_gfx_z_no_zero(((int32_t)((i * 137U + (uint32_t)ctx->takt_counter * 31U) % (uint32_t)VIRT_H)) + 1);
            *(ctx->agent_vx + i) = ptrc_gfx_z_no_zero(44 + (int32_t)(i % 19U));
            *(ctx->agent_vy + i) = ptrc_gfx_z_no_zero((int32_t)(i % 5U) - 2);
        }

        if (ay < 1) {
            ay = 1;
            *(ctx->agent_vy + i) = ptrc_gfx_abs32(*(ctx->agent_vy + i));
        } else if (ay > VIRT_H) {
            ay = VIRT_H;
            *(ctx->agent_vy + i) = -ptrc_gfx_abs32(*(ctx->agent_vy + i));
        }

        /* Interaction with the 1+12 rotating pyramid boundary (deflection + wake vortex) */
        int32_t dx = ax - ctx->pyramid_cx;
        int32_t dy = ay - ctx->pyramid_cy;
        int32_t manhattan = ptrc_gfx_abs32(dx) + ptrc_gfx_abs32(dy);

        if (manhattan <= (pyr_rad + 420)) {
            int32_t push_y = (dy >= 0) ? 18 : -18;
            if (manhattan <= pyr_rad) {
                /* Deflect outside crystal boundary along 24-clock tangent */
                ay = ptrc_gfx_z_no_zero(ctx->pyramid_cy + ((dy >= 0) ? (pyr_rad - ptrc_gfx_abs32(dx) + 24) : -(pyr_rad - ptrc_gfx_abs32(dx) + 24)));
                *(ctx->agent_vx + i) = ptrc_gfx_z_no_zero(36 + ((rot_u & 15)));
                *(ctx->agent_vy + i) = ptrc_gfx_z_no_zero(push_y + (rot_v >> 7));
                uint8_t st = (uint8_t)((*(ctx->agent_state + i)) ^ 0xA5U);
                *(ctx->agent_state + i) = (st == 0U) ? 0xFFU : st;
            } else {
                /* Wake resonance ripple behind the pyramid */
                *(ctx->agent_vy + i) = ptrc_gfx_z_no_zero(*(ctx->agent_vy + i) + ((dx > 0) ? ((rot_v >> 8) * ((i & 1U) ? 1 : -1)) : (push_y >> 2)));
            }
        } else {
            /* Gentle laminar damping back toward horizontal stream */
            if (*(ctx->agent_vy + i) > 3) {
                *(ctx->agent_vy + i) -= 1;
            } else if (*(ctx->agent_vy + i) < -3) {
                *(ctx->agent_vy + i) += 1;
            }
        }

        *(ctx->agent_x + i) = ptrc_gfx_z_no_zero(ax);
        *(ctx->agent_y + i) = ptrc_gfx_z_no_zero(ay);
    }

    ctx->takt_counter++;
    ctx->clock_phase_24 = (ctx->clock_phase_24 % PTRC_GFX_JUNCTIONS) + 1U;
    return PTRC_GFX_OK;
}

int ptrc_gfx_advance_observer_epoch(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) {
        return PTRC_GFX_ERR;
    }
    for (uint32_t t = 0U; t < PTRC_GFX_TAKT_137; t++) {
        ptrc_gfx_step_takt(ctx);
    }
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

    /* 1. Clear background to deep Z \ {0} cosmic navy (1, 2, 6 — zero 0x00 bytes) */
    size_t total_pixels = (size_t)width * (size_t)height;
    for (size_t p = 0U; p < total_pixels; p++) {
        size_t idx = p * 3U;
        *(rgb_out + idx + 0U) = 1U;
        *(rgb_out + idx + 1U) = 2U;
        *(rgb_out + idx + 2U) = 6U;
    }

    uint32_t phase_idx = (ctx->clock_phase_24 - 1U) % PTRC_GFX_JUNCTIONS;
    int32_t rot_u = *(PTRC_CLOCK24_U + phase_idx);
    int32_t rot_v = *(PTRC_CLOCK24_V + phase_idx);
    uint32_t hit_counter = 1U;

    /* 2. Plot all 60,000 free information agents (color-coded by velocity & 256-state register) */
    for (uint32_t i = 0U; i < PTRC_GFX_AGENT_COUNT; i++) {
        int32_t ax = *(ctx->agent_x + i);
        int32_t ay = *(ctx->agent_y + i);
        if (ax < 1 || ax > VIRT_W || ay < 1 || ay > VIRT_H) {
            continue;
        }
        uint32_t px = (uint32_t)(((int64_t)(ax - 1) * (int64_t)width) >> 14);
        uint32_t py = (uint32_t)(((int64_t)(ay - 1) * (int64_t)height) / (int64_t)VIRT_H);
        if (px >= width) px = width - 1U;
        if (py >= height) py = height - 1U;

        uint8_t st = *(ctx->agent_state + i);
        int32_t vy_abs = ptrc_gfx_abs32(*(ctx->agent_vy + i));

        uint8_t r_val, g_val, b_val;
        if (vy_abs > 10) {
            /* High-deflection vortex wake agents -> bright violet/magenta */
            r_val = (uint8_t)(185U + (st & 0x3FU));
            g_val = 58U;
            b_val = (uint8_t)(210U + (st & 0x2AU));
        } else if ((st & 1U) == 0U) {
            /* Laminar cyan resonance agents */
            r_val = 28U;
            g_val = (uint8_t)(175U + (st & 0x4FU));
            b_val = (uint8_t)(215U + (st & 0x27U));
        } else {
            /* Deep azure-teal agents */
            r_val = 42U;
            g_val = (uint8_t)(120U + (st & 0x5FU));
            b_val = (uint8_t)(195U + (st & 0x3BU));
        }

        size_t pix = ((size_t)py * (size_t)width + (size_t)px) * 3U;
        *(rgb_out + pix + 0U) = (r_val == 0U) ? 1U : r_val;
        *(rgb_out + pix + 1U) = (g_val == 0U) ? 1U : g_val;
        *(rgb_out + pix + 2U) = (b_val == 0U) ? 1U : b_val;
        hit_counter++;
    }

    /* 3. Render the 3D rotating 1+12 Golden Pyramid in the front third (~1/5 screen width) */
    int32_t pyr_cx_px = (int32_t)(((int64_t)ctx->pyramid_cx * (int64_t)width) >> 14);
    int32_t pyr_cy_px = (int32_t)(((int64_t)ctx->pyramid_cy * (int64_t)height) / (int64_t)VIRT_H);
    int32_t pyr_half_w = (int32_t)(width / 10U); /* Total width = width / 5 */
    if (pyr_half_w < 8) pyr_half_w = 8;

    int32_t y_min = pyr_cy_px - pyr_half_w;
    int32_t y_max = pyr_cy_px + pyr_half_w;
    int32_t x_min = pyr_cx_px - pyr_half_w;
    int32_t x_max = pyr_cx_px + pyr_half_w;
    if (y_min < 0) y_min = 0;
    if (y_max >= (int32_t)height) y_max = (int32_t)height - 1;
    if (x_min < 0) x_min = 0;
    if (x_max >= (int32_t)width) x_max = (int32_t)width - 1;

    for (int32_t py = y_min; py <= y_max; py++) {
        int32_t dy = py - pyr_cy_px;
        size_t row_off = (size_t)py * (size_t)width * 3U;

        for (int32_t px = x_min; px <= x_max; px++) {
            int32_t dx = px - pyr_cx_px;

            /* Rotate local coordinates via 24-Clock Discrete Quadrance (u^2 + v^2 = 1000^2) */
            int32_t rx = (dx * rot_u - dy * rot_v) >> 10;
            int32_t ry = (dx * rot_v + dy * rot_u) >> 10;

            /* Octahedral / 4-sided pyramid profile */
            int32_t dist = ptrc_gfx_abs32(rx) + ptrc_gfx_abs32(ry);
            if (dist <= pyr_half_w) {
                /* 144-facet crystalline facet shading (bright gold + facet lattice lines) */
                uint32_t facet_id = (uint32_t)(ptrc_gfx_abs32(rx * 3 + ry * 5) % PTRC_GFX_FACETS);
                int32_t fval = *(ctx->sponge + facet_id);
                int32_t facet_border = ((ptrc_gfx_abs32(rx) % 9) == 0 || (ptrc_gfx_abs32(ry) % 9) == 0) ? 1 : 0;

                /* Directional illumination from upper-left facet normal */
                int32_t shade = 215 - ((rx + ry) * 65) / pyr_half_w + (fval & 15);
                if (facet_border) {
                    shade += 32;
                }
                if (shade > 255) shade = 255;
                if (shade < 85) shade = 85;

                uint8_t gr = (uint8_t)shade;
                uint8_t gg = (uint8_t)((shade * 198) >> 8);
                uint8_t gb = (uint8_t)((shade * 54) >> 8);
                if (gb == 0U) gb = 1U;

                size_t pix = row_off + (size_t)px * 3U;
                *(rgb_out + pix + 0U) = gr;
                *(rgb_out + pix + 1U) = gg;
                *(rgb_out + pix + 2U) = gb;
                hit_counter++;
            }
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
