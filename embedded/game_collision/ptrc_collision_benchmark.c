#include <stdio.h>
#include <stdint.h>
#include <time.h>

// --- pTRC 144-FACETTEN KRISTALL-ARCHITEKTUR ---
#define CONTACT_JUNCTIONS 24
#define FREE_FACETS       120
#define TOTAL_FACETS      144
#define MOD_PRIMORIAL     210
#define NUM_OBJECTS       10000

// Flaches 1D-Register: Strikte bipolare Zustände (-1 = Frei, +1 = Kontakt)
// Keine 0 im gesamten Zustandsraum!
static int8_t crystal_register[TOTAL_FACETS];

// Die 12 Grundrichtungen aus deiner 1+12 Kristallstruktur
static const int8_t BASE_12_DIRS[12][3] = {
    { 2,  1, 0}, { 2, -1, 0}, {-2,  1, 0}, {-2, -1, 0},
    { 0,  2, 1}, { 0,  2, -1}, { 0, -2, 1}, { 0, -2, -1},
    { 1,  0, 2}, {-1,  0, 2}, { 1,  0, -2}, {-1,  0, -2}
};

// Kompakte Objektstruktur (reine Ganzzahlen)
typedef struct {
    int32_t pos_phase;   // Aktuelle Position im Primorial-Ring (Modulo 210)
    uint8_t axis_id;     // Aktive Bewegungsachse (0..11)
    int8_t  state;       // Bipolarer Zustand: -1 (frei) oder +1 (Kollision)
} CrystalAgent;

static CrystalAgent agents[NUM_OBJECTS];

// Initialisiert das System komplett null-frei auf -1
void init_bipolar_lattice(void) {
    for (uint16_t i = 0; i < TOTAL_FACETS; i++) {
        crystal_register[i] = -1;
    }

    for (uint32_t i = 0; i < NUM_OBJECTS; i++) {
        agents[i].pos_phase = (int32_t)((i * 13 + 7) % MOD_PRIMORIAL);
        if (agents[i].pos_phase == 0) agents[i].pos_phase = -1; // Null-Bann
        agents[i].axis_id   = (uint8_t)(i % 12);
        agents[i].state     = -1;
    }
}

// Führt einen kompletten Physik- & Kollisionstakt für alle 10.000 Objekte aus
uint32_t step_bipolar_collision_takt(uint32_t system_takt) {
    uint32_t active_collisions = 0;

    // 1. Register für den neuen Takt auf bipolares "Frei" (-1) zurücksetzen
    for (uint16_t f = 0; f < TOTAL_FACETS; f++) {
        crystal_register[f] = -1;
    }

    // 2. Alle 10.000 Objekte durch die 24 Kontaktstellen & 120 Facetten schieben
    for (uint32_t i = 0; i < NUM_OBJECTS; i++) {
        uint8_t ax = agents[i].axis_id;
        int32_t dir_step = BASE_12_DIRS[ax][0] + BASE_12_DIRS[ax][1] + BASE_12_DIRS[ax][2];
        if (dir_step == 0) dir_step = -1; // Gekreuzter Spiegel (-1 statt 0)

        // Ganzzahl-Vorschub im 210er Ring
        int32_t next_pos = (agents[i].pos_phase + dir_step + (int32_t)(system_takt % CONTACT_JUNCTIONS)) % MOD_PRIMORIAL;
        if (next_pos <= 0) next_pos += MOD_PRIMORIAL;
        agents[i].pos_phase = next_pos;

        // Abbildung auf Kontaktstelle (0..23) und Facette (24..143)
        uint8_t junction_idx = (uint8_t)(next_pos % CONTACT_JUNCTIONS);
        uint8_t facet_idx    = (uint8_t)(CONTACT_JUNCTIONS + ((next_pos * 5) % FREE_FACETS));

        // Bipolare Prüfung: Steht hier bereits ein +1 im Kristall?
        if (crystal_register[junction_idx] == 1 && crystal_register[facet_idx] == 1) {
            // KOLLISION (+1) erkannt!
            agents[i].state = 1;
            active_collisions++;
        } else {
            // Freier Durchgang (-1), aber Objekt markiert jetzt diesen Slot mit +1
            agents[i].state = -1;
            crystal_register[junction_idx] = 1;
            crystal_register[facet_idx]    = 1;
        }
    }

    return active_collisions;
}

int main(void) {
    init_bipolar_lattice();

    struct timespec t_start, t_end;
    uint32_t total_hits = 0;
    uint32_t test_takts = 1000;

    printf("=================================================================\n");
    printf("  pTRC BIPOLAR COLLISION ENGINE // 10.000 OBJEKTE BENCHMARK\n");
    printf("  Architektur: 144-Facetten-Kristall | Null-freie (-1/+1) Logik\n");
    printf("=================================================================\n");

    clock_gettime(CLOCK_MONOTONIC, &t_start);

    for (uint32_t takt = 1; takt <= test_takts; takt++) {
        total_hits += step_bipolar_collision_takt(takt);
    }

    clock_gettime(CLOCK_MONOTONIC, &t_end);

    // Exakte Berechnung in Nanosekunden (reine Ganzzahlen)
    uint64_t elapsed_ns = (uint64_t)(t_end.tv_sec - t_start.tv_sec) * 1000000000ULL
                        + (uint64_t)(t_end.tv_nsec - t_start.tv_nsec);
    uint64_t ns_per_takt = elapsed_ns / test_takts;
    uint64_t us_per_takt = ns_per_takt / 1000;

    printf("  Simulierte Takte        : %u (jeweils 10.000 Objekte)\n", test_takts);
    printf("  Erkannte (+1) Kontakte  : %u\n", total_hits);
    printf("  Zeit pro Komplett-Takt  : %lu Mikrosekunden (%lu ns)\n", us_per_takt, ns_per_takt);
    printf("  Moegliche Takte/Sekunde : %lu FPS\n", (ns_per_takt > 0) ? (1000000000ULL / ns_per_takt) : 0);
    printf("=================================================================\n");

    return 0;
}
