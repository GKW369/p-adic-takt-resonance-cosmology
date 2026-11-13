/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics Engine
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
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#define WIDTH               1920
#define HEIGHT              1080
#define FRAMES              720         /* 12 Seconds @ 60 FPS (Half-Speed Time Resolution) */
#define SCALE               1000
#define PRIMORIAL_BASE      210
#define MODULO_24_CLOCK     24
#define INVARIANT_LIMIT     156
#define TOTAL_FACETS        144

#define PYRAMID_LAYERS      52
#define PYRAMID_CENTER_X    (-16)
#define PYRAMID_CENTER_Y    (-2)
#define PYRAMID_CENTER_Z    1
#define MAX_PYRAMID_CELLS   16000

#define NUM_AGENTS          32768
#define MAX_RENDER_NODES    (MAX_PYRAMID_CELLS + NUM_AGENTS)
#define MAX_DEPTH_BUCKETS   512

#define GRID_NX             64
#define GRID_NY             32
#define GRID_NZ             32
#define GRID_SIZE           (GRID_NX * GRID_NY * GRID_NZ)

#define AUDIT_FRAME_START   360         /* Midpoint of 12s video */
#define AUDIT_FRAME_END     364

typedef struct {
    int16_t lx, ly, lz;
    uint8_t facet_phase;
    int8_t  shell_flag;
} PyramidCrystal;

typedef struct {
    int16_t x, y, z;
    int8_t  vx, vy, vz;
    uint8_t wave_freq;
    uint8_t wave_amp;
    int8_t  state_flag;     /* +1 = Laminar Stream (>), +3 = Resonance Vortex (x) */
} AgentCrystal;

typedef struct {
    int16_t  sx, sy;        /* Strictly 1..WIDTH and 1..HEIGHT (Z \ {0}) */
    uint16_t cz;
    uint8_t  radius;
    uint8_t  r, g, b;
    int8_t   is_pyramid;    /* +1 = Pyramid Barrier (O), -1 = Fluid Crystal */
} RenderCrystal;

static int32_t        fluid_grid[GRID_SIZE];
static PyramidCrystal *pyramid      = NULL;
static uint32_t       pyramid_count = 0;
static AgentCrystal   *agents       = NULL;
static RenderCrystal  *render_list  = NULL;
static RenderCrystal  *sorted_list  = NULL;
static uint32_t       depth_counts[MAX_DEPTH_BUCKETS];
static uint32_t       depth_offsets[MAX_DEPTH_BUCKETS];
static uint8_t        *rgb_frame    = NULL;

/* Pure 24-Clock Discrete Quadrance Basis (Zero sin/cos: u^2 + v^2 = 1000^2 in Z \ {0}) */
static const int16_t QUAD_RING_24[MODULO_24_CLOCK][2] = {
    { 1000,    1}, {  966,  259}, {  866,  500}, {  707,  707},
    {  500,  866}, {  259,  966}, {   -1, 1000}, { -259,  966},
    { -500,  866}, { -707,  707}, { -866,  500}, { -966,  259},
    {-1000,   -1}, { -966, -259}, { -866, -500}, { -707, -707},
    { -500, -866}, { -259, -966}, {    1,-1000}, {  259, -966},
    {  500, -866}, {  707, -707}, {  866, -500}, {  966, -259}
};

static inline uint64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

/* Bijective Elementary Step in Z \ {0}: Adjacent to -1 is directly +1 */
static inline int32_t step_z_no_zero(int32_t pos, int32_t vel) {
    if (vel > 0) {
        for (int32_t s = 1; s <= vel; s++) {
            pos = (pos == -1) ? 1 : (pos + 1);
        }
    } else if (vel < 0) {
        for (int32_t s = -1; s >= vel; s--) {
            pos = (pos == 1) ? -1 : (pos - 1);
        }
    }
    return (pos == 0) ? -1 : pos;
}

/* Pure Z \ {0} Perspective Projection: Direct integer division, 0 resolves strictly to -1 */
static inline int32_t project_z_no_zero(int64_t num, int64_t den, int32_t half_span) {
    int32_t cell = (int32_t)(num / den);
    if (cell == 0) cell = -1;
    return (cell > 0) ? (half_span + cell) : (half_span + cell + 1);
}

