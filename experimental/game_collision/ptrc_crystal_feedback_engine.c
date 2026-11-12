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
#include <stdint.h>
#include <inttypes.h>
#include <time.h>

#define CONTACT_JUNCTIONS 24
#define FREE_FACETS       120
#define TOTAL_FACETS      144
#define MOD_PRIMORIAL     210
#define NUM_OBJECTS       10000

// Flaches 1D-Register: Strikte bipolare Zustände (-1 = Frei, +1 = Aktiver Impuls)
static int8_t crystal_register[TOTAL_FACETS];

// Die 12 Grundrichtungen aus der 1+12 Kristallstruktur
static const int8_t BASE_12_DIRS[12][3] = {
    { 2,  1, 0}, { 2, -1, 0}, {-2,  1, 0}, {-2, -1, 0},
    { 0,  2, 1}, { 0,  2, -1}, { 0, -2, 1}, { 0, -2, -1},
    { 1,  0, 2}, {-1,  0, 2}, { 1,  0, -2}, {-1,  0, -2}
};

typedef struct {
    int32_t pos_phase;   // Aktuelle Position im Primorial-Ring (1..210)
    uint8_t axis_id;     // Aktive Bewegungsachse (0..11)
    int8_t  state;       // Bipolarer Zustand: -1 (frei) oder +1 (Rückkopplungs-Impuls)
} CrystalAgent;

static CrystalAgent agents[NUM_OBJECTS];

void init_bipolar_lattice(void) {
    for (uint16_t i = 0; i < TOTAL_FACETS; i++) {
        crystal_register[i] = -1;
    }

    for (uint32_t i = 0; i < NUM_OBJECTS; i++) {
        agents[i].pos_phase = (int32_t)((i * 13 + 7) % MOD_PRIMORIAL);
        if (agents[i].pos_phase <= 0) agents[i].pos_phase = 1;
        agents[i].axis_id   = (uint8_t)(i % 12);
        agents[i].state     = -1;
    }
}

// Schritt 2: Kollisionsprüfung MIT aktiver Rückkopplung der 120 Kristallflächen
uint32_t step_crystal_feedback_takt(uint32_t system_takt) {
    uint32_t feedback_events = 0;

    for (uint32_t i = 0; i < NUM_OBJECTS; i++) {
        uint8_t ax = agents[i].axis_id;
        int32_t dir_step = BASE_12_DIRS[ax][0] + BASE_12_DIRS[ax][1] + BASE_12_DIRS[ax][2];
        if (dir_step == 0) dir_step = -1; // Gekreuzter Spiegel (-1 statt 0)

        // Vorschub im 210er Primorial-Ring (ohne Null)
        int32_t next_pos = (agents[i].pos_phase + dir_step + (int32_t)(system_takt % CONTACT_JUNCTIONS)) % MOD_PRIMORIAL;
        if (next_pos <= 0) next_pos += MOD_PRIMORIAL;
        agents[i].pos_phase = next_pos;

        uint8_t junction_idx = (uint8_t)(next_pos % CONTACT_JUNCTIONS);
        uint8_t facet_idx    = (uint8_t)(CONTACT_JUNCTIONS + ((next_pos * 5) % FREE_FACETS));

        // Prüfen, ob Kontaktstelle UND Kristallfacette geladen (+1) sind
        if (crystal_register[junction_idx] == 1 && crystal_register[facet_idx] == 1) {
            // 1. KOLLISION & RÜCKKOPPLUNG (+1)
            agents[i].state = 1;
            feedback_events++;

            // 2. KRISTALLFLÄCHE GIBT IMPULS ZURÜCK: Richtungsachse wird über den 12er-Ring gespiegelt
            agents[i].axis_id = (uint8_t)((ax + (junction_idx % 11) + 1) % 12);

            // 3. ENTLADUNG INS SYSTEM: Facette gibt ihre Ladung ab und wird wieder frei (-1)
            crystal_register[facet_idx] = -1;
        } else {
            // Freier Durchgang (-1): Objekt speichert seine Information in Kontaktstelle und Facette (+1)
            agents[i].state = -1;
            crystal_register[junction_idx] = 1;
            crystal_register[facet_idx]    = 1;
        }
    }

    return feedback_events;
}

int main(void) {
    init_bipolar_lattice();

    struct timespec t_start, t_end;
    uint64_t total_feedbacks = 0;
    uint32_t test_takts = 1000;

    printf("=================================================================\n");
    printf("  pTRC CRYSTAL FEEDBACK ENGINE // 10.000 OBJEKTE + RUECKKOPPLUNG\n");
    printf("  144-Facetten-Reflexion | Aktive Impuls-Rueckgabe ins System\n");
    printf("=================================================================\n");

    clock_gettime(CLOCK_MONOTONIC, &t_start);

    for (uint32_t takt = 1; takt <= test_takts; takt++) {
        total_feedbacks += step_crystal_feedback_takt(takt);
    }

    clock_gettime(CLOCK_MONOTONIC, &t_end);

    uint64_t elapsed_ns = (uint64_t)(t_end.tv_sec - t_start.tv_sec) * 1000000000ULL
                        + (uint64_t)(t_end.tv_nsec - t_start.tv_nsec);
    uint64_t ns_per_takt = elapsed_ns / test_takts;
    uint64_t us_per_takt = ns_per_takt / 1000;

    printf("  Simulierte Takte        : %u (jeweils 10.000 Objekte)\n", test_takts);
    printf("  Rueckkopplungs-Impulse  : %" PRIu64 " (dynamische Richtungswechsel)\n", total_feedbacks);
    printf("  Zeit pro Komplett-Takt  : %" PRIu64 " Mikrosekunden (%" PRIu64 " ns)\n", us_per_takt, ns_per_takt);
    printf("  Moegliche Takte/Sekunde : %" PRIu64 " FPS\n", (ns_per_takt > 0) ? (1000000000ULL / ns_per_takt) : 0);
    printf("=================================================================\n");

    return 0;
}
