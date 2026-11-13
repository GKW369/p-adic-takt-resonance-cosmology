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
#define FRAMES              360
#define SCALE               1000
#define INVARIANT_LIMIT     156
#define CONTACT_JUNCTIONS   24
#define FREE_FACETS         120
#define TOTAL_FACETS        144

#define PYRAMID_LAYERS      48
#define PYRAMID_CENTER_X    (-25)
#define PYRAMID_CENTER_Y    1
#define PYRAMID_CENTER_Z    1
#define MAX_PYRAMID_CELLS   12000

#define NUM_AGENTS          32768
#define MAX_RENDER_NODES    (MAX_PYRAMID_CELLS + NUM_AGENTS)
#define MAX_DEPTH_BUCKETS   512

#define AUDIT_FRAME_START   180
#define AUDIT_FRAME_END     184

typedef struct {
    int16_t lx, ly, lz;
    uint8_t facet_phase;
    uint8_t shell_flag;
} PyramidCrystal;

typedef struct {
    int16_t x, y, z;
    int8_t  vx, vy, vz;
    uint8_t wave_freq;
    uint8_t wave_amp;
    uint8_t flow_state;
} AgentCrystal;

typedef struct {
    int16_t  sx, sy;
    uint16_t cz;
    uint8_t  radius;
    uint8_t  r, g, b;
    uint8_t  is_pyramid;
} RenderCrystal;

static int8_t         crystal_register[TOTAL_FACETS];
static PyramidCrystal *pyramid      = NULL;
static uint32_t       pyramid_count = 0;
static AgentCrystal   *agents       = NULL;
static RenderCrystal  *render_list  = NULL;
static RenderCrystal  *sorted_list  = NULL;
static uint32_t       depth_counts[MAX_DEPTH_BUCKETS];
static uint32_t       depth_offsets[MAX_DEPTH_BUCKETS];
static uint8_t        *rgb_frame    = NULL;

static const int16_t QUARTER_WAVE_64[64] = {
    1000,1000, 999, 997, 995, 992, 989, 985, 981, 976, 970, 964, 957, 950, 942, 933,
     924, 914, 904, 893, 882, 870, 858, 845, 831, 818, 803, 788, 773, 757, 741, 724,
     707, 690, 672, 653, 634, 615, 596, 576, 556, 535, 514, 493, 471, 450, 428, 405,
     383, 360, 337, 314, 290, 267, 243, 219, 195, 171, 147, 122,  98,  74,  49,  25
};

static inline int32_t get_smooth_cos(uint8_t phase) {
    uint8_t q = phase >> 6;
    uint8_t idx = phase & 63;
    if (q == 0) return  QUARTER_WAVE_64[idx];
    if (q == 1) return (idx == 0) ? 0 : -QUARTER_WAVE_64[64 - idx];
    if (q == 2) return -QUARTER_WAVE_64[idx];
    return (idx == 0) ? 0 : QUARTER_WAVE_64[64 - idx];
}

static inline int32_t get_smooth_sin(uint8_t phase) {
    return get_smooth_cos((uint8_t)(phase - 64));
}

static inline uint64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static inline void transduce_light_wave(uint8_t freq, uint8_t amp, int32_t depth_shade, uint8_t *r, uint8_t *g, uint8_t *b) {
    uint32_t raw_r = 0, raw_g = 0, raw_b = 0;
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
    *r = (uint8_t)((raw_r * gain) >> 8);
    *g = (uint8_t)((raw_g * gain) >> 8);
    *b = (uint8_t)((raw_b * gain) >> 8);
}

static inline void draw_volumetric_crystal(int32_t cx, int32_t cy, int32_t radius, uint8_t r, uint8_t g, uint8_t b) {
    if (radius <= 1) {
        if ((uint32_t)cx < WIDTH && (uint32_t)cy < HEIGHT) {
            size_t idx = ((size_t)cy * WIDTH + (size_t)cx) * 3;
            rgb_frame[idx + 0] = r;
            rgb_frame[idx + 1] = g;
            rgb_frame[idx + 2] = b;
        }
        return;
    }

    int32_t r2 = radius * radius;
    int32_t y_min = (cy - radius < 0) ? 0 : (cy - radius);
    int32_t y_max = (cy + radius >= HEIGHT) ? (HEIGHT - 1) : (cy + radius);
    int32_t x_min = (cx - radius < 0) ? 0 : (cx - radius);
    int32_t x_max = (cx + radius >= WIDTH) ? (WIDTH - 1) : (cx + radius);

    for (int32_t py = y_min; py <= y_max; py++) {
        int32_t dy = py - cy;
        int32_t dy2 = dy * dy;
        size_t row_off = (size_t)py * WIDTH;
        for (int32_t px = x_min; px <= x_max; px++) {
            int32_t dx = px - cx;
            int32_t d2 = dx * dx + dy2;
            if (d2 <= r2) {
                int32_t rim_factor = 255 - ((d2 * 135) / (r2 + 1));
                size_t idx = (row_off + (size_t)px) * 3;
                rgb_frame[idx + 0] = (uint8_t)(((uint32_t)r * (uint32_t)rim_factor) >> 8);
                rgb_frame[idx + 1] = (uint8_t)(((uint32_t)g * (uint32_t)rim_factor) >> 8);
                rgb_frame[idx + 2] = (uint8_t)(((uint32_t)b * (uint32_t)rim_factor) >> 8);
            }
        }
    }
}

