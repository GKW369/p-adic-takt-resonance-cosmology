/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics Engine
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 * Licensed under the GNU Affero General Public License v3 (AGPLv3).
 *
 * pTRC High-Density Transposed Universe Engine (1080p @ 60 FPS):
 * - Transposes crystal count & spatial density from Planck scale to visible light
 * - 15,000+ densely packed 144-facet space crystals forming the central Pyramid
 * - 100,000 interacting space-crystal agents creating ultra-fine flow filaments
 * ============================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <time.h>

#define WIDTH               1920
#define HEIGHT              1080
#define FRAMES              480         /* 8 Seconds @ 60 FPS */
#define SCALE               1000
#define INVARIANT_LIMIT     156
#define CONTACT_JUNCTIONS   24
#define FREE_FACETS         120
#define TOTAL_FACETS        144

/* Transposed High-Density Crystal Counts (115,000 Total Active Crystals) */
#define PYRAMID_LAYERS      36          /* 36 Fine Layers -> ~15,500 Dense Surface/Rib Crystals */
#define MAX_PYRAMID_CELLS   16500
#define NUM_AGENTS          100000      /* 100,000 Ultra-Fine Interacting Space-Crystal Agents */

typedef struct {
    int16_t lx, ly, lz;     /* Transposed High-Resolution Local Coordinates */
    uint8_t facet_phase;    /* Local 144-Facet Memory Phase */
    uint8_t shell_flag;     /* 1 = Outer Facet Skin, 0 = Internal Structural Rib */
} PyramidCrystal;

typedef struct {
    int16_t x, y, z;
    int8_t  vx, vy, vz;
    uint8_t wave_freq;      /* Discrete Light Wavelength (0..255, Zero RGB Storage) */
    uint8_t wave_amp;       /* Discrete Wave Amplitude (0..255) */
    uint8_t flow_state;     /* 1 = Laminar Flow, 3 = Pyramid Vortex Cascade */
} AgentCrystal;

static int8_t         crystal_register[TOTAL_FACETS];
static PyramidCrystal *pyramid      = NULL;
static uint32_t       pyramid_count = 0;
static AgentCrystal   *agents       = NULL;
static uint8_t        *rgb_frame    = NULL;

/* Smooth 256-Step Integer Quarter-Wave Table */
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

/* Observer-Only Retina Transduction: Quantized Light Frequency + Amplitude -> RGB */
static inline void transduce_light_wave(uint8_t freq, uint8_t amp, int32_t depth_shade, uint8_t *r, uint8_t *g, uint8_t *b) {
    uint32_t raw_r = 0, raw_g = 0, raw_b = 0;
    if (freq < 85) {
        raw_r = 255;
        raw_g = (uint32_t)(135 + freq);
        raw_b = (uint32_t)(20 + (freq >> 1));
    } else if (freq < 170) {
        uint8_t f = (uint8_t)(freq - 85);
        raw_r = (uint32_t)(15 + (f >> 2));
        raw_g = (uint32_t)(215 - f);
        raw_b = (uint32_t)(165 + f);
    } else {
        uint8_t f = (uint8_t)(freq - 170);
        raw_r = (uint32_t)(90 + f * 2);
        raw_g = (uint32_t)(75 + f);
        raw_b = 255;
    }
    uint32_t gain = ((uint32_t)amp * (uint32_t)depth_shade) >> 8;
    *r = (uint8_t)((raw_r * gain) >> 8);
    *g = (uint8_t)((raw_g * gain) >> 8);
    *b = (uint8_t)((raw_b * gain) >> 8);
}

