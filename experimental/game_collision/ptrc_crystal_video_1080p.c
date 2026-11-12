#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <time.h>

// --- pTRC 1080p FULL-HD 3D-VIDEO-SYNTHESE (ZERO-FLOAT C-CORE) ---
#define CONTACT_JUNCTIONS 24
#define FREE_FACETS       120
#define TOTAL_FACETS      144
#define INVARIANT_LIMIT   156
#define SCALE             1000
#define NUM_PARTICLES     10000

// Native Full-HD 1080p Auflösung
#define WIDTH  1920
#define HEIGHT 1080
#define FRAMES 360   // 6 Sekunden bei 60 FPS

static int8_t crystal_register[TOTAL_FACETS];

typedef struct {
    int8_t dx;
    int8_t dy;
    int8_t dz;
} CrystalDir;

// Die 12 Grundrichtungen aus der 1+12 Kristallstruktur
static const CrystalDir BASE_12_DIRS = {
    { 2,  1,  0}, { 2, -1,  0}, {-2,  1,  0}, {-2, -1,  0},
    { 0,  2,  1}, { 0,  2, -1}, { 0, -2,  1}, { 0, -2, -1},
    { 1,  0,  2}, {-1,  0,  2}, { 1,  0, -2}, {-1,  0, -2}
};

typedef struct {
    int32_t x, y, z;
    uint8_t axis_id;
    int8_t  flow_state;
} Particle3D;

static Particle3D particles[NUM_PARTICLES];
// 1920 * 1080 * 3 Bytes (RGB24) = ca. 6,2 MB im RAM
static uint8_t rgb_frame[HEIGHT * WIDTH * 3];

void init_3d_lattice(void) {
    for (uint16_t f = 0; f < TOTAL_FACETS; f++) {
        crystal_register[f] = -1;
    }

    for (uint32_t i = 0; i < NUM_PARTICLES; i++) {
        int32_t sx = (int32_t)((i * 17) % 81) - 40;
        int32_t sy = (int32_t)((i * 31) % 51) - 25;
        int32_t sz = (int32_t)((i * 43) % 61) - 30;

        particles[i].x = (sx == 0) ? -1 : sx;
        particles[i].y = (sy == 0) ? -1 : sy;
        particles[i].z = (sz == 0) ? -1 : sz;
        particles[i].axis_id    = (uint8_t)(i % 12);
        particles[i].flow_state = 1;
    }
}

// Zeichnet ein formschlüssiges 3x3-Kristallkreuz direkt in den 1080p-RGB-Puffer
static inline void draw_crystal_node(int32_t cx, int32_t cy, uint8_t r, uint8_t g, uint8_t b) {
    const int8_t ox = {0, -1, 1,  0, 0};
    const int8_t oy = {0,  0, 0, -1, 1};

    for (int k = 0; k < 5; k++) {
        int32_t px = cx + ox[k];
        int32_t py = cy + oy[k];
        if (px >= 0 && px < WIDTH && py >= 0 && py < HEIGHT) {
            size_t idx = ((size_t)py * WIDTH + (size_t)px) * 3;
            // Kern voll beleuchtet, Kreuzachsen harmonisch halbiert
            rgb_frame[idx + 0] = (k == 0) ? r : (uint8_t)(r >> 1);
            rgb_frame[idx + 1] = (k == 0) ? g : (uint8_t)(g >> 1);
            rgb_frame[idx + 2] = (k == 0) ? b : (uint8_t)(b >> 1);
        }
    }
}