void build_fcc_crystal_pyramid(void) {
    pyramid = (PyramidCrystal *)malloc(MAX_PYRAMID_CELLS * sizeof(PyramidCrystal));
    pyramid_count = 0;

    for (int32_t layer = 0; layer < PYRAMID_LAYERS; layer++) {
        int32_t half = (PYRAMID_LAYERS - layer) / 2;
        int32_t y_pos = ((PYRAMID_LAYERS / 2) - layer);

        for (int32_t iz = -half; iz <= half; iz++) {
            for (int32_t ix = -half; ix <= half; ix++) {
                if (((ix + y_pos + iz) & 1) != 0) continue;

                int32_t on_edge = (ix >= half - 1 || ix <= -half + 1 || iz >= half - 1 || iz <= -half + 1);
                int32_t on_base = (layer <= 1);
                if (on_edge || on_base) {
                    if (pyramid_count < MAX_PYRAMID_CELLS) {
                        pyramid[pyramid_count].lx = (int16_t)ix;
                        pyramid[pyramid_count].ly = (int16_t)y_pos;
                        pyramid[pyramid_count].lz = (int16_t)iz;
                        pyramid[pyramid_count].facet_phase = (uint8_t)((layer * 7 + ix * 11 + iz * 13) & 0xFF);
                        pyramid[pyramid_count].shell_flag = (uint8_t)(on_edge ? 1 : 0);
                        pyramid_count++;
                    }
                }
            }
        }
    }
}

void respawn_agent_at_inlet(uint32_t i, uint32_t seed_offset) {
    uint32_t h1 = (i * 2654435761U) + (seed_offset * 1597334677U);
    uint32_t h2 = (h1 ^ (h1 >> 15)) * 2246822519U;
    uint32_t h3 = (h2 ^ (h2 >> 13)) * 3266489917U;

    int32_t sx = -195 + (int32_t)(h1 % 47U);
    int32_t sy = (int32_t)(h2 % 130U) - 65;
    int32_t sz = (int32_t)(h3 % 130U) - 65;

    if (sy >= 0) sy += 1;
    if (sz >= 0) sz += 1;
    if (((sx + sy + sz) & 1) != 0) sx += 1;
    if (sx == 0) sx = -1;

    agents[i].x = (int16_t)sx;
    agents[i].y = (int16_t)sy;
    agents[i].z = (int16_t)sz;

    agents[i].vx = (int8_t)(1 + (int32_t)(h3 % 3U));
    agents[i].vy = 0;
    agents[i].vz = 0;

    agents[i].wave_freq  = (uint8_t)(92 + ((sy + 65) >> 1));
    agents[i].wave_amp   = (uint8_t)(175 + (h2 & 63));
    agents[i].flow_state = 1;
}

void init_volumetric_universe(void) {
    agents      = (AgentCrystal *)malloc(NUM_AGENTS * sizeof(AgentCrystal));
    render_list = (RenderCrystal *)malloc(MAX_RENDER_NODES * sizeof(RenderCrystal));
    sorted_list = (RenderCrystal *)malloc(MAX_RENDER_NODES * sizeof(RenderCrystal));
    rgb_frame   = (uint8_t *)malloc((size_t)HEIGHT * WIDTH * 3);

    build_fcc_crystal_pyramid();

    for (uint32_t i = 0; i < NUM_AGENTS; i++) {
        respawn_agent_at_inlet(i, i * 17U + 3U);
        uint32_t spread = (i * 2654435761U) % 388U;
        int32_t ix = -195 + (int32_t)spread;
        if (((ix + agents[i].y + agents[i].z) & 1) != 0) ix += 1;
        if (ix == 0) ix = -1;
        agents[i].x = (int16_t)ix;
    }
}