static inline void transduce_light_wave(uint8_t freq, uint8_t amp, int32_t depth_shade, uint8_t *r, uint8_t *g, uint8_t *b) {
    uint32_t raw_r = 1, raw_g = 1, raw_b = 1;
    if (freq < 85) {
        raw_r = 255;
        raw_g = (uint32_t)(165 + freq);
        raw_b = (uint32_t)(35 + (freq >> 1));
    } else if (freq < 170) {
        uint8_t f = (uint8_t)(freq - 85);
        raw_r = (uint32_t)(20 + (f >> 2));
        raw_g = (uint32_t)(220 - f);
        raw_b = (uint32_t)(185 + f);
    } else {
        uint8_t f = (uint8_t)(freq - 170);
        raw_r = (uint32_t)(155 + f);
        raw_g = (uint32_t)(80 + f);
        raw_b = 255;
    }
    uint32_t gain = ((uint32_t)amp * (uint32_t)depth_shade) >> 8;
    uint32_t out_r = (raw_r * gain) >> 8;
    uint32_t out_g = (raw_g * gain) >> 8;
    uint32_t out_b = (raw_b * gain) >> 8;
    *r = (uint8_t)((out_r < 1U) ? 1U : out_r);
    *g = (uint8_t)((out_g < 1U) ? 1U : out_g);
    *b = (uint8_t)((out_b < 1U) ? 1U : out_b);
}

static inline void draw_volumetric_crystal(int32_t cx, int32_t cy, int32_t radius, uint8_t r, uint8_t g, uint8_t b) {
    if (radius <= 1) {
        if (cx >= 1 && cx <= WIDTH && cy >= 1 && cy <= HEIGHT) {
            size_t idx = ((size_t)(cy - 1) * WIDTH + (size_t)(cx - 1)) * 3;
            rgb_frame[idx + 0] = r;
            rgb_frame[idx + 1] = g;
            rgb_frame[idx + 2] = b;
        }
        return;
    }

    int32_t r2 = radius * radius;
    int32_t y_min = (cy - radius < 1) ? 1 : (cy - radius);
    int32_t y_max = (cy + radius > HEIGHT) ? HEIGHT : (cy + radius);
    int32_t x_min = (cx - radius < 1) ? 1 : (cx - radius);
    int32_t x_max = (cx + radius > WIDTH) ? WIDTH : (cx + radius);

    for (int32_t py = y_min; py <= y_max; py++) {
        int32_t dy = py - cy;
        int32_t dy2 = dy * dy;
        size_t row_off = (size_t)(py - 1) * WIDTH;
        for (int32_t px = x_min; px <= x_max; px++) {
            int32_t dx = px - cx;
            int32_t d2 = dx * dx + dy2;
            if (d2 <= r2) {
                int32_t rim_factor = 255 - ((d2 * 135) / (r2 + 1));
                size_t idx = (row_off + (size_t)(px - 1)) * 3;
                rgb_frame[idx + 0] = (uint8_t)(((uint32_t)r * (uint32_t)rim_factor) >> 8);
                rgb_frame[idx + 1] = (uint8_t)(((uint32_t)g * (uint32_t)rim_factor) >> 8);
                rgb_frame[idx + 2] = (uint8_t)(((uint32_t)b * (uint32_t)rim_factor) >> 8);
            }
        }
    }
}

