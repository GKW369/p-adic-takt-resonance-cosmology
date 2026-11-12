#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

// --- pTRC 144-FACETTEN 3D-ECHTZEIT-ENGINE ---
#define CONTACT_JUNCTIONS 24
#define FREE_FACETS       120
#define TOTAL_FACETS      144
#define MOD_PRIMORIAL     210
#define INVARIANT_LIMIT   156
#define SCALE             1000
#define NUM_PARTICLES     10000

// Viewport-Dimensionen (optimiert für Terminal & 64-Zoll-TV)
#define VIEW_W 120
#define VIEW_H 36

// Flaches 144-Facetten-Register ohne Null (-1 = Frei, +1 = Strom, +3 = Wirbel)
static int8_t crystal_register[TOTAL_FACETS];

// Die 12 Grundrichtungen aus der 1+12 Kristallstruktur
static const int8_t BASE_12_DIRS = {
    { 2,  1, 0}, { 2, -1, 0}, {-2,  1, 0}, {-2, -1, 0},
    { 0,  2, 1}, { 0,  2, -1}, { 0, -2, 1}, { 0, -2, -1},
    { 1,  0, 2}, {-1,  0, 2}, { 1,  0, -2}, {-1,  0, -2}
};

typedef struct {
    int32_t x, y, z;     // 3D-Koordinaten im Ganzzahlraum (Z^3)
    uint8_t axis_id;     // Aktive Kristallachse (0..11)
    int8_t  flow_state;  // +1 (Direkter Strom >) oder +3 (Wirbel-Kaskade x)
} Particle3D;

static Particle3D particles[NUM_PARTICLES];
static char screen_grid[VIEW_H][VIEW_W];
static char render_buffer[VIEW_H * (VIEW_W + 16) + 512];

void init_3d_lattice(void) {
    for (uint16_t f = 0; f < TOTAL_FACETS; f++) {
        crystal_register[f] = -1;
    }

    for (uint32_t i = 0; i < NUM_PARTICLES; i++) {
        // Symmetrische Startverteilung um den Ursprung (ohne Null)
        int32_t sx = (int32_t)((i * 17) % 61) - 30;
        int32_t sy = (int32_t)((i * 31) % 31) - 15;
        int32_t sz = (int32_t)((i * 43) % 41) - 20;

        particles[i].x = (sx == 0) ? -1 : sx;
        particles[i].y = (sy == 0) ? -1 : sy;
        particles[i].z = (sz == 0) ? -1 : sz;
        particles[i].axis_id    = (uint8_t)(i % 12);
        particles[i].flow_state = 1;
    }
}

