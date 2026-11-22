/* ==============================================================================
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
 * ============================================================================== */

#include "ptrc_game_collision.h"

static inline int32_t ptrc_gc_abs32(int32_t v) {
    return (v < 0) ? -v : v;
}

uint64_t ptrc_gc_compute_lockstep_hash(const ptrc_gc_world_t *world) {
    if (!world) return 1ULL;

    /* Deterministischer 64-Bit Primorial-FNV-Hash ueber alle 60.000 Koerper (Z \ {0}) */
    uint64_t h = 14695981039346656037ULL ^ world->sim.takt_counter;
    for (uint32_t i = 0U; i < PTRC_WIND_AGENTS; i++) {
        const ptrc_wind_agent_t *ag = &world->sim.agents[i];
        uint64_t packed = ((uint64_t)(uint16_t)ag->x) |
                          (((uint64_t)(uint16_t)ag->y) << 16U) |
                          (((uint64_t)(uint16_t)ag->z) << 32U) |
                          (((uint64_t)ag->state_byte) << 48U);
        h ^= packed;
        h *= 1099511628211ULL;
    }
    return (h == 0ULL) ? 1ULL : h;
}

int ptrc_gc_init(ptrc_gc_world_t *world, uint64_t seed) {
    if (!world) return PTRC_GC_ERR;

    if (ptrc_gfx_init(&world->sim, seed) != PTRC_GFX_OK) {
        return PTRC_GC_ERR;
    }

    world->total_collisions = 0ULL;
    world->rigid_pyramid_hits = 0ULL;
    world->rigid_sphere_hits = 0ULL;
    world->particle_collisions = 0ULL;
    world->tunneling_escapes = 0ULL;
    world->active_rigid_bodies = 2U; /* Rotierende 3D-Kristallpyramide + 3D-Kristallkugel */
    world->active_crystal_nodes = PTRC_WIND_AGENTS * PTRC_GFX_CLUSTER_13;
    world->lockstep_state_hash = ptrc_gc_compute_lockstep_hash(world);
    return PTRC_GC_OK;
}

int ptrc_gc_step_tick(ptrc_gc_world_t *world) {
    if (!world) return PTRC_GC_ERR;

    uint32_t prev_deflections = world->sim.deflection_count;
    if (ptrc_gfx_step_takt_adaptive(&world->sim) != PTRC_GFX_OK) {
        return PTRC_GC_ERR;
    }

    uint32_t tick_collisions = world->sim.deflection_count - prev_deflections;
    uint32_t pyr_hits = 0U;
    uint32_t sph_hits = 0U;
    uint32_t escapes = 0U;

    for (uint32_t i = 0U; i < PTRC_WIND_AGENTS; i++) {
        const ptrc_wind_agent_t *ag = &world->sim.agents[i];
        int32_t ax = (int32_t)ag->x;
        int32_t ay = (int32_t)ag->y;
        int32_t az = (int32_t)ag->z;

        /* 0-Tunneling-Invariante: kein Koerper darf den Kanal verlassen oder 0 treffen */
        if (ax == 0 || ay == 0 || az == 0 ||
            ptrc_gc_abs32(ax) > PTRC_TUNNEL_HALF_X ||
            ptrc_gc_abs32(ay) > PTRC_TUNNEL_HALF_Y ||
            ptrc_gc_abs32(az) > PTRC_TUNNEL_HALF_Z) {
            escapes++;
        }

        /* Klassifikation der Rigid-Body-Treffer anhand des optischen Kaskaden-Registers */
        uint8_t opt = (uint8_t)((ag->state_byte >> 5U) & 3U);
        if (opt == PTRC_OPTICS_FIELD_COUPLED && ag->vx == 1 && (pyr_hits + sph_hits) < tick_collisions) {
            pyr_hits++;
        } else if (opt == PTRC_OPTICS_CRYSTALLINE && ag->vx == 1 && (pyr_hits + sph_hits) < tick_collisions) {
            sph_hits++;
        }
    }

    uint64_t rigid_sum = (uint64_t)pyr_hits + (uint64_t)sph_hits;
    uint64_t part_sum = ((uint64_t)tick_collisions > rigid_sum)
                        ? ((uint64_t)tick_collisions - rigid_sum)
                        : 0ULL;

    world->total_collisions += (uint64_t)tick_collisions;
    world->rigid_pyramid_hits += (uint64_t)pyr_hits;
    world->rigid_sphere_hits += (uint64_t)sph_hits;
    world->particle_collisions += part_sum;
    world->tunneling_escapes += (uint64_t)escapes;
    world->lockstep_state_hash = ptrc_gc_compute_lockstep_hash(world);
    return PTRC_GC_OK;
}

int ptrc_gc_render_rgb24(ptrc_gc_world_t *world, uint32_t width, uint32_t height, uint8_t *rgb_out) {
    if (!world) return PTRC_GC_ERR;
    return ptrc_gfx_render_observer_rgb24(&world->sim, width, height, rgb_out);
}

void ptrc_gc_wipe(ptrc_gc_world_t *world) {
    if (!world) return;
    ptrc_gfx_wipe(&world->sim);
    volatile uint8_t *p = (volatile uint8_t *)world;
    for (size_t i = 0U; i < sizeof(*world); i++) {
        p[i] = 0xFFU;
    }
}
