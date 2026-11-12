/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics Engine
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 * Licensed under the GNU Affero General Public License v3 (AGPLv3).
 *
 * pTRC Light-Speed Universe Engine (c = 1 Cell/Takt, 120 FPS Transposition):
 * - Zero RGB storage in space: stores discrete Wave Frequency & Amplitude
 * - c = 1 Lattice Propagation across the 1+12 Closest-Packed Crystal Grid
 * - Dynamic Nanosecond Render Transposition locking onto 120 FPS (8,333,333 ns)
 * ============================================================================== */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define WIDTH               1920
#define HEIGHT              1080
#define TARGET_FPS          120
#define FRAME_BUDGET_NS     8333333ULL  /* 1,000,000,000 ns / 120 FPS */
#define NUM_CRYSTALS        4096
#define BASE_RENDER_TAKT    137
#define FREE_FACETS         120
#define MAX_ELEMENT         81
#define DNA_BASE_START      82

/* 12 Neighbor Vectors of the 1+12 Closest-Packed Lattice (c = 1 Step/Takt) */
static const int8_t FCC_12_VECTORS = {
    { 1,  1,  0}, { 1, -1,  0}, {-1,  1,  0}, {-1, -1,  0},
    { 1,  0,  1}, { 1,  0, -1}, {-1,  0,  1}, {-1,  0, -1},
    { 0,  1,  1}, { 0,  1, -1}, { 0, -1,  1}, { 0, -1, -1}
};

typedef struct {
    int32_t x, y, z;                    /* Discrete 1+12 Lattice Coordinates */
    uint8_t core_state;                 /* 1..81 Elements, 82..145 DNA, 255 Vacuum */
    uint8_t wave_freq;                  /* Discrete Wavelength Raster (0..255, NO RGB) */
    uint8_t wave_amp;                   /* Discrete Wave Amplitude / Energy (0..255) */
    uint8_t love_cohesion;              /* 1-Byte Love / Bonding Resonance */
    uint8_t outer_facets[FREE_FACETS];  /* 120 Decentralized Memory Facets */
} ptrc_wave_crystal_t;

static uint8_t retina_rgb[WIDTH * HEIGHT * 3];
static ptrc_wave_crystal_t space_grid[NUM_CRYSTALS];

static inline uint64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

/* Observer-Only Retina Transduction: Converts Discrete Wave (Freq + Amp) to RGB */
static inline void transduce_wave_to_rgb(uint8_t freq, uint8_t amp, uint8_t *r, uint8_t *g, uint8_t *b) {
    uint16_t raw_r = 0, raw_g = 0, raw_b = 0;
    if (freq < 85) {
        /* Long-wave Infrared / Warm Gold Spectrum */
        raw_r = (uint16_t)(255 - freq * 2);
        raw_g = (uint16_t)(freq * 3);
        raw_b = 24;
    } else if (freq < 170) {
        /* Mid-wave Emerald / Cyan Resonance Spectrum */
        uint8_t f = (uint8_t)(freq - 85);
        raw_r = 20;
        raw_g = (uint16_t)(255 - f * 2);
        raw_b = (uint16_t)(f * 3);
    } else {
        /* Short-wave Violet / High-Energy Quantum Spectrum */
        uint8_t f = (uint8_t)(freq - 170);
        raw_r = (uint16_t)(f * 3);
        raw_g = 32;
        raw_b = (uint16_t)(255 - f);
    }
    /* Modulate intensity purely by integer Wave Amplitude (>> 8) */
    *r = (uint8_t)((raw_r * (uint16_t)amp) >> 8);
    *g = (uint8_t)((raw_g * (uint16_t)amp) >> 8);
    *b = (uint8_t)((raw_b * (uint16_t)amp) >> 8);
}

