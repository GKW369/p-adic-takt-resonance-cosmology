/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics Engine
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 * Licensed under the GNU Affero General Public License v3 (AGPLv3).
 *
 * pTRC 3D Wind-Tunnel & Rotating Pyramid Cluster Engine (1080p @ 60 FPS)
 * Hardware Benchmark Target: Acer Aspire E1-570 (Intel Core i3 Pure Z-Clock)
 * ============================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <time.h>

#define WIDTH               1920
#define HEIGHT              1080
#define FRAMES              360         /* 6 Seconds @ 60 FPS */
#define SCALE               1000
#define INVARIANT_LIMIT     156
#define CONTACT_JUNCTIONS   24
#define FREE_FACETS         120
#define TOTAL_FACETS        144

#define PYRAMID_LAYERS      52          /* ~12,000 Dense 144-Facet Crystals (~1/4 Viewport) */
#define MAX_PYRAMID_CELLS   14000
#define NUM_AGENTS          65536       /* 2^16 Laminar Wind-Tunnel Space Crystals */

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
    uint8_t wave_freq;      /* Discrete Wavelength (0..255, Zero RGB in Space) */
    uint8_t wave_amp;       /* Discrete Wave Amplitude (0..255) */
    uint8_t flow_state;     /* 1 = Laminar Stream, 3 = Deflected Vortex */
} AgentCrystal;

static int8_t         crystal_register[TOTAL_FACETS];
static PyramidCrystal *pyramid      = NULL;
static uint32_t       pyramid_count = 0;
static AgentCrystal   *agents       = NULL;
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
        raw_g = (uint32_t)(160 + freq);
        raw_b = (uint32_t)(30 + (freq >> 1));
    } else if (freq < 170) {
        uint8_t f = (uint8_t)(freq - 85);
        raw_r = (uint32_t)(18 + (f >> 2));
        raw_g = (uint32_t)(225 - f);
        raw_b = (uint32_t)(175 + f);
    } else {
        uint8_t f = (uint8_t)(freq - 170);
        raw_r = (uint32_t)(140 + f);
        raw_g = (uint32_t)(85 + f);
        raw_b = 255;
    }
    uint32_t gain = ((uint32_t)amp * (uint32_t)depth_shade) >> 8;
    *r = (uint8_t)((raw_r * gain) >> 8);
    *g = (uint8_t)((raw_g * gain) >> 8);
    *b = (uint8_t)((raw_b * gain) >> 8);
}

static inline void plot_crystal_pixel(int32_t cx, int32_t cy, uint8_t r, uint8_t g, uint8_t b, int32_t is_pyramid) {
    if ((uint32_t)cx >= (WIDTH - 2) || (uint32_t)cy >= (HEIGHT - 2)) return;

    size_t idx = ((size_t)cy * WIDTH + (size_t)cx) * 3;
    uint16_t nr = rgb_frame[idx + 0] + r;
    uint16_t ng = rgb_frame[idx + 1] + g;
    uint16_t nb = rgb_frame[idx + 2] + b;
    rgb_frame[idx + 0] = (nr > 255) ? 255 : (uint8_t)nr;
    rgb_frame[idx + 1] = (ng > 255) ? 255 : (uint8_t)ng;
    rgb_frame[idx + 2] = (nb > 255) ? 255 : (uint8_t)nb;

    if (is_pyramid) {
        uint8_t hr = r >> 1, hg = g >> 1, hb = b >> 1;
        size_t offsets[3] = { 3, WIDTH * 3, (WIDTH + 1) * 3 };
        for (int k = 0; k < 3; k++) {
            size_t o = idx + offsets[k];
            rgb_frame[o + 0] = (rgb_frame[o + 0] + hr > 255) ? 255 : (uint8_t)(rgb_frame[o + 0] + hr);
            rgb_frame[o + 1] = (rgb_frame[o + 1] + hg > 255) ? 255 : (uint8_t)(rgb_frame[o + 1] + hg);
            rgb_frame[o + 2] = (rgb_frame[o + 2] + hb > 255) ? 255 : (uint8_t)(rgb_frame[o + 2] + hb);
        }
    }
}