void render_1080p_takt(uint32_t takt) {
    for (uint16_t f = 0; f < TOTAL_FACETS; f++) {
        crystal_register[f] = -1;
    }
    // Hintergrund tiefes Kosmos-Schwarz (0, 0, 0)
    memset(rgb_frame, 0, sizeof(rgb_frame));

    // Sanfte 3D-Kameradrehung über den Modulo-24-Takt
    int32_t cam_twist = (int32_t)((takt / 3) % 24) - 12;
    if (cam_twist == 0) cam_twist = -1;

    for (uint32_t i = 0; i < NUM_PARTICLES; i++) {
        uint8_t ax = particles[i].axis_id;
        CrystalDir d = BASE_12_DIRS[ax];

        int32_t nx = particles[i].x + d.dx;
        int32_t ny = particles[i].y + d.dy;
        int32_t nz = particles[i].z + d.dz;

        // Null-Übersprung (-1 statt 0)
        if (nx == 0) nx = (d.dx > 0) ? 1 : -1;
        if (ny == 0) ny = (d.dy > 0) ? 1 : -1;
        if (nz == 0) nz = (d.dz > 0) ? 1 : -1;

        // Sphärische Kristallgrenze via Quadrance
        int32_t quadrance = (nx * nx) + (ny * ny) + (nz * nz);
        if (quadrance > 2800) {
            nx = -nx / 2;
            ny = -ny / 2;
            nz = -nz / 2;
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
            particles[i].x = nx;
            particles[i].y = ny;
            particles[i].z = nz;
            particles[i].flow_state = 1;
        } else {
            uint8_t alt_ax = (uint8_t)((ax + (f_idx % 11) + 1) % 12);
            CrystalDir alt_d = BASE_12_DIRS[alt_ax];
            particles[i].axis_id = alt_ax;
            particles[i].x = nx + alt_d.dx;
            particles[i].y = ny + alt_d.dy;
            particles[i].z = nz + alt_d.dz;
            particles[i].flow_state = 3;
        }

        // 3D-Retina-Projektion auf 1920x1080
        int32_t rot_x = particles[i].x + (particles[i].z * cam_twist) / 24;
        int32_t rot_z = particles[i].z - (particles[i].x * cam_twist) / 24 + 90;

        int32_t denom = ((rot_z * SCALE) / 1414) + INVARIANT_LIMIT;
        if (denom > 0) {
            int32_t proj_x = ((rot_x * 2600 * SCALE) / denom) / 100 + (WIDTH / 2);
            int32_t proj_y = ((particles[i].y * 2600 * SCALE) / denom) / 100 + (HEIGHT / 2);

            if (particles[i].flow_state == 1) {
                // Direkter Strom (+1): Spektral-Gold
                draw_crystal_node(proj_x, proj_y, 255, 200, 30);
            } else {
                // Wirbel-Kaskade (+3): Leuchtendes Cyan (tiefenabgestuft)
                uint8_t blue_glow = (uint8_t)(160 + (f_idx % 95));
                draw_crystal_node(proj_x, proj_y, 0, 230, blue_glow);
            }
        }
    }
}

int main(void) {
    init_3d_lattice();

    const char *output_file = "ptrc_crystal_3d_1080p.mp4";
    char ffmpeg_cmd;
    snprintf(ffmpeg_cmd, sizeof(ffmpeg_cmd),
        "ffmpeg -y -f rawvideo -vcodec rawvideo -pix_fmt rgb24 "
        "-s %dx%d -r 60 -i - -c:v libx264 -crf 16 -preset fast -pix_fmt yuv420p %s",
        WIDTH, HEIGHT, output_file);

    printf("=================================================================\n");
    printf("  pTRC 1080p 3D CRYSTAL VIDEO SYNTHESIS (10.000 PARTIKEL @ 60 FPS)\n");
    printf("=================================================================\n");
    printf(" -> Starte FFmpeg-Pipe nach '%s'...\n", output_file);

    FILE *pipe = popen(ffmpeg_cmd, "w");
    if (!pipe) {
        printf("[-] Fehler: FFmpeg konnte nicht gestartet werden (bitte 'ffmpeg' installieren).\n");
        return 1;
    }

    struct timespec t_start, t_end;
    uint64_t total_render_ns = 0;

    for (uint32_t frame = 1; frame <= FRAMES; frame++) {
        clock_gettime(CLOCK_MONOTONIC, &t_start);
        render_1080p_takt(frame);
        clock_gettime(CLOCK_MONOTONIC, &t_end);

        total_render_ns += (uint64_t)(t_end.tv_sec - t_start.tv_sec) * UINT64_C(1000000000)
                         + (uint64_t)(t_end.tv_nsec - t_start.tv_nsec);

        fwrite(rgb_frame, 1, sizeof(rgb_frame), pipe);

        if (frame % 60 == 0) {
            printf("    + %u / %u Frames (1080p) synthetisiert...\n", frame, FRAMES);
        }
    }

    int status = pclose(pipe);
    uint64_t avg_us = (total_render_ns / FRAMES) / 1000;

    if (status == 0) {
        printf("-----------------------------------------------------------------\n");
        printf(" [ OK ] 1080p-60FPS-Video erfolgreich gespeichert: %s\n", output_file);
        printf(" -> Reine C-Rechenzeit pro 1080p-Frame: %" PRIu64 " Mikrosekunden!\n", avg_us);
        printf("=================================================================\n");
    } else {
        printf("[-] FFmpeg-Beendigung mit Status %d. Bitte pruefen, ob ffmpeg installiert ist.\n", status);
    }

    return 0;
}