/* Rasterizes 144-Facet Crystal Projection using Dynamic Transposition Stride */
static void draw_transposed_crystal(int32_t cx, int32_t cy, int32_t radius, uint8_t stride, const ptrc_wave_crystal_t *c) {
    if (radius < 2) radius = 2;
    if (radius > 14) radius = 14;

    uint8_t base_r, base_g, base_b;
    transduce_wave_to_rgb(c->wave_freq, c->wave_amp, &base_r, &base_g, &base_b);

    int32_t step = (int32_t)stride;
    for (int32_t dy = -radius; dy <= radius; dy += step) {
        int32_t ady = (dy < 0) ? -dy : dy;
        for (int32_t dx = -radius; dx <= radius; dx += step) {
            int32_t adx = (dx < 0) ? -dx : dx;
            if ((adx + (ady >> 1) <= radius) && (ady <= (radius * 7) / 8)) {
                uint8_t sector = (uint8_t)(((adx * 3 + ady * 5) ^ (dx < 0 ? 7 : 2)) % FREE_FACETS);
                int32_t mod = (int32_t)(c->outer_facets[sector] >> 3) - 16;
                if (adx == ady || adx == 0 || ady == 0) mod += 28;

                int32_t r = (int32_t)base_r + mod;
                int32_t g = (int32_t)base_g + mod;
                int32_t b = (int32_t)base_b + mod;

                uint8_t ur = (uint8_t)(r < 0 ? 0 : (r > 255 ? 255 : r));
                uint8_t ug = (uint8_t)(g < 0 ? 0 : (g > 255 ? 255 : g));
                uint8_t ub = (uint8_t)(b < 0 ? 0 : (b > 255 ? 255 : b));

                /* Fill transposed macro-block (1x1 at full speed, 2x2 or 3x3 when transposed) */
                for (int32_t by = 0; by < step; by++) {
                    int32_t py = cy + dy + by;
                    if ((uint32_t)py >= HEIGHT) continue;
                    for (int32_t bx = 0; bx < step; bx++) {
                        int32_t px = cx + dx + bx;
                        if ((uint32_t)px >= WIDTH) continue;
                        size_t idx = ((size_t)py * WIDTH + (size_t)px) * 3;
                        retina_rgb[idx]     = ur;
                        retina_rgb[idx + 1] = ug;
                        retina_rgb[idx + 2] = ub;
                    }
                }
            }
        }
    }
}

/* Physics Step at Speed of Light: c = 1 Crystal Unit per Takt */
static void universe_lightspeed_takt(uint32_t takt) {
    for (size_t i = 0; i < NUM_CRYSTALS; i++) {
        ptrc_wave_crystal_t *a = &space_grid[i];
        size_t j = (i + 1 + (takt % 29)) % NUM_CRYSTALS;
        ptrc_wave_crystal_t *b = &space_grid[j];

        /* c = 1 Propagation along 1+12 FCC lattice vector */
        uint8_t v_idx = (uint8_t)((takt + a->wave_freq) % 12);
        a->x += FCC_12_VECTORS[v_idx];
        a->y += FCC_12_VECTORS[v_idx];
        a->z += FCC_12_VECTORS[v_idx];

        /* Wave Interference & Love-Cohesion Coupling */
        int32_t dx = b->x - a->x;
        int32_t dy = b->y - a->y;
        int32_t dz = b->z - a->z;
        int32_t dist_sq = dx * dx + dy * dy + dz * dz;

        if (dist_sq <= 144) {
            /* Constructive wave superposition (Frequency & Amplitude exchange) */
            a->wave_freq = (uint8_t)((((uint16_t)a->wave_freq + (uint16_t)b->wave_freq) >> 1) + 1);
            uint16_t amp_sum = (uint16_t)a->wave_amp + (uint16_t)(b->wave_amp >> 3);
            a->wave_amp = (amp_sum > 255) ? 255 : (uint8_t)amp_sum;

            if ((uint16_t)a->love_cohesion + (uint16_t)b->love_cohesion >= 220) {
                a->x += (dx > 0) ? 1 : (dx < 0 ? -1 : 0);
                a->y += (dy > 0) ? 1 : (dy < 0 ? -1 : 0);
                a->z += (dz > 0) ? 1 : (dz < 0 ? -1 : 0);
            }
        } else if (a->wave_amp > 48) {
            a->wave_amp--; /* Natural spatial dispersion */
        }

        uint8_t f_slot = (uint8_t)((takt + i) % FREE_FACETS);
        a->outer_facets[f_slot] = (uint8_t)((a->outer_facets[f_slot] + a->wave_freq) ^ a->wave_amp);
    }
}

