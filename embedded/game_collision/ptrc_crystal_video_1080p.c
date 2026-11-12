/*
 * ==============================================================================
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
 * ==============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <time.h>

#define CONTACT_JUNCTIONS 24
#define FREE_FACETS       120
#define TOTAL_FACETS      144
#define INVARIANT_LIMIT   156
#define SCALE             1000
#define NUM_PARTICLES     25000

#define WIDTH  1920
#define HEIGHT 1080
#define FRAMES 360

typedef struct {
    int8_t dx, dy, dz;
} CrystalDir;

typedef struct {
    int32_t x, y, z;
    uint8_t axis_id;
    int8_t  flow_state;
} Particle3D;

static int8_t     *crystal_register = NULL;
static Particle3D *particles        = NULL;
static uint8_t    *rgb_frame        = NULL;

static inline int32_t get_mod24_cos(uint8_t idx) {
    switch (idx % 24) {
        case 0: return 1000;  case 1: return 966;   case 2: return 866;   case 3: return 707;
        case 4: return 500;   case 5: return 259;   case 6: return 0;     case 7: return -259;
        case 8: return -500;  case 9: return -707;  case 10: return -866; case 11: return -966;
        case 12: return -1000;case 13: return -966; case 14: return -866; case 15: return -707;
        case 16: return -500; case 17: return -259; case 18: return 0;    case 19: return 259;
        case 20: return 500;  case 21: return 707;  case 22: return 866;  default: return 966;
    }
}

static inline int32_t get_mod24_sin(uint8_t idx) {
    return get_mod24_cos((uint8_t)((idx + 18) % 24));
}

static inline CrystalDir get_crystal_dir(uint8_t ax) {
    CrystalDir d;
    switch (ax % 12) {
        case 0:  d.dx =  2; d.dy =  1; d.dz =  0; break;
        case 1:  d.dx =  2; d.dy = -1; d.dz =  0; break;
        case 2:  d.dx = -2; d.dy =  1; d.dz =  0; break;
        case 3:  d.dx = -2; d.dy = -1; d.dz =  0; break;
        case 4:  d.dx =  0; d.dy =  2; d.dz =  1; break;
        case 5:  d.dx =  0; d.dy =  2; d.dz = -1; break;
        case 6:  d.dx =  0; d.dy = -2; d.dz =  1; break;
        case 7:  d.dx =  0; d.dy = -2; d.dz = -1; break;
        case 8:  d.dx =  1; d.dy =  0; d.dz =  2; break;
        case 9:  d.dx = -1; d.dy =  0; d.dz =  2; break;
        case 10: d.dx =  1; d.dy =  0; d.dz = -2; break;
        default: d.dx = -1; d.dy =  0; d.dz = -2; break;
    }
    return d;
}

void init_3d_lattice(void) {
    crystal_register = (int8_t *)malloc(TOTAL_FACETS * sizeof(int8_t));
    particles        = (Particle3D *)malloc(NUM_PARTICLES * sizeof(Particle3D));
    rgb_frame        = (uint8_t *)malloc((size_t)HEIGHT * WIDTH * 3);

    for (uint32_t i = 0; i < NUM_PARTICLES; i++) {
        int32_t sx = (int32_t)((i * 17) % 61) - 30;
        int32_t sy = (int32_t)((i * 31) % 61) - 30;
        int32_t sz = (int32_t)((i * 43) % 61) - 30;

        particles[i].x = (sx == 0) ? -1 : sx;
        particles[i].y = (sy == 0) ? -1 : sy;
        particles[i].z = (sz == 0) ? -1 : sz;
        particles[i].axis_id    = (uint8_t)(i % 12);
        particles[i].flow_state = 1;
    }
}
static inline void draw_glowing_crystal(int32_t cx, int32_t cy, uint8_t r, uint8_t g, uint8_t b, int32_t depth_shade) {
    // Vorab mit Tiefenfaktor (45..255) skalieren (rein ganzzahlig)
    uint16_t base_r = (uint16_t)((r * depth_shade) >> 8);
    uint16_t base_g = (uint16_t)((g * depth_shade) >> 8);
    uint16_t base_b = (uint16_t)((b * depth_shade) >> 8);

    for (int32_t dy = -2; dy <= 2; dy++) {
        int32_t py = cy + dy;
        if (py < 0 || py >= HEIGHT) continue;
        for (int32_t dx = -2; dx <= 2; dx++) {
            int32_t px = cx + dx;
            if (px < 0 || px >= WIDTH) continue;
            int32_t dist_sq = dx * dx + dy * dy;
            if (dist_sq > 4) continue;

            uint8_t shift = (dist_sq == 0) ? 0 : ((dist_sq <= 2) ? 1 : 2);
            size_t idx = ((size_t)py * WIDTH + (size_t)px) * 3;
            uint16_t nr = rgb_frame[idx + 0] + (base_r >> shift);
            uint16_t ng = rgb_frame[idx + 1] + (base_g >> shift);
            uint16_t nb = rgb_frame[idx + 2] + (base_b >> shift);

            rgb_frame[idx + 0] = (nr > 255) ? 255 : (uint8_t)nr;
            rgb_frame[idx + 1] = (ng > 255) ? 255 : (uint8_t)ng;
            rgb_frame[idx + 2] = (nb > 255) ? 255 : (uint8_t)nb;
        }
    }
}

void render_1080p_takt(uint32_t takt) {
    for (uint16_t f = 0; f < TOTAL_FACETS; f++) crystal_register[f] = -1;
    memset(rgb_frame, 0, (size_t)HEIGHT * WIDTH * 3);

    uint8_t angle_idx = (uint8_t)((takt / 6) % 24);
    int32_t cos_a = get_mod24_cos(angle_idx);
    int32_t sin_a = get_mod24_sin(angle_idx);

    for (uint32_t i = 0; i < NUM_PARTICLES; i++) {
        uint8_t ax = particles[i].axis_id;
        CrystalDir d = get_crystal_dir(ax);

        int32_t nx = particles[i].x + d.dx;
        int32_t ny = particles[i].y + d.dy;
        int32_t nz = particles[i].z + d.dz;
        if (nx == 0) nx = (d.dx > 0) ? 1 : -1;
        if (ny == 0) ny = (d.dy > 0) ? 1 : -1;
        if (nz == 0) nz = (d.dz > 0) ? 1 : -1;

        int32_t quadrance = (nx * nx) + (ny * ny) + (nz * nz);
        if (quadrance > 1600) {
            nx = -nx / 2; ny = -ny / 2; nz = -nz / 2;
            if (nx == 0) nx = -1;
            if (ny == 0) ny = -1;
            if (nz == 0) nz = -1;
            quadrance = (nx * nx) + (ny * ny) + (nz * nz);
        }

        uint32_t phase_key = (uint32_t)(quadrance + takt);
        uint8_t j_idx = (uint8_t)(phase_key % CONTACT_JUNCTIONS);
        uint8_t f_idx = (uint8_t)(CONTACT_JUNCTIONS + ((phase_key * 5) % FREE_FACETS));

        if (crystal_register[j_idx] == -1) {
            crystal_register[j_idx] = 1;
            particles[i].x = nx; particles[i].y = ny; particles[i].z = nz;
            particles[i].flow_state = 1;
        } else {
            uint8_t alt_ax = (uint8_t)((ax + (f_idx % 11) + 1) % 12);
            CrystalDir alt_d = get_crystal_dir(alt_ax);
            particles[i].axis_id = alt_ax;
            particles[i].x = nx + alt_d.dx;
            particles[i].y = ny + alt_d.dy;
            particles[i].z = nz + alt_d.dz;
            particles[i].flow_state = 3;
        }

        int64_t rot_x_scaled = (int64_t)particles[i].x * cos_a - (int64_t)particles[i].z * sin_a;
        int64_t tmp_z_scaled = (int64_t)particles[i].x * sin_a + (int64_t)particles[i].z * cos_a;
        int64_t rot_y_scaled = ((int64_t)particles[i].y * SCALE * 866 - tmp_z_scaled * 500) / SCALE;
        int64_t rot_z        = ((int64_t)particles[i].y * 500 + (tmp_z_scaled * 866) / SCALE) / SCALE + 110;

        int64_t denom = ((rot_z * SCALE) / 1414) + INVARIANT_LIMIT;
        if (denom > 0) {
            int32_t proj_x = (int32_t)((rot_x_scaled * 2200) / (denom * 100)) + (WIDTH / 2);
            int32_t proj_y = (int32_t)((rot_y_scaled * 2200) / (denom * 100)) + (HEIGHT / 2);

            if (proj_x >= 0 && proj_x < WIDTH && proj_y >= 0 && proj_y < HEIGHT) {
                // Tiefen-Helligkeit aus rot_z ableiten (vorne ~65 -> 255 hell, hinten ~155 -> 45 dunkel)
                int32_t depth_shade = 255 - ((int32_t)(rot_z - 65) * 2);
                if (depth_shade < 45)  depth_shade = 45;
                if (depth_shade > 255) depth_shade = 255;

                if (particles[i].flow_state == 1) draw_glowing_crystal(proj_x, proj_y, 255, 210, 40, depth_shade);
                else draw_glowing_crystal(proj_x, proj_y, 18, 120, 210, depth_shade);
            }
        }
    }
}

int main(void) {
    init_3d_lattice();
    const char *output_file = "ptrc_crystal_3d_1080p.mp4";
    char *ffmpeg_cmd = (char *)malloc(512);
    snprintf(ffmpeg_cmd, 512,
        "ffmpeg -y -f rawvideo -vcodec rawvideo -pix_fmt rgb24 "
        "-s %dx%d -r 60 -i - -c:v libx264 -crf 16 -preset fast -pix_fmt yuv420p %s",
        WIDTH, HEIGHT, output_file);

    FILE *pipe = popen(ffmpeg_cmd, "w");
    if (!pipe) return 1;

    struct timespec t_start, t_end;
    uint64_t total_render_ns = 0;

    for (uint32_t frame = 1; frame <= FRAMES; frame++) {
        clock_gettime(CLOCK_MONOTONIC, &t_start);
        render_1080p_takt(frame);
        clock_gettime(CLOCK_MONOTONIC, &t_end);
        total_render_ns += (uint64_t)(t_end.tv_sec - t_start.tv_sec) * UINT64_C(1000000000)
                         + (uint64_t)(t_end.tv_nsec - t_start.tv_nsec);
        fwrite(rgb_frame, 1, (size_t)HEIGHT * WIDTH * 3, pipe);
        if (frame % 60 == 0) printf(" + %u / %u Frames...\n", frame, FRAMES);
    }

    pclose(pipe);
    printf(" [ OK ] 3D-Tiefennebel-Video fertig! Rechenzeit pro Frame: %" PRIu64 " us\n", (total_render_ns / FRAMES) / 1000);
    free(ffmpeg_cmd); free(crystal_register); free(particles); free(rgb_frame);
    return 0;
}