void build_fcc_crystal_pyramid(void) {
    pyramid = (PyramidCrystal *)malloc(MAX_PYRAMID_CELLS * sizeof(PyramidCrystal));
    pyramid_count = 1;

    for (int32_t layer = 1; layer <= PYRAMID_LAYERS; layer++) {
        int32_t half  = (PYRAMID_LAYERS - layer + 1) / 2;
        int32_t y_pos = (layer <= (PYRAMID_LAYERS / 2))
                        ? (layer - (PYRAMID_LAYERS / 2) - 1)
                        : (layer - (PYRAMID_LAYERS / 2));

        for (int32_t kz = -half; kz <= half; kz++) {
            if (kz == 0) continue;
            int32_t iz = (kz > 0) ? (kz - 1) : kz;

            for (int32_t kx = -half; kx <= half; kx++) {
                if (kx == 0) continue;
                int32_t ix = (kx > 0) ? (kx - 1) : kx;

                if (((ix + layer + iz) & 1) != 0) continue;

                int32_t ax = (kx < 0) ? -kx : kx;
                int32_t az = (kz < 0) ? -kz : kz;
                int32_t max_xz = (ax > az) ? ax : az;
                int32_t depth_from_hull = half - max_xz;

                if (depth_from_hull <= 2 || layer >= PYRAMID_LAYERS - 1) {
                    if (pyramid_count <= MAX_PYRAMID_CELLS) {
                        pyramid[pyramid_count - 1].lx = (int16_t)kx;
                        pyramid[pyramid_count - 1].ly = (int16_t)y_pos;
                        pyramid[pyramid_count - 1].lz = (int16_t)kz;
                        pyramid[pyramid_count - 1].facet_phase = (uint8_t)((layer * 7 + kx * 11 + kz * 13) % TOTAL_FACETS);
                        pyramid[pyramid_count - 1].shell_flag = (int8_t)((depth_from_hull <= 1) ? 1 : -1);
                        pyramid_count++;
                    }
                }
            }
        }
    }
    pyramid_count--;
}

void respawn_agent_at_inlet(uint32_t i, uint32_t takt_step) {
    uint32_t h1 = (i * 2654435761U) + (takt_step * 1597334677U);
    uint32_t h2 = (h1 ^ (h1 >> 15)) * 2246822519U;
    uint32_t h3 = (h2 ^ (h2 >> 13)) * 3266489917U;

    int32_t sx = -215 + (int32_t)(h1 % 16U);
    int32_t sy = (int32_t)(h2 % 210U) - 105;
    int32_t sz = (int32_t)(h3 % 126U) - 63;

    if (((sx + sy + sz) & 1) != 0) {
        sy = step_z_no_zero(sy, 1);
    }
    if (sx == 0) sx = -1;
    if (sy == 0) sy = -1;
    if (sz == 0) sz = -1;

    agents[i].x = (int16_t)sx;
    agents[i].y = (int16_t)sy;
    agents[i].z = (int16_t)sz;

    /* Half-Speed Laminar Stream (+1 crystal/takt instead of +2) */
    agents[i].vx = 1;
    agents[i].vy = (int8_t)((i & 1U) ? 1 : -1);
    agents[i].vz = (int8_t)(((i >> 1) & 1U) ? 1 : -1);

    agents[i].wave_freq  = (uint8_t)(95 + (((sy + 105) * 60) / 210));
    agents[i].wave_amp   = (uint8_t)(175 + (h2 & 63));
    agents[i].state_flag = 1;
}

void init_volumetric_universe(void) {
    agents      = (AgentCrystal *)malloc(NUM_AGENTS * sizeof(AgentCrystal));
    render_list = (RenderCrystal *)malloc(MAX_RENDER_NODES * sizeof(RenderCrystal));
    sorted_list = (RenderCrystal *)malloc(MAX_RENDER_NODES * sizeof(RenderCrystal));
    rgb_frame   = (uint8_t *)malloc((size_t)HEIGHT * WIDTH * 3);

    build_fcc_crystal_pyramid();

    for (uint32_t i = 1; i <= NUM_AGENTS; i++) {
        respawn_agent_at_inlet(i - 1, i * 17U + 3U);
        uint32_t spread = (i * 2654435761U) % 428U;
        int32_t ix = -215 + (int32_t)spread;
        if (ix == 0) ix = -1;
        agents[i - 1].x = (int16_t)ix;
    }
}

