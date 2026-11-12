/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics Engine
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 * Licensed under the GNU Affero General Public License v3 (AGPLv3).
 *
 * pTRC Light-Speed Universe Video Engine (1080p, c = 1, 120 FPS Transposition)
 * ============================================================================== */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define WIDTH               1920
#define HEIGHT              1080
#define TARGET_FPS          120
#define FRAME_BUDGET_NS     8333333ULL
#define NUM_CRYSTALS        6000
#define TOTAL_VIDEO_FRAMES  360
#define BASE_RENDER_TAKT    137
#define FREE_FACETS         120
#define MAX_ELEMENT         81
#define GRID_BUCKETS        4096

static const int8_t FCC_12_VECTORS = {
    { 1,  1,  0}, { 1, -1,  0}, {-1,  1,  0}, {-1, -1,  0},
    { 1,  0,  1}, { 1,  0, -1}, {-1,  0,  1}, {-1,  0, -1},
    { 0,  1,  1}, { 0,  1, -1}, { 0, -1,  1}, { 0, -1, -1}
};

static const uint8_t FONT_5X7 = {
    {0x1E,0x11,0x13,0x15,0x19,0x11,0x1E}, /* 0 */
    {0x04,0x0C,0x04,0x04,0x04,0x04,0x0E}, /* 1 */
    {0x1E,0x01,0x01,0x1E,0x10,0x10,0x1F}, /* 2 */
    {0x1E,0x01,0x01,0x0E,0x01,0x01,0x1E}, /* 3 */
    {0x02,0x06,0x0A,0x12,0x1F,0x02,0x02}, /* 4 */
    {0x1F,0x10,0x1E,0x01,0x01,0x01,0x1E}, /* 5 */
    {0x0E,0x10,0x10,0x1E,0x11,0x11,0x1E}, /* 6 */
    {0x1F,0x01,0x02,0x04,0x08,0x08,0x08}, /* 7 */
    {0x1E,0x11,0x11,0x1E,0x11,0x11,0x1E}, /* 8 */
    {0x1E,0x11,0x11,0x1F,0x01,0x01,0x1E}  /* 9 */
};

typedef struct {
    int32_t x, y, z;
    uint8_t core_state;                 /* 1..81 Elements, 82..145 DNA */
    uint8_t wave_freq;                  /* Discrete Wavelength (0..255, NO RGB) */
    uint8_t wave_amp;                   /* Discrete Wave Amplitude (0..255) */
    uint8_t love_cohesion;              /* 1-Byte Cohesion / Bonding Affinity */
    uint8_t outer_facets[FREE_FACETS];  /* 120 Decentralized Memory Facets */
} ptrc_wave_crystal_t;

static uint8_t retina_rgb[WIDTH * HEIGHT * 3];
static ptrc_wave_crystal_t space_grid[NUM_CRYSTALS];
static int32_t spatial_head[GRID_BUCKETS];
static int32_t spatial_next[NUM_CRYSTALS];

static inline uint64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static inline uint32_t hash_3d_cell(int32_t x, int32_t y, int32_t z) {
    uint32_t ux = (uint32_t)(x >> 4) * 73856093U;
    uint32_t uy = (uint32_t)(y >> 4) * 19349663U;
    uint32_t uz = (uint32_t)(z >> 4) * 83492791U;
    return (ux ^ uy ^ uz) & (GRID_BUCKETS - 1);
}

static inline void transduce_wave_to_rgb(uint8_t freq, uint8_t amp, uint8_t *r, uint8_t *g, uint8_t *b) {
    uint16_t raw_r = 0, raw_g = 0, raw_b = 0;
    if (freq < 85) {
        raw_r = (uint16_t)(255 - freq * 2);
        raw_g = (uint16_t)(freq * 3);
        raw_b = 36;
    } else if (freq < 170) {
        uint8_t f = (uint8_t)(freq - 85);
        raw_r = 24;
        raw_g = (uint16_t)(255 - f * 2);
        raw_b = (uint16_t)(f * 3);
    } else {
        uint8_t f = (uint8_t)(freq - 170);
        raw_r = (uint16_t)(f * 3);
        raw_g = 48;
        raw_b = (uint16_t)(255 - f);
    }
    *r = (uint8_t)((raw_r * (uint16_t)amp) >> 8);
    *g = (uint8_t)((raw_g * (uint16_t)amp) >> 8);
    *b = (uint8_t)((raw_b * (uint16_t)amp) >> 8);
}

