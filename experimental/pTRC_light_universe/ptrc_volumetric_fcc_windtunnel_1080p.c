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
#define FRAMES              720         /* 12 Seconds @ 60 FPS */
#define SCALE               1000
#define PRIMORIAL_BASE      210
#define MODULO_24_CLOCK     24
#define FINE_QUAD_STEPS     192         /* 8 x 24 = 192 smooth 1-takt quadrance steps */
#define INVARIANT_LIMIT     156
#define TOTAL_FACETS        144

#define PYRAMID_LAYERS      52
#define PYRAMID_CENTER_X    (-16)
#define PYRAMID_CENTER_Y    (-2)
#define PYRAMID_CENTER_Z    24
#define MAX_PYRAMID_CELLS   16000

#define NUM_AGENTS          49152
#define MAX_RENDER_NODES    (MAX_PYRAMID_CELLS + NUM_AGENTS)
#define MAX_DEPTH_BUCKETS   512

#define CONTACT_TABLE_SIZE  131072
#define CONTACT_TABLE_MASK  (CONTACT_TABLE_SIZE - 1)

#define AUDIT_FRAME_START   360
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
    int8_t  state_flag;     /* +1 = Undisturbed Stream, +3 = Post-Collision Wave */
} AgentCrystal;

typedef struct {
    int16_t  sx, sy;        /* Strictly 1..WIDTH and 1..HEIGHT (Z \ {0}) */
    uint16_t cz;
    uint8_t  radius;
    uint8_t  r, g, b;
    int8_t   is_pyramid;    /* +1 = Motorized Pyramid Barrier, -1 = Fluid Crystal */
} RenderCrystal;

static int32_t        occ_slot[CONTACT_TABLE_SIZE];
static int32_t        claim_slot[CONTACT_TABLE_SIZE];
static PyramidCrystal *pyramid      = NULL;
static uint32_t       pyramid_count = 0;
static AgentCrystal   *agents       = NULL;
static RenderCrystal  *render_list  = NULL;
static RenderCrystal  *sorted_list  = NULL;
static uint32_t       depth_counts[MAX_DEPTH_BUCKETS];
static uint32_t       depth_offsets[MAX_DEPTH_BUCKETS];
static uint8_t        *rgb_frame    = NULL;

/* Pure 192-Step (8 x 24) Discrete Quadrance Ring: u^2 + v^2 = 1000^2 in Z \ {0} */
static const int16_t QUAD_RING_192[FINE_QUAD_STEPS][2] = {
    { 1000,    1}, {  999,   33}, {  998,   65}, {  995,   98}, {  991,  131}, {  987,  163},
    {  981,  195}, {  974,  227}, {  966,  259}, {  957,  290}, {  947,  321}, {  936,  352},
    {  924,  383}, {  911,  413}, {  897,  442}, {  882,  471}, {  866,  500}, {  849,  528},
    {  831,  556}, {  813,  583}, {  793,  609}, {  773,  634}, {  752,  659}, {  730,  683},
    {  707,  707}, {  683,  730}, {  659,  752}, {  634,  773}, {  609,  793}, {  583,  813},
    {  556,  831}, {  528,  849}, {  500,  866}, {  471,  882}, {  442,  897}, {  413,  911},
    {  383,  924}, {  352,  936}, {  321,  947}, {  290,  957}, {  259,  966}, {  227,  974},
    {  195,  981}, {  163,  987}, {  131,  991}, {   98,  995}, {   65,  998}, {   33,  999},
    {   -1, 1000}, {  -33,  999}, {  -65,  998}, {  -98,  995}, { -131,  991}, { -163,  987},
    { -195,  981}, { -227,  974}, { -259,  966}, { -290,  957}, { -321,  947}, { -352,  936},
    { -383,  924}, { -413,  911}, { -442,  897}, { -471,  882}, { -500,  866}, { -528,  849},
    { -556,  831}, { -583,  813}, { -609,  793}, { -634,  773}, { -659,  752}, { -683,  730},
    { -707,  707}, { -730,  683}, { -752,  659}, { -773,  634}, { -793,  609}, { -813,  583},
    { -831,  556}, { -849,  528}, { -866,  500}, { -882,  471}, { -897,  442}, { -911,  413},
    { -924,  383}, { -936,  352}, { -947,  321}, { -957,  290}, { -966,  259}, { -974,  227},
    { -981,  195}, { -987,  163}, { -991,  131}, { -995,   98}, { -998,   65}, { -999,   33},
    {-1000,   -1}, { -999,  -33}, { -998,  -65}, { -995,  -98}, { -991, -131}, { -987, -163},
    { -981, -195}, { -974, -227}, { -966, -259}, { -957, -290}, { -947, -321}, { -936, -352},
    { -924, -383}, { -911, -413}, { -897, -442}, { -882, -471}, { -866, -500}, { -849, -528},
    { -831, -556}, { -813, -583}, { -793, -609}, { -773, -634}, { -752, -659}, { -730, -683},
    { -707, -707}, { -683, -730}, { -659, -752}, { -634, -773}, { -609, -793}, { -583, -813},
    { -556, -831}, { -528, -849}, { -500, -866}, { -471, -882}, { -442, -897}, { -413, -911},
    { -383, -924}, { -352, -936}, { -321, -947}, { -290, -957}, { -259, -966}, { -227, -974},
    { -195, -981}, { -163, -987}, { -131, -991}, {  -98, -995}, {  -65, -998}, {  -33, -999},
    {    1,-1000}, {   33, -999}, {   65, -998}, {   98, -995}, {  131, -991}, {  163, -987},
    {  195, -981}, {  227, -974}, {  259, -966}, {  290, -957}, {  321, -947}, {  352, -936},
    {  383, -924}, {  413, -911}, {  442, -897}, {  471, -882}, {  500, -866}, {  528, -849},
    {  556, -831}, {  583, -813}, {  609, -793}, {  634, -773}, {  659, -752}, {  683, -730},
    {  707, -707}, {  730, -683}, {  752, -659}, {  773, -634}, {  793, -609}, {  813, -583},
    {  831, -556}, {  849, -528}, {  866, -500}, {  882, -471}, {  897, -442}, {  911, -413},
    {  924, -383}, {  936, -352}, {  947, -321}, {  957, -290}, {  966, -259}, {  974, -227},
    {  981, -195}, {  987, -163}, {  991, -131}, {  995,  -98}, {  998,  -65}, {  999,  -33}
};