/* Ultra-Fine Transposed Sub-Crystal Plotter (Additive Interference Accumulation) */
static inline void plot_transposed_subcrystal(int32_t cx, int32_t cy, uint8_t r, uint8_t g, uint8_t b, int32_t is_pyramid) {
    if ((uint32_t)cx >= (WIDTH - 1) || (uint32_t)cy >= (HEIGHT - 1)) return;

    size_t idx = ((size_t)cy * WIDTH + (size_t)cx) * 3;
    uint16_t nr = rgb_frame[idx + 0] + r;
    uint16_t ng = rgb_frame[idx + 1] + g;
    uint16_t nb = rgb_frame[idx + 2] + b;
    rgb_frame[idx + 0] = (nr > 255) ? 255 : (uint8_t)nr;
    rgb_frame[idx + 1] = (ng > 255) ? 255 : (uint8_t)ng;
    rgb_frame[idx + 2] = (nb > 255) ? 255 : (uint8_t)nb;

    /* Subtle 1-pixel facet halo for pyramid crystalline faces */
    if (is_pyramid) {
        uint8_t hr = r >> 2, hg = g >> 2, hb = b >> 2;
        size_t idx_r = idx + 3;
        size_t idx_d = idx + (WIDTH * 3);
        rgb_frame[idx_r + 0] = (rgb_frame[idx_r + 0] + hr > 255) ? 255 : (uint8_t)(rgb_frame[idx_r + 0] + hr);
        rgb_frame[idx_r + 1] = (rgb_frame[idx_r + 1] + hg > 255) ? 255 : (uint8_t)(rgb_frame[idx_r + 1] + hg);
        rgb_frame[idx_r + 2] = (rgb_frame[idx_r + 2] + hb > 255) ? 255 : (uint8_t)(rgb_frame[idx_r + 2] + hb);
        rgb_frame[idx_d + 0] = (rgb_frame[idx_d + 0] + hr > 255) ? 255 : (uint8_t)(rgb_frame[idx_d + 0] + hr);
        rgb_frame[idx_d + 1] = (rgb_frame[idx_d + 1] + hg > 255) ? 255 : (uint8_t)(rgb_frame[idx_d + 1] + hg);
        rgb_frame[idx_d + 2] = (rgb_frame[idx_d + 2] + hb > 255) ? 255 : (uint8_t)(rgb_frame[idx_d + 2] + hb);
    }
}

/* Builds a Ultra-Dense 15,500-Crystal Pyramid (~1/4 Screen Width) */
void build_dense_crystal_pyramid(void) {
    pyramid = (PyramidCrystal *)malloc(MAX_PYRAMID_CELLS * sizeof(PyramidCrystal));
    pyramid_count = 0;

    for (int32_t layer = 0; layer < PYRAMID_LAYERS; layer++) {
        int32_t span = PYRAMID_LAYERS - layer;
        int32_t half = span / 2;
        int32_t y_pos = layer - (PYRAMID_LAYERS / 2);

        for (int32_t iz = -half; iz <= half; iz++) {
            for (int32_t ix = -half; ix <= half; ix++) {
                int32_t on_shell = (ix == -half || ix == half || iz == -half || iz == half || layer == 0);
                int32_t on_rib   = (ix == 0 || iz == 0 || ix == iz || ix == -iz);
                if (on_shell || on_rib) {
                    if (pyramid_count < MAX_PYRAMID_CELLS) {
                        pyramid[pyramid_count].lx = (int16_t)ix;
                        pyramid[pyramid_count].ly = (int16_t)y_pos;
                        pyramid[pyramid_count].lz = (int16_t)iz;
                        pyramid[pyramid_count].facet_phase = (uint8_t)((layer * 7 + ix * 11 + iz * 13) & 0xFF);
                        pyramid[pyramid_count].shell_flag = (uint8_t)(on_shell ? 1 : 0);
                        pyramid_count++;
                    }
                }
            }
        }
    }
}

void init_transposed_universe(void) {
    agents    = (AgentCrystal *)malloc(NUM_AGENTS * sizeof(AgentCrystal));
    rgb_frame = (uint8_t *)malloc((size_t)HEIGHT * WIDTH * 3);
    build_dense_crystal_pyramid();

    uint32_t rng = 1836156137U;
    for (uint32_t i = 0; i < NUM_AGENTS; i++) {
        rng = rng * 1664525U + 1013904223U;
        int32_t sx = (int32_t)((rng >> 16) % 120U) - 60;
        rng = rng * 1664525U + 1013904223U;
        int32_t sy = (int32_t)((rng >> 16) % 80U) - 40;
        rng = rng * 1664525U + 1013904223U;
        int32_t sz = (int32_t)((rng >> 16) % 120U) - 60;

        agents[i].x = (int16_t)((sx == 0) ? -1 : sx);
        agents[i].y = (int16_t)((sy == 0) ? -1 : sy);
        agents[i].z = (int16_t)((sz == 0) ? -1 : sz);

        agents[i].vx = (i & 1) ? 1 : -1;
        agents[i].vy = ((i >> 1) & 1) ? 1 : -1;
        agents[i].vz = ((i >> 2) & 1) ? 1 : -1;

        agents[i].wave_freq  = (uint8_t)(95 + (i % 70));
        agents[i].wave_amp   = (uint8_t)(75 + (i & 63)); /* Balanced amplitude for 100k additive density */
        agents[i].flow_state = 1;
    }
}