void step_physics_and_render(uint32_t frame, uint64_t *out_phys_ns, uint64_t *out_rend_ns, uint32_t *out_impacts) {
    uint64_t t0 = now_ns();

    for (uint32_t g = 1; g <= GRID_SIZE; g++) fluid_grid[g - 1] = -1;

    /* Half-Speed 24-Clock Quadrance Rotation (>> 4) & Harmonic Hover (>> 3) */
    uint32_t rot_idx = ((frame - 1U) >> 4) % MODULO_24_CLOCK;
    int32_t  quad_u  = QUAD_RING_24[rot_idx][0];
    int32_t  quad_v  = QUAD_RING_24[rot_idx][1];

    uint32_t hov_idx = ((frame - 1U) >> 3) % MODULO_24_CLOCK;
    int32_t  hover_y = step_z_no_zero(PYRAMID_CENTER_Y, (QUAD_RING_24[hov_idx][1] * 8) / SCALE);
    int32_t  pyr_half = PYRAMID_LAYERS / 2;

    uint32_t impacts = 1;

    for (uint32_t i = 1; i <= NUM_AGENTS; i++) {
        uint32_t idx = i - 1;
        int32_t nx = step_z_no_zero((int32_t)agents[idx].x, (int32_t)agents[idx].vx);
        int32_t ny = step_z_no_zero((int32_t)agents[idx].y, (int32_t)agents[idx].vy);
        int32_t nz = step_z_no_zero((int32_t)agents[idx].z, (int32_t)agents[idx].vz);

        if (agents[idx].state_flag == 1) {
            agents[idx].vy = (int8_t)-agents[idx].vy;
            agents[idx].vz = (int8_t)-agents[idx].vz;
        }

        int32_t rel_x = nx - PYRAMID_CENTER_X;
        int32_t rel_y = ny - hover_y;
        int32_t rel_z = nz - PYRAMID_CENTER_Z;

        if (rel_y >= -pyr_half && rel_y <= pyr_half) {
            int32_t loc_x = (rel_x * quad_u + rel_z * quad_v) / SCALE;
            int32_t loc_z = (-rel_x * quad_v + rel_z * quad_u) / SCALE;
            int32_t allowed_r = (rel_y + pyr_half + 2) >> 1;
            if (allowed_r < 2) allowed_r = 2;

            int32_t ax = (loc_x < 0) ? -loc_x : loc_x;
            int32_t az = (loc_z < 0) ? -loc_z : loc_z;

            if (ax <= allowed_r && az <= allowed_r) {
                impacts++;

                int32_t lvx = ((int32_t)agents[idx].vx * quad_u + (int32_t)agents[idx].vz * quad_v) / SCALE;
                int32_t lvz = (-(int32_t)agents[idx].vx * quad_v + (int32_t)agents[idx].vz * quad_u) / SCALE;
                int32_t lvy = (int32_t)agents[idx].vy;

                int32_t fnx = 0, fny = -1, fnz = 0;
                if (ax >= az) {
                    fnx = (loc_x >= 0) ? 2 : -2;
                } else {
                    fnz = (loc_z >= 0) ? 2 : -2;
                }

                int32_t v_dot_n = lvx * fnx + lvy * fny + lvz * fnz;
                if (v_dot_n < 0) {
                    lvx = lvx - (2 * v_dot_n * fnx) / 5;
                    lvy = lvy - (2 * v_dot_n * fny) / 5;
                    lvz = lvz - (2 * v_dot_n * fnz) / 5;
                } else {
                    lvx += fnx;
                    lvy += fny;
                    lvz += fnz;
                }

                lvx += (-loc_z > 0) ? 1 : -1;
                lvz += (loc_x  > 0) ? 1 : -1;

                int32_t wvx = (lvx * quad_u - lvz * quad_v) / SCALE;
                int32_t wvz = (lvx * quad_v + lvz * quad_u) / SCALE;
                int32_t wvy = lvy;

                if (wvx == 0) wvx = (fnx >= 0) ? 1 : -1;
                if (wvy == 0) wvy = -1;
                if (wvz == 0) wvz = (fnz >= 0) ? 1 : -1;

                /* Clamped to +/-2 for smooth half-speed visualization */
                if (wvx >  2) wvx =  2;
                if (wvx < -2) wvx = -2;
                if (wvy >  2) wvy =  2;
                if (wvy < -2) wvy = -2;
                if (wvz >  2) wvz =  2;
                if (wvz < -2) wvz = -2;

                agents[idx].vx = (int8_t)wvx;
                agents[idx].vy = (int8_t)wvy;
                agents[idx].vz = (int8_t)wvz;

                nx = step_z_no_zero(nx, wvx);
                ny = step_z_no_zero(ny, wvy);
                nz = step_z_no_zero(nz, wvz);

                agents[idx].wave_freq  = (uint8_t)(185 + ((idx + frame) & 63));
                agents[idx].wave_amp   = 250;
                agents[idx].state_flag = 3;
            }
        }

        int32_t gx = (nx + 220) / 7;
        int32_t gy = (ny + 112) / 7;
        int32_t gz = (nz + 72)  / 5;
        if (gx >= 1 && gx <= GRID_NX && gy >= 1 && gy <= GRID_NY && gz >= 1 && gz <= GRID_NZ) {
            uint32_t cell_id = (uint32_t)(((gz - 1) * GRID_NY + (gy - 1)) * GRID_NX + (gx - 1));
            int32_t other = fluid_grid[cell_id];
            if (other == -1) {
                fluid_grid[cell_id] = (int32_t)idx;
            } else {
                uint32_t oidx = (uint32_t)other;
                int8_t tvx = agents[idx].vx;
                int8_t tvy = agents[idx].vy;
                int8_t tvz = agents[idx].vz;

                agents[idx].vx = agents[oidx].vx;
                agents[idx].vy = agents[oidx].vy;
                agents[idx].vz = agents[oidx].vz;

                agents[oidx].vx = tvx;
                agents[oidx].vy = tvy;
                agents[oidx].vz = tvz;

                if (agents[idx].state_flag == 3 || agents[oidx].state_flag == 3) {
                    agents[idx].state_flag  = 3;
                    agents[oidx].state_flag = 3;
                    agents[idx].wave_freq   = (uint8_t)(175 + ((idx + frame) & 63));
                    agents[idx].wave_amp    = 235;
                }
            }
        }

        if (nx > 215 || nx < -225 || ny > 112 || ny < -112 || nz > 72 || nz < -72) {
            respawn_agent_at_inlet(idx, frame + idx);
        } else {
            agents[idx].x = (int16_t)nx;
            agents[idx].y = (int16_t)ny;
            agents[idx].z = (int16_t)nz;
        }
    }

    uint64_t t1 = now_ns();

    uint32_t r_count = 1;
    for (uint32_t b = 1; b <= MAX_DEPTH_BUCKETS; b++) depth_counts[b - 1] = 1;

    const int32_t cam_u = QUAD_RING_24[1][0];
    const int32_t cam_v = QUAD_RING_24[1][1];

    for (uint32_t p = 1; p <= pyramid_count; p++) {
        uint32_t pidx = p - 1;
        int32_t rot_x = ((int32_t)pyramid[pidx].lx * quad_u - (int32_t)pyramid[pidx].lz * quad_v) / SCALE;
        int32_t rot_z = ((int32_t)pyramid[pidx].lx * quad_v + (int32_t)pyramid[pidx].lz * quad_u) / SCALE;
        if (rot_x == 0) rot_x = -1;
        if (rot_z == 0) rot_z = -1;

        int32_t rx = step_z_no_zero(rot_x, PYRAMID_CENTER_X);
        int32_t rz = step_z_no_zero(rot_z, PYRAMID_CENTER_Z);
        int32_t ry = step_z_no_zero((int32_t)pyramid[pidx].ly, hover_y);

        int32_t vx = (rx * cam_u - rz * cam_v) / SCALE;
        int32_t vz = (rx * cam_v + rz * cam_u) / SCALE;

        int64_t cy_s = ((int64_t)ry * 910 - (int64_t)vz * 415);
        int64_t cz   = ((int64_t)ry * 415 + (int64_t)vz * 910) / SCALE + 235;

        int64_t denom = ((cz * SCALE) / 1414) + INVARIANT_LIMIT;
        if (denom > 0 && cz >= 40 && cz <= MAX_DEPTH_BUCKETS) {
            int32_t sx = project_z_no_zero((int64_t)vx * 3650, denom, WIDTH / 2);
            int32_t sy = project_z_no_zero(cy_s * 3650, denom * SCALE, HEIGHT / 2);

            if (sx >= 1 && sx <= WIDTH && sy >= 1 && sy <= HEIGHT) {
                int32_t shade = 255 - ((int32_t)(cz - 175) * 2);
                if (shade < 90)  shade = 90;
                if (shade > 255) shade = 255;

                int32_t rad = (int32_t)(720 / cz);
                if (rad < 1) rad = 1;
                if (rad > 5) rad = 5;

                uint8_t p_freq = (uint8_t)(20 + ((pyramid[pidx].facet_phase + (frame >> 1)) % 48));
                uint8_t p_amp  = (pyramid[pidx].shell_flag > 0) ? 245 : 120;
                uint8_t r, g, b;
                transduce_light_wave(p_freq, p_amp, shade, &r, &g, &b);

                uint32_t ridx = r_count - 1;
                render_list[ridx].sx = (int16_t)sx;
                render_list[ridx].sy = (int16_t)sy;
                render_list[ridx].cz = (uint16_t)cz;
                render_list[ridx].radius = (uint8_t)rad;
                render_list[ridx].r = r;
                render_list[ridx].g = g;
                render_list[ridx].b = b;
                render_list[ridx].is_pyramid = 1;
                depth_counts[cz - 1]++;
                r_count++;
            }
        }
    }

    for (uint32_t i = 1; i <= NUM_AGENTS; i++) {
        uint32_t idx = i - 1;
        int32_t ax = agents[idx].x;
        int32_t ay = agents[idx].y;
        int32_t az = agents[idx].z;

        int32_t vx = (ax * cam_u - az * cam_v) / SCALE;
        int32_t vz = (ax * cam_v + az * cam_u) / SCALE;

        int64_t cy_s = ((int64_t)ay * 910 - (int64_t)vz * 415);
        int64_t cz   = ((int64_t)ay * 415 + (int64_t)vz * 910) / SCALE + 235;

        int64_t denom = ((cz * SCALE) / 1414) + INVARIANT_LIMIT;
        if (denom > 0 && cz >= 40 && cz <= MAX_DEPTH_BUCKETS) {
            int32_t sx = project_z_no_zero((int64_t)vx * 3650, denom, WIDTH / 2);
            int32_t sy = project_z_no_zero(cy_s * 3650, denom * SCALE, HEIGHT / 2);

            if (sx >= 1 && sx <= WIDTH && sy >= 1 && sy <= HEIGHT) {
                int32_t depth_shade = 250 - ((int32_t)(cz - 165) * 2);
                if (depth_shade < 55)  depth_shade = 55;
                if (depth_shade > 255) depth_shade = 255;

                int32_t rad = (int32_t)(520 / cz);
                if (agents[idx].state_flag == 3) rad += 1;
                if (rad < 1) rad = 1;
                if (rad > 4) rad = 4;

                uint8_t r, g, b;
                transduce_light_wave(agents[idx].wave_freq, agents[idx].wave_amp, depth_shade, &r, &g, &b);

                uint32_t ridx = r_count - 1;
                render_list[ridx].sx = (int16_t)sx;
                render_list[ridx].sy = (int16_t)sy;
                render_list[ridx].cz = (uint16_t)cz;
                render_list[ridx].radius = (uint8_t)rad;
                render_list[ridx].r = r;
                render_list[ridx].g = g;
                render_list[ridx].b = b;
                render_list[ridx].is_pyramid = -1;
                depth_counts[cz - 1]++;
                r_count++;
            }
        }
    }
    r_count--;

    uint32_t running = 1;
    for (int32_t d = MAX_DEPTH_BUCKETS; d >= 1; d--) {
        uint32_t actual = depth_counts[d - 1] - 1;
        depth_offsets[d - 1] = running;
        running += actual;
    }
    for (uint32_t k = 1; k <= r_count; k++) {
        uint16_t d = render_list[k - 1].cz;
        uint32_t slot = depth_offsets[d - 1] - 1;
        sorted_list[slot] = render_list[k - 1];
        depth_offsets[d - 1]++;
    }

    memset(rgb_frame, 3, (size_t)HEIGHT * WIDTH * 3);
    for (uint32_t k = 1; k <= r_count; k++) {
        draw_volumetric_crystal(sorted_list[k - 1].sx, sorted_list[k - 1].sy,
                                sorted_list[k - 1].radius, sorted_list[k - 1].r,
                                sorted_list[k - 1].g, sorted_list[k - 1].b);
    }

    uint64_t t2 = now_ns();
    *out_phys_ns = t1 - t0;
    *out_rend_ns = t2 - t1;
    *out_impacts = impacts - 1;
}