static void draw_digit(int32_t ox, int32_t oy, int32_t digit, int32_t scale) {
    if ((uint32_t)digit > 9) return;
    for (int32_t r = 0; r < 7; r++) {
        uint8_t row = FONT_5X7[digit][r];
        for (int32_t c = 0; c < 5; c++) {
            if (row & (1 << (4 - c))) {
                for (int32_t sy = 0; sy < scale; sy++) {
                    for (int32_t sx = 0; sx < scale; sx++) {
                        int32_t px = ox + c * scale + sx;
                        int32_t py = oy + r * scale + sy;
                        if ((uint32_t)px < WIDTH && (uint32_t)py < HEIGHT) {
                            size_t idx = ((size_t)py * WIDTH + (size_t)px) * 3;
                            retina_rgb[idx] = 120; retina_rgb[idx + 1] = 245; retina_rgb[idx + 2] = 210;
                        }
                    }
                }
            }
        }
    }
}

static void draw_uint_hud(int32_t ox, int32_t oy, uint64_t val, int32_t digits, int32_t scale) {
    for (int32_t d = digits - 1; d >= 0; d--) {
        draw_digit(ox + d * (6 * scale), oy, (int32_t)(val % 10ULL), scale);
        val /= 10ULL;
    }
}

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
                if (adx == ady || adx == 0 || ady == 0) mod += 32;

                int32_t r = (int32_t)base_r + mod;
                int32_t g = (int32_t)base_g + mod;
                int32_t b = (int32_t)base_b + mod;

                uint8_t ur = (uint8_t)(r < 0 ? 0 : (r > 255 ? 255 : r));
                uint8_t ug = (uint8_t)(g < 0 ? 0 : (g > 255 ? 255 : g));
                uint8_t ub = (uint8_t)(b < 0 ? 0 : (b > 255 ? 255 : b));

                for (int32_t by = 0; by < step; by++) {
                    int32_t py = cy + dy + by;
                    if ((uint32_t)py >= HEIGHT) continue;
                    for (int32_t bx = 0; bx < step; bx++) {
                        int32_t px = cx + dx + bx;
                        if ((uint32_t)px >= WIDTH) continue;
                        size_t idx = ((size_t)py * WIDTH + (size_t)px) * 3;
                        retina_rgb[idx] = ur; retina_rgb[idx + 1] = ug; retina_rgb[idx + 2] = ub;
                    }
                }
            }
        }
    }
}

static void universe_lightspeed_takt(uint32_t takt) {
    memset(spatial_head, -1, sizeof(spatial_head));
    for (int32_t i = 0; i < NUM_CRYSTALS; i++) {
        uint32_t h = hash_3d_cell(space_grid[i].x, space_grid[i].y, space_grid[i].z);
        spatial_next[i] = spatial_head[h];
        spatial_head[h] = i;
    }

    for (int32_t i = 0; i < NUM_CRYSTALS; i++) {
        ptrc_wave_crystal_t *a = &space_grid[i];

        uint8_t v_idx = (uint8_t)((takt + a->wave_freq) % 12);
        a->x += FCC_12_VECTORS[v_idx];
        a->y += FCC_12_VECTORS[v_idx];
        a->z += FCC_12_VECTORS[v_idx];

        uint32_t h = hash_3d_cell(a->x, a->y, a->z);
        int32_t neighbor = spatial_head[h];
        int32_t checks = 0;
        while (neighbor != -1 && checks < 6) {
            if (neighbor != i) {
                ptrc_wave_crystal_t *b = &space_grid[neighbor];
                int32_t dx = b->x - a->x;
                int32_t dy = b->y - a->y;
                int32_t dz = b->z - a->z;
                int32_t dist_sq = dx * dx + dy * dy + dz * dz;

                if (dist_sq > 4 && dist_sq <= 256) {
                    a->wave_freq = (uint8_t)((((uint16_t)a->wave_freq + (uint16_t)b->wave_freq) >> 1) + 1);
                    uint16_t amp_sum = (uint16_t)a->wave_amp + (uint16_t)(b->wave_amp >> 4);
                    a->wave_amp = (amp_sum > 255) ? 255 : (uint8_t)amp_sum;

                    if ((uint16_t)a->love_cohesion + (uint16_t)b->love_cohesion >= 210) {
                        a->x += (dx > 0) ? 1 : (dx < 0 ? -1 : 0);
                        a->y += (dy > 0) ? 1 : (dy < 0 ? -1 : 0);
                        a->z += (dz > 0) ? 1 : (dz < 0 ? -1 : 0);
                    }
                }
            }
            neighbor = spatial_next[neighbor];
            checks++;
        }

        if (a->x > 360) a->x -= 720; else if (a->x < -360) a->x += 720;
        if (a->y > 220) a->y -= 440; else if (a->y < -220) a->y += 440;
        if (a->z > 260) a->z -= 520; else if (a->z < -260) a->z += 520;

        if (a->wave_amp > 64 && (takt & 3) == 0) a->wave_amp--;

        uint8_t f_slot = (uint8_t)((takt + (uint32_t)i) % FREE_FACETS);
        a->outer_facets[f_slot] = (uint8_t)((a->outer_facets[f_slot] + a->wave_freq) ^ a->wave_amp);
    }
}