void build_dense_crystal_pyramid(void) {
    pyramid = (PyramidCrystal *)malloc(MAX_PYRAMID_CELLS * sizeof(PyramidCrystal));
    pyramid_count = 0;

    for (int32_t layer = 0; layer < PYRAMID_LAYERS; layer++) {
        int32_t half = (PYRAMID_LAYERS - layer) / 2;
        int32_t y_pos = ((PYRAMID_LAYERS / 2) - layer);

        for (int32_t iz = -half; iz <= half; iz++) {
            for (int32_t ix = -half; ix <= half; ix++) {
                int32_t on_edge = (ix == -half || ix == half || iz == -half || iz == half);
                int32_t on_base = (layer == 0 && ((ix + iz) & 1) == 0);
                int32_t on_diag = (ix == iz || ix == -iz);
                if (on_edge || on_base || on_diag) {
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
    uint32_t h = (i * 2654435761U) ^ (seed_offset * 374761393U);
    int32_t sx = -115 + (int32_t)((h >> 24) & 31);
    int32_t sy = (int32_t)(((h >> 12) % 96U)) - 48;
    int32_t sz = (int32_t)((h % 96U)) - 48;

    agents[i].x = (int16_t)((sx == 0) ? -1 : sx);
    agents[i].y = (int16_t)((sy == 0) ? -1 : sy);
    agents[i].z = (int16_t)((sz == 0) ? -1 : sz);

    agents[i].vx = (int8_t)(1 + (i & 1));
    agents[i].vy = 0;
    agents[i].vz = 0;

    agents[i].wave_freq  = (uint8_t)(95 + ((sy + 48) >> 1));
    agents[i].wave_amp   = (uint8_t)(125 + (i & 63));
    agents[i].flow_state = 1;
}

void init_windtunnel_universe(void) {
    agents    = (AgentCrystal *)malloc(NUM_AGENTS * sizeof(AgentCrystal));
    rgb_frame = (uint8_t *)malloc((size_t)HEIGHT * WIDTH * 3);
    build_dense_crystal_pyramid();

    for (uint32_t i = 0; i < NUM_AGENTS; i++) {
        respawn_agent_at_inlet(i, i);
        agents[i].x = (int16_t)(-110 + (int32_t)(i % 210));
        if (agents[i].x == 0) agents[i].x = -1;
    }
}

void step_physics_and_render(uint32_t frame, uint64_t *out_phys_ns, uint64_t *out_rend_ns, uint32_t *out_impacts) {
    uint64_t t0 = now_ns();

    for (uint16_t f = 0; f < TOTAL_FACETS; f++) crystal_register[f] = -1;

    uint8_t pyr_rot_phase = (uint8_t)(frame & 0xFF);
    uint8_t hover_phase   = (uint8_t)((frame * 2) & 0xFF);
    int32_t cos_p         = get_smooth_cos(pyr_rot_phase);
    int32_t sin_p         = get_smooth_sin(pyr_rot_phase);
    int32_t hover_y       = (get_smooth_sin(hover_phase) * 7) / SCALE;
    int32_t pyr_half      = PYRAMID_LAYERS / 2;

    uint32_t impacts = 0;

    for (uint32_t i = 0; i < NUM_AGENTS; i++) {
        int32_t nx = (int32_t)agents[i].x + agents[i].vx;
        int32_t ny = (int32_t)agents[i].y + agents[i].vy;
        int32_t nz = (int32_t)agents[i].z + agents[i].vz;

        if (nx == 0) nx = 1;
        if (ny == 0) ny = (agents[i].vy >= 0) ? 1 : -1;
        if (nz == 0) nz = (agents[i].vz >= 0) ? 1 : -1;

        int32_t rel_y = ny - hover_y;
        if (rel_y >= -pyr_half && rel_y <= pyr_half) {
            int32_t allowed_r = (rel_y + pyr_half) >> 1;
            if (allowed_r < 2) allowed_r = 2;
            int32_t ax = (nx < 0) ? -nx : nx;
            int32_t az = (nz < 0) ? -nz : nz;

            if (ax <= allowed_r && az <= allowed_r) {
                impacts++;
                agents[i].vx = (nx < 0) ? -1 : 2;
                agents[i].vy = (rel_y <= 0) ? -1 : 1;
                agents[i].vz = (nz >= 0) ? 1 : -1;

                if (cos_p > 0) agents[i].vz = (int8_t)-agents[i].vz;

                nx += agents[i].vx * 2;
                ny += agents[i].vy;
                nz += agents[i].vz * 2;

                agents[i].wave_freq  = (uint8_t)(185 + ((i + frame) & 63));
                agents[i].wave_amp   = 245;
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

        if (nx > 115 || nx < -125 || ny > 58 || ny < -58 || nz > 65 || nz < -65) {
            respawn_agent_at_inlet(i, frame + i);
        } else {
            agents[i].x = (int16_t)nx;
            agents[i].y = (int16_t)ny;
            agents[i].z = (int16_t)nz;
        }
    }

    uint64_t t1 = now_ns();
    memset(rgb_frame, 4, (size_t)HEIGHT * WIDTH * 3);

    for (uint32_t p = 0; p < pyramid_count; p++) {
        int32_t rx = ((int32_t)pyramid[p].lx * cos_p - (int32_t)pyramid[p].lz * sin_p) / SCALE;
        int32_t rz = ((int32_t)pyramid[p].lx * sin_p + (int32_t)pyramid[p].lz * cos_p) / SCALE;
        int32_t ry = (int32_t)pyramid[p].ly + hover_y;

        int64_t cy_s = ((int64_t)ry * 925 - (int64_t)rz * 380);
        int64_t cz   = ((int64_t)ry * 380 + (int64_t)rz * 925) / SCALE + 115;

        int64_t denom = ((cz * SCALE) / 1414) + INVARIANT_LIMIT;
        if (denom > 0) {
            int32_t sx = (int32_t)(((int64_t)rx * 2550) / denom) + (WIDTH / 2);
            int32_t sy = (int32_t)((cy_s * 2550) / (denom * SCALE)) + (HEIGHT / 2);

            int32_t shade = 255 - ((int32_t)(cz - 85) * 3);
            if (shade < 95) shade = 95;
            if (shade > 255) shade = 255;

            uint8_t p_freq = (uint8_t)(18 + ((pyramid[p].facet_phase + frame) & 50));
            uint8_t p_amp  = pyramid[p].shell_flag ? 240 : 160;
            uint8_t r, g, b;
            transduce_light_wave(p_freq, p_amp, shade, &r, &g, &b);
            plot_crystal_pixel(sx, sy, r, g, b, pyramid[p].shell_flag);
        }
    }
    for (uint32_t i = 0; i < NUM_AGENTS; i++) {
        int32_t nx = agents[i].x;
        int32_t ny = agents[i].y;
        int32_t nz = agents[i].z;

        int64_t cy_s = ((int64_t)ny * 925 - (int64_t)nz * 380);
        int64_t cz   = ((int64_t)ny * 380 + (int64_t)nz * 925) / SCALE + 115;

        int64_t denom = ((cz * SCALE) / 1414) + INVARIANT_LIMIT;
        if (denom > 0) {
            int32_t sx = (int32_t)(((int64_t)nx * 2550) / denom) + (WIDTH / 2);
            int32_t sy = (int32_t)((cy_s * 2550) / (denom * SCALE)) + (HEIGHT / 2);

            if ((uint32_t)sx < WIDTH && (uint32_t)sy < HEIGHT) {
                int32_t depth_shade = 245 - ((int32_t)(cz - 70) * 2);
                if (depth_shade < 60)  depth_shade = 60;
                if (depth_shade > 255) depth_shade = 255;

                uint8_t r, g, b;
                transduce_light_wave(agents[i].wave_freq, agents[i].wave_amp, depth_shade, &r, &g, &b);
                plot_crystal_pixel(sx, sy, r, g, b, 0);
            }
        }
    }

    uint64_t t2 = now_ns();
    *out_phys_ns = t1 - t0;
    *out_rend_ns = t2 - t1;
    *out_impacts = impacts;
}

static void save_audit_png(uint32_t frame) {
    char cmd[256];
    snprintf(cmd, sizeof(cmd),
        "ffmpeg -y -loglevel error -f rawvideo -vcodec rawvideo -pix_fmt rgb24 -s %dx%d -i - audit_takt_%03u.png",
        WIDTH, HEIGHT, frame);
    FILE *img_pipe = popen(cmd, "w");
    if (img_pipe) {
        fwrite(rgb_frame, 1, (size_t)HEIGHT * WIDTH * 3, img_pipe);
        pclose(img_pipe);
    }
}

int main(void) {
    init_windtunnel_universe();

    const char *output_file = "ptrc_windtunnel_pyramid_1080p.mp4";
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
    printf("  pTRC 3D WIND-TUNNEL & PYRAMID CLUSTER ENGINE (1080p | ZERO-FLOAT C99)\n");
    printf("  Hardware Target : Acer Aspire E1-570 (Intel Core i3 Pure Integer Z-Clock)\n");
    printf("  Active Crystals : %u Pyramid Cells + %u Laminar Wind-Tunnel Agents\n", pyramid_count, NUM_AGENTS);
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
            printf(" + Takt %03u/%03u | Physik: %5" PRIu64 " us | 1080p Render: %5" PRIu64 " us | Pyramiden-Treffer: %u\n",
                   frame + 1, FRAMES, p_ns / 1000ULL, r_ns / 1000ULL, imp);
        }
    }

    pclose(pipe);

    uint64_t avg_phys_us = (sum_phys_ns / FRAMES) / 1000ULL;
    uint64_t avg_rend_us = (sum_rend_ns / FRAMES) / 1000ULL;
    uint64_t avg_tot_us  = avg_phys_us + avg_rend_us;
    uint64_t phys_fps    = (avg_phys_us > 0ULL) ? (1000000ULL / avg_phys_us) : 0ULL;
    uint64_t total_fps   = (avg_tot_us  > 0ULL) ? (1000000ULL / avg_tot_us)  : 0ULL;

    printf("-------------------------------------------------------------------------------\n");
    printf("  ACER ASPIRE E1-570 HARDWARE BENCHMARK (%" PRIu32 " INTERACTING 3D CRYSTALS):\n", pyramid_count + NUM_AGENTS);
    printf("  • Reine Ganzzahl-Physik (ohne GPU) : %" PRIu64 " us / Takt (~%" PRIu64 " FPS)\n", avg_phys_us, phys_fps);
    printf("  • 1080p Wellen-Rasterung (CPU)     : %" PRIu64 " us / Frame\n", avg_rend_us);
    printf("  • Gesamtzeit inkl. Full-HD Export  : %" PRIu64 " us / Frame (~%" PRIu64 " FPS)\n", avg_tot_us, total_fps);
    printf("  • Pyramiden-Kollisionen gesamt     : %" PRIu64 " Abprall-Events\n", sum_impacts);
    printf("  • Analyse-Frames exportiert        : audit_takt_180.png .. audit_takt_184.png\n");
    printf("===============================================================================\n");

    free(pyramid);
    free(agents);
    free(rgb_frame);
    return 0;
}