int main(void) {
    for (size_t i = 0; i < NUM_CRYSTALS; i++) {
        uint32_t seed = (uint32_t)(i * 1836 + 156);
        space_grid[i].x = (int32_t)((seed % 480) - 240);
        space_grid[i].y = (int32_t)(((seed / 7) % 320) - 160);
        space_grid[i].z = (int32_t)(((seed / 13) % 320) - 160);
        space_grid[i].core_state = (uint8_t)(1 + (i % MAX_ELEMENT));
        space_grid[i].wave_freq = (uint8_t)((i * 19) & 0xFF);
        space_grid[i].wave_amp = (uint8_t)(120 + (i & 127));
        space_grid[i].love_cohesion = (uint8_t)(80 + ((i * 17) % 175));
        for (size_t f = 0; f < FREE_FACETS; f++) {
            space_grid[i].outer_facets[f] = (uint8_t)((seed + f * 11) & 0xFF);
        }
    }

    uint8_t render_stride = 1;          /* 1 = Full Facet Resolution, 2..4 = Transposed */
    uint32_t render_takt_div = BASE_RENDER_TAKT;
    uint32_t total_frames = 120;        /* 1 Second Benchmark at 120 FPS Target */
    uint64_t total_render_ns = 0;

    for (uint32_t frame = 0; frame < total_frames; frame++) {
        /* Advance physics at c = 1 cell/takt */
        for (uint32_t t = 0; t < render_takt_div; t++) {
            universe_lightspeed_takt(frame * render_takt_div + t);
        }

        /* Measure Observer Render Plane & Transpose dynamically to lock 120 FPS */
        uint64_t t0 = now_ns();
        memset(retina_rgb, 4, sizeof(retina_rgb));
        for (size_t i = 0; i < NUM_CRYSTALS; i++) {
            const ptrc_wave_crystal_t *c = &space_grid[i];
            int32_t pz = c->z + 320;
            if (pz <= 30 || pz > 900) continue;

            int32_t sx = (WIDTH / 2) + ((c->x * 520) / pz);
            int32_t sy = (HEIGHT / 2) + ((c->y * 520) / pz);
            if (sx < -20 || sx >= WIDTH + 20 || sy < -20 || sy >= HEIGHT + 20) continue;

            draw_transposed_crystal(sx, sy, 1500 / pz, render_stride, c);
        }
        uint64_t frame_ns = now_ns() - t0;
        total_render_ns += frame_ns;

        /* Dynamic Transposition Governor targeting 120 FPS (8,333,333 ns/frame) */
        if (frame_ns > FRAME_BUDGET_NS) {
            if (render_stride < 4) render_stride++;
            else if (render_takt_div > 17) render_takt_div = render_takt_div >> 1;
        } else if (frame_ns < (FRAME_BUDGET_NS >> 1) && render_stride > 1) {
            render_stride--;
        }
    }

    uint64_t avg_ns = total_render_ns / total_frames;
    uint64_t achieved_fps = (avg_ns > 0) ? (1000000000ULL / avg_ns) : 9999ULL;
    printf("===========================================================================\n");
    printf("  pTRC LIGHT-SPEED UNIVERSE ENGINE (c = 1 Cell/Takt | 120 FPS Transposition)\n");
    printf("===========================================================================\n");
    printf("  • Avg Frame Render Time : %llu us (Target Budget: 8,333 us)\n", (unsigned long long)(avg_ns / 1000ULL));
    printf("  • Achieved Render Rate  : %llu FPS\n", (unsigned long long)achieved_fps);
    printf("  • Active Transposition  : Facet Stride = %u | Render Takt = %u\n", render_stride, render_takt_div);
    printf("===========================================================================\n");
    return 0;
}