void step_and_project_frame(uint32_t takt, uint32_t *out_streams, uint32_t *out_vortices) {
    uint32_t streams = 0;
    uint32_t vortices = 0;

    // 1. Register & Bildschirm-Matrix für neuen Takt vorbereiten
    for (uint16_t f = 0; f < TOTAL_FACETS; f++) {
        crystal_register[f] = -1;
    }
    memset(screen_grid, ' ', sizeof(screen_grid));

    // Leichte 3D-Kameradrehung über Modulo-24-Takt (reine Ganzzahlen)
    int32_t cam_twist = (int32_t)(takt % 24) - 12;
    if (cam_twist == 0) cam_twist = -1;

    // 2. Alle 10.000 3D-Partikel berechnen, umlenken und auf Retina projizieren
    for (uint32_t i = 0; i < NUM_PARTICLES; i++) {
        uint8_t ax = particles[i].axis_id;

        int32_t nx = particles[i].x + BASE_12_DIRS[ax];
        int32_t ny = particles[i].y + BASE_12_DIRS[ax];
        int32_t nz = particles[i].z + BASE_12_DIRS[ax];

        // Gekreuzter Plichta-Spiegel: Null-Übersprung (-1 statt 0)
        if (nx == 0) nx = (BASE_12_DIRS[ax] > 0) ? 1 : -1;
        if (ny == 0) ny = (BASE_12_DIRS[ax] > 0) ? 1 : -1;
        if (nz == 0) nz = (BASE_12_DIRS[ax] > 0) ? 1 : -1;

        // Sphärische Kristall-Begrenzung via Quadrance (Q = x^2 + y^2 + z^2)
        int32_t quadrance = (nx * nx) + (ny * ny) + (nz * nz);
        if (quadrance > 1800) {
            // Spiegelung am Außenrand des Kristalls zurück nach innen
            nx = -nx / 2;
            ny = -ny / 2;
            nz = -nz / 2;
            if (nx == 0) nx = -1;
            if (ny == 0) ny = -1;
            if (nz == 0) nz = -1;
            quadrance = (nx * nx) + (ny * ny) + (nz * nz);
        }

        // Abbildung auf die 24 Kontaktstellen & 120 Kristallfacetten
        uint32_t phase_key = (uint32_t)(quadrance + takt);
        uint8_t j_idx = (uint8_t)(phase_key % CONTACT_JUNCTIONS);
        uint8_t f_idx = (uint8_t)(CONTACT_JUNCTIONS + ((phase_key * 5) % FREE_FACETS));

        if (crystal_register[j_idx] == -1) {
            // Freier Hauptkanal (+1)
            crystal_register[j_idx] = 1;
            particles[i].x = nx;
            particles[i].y = ny;
            particles[i].z = nz;
            particles[i].flow_state = 1;
            streams++;
        } else {
            // Kaskaden-Kollision (+3): Umlenkung über die 120 Facetten
            uint8_t alt_ax = (uint8_t)((ax + (f_idx % 11) + 1) % 12);
            particles[i].axis_id = alt_ax;
            particles[i].x = nx + BASE_12_DIRS[alt_ax];
            particles[i].y = ny + BASE_12_DIRS[alt_ax];
            particles[i].z = nz + BASE_12_DIRS[alt_ax];
            particles[i].flow_state = 3;
            vortices++;
        }

        // 3. pTRC 3D-Retina-Projektion (reine Festkomma-Division)
        int32_t rot_x = particles[i].x + (particles[i].z * cam_twist) / 24;
        int32_t rot_z = particles[i].z - (particles[i].x * cam_twist) / 24 + 75;

        int32_t denom = ((rot_z * SCALE) / 1414) + INVARIANT_LIMIT;
        if (denom > 0) {
            // Faktor 2 horizontal gleicht das Seitenverhältnis von Terminal-Zeichen aus
            int32_t proj_x = ((rot_x * 220 * SCALE) / denom) / 100 + (VIEW_W / 2);
            int32_t proj_y = ((particles[i].y * 110 * SCALE) / denom) / 100 + (VIEW_H / 2);

            if (proj_x >= 0 && proj_x < VIEW_W && proj_y >= 0 && proj_y < VIEW_H) {
                if (particles[i].flow_state == 1) {
                    screen_grid[proj_y][proj_x] = '@'; // Aktiver Hauptstrom (24er Ring)
                } else if (screen_grid[proj_y][proj_x] == ' ') {
                    screen_grid[proj_y][proj_x] = '.'; // Wirbel-Kaskade (120er Facetten)
                }
            }
        }
    }

    *out_streams = streams;
    *out_vortices = vortices;
}

int main(void) {
    init_3d_lattice();

    // Alternate Screen Buffer aktivieren & Cursor ausblenden
    printf("\033[?1049h\033[?25l");
    fflush(stdout);

    uint32_t total_frames = 300; // 5 Sekunden Live-Animation bei 60 FPS
    struct timespec t_start, t_end;
    uint64_t total_compute_ns = 0;

    for (uint32_t frame = 1; frame <= total_frames; frame++) {
        uint32_t streams = 0, vortices = 0;

        clock_gettime(CLOCK_MONOTONIC, &t_start);
        step_and_project_frame(frame, &streams, &vortices);
        clock_gettime(CLOCK_MONOTONIC, &t_end);

        total_compute_ns += (uint64_t)(t_end.tv_sec - t_start.tv_sec) * UINT64_C(1000000000)
                          + (uint64_t)(t_end.tv_nsec - t_start.tv_nsec);

        // Kompletten Frame in einen einzigen String-Buffer schreiben (0 Flackern)
        int offset = snprintf(render_buffer, sizeof(render_buffer),
            "\033[H========================================================================================================================\n"
            "  pTRC 3D REALTIME CRYSTAL ENGINE | 10.000 PARTIKEL IN Z^3 | TAKT: %03u/%03u | STROM (+1): %2u | WIRBEL (+3): %4u\n"
            "========================================================================================================================\n",
            frame, total_frames, streams, vortices);

        for (int y = 0; y < VIEW_H; y++) {
            memcpy(render_buffer + offset, screen_grid[y], VIEW_W);
            offset += VIEW_W;
            render_buffer[offset++] = '\n';
        }
        offset += snprintf(render_buffer + offset, sizeof(render_buffer) - offset,
            "========================================================================================================================\n");

        fwrite(render_buffer, 1, (size_t)offset, stdout);
        fflush(stdout);

        // 16 ms Pause für flüssige 60 FPS Darstellung
        usleep(16000);
    }

    // Terminal wiederherstellen & Messwerte ausgeben
    printf("\033[?25h\033[?1049l");
    uint64_t avg_us = (total_compute_ns / total_frames) / 1000;
    printf("[ pTRC 3D LIVE ENGINE ] 300 Frames mit je 10.000 3D-Partikeln gerendert.\n");
    printf(" -> Durchschnittliche Physik- & Projektionszeit pro Frame: %" PRIu64 " Mikrosekunden!\n", avg_us);

    return 0;
}