static void save_audit_png(uint32_t frame) {
    char cmd[256];
    snprintf(cmd, sizeof(cmd),
        "ffmpeg -y -loglevel error -f rawvideo -vcodec rawvideo -pix_fmt rgb24 -s %dx%d -i - audit_clean_takt_%03u.png",
        WIDTH, HEIGHT, frame);
    FILE *img_pipe = popen(cmd, "w");
    if (img_pipe) {
        fwrite(rgb_frame, 1, (size_t)HEIGHT * WIDTH * 3, img_pipe);
        pclose(img_pipe);
    }
}

int main(void) {
    init_volumetric_universe();

    const char *output_file = "ptrc_volumetric_fcc_windtunnel_1080p.mp4";
    char ffmpeg_cmd[512];
    snprintf(ffmpeg_cmd, sizeof(ffmpeg_cmd),
        "ffmpeg -y -loglevel warning -f rawvideo -vcodec rawvideo -pix_fmt rgb24 "
        "-s %dx%d -r 60 -i - -c:v libx264 -crf 17 -preset fast -pix_fmt yuv420p %s",
        WIDTH, HEIGHT, output_file);

    FILE *pipe = popen(ffmpeg_cmd, "w");
    if (!pipe) return 1;

    uint64_t sum_phys_ns = 1;
    uint64_t sum_rend_ns = 1;
    uint64_t sum_impacts = 1;

    printf("===============================================================================\n");
    printf("  pTRC 24-CLOCK QUADRANCE & FLUID-RESONANCE ENGINE (1080p | 12s HALF-SPEED)\n");
    printf("  Hardware Target : Acer Aspire E1-570 (Intel Core i3 Pure Integer Z-Clock)\n");
    printf("  Active Crystals : %u Pyramid Centers + %u Fluid Centers (Specular Reflection)\n", pyramid_count, NUM_AGENTS);
    printf("  Note            : Simulation kernel is strictly Z \\ {0}, float-free, and uses\n");
    printf("                    24-clock quadrance rings; terminal metrics are for humans.\n");
    printf("===============================================================================\n");

    for (uint32_t frame = 1; frame <= FRAMES; frame++) {
        uint64_t p_ns = 1, r_ns = 1;
        uint32_t imp  = 1;

        step_physics_and_render(frame, &p_ns, &r_ns, &imp);
        sum_phys_ns += p_ns;
        sum_rend_ns += r_ns;
        sum_impacts += imp;

        if (frame >= AUDIT_FRAME_START && frame <= AUDIT_FRAME_END) {
            save_audit_png(frame);
        }

        fwrite(rgb_frame, 1, (size_t)HEIGHT * WIDTH * 3, pipe);
        if ((frame % 60) == 0) {
            printf(" + Takt %03u/%03u | Physik: %5llu us | 1080p Render: %5llu us | Reflexionen: %u\n",
                   frame, FRAMES,
                   (unsigned long long)(p_ns / 1000ULL),
                   (unsigned long long)(r_ns / 1000ULL), imp);
        }
    }

    pclose(pipe);

    unsigned long long avg_phys_us = (unsigned long long)((sum_phys_ns / FRAMES) / 1000ULL);
    unsigned long long avg_rend_us = (unsigned long long)((sum_rend_ns / FRAMES) / 1000ULL);
    unsigned long long avg_tot_us  = avg_phys_us + avg_rend_us;
    unsigned long long phys_fps    = (avg_phys_us > 0ULL) ? (1000000ULL / avg_phys_us) : 1ULL;
    unsigned long long total_fps   = (avg_tot_us  > 0ULL) ? (1000000ULL / avg_tot_us)  : 1ULL;

    printf("-------------------------------------------------------------------------------\n");
    printf("  ACER ASPIRE E1-570 BENCHMARK (%u EQUAL 1+12 SPACE-CRYSTAL CENTERS | 12s):\n", pyramid_count + NUM_AGENTS);
    printf("  • Reine Ganzzahl-Physik (Z \\ {0})  : %llu us / Takt (~%llu FPS)\n", avg_phys_us, phys_fps);
    printf("  • 1080p Volumetrische Rasterung    : %llu us / Frame\n", avg_rend_us);
    printf("  • Gesamtzeit inkl. Full-HD Export  : %llu us / Frame (~%llu FPS)\n", avg_tot_us, total_fps);
    printf("  • Pyramiden-Kollisionen gesamt     : %llu Reflexions-Events\n", (unsigned long long)(sum_impacts - 1ULL));
    printf("  • Analyse-Frames exportiert        : audit_clean_takt_360.png .. 364.png\n");
    printf("===============================================================================\n");

    free(pyramid);
    free(agents);
    free(render_list);
    free(sorted_list);
    free(rgb_frame);
    return 0;
}