static inline int32_t step_z_no_zero(int32_t pos, int32_t vel) {
    if (vel > 0) {
        for (int32_t s = 0; s < vel; s++) {
            pos = (pos == -1) ? 1 : (pos + 1);
        }
    } else if (vel < 0) {
        for (int32_t s = 0; s > vel; s--) {
            pos = (pos == 1) ? -1 : (pos - 1);
        }
    }
    return pos;
}

void step_physics_and_render(uint32_t frame, uint64_t *out_phys_ns, uint64_t *out_rend_ns, uint32_t *out_impacts) {
    uint64_t t0 = now_ns();

    for (uint16_t f = 0; f < TOTAL_FACETS; f++) crystal_register[f] = -1;

    uint8_t pyr_rot_phase = (uint8_t)(frame & 0xFF);
    uint8_t hover_phase   = (uint8_t)((frame * 2) & 0xFF);
    int32_t cos_p         = get_smooth_cos(pyr_rot_phase);
    int32_t sin_p         = get_smooth_sin(pyr_rot_phase);
    int32_t hover_y       = PYRAMID_CENTER_Y + ((get_smooth_sin(hover_phase) * 9) / SCALE);
    if (hover_y == 0) hover_y = 1;
    int32_t pyr_half      = PYRAMID_LAYERS / 2;

    uint32_t impacts = 0;

    for (uint32_t i = 0; i < NUM_AGENTS; i++) {
        int32_t nx = step_z_no_zero((int32_t)agents[i].x, (int32_t)agents[i].vx);
        int32_t ny = step_z_no_zero((int32_t)agents[i].y, (int32_t)agents[i].vy);
        int32_t nz = step_z_no_zero((int32_t)agents[i].z, (int32_t)agents[i].vz);

        int32_t rel_x = nx - PYRAMID_CENTER_X;
        int32_t rel_y = ny - hover_y;
        int32_t rel_z = nz - PYRAMID_CENTER_Z;

        if (rel_y >= -pyr_half && rel_y <= pyr_half) {
            int32_t allowed_r = (rel_y + pyr_half) >> 1;
            if (allowed_r < 3) allowed_r = 3;
            int32_t ax = (rel_x < 0) ? -rel_x : rel_x;
            int32_t az = (rel_z < 0) ? -rel_z : rel_z;

            if (ax <= allowed_r && az <= allowed_r) {
                impacts++;
                agents[i].vx = (rel_x < 0) ? -1 : 2;
                agents[i].vy = (rel_y <= 0) ? -1 : 1;
                agents[i].vz = (rel_z >= 0) ? 1 : -1;

                if (cos_p > 0) agents[i].vz = (int8_t)-agents[i].vz;

                nx = step_z_no_zero(nx, (int32_t)agents[i].vx * 2);
                ny = step_z_no_zero(ny, (int32_t)agents[i].vy * 2);
                nz = step_z_no_zero(nz, (int32_t)agents[i].vz * 2);

                agents[i].wave_freq  = (uint8_t)(185 + ((i + frame) & 63));
                agents[i].wave_amp   = 252;
                agents[i].flow_state = 3;
            }
        }

        if (agents[i].flow_state == 3) {
            uint32_t phase_key = (uint32_t)(nx * nx + ny * ny + nz * nz + frame);
            uint8_t j_idx = (uint8_t)(phase_key % CONTACT_JUNCTIONS);
            if (crystal_register[j_idx] == -1) {
                crystal_register[j_idx] = 1;
                if (agents[i].vx < 1) agents[i].vx = 1;
                if ((frame & 3) == 0) {
                    agents[i].vy = 0;
                    agents[i].vz = 0;
                }
            } else {
                uint8_t f_slot = (uint8_t)((phase_key * 5) % FREE_FACETS);
                if ((f_slot & 3) == 0) {
                    agents[i].vy = (f_slot & 4) ? 1 : -1;
                    agents[i].vz = (f_slot & 8) ? 1 : -1;
                }
            }
        }

        if (nx > 195 || nx < -205 || ny > 75 || ny < -75 || nz > 75 || nz < -75) {
            respawn_agent_at_inlet(i, frame + i);
        } else {
            agents[i].x = (int16_t)nx;
            agents[i].y = (int16_t)ny;
            agents[i].z = (int16_t)nz;
        }
    }

    uint64_t t1 = now_ns();

    uint32_t r_count = 0;
    memset(depth_counts, 0, sizeof(depth_counts));

    const int32_t cam_cos_y = 966;
    const int32_t cam_sin_y = 259;

    for (uint32_t p = 0; p < pyramid_count; p++) {
        int32_t rx = (((int32_t)pyramid[p].lx * cos_p - (int32_t)pyramid[p].lz * sin_p) / SCALE) + PYRAMID_CENTER_X;
        int32_t rz = (((int32_t)pyramid[p].lx * sin_p + (int32_t)pyramid[p].lz * cos_p) / SCALE) + PYRAMID_CENTER_Z;
        int32_t ry = (int32_t)pyramid[p].ly + hover_y;

        int32_t vx = (rx * cam_cos_y - rz * cam_sin_y) / SCALE;
        int32_t vz = (rx * cam_sin_y + rz * cam_cos_y) / SCALE;

        int64_t cy_s = ((int64_t)ry * 910 - (int64_t)vz * 415);
        int64_t cz   = ((int64_t)ry * 415 + (int64_t)vz * 910) / SCALE + 235;

        int64_t denom = ((cz * SCALE) / 1414) + INVARIANT_LIMIT;
        if (denom > 0 && cz >= 40 && cz < MAX_DEPTH_BUCKETS) {
            int32_t sx = (int32_t)(((int64_t)vx * 3650) / denom) + (WIDTH / 2);
            int32_t sy = (int32_t)((cy_s * 3650) / (denom * SCALE)) + (HEIGHT / 2);

            if ((uint32_t)sx < WIDTH && (uint32_t)sy < HEIGHT) {
                int32_t shade = 255 - ((int32_t)(cz - 175) * 2);
                if (shade < 90)  shade = 90;
                if (shade > 255) shade = 255;

                int32_t rad = (int32_t)(720 / cz);
                if (rad < 1) rad = 1;
                if (rad > 5) rad = 5;

                uint8_t p_freq = (uint8_t)(20 + ((pyramid[p].facet_phase + frame) & 48));
                uint8_t p_amp  = pyramid[p].shell_flag ? 245 : 175;
                uint8_t r, g, b;
                transduce_light_wave(p_freq, p_amp, shade, &r, &g, &b);

                render_list[r_count].sx = (int16_t)sx;
                render_list[r_count].sy = (int16_t)sy;
                render_list[r_count].cz = (uint16_t)cz;
                render_list[r_count].radius = (uint8_t)rad;
                render_list[r_count].r = r;
                render_list[r_count].g = g;
                render_list[r_count].b = b;
                render_list[r_count].is_pyramid = 1;
                depth_counts[cz]++;
                r_count++;
            }
        }
    }

    for (uint32_t i = 0; i < NUM_AGENTS; i++) {
        int32_t ax = agents[i].x;
        int32_t ay = agents[i].y;
        int32_t az = agents[i].z;

        int32_t vx = (ax * cam_cos_y - az * cam_sin_y) / SCALE;
        int32_t vz = (ax * cam_sin_y + az * cam_cos_y) / SCALE;

        int64_t cy_s = ((int64_t)ay * 910 - (int64_t)vz * 415);
        int64_t cz   = ((int64_t)ay * 415 + (int64_t)vz * 910) / SCALE + 235;

        int64_t denom = ((cz * SCALE) / 1414) + INVARIANT_LIMIT;
        if (denom > 0 && cz >= 40 && cz < MAX_DEPTH_BUCKETS) {
            int32_t sx = (int32_t)(((int64_t)vx * 3650) / denom) + (WIDTH / 2);
            int32_t sy = (int32_t)((cy_s * 3650) / (denom * SCALE)) + (HEIGHT / 2);

            if ((uint32_t)sx < WIDTH && (uint32_t)sy < HEIGHT) {
                int32_t depth_shade = 250 - ((int32_t)(cz - 165) * 2);
                if (depth_shade < 55)  depth_shade = 55;
                if (depth_shade > 255) depth_shade = 255;

                int32_t rad = (int32_t)(520 / cz);
                if (agents[i].flow_state == 3) rad += 1;
                if (rad < 1) rad = 1;
                if (rad > 4) rad = 4;

                uint8_t r, g, b;
                transduce_light_wave(agents[i].wave_freq, agents[i].wave_amp, depth_shade, &r, &g, &b);

                render_list[r_count].sx = (int16_t)sx;
                render_list[r_count].sy = (int16_t)sy;
                render_list[r_count].cz = (uint16_t)cz;
                render_list[r_count].radius = (uint8_t)rad;
                render_list[r_count].r = r;
                render_list[r_count].g = g;
                render_list[r_count].b = b;
                render_list[r_count].is_pyramid = 0;
                depth_counts[cz]++;
                r_count++;
            }
        }
    }

    uint32_t running = 0;
    for (int32_t d = MAX_DEPTH_BUCKETS - 1; d >= 0; d--) {
        depth_offsets[d] = running;
        running += depth_counts[d];
    }
    for (uint32_t k = 0; k < r_count; k++) {
        uint16_t d = render_list[k].cz;
        sorted_list[depth_offsets[d]++] = render_list[k];
    }

    memset(rgb_frame, 3, (size_t)HEIGHT * WIDTH * 3);
    for (uint32_t k = 0; k < r_count; k++) {
        draw_volumetric_crystal(sorted_list[k].sx, sorted_list[k].sy,
                                sorted_list[k].radius, sorted_list[k].r,
                                sorted_list[k].g, sorted_list[k].b);
    }

    uint64_t t2 = now_ns();
    *out_phys_ns = t1 - t0;
    *out_rend_ns = t2 - t1;
    *out_impacts = impacts;
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

    uint64_t sum_phys_ns = 0;
    uint64_t sum_rend_ns = 0;
    uint64_t sum_impacts = 0;

    printf("===============================================================================\n");
    printf("  pTRC VOLUMETRIC 1+12 FCC SPACE-CRYSTAL ENGINE (1080p | ZERO-FLOAT C99)\n");
    printf("  Hardware Target : Acer Aspire E1-570 (Intel Core i3 Pure Integer Z-Clock)\n");
    printf("  Active Crystals : %u Pyramid Cells + %u Volumetric Wind-Tunnel Crystals\n", pyramid_count, NUM_AGENTS);
    printf("===============================================================================\n");

    for (uint32_t frame = 0; frame < FRAMES; frame++) {
        uint64_t p_ns = 0, r_ns = 0;
        uint32_t imp  = 0;

        step_physics_and_render(frame, &p_ns, &r_ns, &imp);
        sum_phys_ns += p_ns;
        sum_rend_ns += r_ns;
        sum_impacts += imp;

        if (frame >= AUDIT_FRAME_START && frame <= AUDIT_FRAME_END) {
            save_audit_png(frame);
        }

        fwrite(rgb_frame, 1, (size_t)HEIGHT * WIDTH * 3, pipe);
        if ((frame + 1) % 60 == 0) {
            printf(" + Takt %03u/%03u | Physik: %5llu us | 1080p Render: %5llu us | Treffer: %u\n",
                   frame + 1, FRAMES,
                   (unsigned long long)(p_ns / 1000ULL),
                   (unsigned long long)(r_ns / 1000ULL), imp);
        }
    }

    pclose(pipe);

    unsigned long long avg_phys_us = (unsigned long long)((sum_phys_ns / FRAMES) / 1000ULL);
    unsigned long long avg_rend_us = (unsigned long long)((sum_rend_ns / FRAMES) / 1000ULL);
    unsigned long long avg_tot_us  = avg_phys_us + avg_rend_us;
    unsigned long long phys_fps    = (avg_phys_us > 0ULL) ? (1000000ULL / avg_phys_us) : 0ULL;
    unsigned long long total_fps   = (avg_tot_us  > 0ULL) ? (1000000ULL / avg_tot_us)  : 0ULL;

    printf("-------------------------------------------------------------------------------\n");
    printf("  ACER ASPIRE E1-570 BENCHMARK (%u VOLUMETRIC 1+12 CRYSTALS):\n", pyramid_count + NUM_AGENTS);
    printf("  • Reine Ganzzahl-Physik (ohne GPU) : %llu us / Takt (~%llu FPS)\n", avg_phys_us, phys_fps);
    printf("  • 1080p Volumetrische Rasterung    : %llu us / Frame\n", avg_rend_us);
    printf("  • Gesamtzeit inkl. Full-HD Export  : %llu us / Frame (~%llu FPS)\n", avg_tot_us, total_fps);
    printf("  • Pyramiden-Kollisionen gesamt     : %llu Abprall-Events\n", (unsigned long long)sum_impacts);
    printf("  • Analyse-Frames exportiert        : audit_clean_takt_180.png .. 184.png\n");
    printf("===============================================================================\n");

    free(pyramid);
    free(agents);
    free(render_list);
    free(sorted_list);
    free(rgb_frame);
    return 0;
}