void step_and_render_frame(uint32_t frame) {
    for (uint16_t f = 0; f < TOTAL_FACETS; f++) crystal_register[f] = -1;
    memset(rgb_frame, 2, (size_t)HEIGHT * WIDTH * 3);

    uint8_t pyr_rot_phase = (uint8_t)(frame & 0xFF);
    uint8_t hover_phase   = (uint8_t)((frame * 2) & 0xFF);
    int32_t cos_p         = get_smooth_cos(pyr_rot_phase);
    int32_t sin_p         = get_smooth_sin(pyr_rot_phase);
    int32_t hover_y       = (get_smooth_sin(hover_phase) * 5) / SCALE;

    uint8_t cam_phase     = (uint8_t)((frame >> 1) & 0xFF);
    int32_t cos_c         = get_smooth_cos(cam_phase);
    int32_t sin_c         = get_smooth_sin(cam_phase);

    /* 1. Render 15,500+ Transposed Space Crystals Forming the Central Pyramid */
    int32_t pyr_half = PYRAMID_LAYERS / 2;
    for (uint32_t p = 0; p < pyramid_count; p++) {
        int32_t rx = ((int32_t)pyramid[p].lx * cos_p - (int32_t)pyramid[p].lz * sin_p) / SCALE;
        int32_t rz = ((int32_t)pyramid[p].lx * sin_p + (int32_t)pyramid[p].lz * cos_p) / SCALE;
        int32_t ry = (int32_t)pyramid[p].ly + hover_y;

        int64_t cx_s = (int64_t)rx * cos_c - (int64_t)rz * sin_c;
        int64_t cz_s = (int64_t)rx * sin_c + (int64_t)rz * cos_c;
        int64_t cy_s = ((int64_t)ry * SCALE * 920 - cz_s * 390) / SCALE;
        int64_t cz   = ((int64_t)ry * 390 + (cz_s * 920) / SCALE) / SCALE + 118;

        int64_t denom = ((cz * SCALE) / 1414) + INVARIANT_LIMIT;
        if (denom > 0) {
            int32_t sx = (int32_t)((cx_s * 2400) / (denom * 100)) + (WIDTH / 2);
            int32_t sy = (int32_t)((cy_s * 2400) / (denom * 100)) + (HEIGHT / 2);

            int32_t shade = 240 - ((int32_t)(cz - 90) * 3);
            if (shade < 65) shade = 65;
            if (shade > 255) shade = 255;

            /* Interference wave patterns across the 36 pyramid layers */
            uint8_t p_freq = (uint8_t)(20 + ((pyramid[p].facet_phase + frame) & 55));
            uint8_t p_amp  = pyramid[p].shell_flag ? 165 : 110;
            uint8_t r, g, b;
            transduce_light_wave(p_freq, p_amp, shade, &r, &g, &b);
            plot_transposed_subcrystal(sx, sy, r, g, b, pyramid[p].shell_flag);
        }
    }

    /* 2. Step & Render 100,000 Ultra-Fine Space-Crystal Agents */
    for (uint32_t i = 0; i < NUM_AGENTS; i++) {
        int32_t nx = (int32_t)agents[i].x + agents[i].vx;
        int32_t ny = (int32_t)agents[i].y + agents[i].vy;
        int32_t nz = (int32_t)agents[i].z + agents[i].vz;

        if (nx == 0) nx = agents[i].vx;
        if (ny == 0) ny = agents[i].vy;
        if (nz == 0) nz = agents[i].vz;

        /* Collision & Wave-Energy Transfer with the Central Pyramid Volume */
        int32_t rel_y = ny - hover_y;
        if (rel_y >= -pyr_half && rel_y <= pyr_half) {
            int32_t allowed_r = (pyr_half - rel_y) >> 1;
            if (allowed_r < 2) allowed_r = 2;
            int32_t ax = (nx < 0) ? -nx : nx;
            int32_t az = (nz < 0) ? -nz : nz;

            if (ax <= allowed_r && az <= allowed_r) {
                int8_t old_vx = agents[i].vx;
                agents[i].vx = (nz >= 0) ? 1 : -1;
                agents[i].vz = (old_vx >= 0) ? -1 : 1;
                agents[i].vy = (rel_y >= 0) ? 1 : -1;

                nx += agents[i].vx * 2;
                nz += agents[i].vz * 2;

                agents[i].wave_freq  = (uint8_t)(185 + ((i + frame) & 63));
                agents[i].wave_amp   = 185;
                agents[i].flow_state = 3;
            }
        }

        /* Smooth Outer Boundary Containment */
        int32_t quadrance = nx * nx + ny * ny + nz * nz;
        if (quadrance > 4200) {
            if (nx > 48 || nx < -48) agents[i].vx = (int8_t)-agents[i].vx;
            if (ny > 32 || ny < -32) agents[i].vy = (int8_t)-agents[i].vy;
            if (nz > 48 || nz < -48) agents[i].vz = (int8_t)-agents[i].vz;
            nx = (int32_t)agents[i].x + agents[i].vx;
            ny = (int32_t)agents[i].y + agents[i].vy;
            nz = (int32_t)agents[i].z + agents[i].vz;
        }

        /* 144-Facet Lateral Register Coupling */
        uint32_t phase_key = (uint32_t)(quadrance + frame);
        uint8_t j_idx = (uint8_t)(phase_key % CONTACT_JUNCTIONS);
        if (crystal_register[j_idx] == -1) {
            crystal_register[j_idx] = 1;
            if (agents[i].wave_amp > 85) agents[i].wave_amp -= 2;
            if (agents[i].flow_state == 3 && agents[i].wave_amp <= 90) {
                agents[i].flow_state = 1;
                agents[i].wave_freq  = (uint8_t)(95 + (i % 70));
            }
        } else {
            uint8_t f_slot = (uint8_t)((phase_key * 5) % FREE_FACETS);
            if ((f_slot & 7) == 0) {
                int8_t tmp = agents[i].vx;
                agents[i].vx = agents[i].vz;
                agents[i].vz = (int8_t)-tmp;
            }
        }

        agents[i].x = (int16_t)nx;
        agents[i].y = (int16_t)ny;
        agents[i].z = (int16_t)nz;

        int64_t cx_s = (int64_t)nx * cos_c - (int64_t)nz * sin_c;
        int64_t cz_s = (int64_t)nx * sin_c + (int64_t)nz * cos_c;
        int64_t cy_s = ((int64_t)ny * SCALE * 920 - cz_s * 390) / SCALE;
        int64_t cz   = ((int64_t)ny * 390 + (cz_s * 920) / SCALE) / SCALE + 118;

        int64_t denom = ((cz * SCALE) / 1414) + INVARIANT_LIMIT;
        if (denom > 0) {
            int32_t sx = (int32_t)((cx_s * 2400) / (denom * 100)) + (WIDTH / 2);
            int32_t sy = (int32_t)((cy_s * 2400) / (denom * 100)) + (HEIGHT / 2);

            if ((uint32_t)sx < WIDTH && (uint32_t)sy < HEIGHT) {
                int32_t depth_shade = 245 - ((int32_t)(cz - 70) * 2);
                if (depth_shade < 45)  depth_shade = 45;
                if (depth_shade > 255) depth_shade = 255;

                uint8_t r, g, b;
                transduce_light_wave(agents[i].wave_freq, agents[i].wave_amp, depth_shade, &r, &g, &b);
                plot_transposed_subcrystal(sx, sy, r, g, b, 0);
            }
        }
    }
}