int main(void) {
    uint32_t rng = 1836156137U;
    for (size_t i = 0; i < NUM_CRYSTALS; i++) {
        rng = rng * 1664525U + 1013904223U;
        space_grid[i].x = (int32_t)((rng >> 16) % 720U) - 360;
        rng = rng * 1664525U + 1013904223U;
        space_grid[i].y = (int32_t)((rng >> 16) % 440U) - 220;
        rng = rng * 1664525U + 1013904223U;
        space_grid[i].z = (int32_t)((rng >> 16) % 520U) - 260;

        space_grid[i].core_state = (uint8_t)(1 + (i % MAX_ELEMENT));
        space_grid[i].wave_freq = (uint8_t)((rng >> 8) & 0xFF);
        space_grid[i].wave_amp = (uint8_t)(140 + ((rng >> 16) & 115));
        space_grid[i].love_cohesion = (uint8_t)(90 + ((i * 19) % 165));
        for (size_t f = 0; f < FREE_FACETS; f++) {
            space_grid[i].outer_facets[f] = (uint8_t)((rng + f * 13) & 0xFF);
        }
    }

    FILE *pipe = popen(
        "ffmpeg -y -f rawvideo -vcodec rawvideo -pix_fmt rgb24 -s 1920x1080 -r 60 -i - "
        "-c:v libx264 -pix_fmt yuv420p -crf 17 ptrc_light_universe_1080p.mp4", "w"
    );
    if (!pipe) {
        fprintf(stderr, "Error: ffmpeg pipe could not be opened.\n");
        return 1;
    }

    uint8_t render_stride = 1;
    uint32_t render_takt_div = BASE_RENDER_TAKT;
    uint64_t global_takt = 0;

    for (uint32_t frame = 0; frame < TOTAL_VIDEO_FRAMES; frame++) {
        for (uint32_t t = 0; t < render_takt_div; t++) {
            universe_lightspeed_takt((uint32_t)global_takt++);
        }

        uint64_t t0 = now_ns();
        memset(retina_rgb, 5, sizeof(retina_rgb));

        for (size_t i = 0; i < NUM_CRYSTALS; i++) {
            const ptrc_wave_crystal_t *c = &space_grid[i];
            int32_t pz = c->z + 360;
            if (pz <= 40 || pz > 800) continue;

            int32_t sx = (WIDTH / 2) + ((c->x * 580) / pz);
            int32_t sy = (HEIGHT / 2) + ((c->y * 580) / pz);
            if (sx < -20 || sx >= WIDTH + 20 || sy < -20 || sy >= HEIGHT + 20) continue;

            draw_transposed_crystal(sx, sy, 1600 / pz, render_stride, c);
        }

        uint64_t frame_ns = now_ns() - t0;
        uint64_t live_fps = (frame_ns > 0) ? (1000000000ULL / frame_ns) : 999ULL;
        if (live_fps > 999ULL) live_fps = 999ULL;

        draw_uint_hud(32, 28, global_takt, 6, 3);
        draw_uint_hud(32, 62, live_fps, 3, 3);
        draw_uint_hud(120, 62, (uint64_t)render_stride, 1, 3);

        if (frame_ns > FRAME_BUDGET_NS) {
            if (render_stride < 4) render_stride++;
            else if (render_takt_div > 17) render_takt_div = render_takt_div >> 1;
        } else if (frame_ns < (FRAME_BUDGET_NS >> 1) && render_stride > 1) {
            render_stride--;
        }

        fwrite(retina_rgb, 1, sizeof(retina_rgb), pipe);
    }

    pclose(pipe);
    printf("Rendered 1080p Light-Speed Universe Video -> ptrc_light_universe_1080p.mp4\n");
    return 0;
}
