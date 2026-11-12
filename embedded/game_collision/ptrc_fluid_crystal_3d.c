#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <time.h>

#define CONTACT_JUNCTIONS 24
#define FREE_FACETS       120
#define TOTAL_FACETS      144
#define MOD_PRIMORIAL     210
#define NUM_OBJECTS       10000

// Flaches 144-Facetten-Register ohne Null:
// -1 = Frei | +1 = Primärer Strom (>) | +3 = Abgelenkter Wirbel-Impuls (x)
static int8_t crystal_register[TOTAL_FACETS];

// Die 12 Grundrichtungen aus der 1+12 Kristallstruktur (3D-Vektoren)
static const int8_t BASE_12_DIRS[12][3] = {
    { 2,  1, 0}, { 2, -1, 0}, {-2,  1, 0}, {-2, -1, 0},
    { 0,  2, 1}, { 0,  2, -1}, { 0, -2, 1}, { 0, -2, -1},
    { 1,  0, 2}, {-1,  0, 2}, { 1,  0, -2}, {-1,  0, -2}
};

typedef struct {
    int32_t pos_phase;   // Position im 210er Ring (1..210)
    uint8_t axis_id;     // Aktive 3D-Kristallachse (0..11)
    int8_t  flow_state;  // -1 (Frei), +1 (Strom), +3 (Wirbel-Kaskade)
} CrystalParticle;

static CrystalParticle particles[NUM_OBJECTS];

void init_crystal_fluid(void) {
    for (uint16_t f = 0; f < TOTAL_FACETS; f++) {
        crystal_register[f] = -1;
    }

    for (uint32_t i = 0; i < NUM_OBJECTS; i++) {
        particles[i].pos_phase  = (int32_t)((i * 13 + 7) % MOD_PRIMORIAL);
        if (particles[i].pos_phase <= 0) particles[i].pos_phase = 1;
        particles[i].axis_id    = (uint8_t)(i % 12);
        particles[i].flow_state = 1; // Startet als primärer Strom (+1)
    }
}

// Überträgt deine Kaskaden-Logik aus fluid_resonance.py auf den 3D-144-Facetten-Kristall
void step_crystal_cascade(uint32_t step, uint32_t *out_primary, uint32_t *out_vortex) {
    uint32_t primary_moves = 0;
    uint32_t vortex_cascades = 0;

    // Register-Maske für den aktuellen Takt auf -1 (Frei) setzen
    for (uint16_t f = 0; f < TOTAL_FACETS; f++) {
        crystal_register[f] = -1;
    }

    for (uint32_t i = 0; i < NUM_OBJECTS; i++) {
        uint8_t ax = particles[i].axis_id;
        int32_t dir_step = BASE_12_DIRS[ax][0] + BASE_12_DIRS[ax][1] + BASE_12_DIRS[ax][2];
        if (dir_step == 0) dir_step = -1; // Gekreuzter Spiegel (-1 statt 0)

        // Primäres Ziel im 210er Ring berechnen
        int32_t nx = (particles[i].pos_phase + dir_step + (int32_t)(step % CONTACT_JUNCTIONS)) % MOD_PRIMORIAL;
        if (nx <= 0) nx += MOD_PRIMORIAL;

        uint8_t j_idx = (uint8_t)(nx % CONTACT_JUNCTIONS);
        uint8_t f_idx = (uint8_t)(CONTACT_JUNCTIONS + ((nx * 5) % FREE_FACETS));

        // 1. PRÜFUNG: Ist der primäre Ziel-Slot frei (-1)?
        if (crystal_register[j_idx] == -1) {
            crystal_register[j_idx] = 1;
            particles[i].pos_phase  = nx;
            particles[i].flow_state = 1; // Fließt ungestört als Strom (+1)
            primary_moves++;
        } 
        // 2. KASKADE (wie in fluid_resonance.py): Primärweg blockiert -> Ausweichen über die 120 Kristallfacetten!
        else {
            // Spiegel-Symmetrie über die Kristallachse (Ausweich-Kaskade)
            uint8_t alt_ax = (uint8_t)((ax + (step % 11) + 1) % 12);
            int32_t alt_step = BASE_12_DIRS[alt_ax][0] - BASE_12_DIRS[alt_ax][1] + BASE_12_DIRS[alt_ax][2];
            if (alt_step == 0) alt_step = -1;

            int32_t ny_cascade = (nx + alt_step) % MOD_PRIMORIAL;
            if (ny_cascade <= 0) ny_cascade += MOD_PRIMORIAL;

            uint8_t cascade_facet = (uint8_t)(CONTACT_JUNCTIONS + ((ny_cascade * 7) % FREE_FACETS));

            // Impuls wird an die freie Facette weitergegeben -> Teilchen wird zum Wirbel (+3)
            crystal_register[cascade_facet] = 3;
            particles[i].pos_phase  = ny_cascade;
            particles[i].axis_id    = alt_ax;
            particles[i].flow_state = 3;
            vortex_cascades++;
        }
    }

    *out_primary = primary_moves;
    *out_vortex  = vortex_cascades;
}

int main(void) {
    init_crystal_fluid();

    struct timespec t_start, t_end;
    uint64_t sum_primary = 0;
    uint64_t sum_vortex  = 0;
    uint32_t test_takts  = 1000;

    printf("=================================================================\n");
    printf("  pTRC 3D CRYSTAL FLUID ENGINE // KASKADEN-KOLLISIONS-WEITERGABE\n");
    printf("  10.000 Partikel | 144-Facetten-Register | Null-frei (-1/+1/+3)\n");
    printf("=================================================================\n");

    clock_gettime(CLOCK_MONOTONIC, &t_start);

    for (uint32_t takt = 1; takt <= test_takts; takt++) {
        uint32_t p_cnt = 0, v_cnt = 0;
        step_crystal_cascade(takt, &p_cnt, &v_cnt);
        sum_primary += p_cnt;
        sum_vortex  += v_cnt;
    }

    clock_gettime(CLOCK_MONOTONIC, &t_end);

    uint64_t elapsed_ns = (uint64_t)(t_end.tv_sec - t_start.tv_sec) * 1000000000ULL
                        + (uint64_t)(t_end.tv_nsec - t_start.tv_nsec);
    uint64_t ns_per_takt = elapsed_ns / test_takts;
    uint64_t us_per_takt = ns_per_takt / 1000;

    printf("  Simulierte Takte          : %u (jeweils 10.000 Partikel)\n", test_takts);
    printf("  Direkte Stroeme (+1)      : %" PRIu64 "\n", sum_primary);
    printf("  Wirbel-Kaskaden (+3)      : %" PRIu64 " (umgelenkte Kollisionen)\n", sum_vortex);
    printf("  Zeit pro Komplett-Takt    : %" PRIu64 " Mikrosekunden (%" PRIu64 " ns)\n", us_per_takt, ns_per_takt);
    printf("  Moegliche Takte/Sekunde   : %" PRIu64 " FPS\n", (ns_per_takt > 0) ? (1000000000ULL / ns_per_takt) : 0);
    printf("=================================================================\n");

    return 0;
}