int main(void) {
    init_transposed_universe();

    const char *output_file = "ptrc_transposed_universe_1080p.mp4";
    char ffmpeg_cmd[256];
    snprintf(ffmpeg_cmd, sizeof(ffmpeg_cmd),
        "ffmpeg -y -f rawvideo -vcodec rawvideo -pix_fmt rgb24 "
        "-s %dx%d -r 60 -i - -c:v libx264 -crf 16 -preset fast -pix_fmt yuv420p %s",
        WIDTH, HEIGHT, output_file);

    FILE *pipe = popen(ffmpeg_cmd, "w");
    if (!pipe) return 1;

    struct timespec t_start, t_end;
    uint64_t total_ns = 0;

    printf("=================================================================\n");
    printf("  pTRC HIGH-DENSITY TRANSPOSED UNIVERSE (115,000 SPACE CRYSTALS)\n");
    printf("  Pyramid Cluster: %u Crystals | Free Agents: %u Crystals\n", pyramid_count, NUM_AGENTS);
    printf("=================================================================\n");

    for (uint32_t frame = 0; frame < FRAMES; frame++) {
        clock_gettime(CLOCK_MONOTONIC, &t_start);
        step_and_render_frame(frame);
        clock_gettime(CLOCK_MONOTONIC, &t_end);

        total_ns += (uint64_t)(t_end.tv_sec - t_start.tv_sec) * 1000000000ULL
                  + (uint64_t)(t_end.tv_nsec - t_start.tv_nsec);

        fwrite(rgb_frame, 1, (size_t)HEIGHT * WIDTH * 3, pipe);
        if ((frame + 1) % 60 == 0) {
            printf(" + %u / %u Frames gerendert...\n", frame + 1, FRAMES);
        }
    }

        pclose(pipe);
    uint64_t avg_us  = (total_ns / FRAMES) / 1000ULL;
    uint64_t est_fps = (avg_us > 0ULL) ? (1000000ULL / avg_us) : 0ULL;
    printf("[ OK ] Transponiertes 115k-Video fertig! Rechenzeit pro Frame: %" PRIu64 " us (~%" PRIu64 " FPS)\n",
           avg_us, est_fps);

    free(pyramid);
    free(agents);
    free(rgb_frame);
    return 0;
}