static inline uint64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static inline uint32_t crystal_hash(int32_t x, int32_t y, int32_t z) {
    uint32_t key = ((uint32_t)(uint16_t)x * 73856093U) ^
                   ((uint32_t)(uint16_t)y * 19349663U) ^
                   ((uint32_t)(uint16_t)z * 83492791U);
    return key & CONTACT_TABLE_MASK;
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

/* Sign-Preserving Z \ {0} Perspective Projection: Eliminates center-line double-binning */
static inline int32_t project_z_no_zero(int64_t num, int64_t den, int32_t half_span) {
    if (num > 0) {
        int32_t cell = (int32_t)(num / den) + 1;
        return half_span + cell;
    } else {
        int32_t cell = (int32_t)(num / den) - 1;
        return half_span + cell + 1;
    }
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

/* Dense 1+12 Upright Pyramid: Unit-step Z \ {0} coordinates without double-step gaps */
void build_fcc_crystal_pyramid(void) {
    pyramid = (PyramidCrystal *)malloc(MAX_PYRAMID_CELLS * sizeof(PyramidCrystal));
    pyramid_count = 1;

    for (int32_t layer = 1; layer <= PYRAMID_LAYERS; layer++) {
        int32_t half  = (layer + 1) / 2;
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
    int32_t sz = (int32_t)(h3 % 156U) - 78;

    if (((sx + sy + sz) & 1) != 0) {
        sy = step_z_no_zero(sy, 1);
    }
    if (sx == 0) sx = -1;
    if (sy == 0) sy = -1;
    if (sz == 0) sz = -1;

    agents[i].x = (int16_t)sx;
    agents[i].y = (int16_t)sy;
    agents[i].z = (int16_t)sz;

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

void update_agents(uint32_t takt_step) {
    memset(occ_slot, 0, sizeof(occ_slot));
    memset(claim_slot, 0, sizeof(claim_slot));

    for (uint32_t i = 0; i < NUM_AGENTS; i++) {
        AgentCrystal *ag = &agents[i];

        int32_t nx = step_z_no_zero(ag->x, ag->vx);
        int32_t ny = step_z_no_zero(ag->y, ag->vy);
        int32_t nz = step_z_no_zero(ag->z, ag->vz);

        /* Boundary collision check against pyramid or domain walls */
        int hit_barrier = 0;
        for (uint32_t p = 0; p < pyramid_count; p++) {
            int32_t px = PYRAMID_CENTER_X + pyramid[p].lx;
            int32_t py = PYRAMID_CENTER_Y + pyramid[p].ly;
            int32_t pz = PYRAMID_CENTER_Z + pyramid[p].lz;

            if (nx == px && ny == py && nz == pz) {
                hit_barrier = 1;
                break;
            }
        }

        if (nx > 220 || hit_barrier) {
            respawn_agent_at_inlet(i, takt_step);
        } else {
            ag->x = (int16_t)nx;
            ag->y = (int16_t)ny;
            ag->z = (int16_t)nz;

            if (hit_barrier) {
                ag->state_flag = 3;
                ag->vy = (int8_t)(-ag->vy);
                ag->vz = (int8_t)(-ag->vz);
            }
        }
    }
}

void render_frame(uint32_t takt_step) {
    memset(rgb_frame, 8, (size_t)HEIGHT * WIDTH * 3);
    memset(depth_counts, 0, sizeof(depth_counts));

    uint32_t r_count = 0;

    /* Add Pyramid */
    int q_idx = (takt_step % FINE_QUAD_STEPS);
    int16_t cos_q = QUAD_RING_192[q_idx][0];
    int16_t sin_q = QUAD_RING_192[q_idx][1];

    for (uint32_t p = 0; p < pyramid_count; p++) {
        int32_t lx = pyramid[p].lx;
        int32_t ly = pyramid[p].ly;
        int32_t lz = pyramid[p].lz;

        int32_t rx = (int32_t)(((int64_t)lx * cos_q - (int64_t)lz * sin_q) / SCALE);
        int32_t rz = (int32_t)(((int64_t)lx * sin_q + (int64_t)lz * cos_q) / SCALE);
        int32_t wx = PYRAMID_CENTER_X + rx;
        int32_t wy = PYRAMID_CENTER_Y + ly;
        int32_t wz = PYRAMID_CENTER_Z + rz;

        int32_t sx = project_z_no_zero((int64_t)wx * 480, (wz + 320), WIDTH / 2);
        int32_t sy = project_z_no_zero((int64_t)wy * 480, (wz + 320), HEIGHT / 2);

        if (sx >= 1 && sx <= WIDTH && sy >= 1 && sy <= HEIGHT) {
            uint16_t cz = (wz < 1) ? 1 : ((wz >= (int32_t)MAX_DEPTH_BUCKETS) ? (MAX_DEPTH_BUCKETS - 1) : (uint16_t)wz);
            render_list[r_count].sx = (int16_t)sx;
            render_list[r_count].sy = (int16_t)sy;
            render_list[r_count].cz = cz;
            render_list[r_count].radius = 2;
            render_list[r_count].r = 230;
            render_list[r_count].g = 235;
            render_list[r_count].b = 245;
            render_list[r_count].is_pyramid = 1;
            depth_counts[cz]++;
            r_count++;
        }
    }

    /* Add Agents */
    for (uint32_t i = 0; i < NUM_AGENTS; i++) {
        int32_t wx = agents[i].x;
        int32_t wy = agents[i].y;
        int32_t wz = agents[i].z;

        int32_t sx = project_z_no_zero((int64_t)wx * 480, (wz + 320), WIDTH / 2);
        int32_t sy = project_z_no_zero((int64_t)wy * 480, (wz + 320), HEIGHT / 2);

        if (sx >= 1 && sx <= WIDTH && sy >= 1 && sy <= HEIGHT) {
            uint16_t cz = (wz < 1) ? 1 : ((wz >= (int32_t)MAX_DEPTH_BUCKETS) ? (MAX_DEPTH_BUCKETS - 1) : (uint16_t)wz);
            uint8_t cr, cg, cb;
            int32_t shade = 180 + ((wz + 78) * 75) / 156;
            if (shade < 60) shade = 60;
            if (shade > 255) shade = 255;

            transduce_light_wave(agents[i].wave_freq, agents[i].wave_amp, shade, &cr, &cg, &cb);

            render_list[r_count].sx = (int16_t)sx;
            render_list[r_count].sy = (int16_t)sy;
            render_list[r_count].cz = cz;
            render_list[r_count].radius = (agents[i].state_flag == 3) ? 2 : 1;
            render_list[r_count].r = cr;
            render_list[r_count].g = cg;
            render_list[r_count].b = cb;
            render_list[r_count].is_pyramid = -1;
            depth_counts[cz]++;
            r_count++;
        }
    }

    /* Bucket prefix sum */
    depth_offsets[0] = 0;
    for (uint32_t d = 1; d < MAX_DEPTH_BUCKETS; d++) {
        depth_offsets[d] = depth_offsets[d - 1] + depth_counts[d - 1];
    }

    for (uint32_t i = 0; i < r_count; i++) {
        uint16_t cz = render_list[i].cz;
        uint32_t pos = depth_offsets[cz]++;
        sorted_list[pos] = render_list[i];
    }

    for (uint32_t i = 0; i < r_count; i++) {
        RenderCrystal *rc = &sorted_list[i];
        draw_volumetric_crystal(rc->sx, rc->sy, rc->radius, rc->r, rc->g, rc->b);
    }
}

void write_ppm_frame(uint32_t frame_idx) {
    char filename[64];
    snprintf(filename, sizeof(filename), "frame_%04d.ppm", frame_idx);
    FILE *f = fopen(filename, "wb");
    if (!f) return;
    fprintf(f, "P6\n%d %d\n255\n", WIDTH, HEIGHT);
    fwrite(rgb_frame, 1, (size_t)WIDTH * HEIGHT * 3, f);
    fclose(f);
}

int main(void) {
    init_volumetric_universe();

    for (uint32_t f = 0; f < FRAMES; f++) {
        update_agents(f);
        render_frame(f);
        if (f % 60 == 0) {
            write_ppm_frame(f);
        }
    }

    free(pyramid);
    free(agents);
    free(render_list);
    free(sorted_list);
    free(rgb_frame);
    return 0;
}
