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

#ifndef PTRC_GAME_COLLISION_H
#define PTRC_GAME_COLLISION_H

#include "../graphics/ptrc_light_universe.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PTRC_GC_OK                  1
#define PTRC_GC_ERR                 (-1)
#define PTRC_GC_LOCKSTEP_VALID      1

typedef struct {
    ptrc_gfx_ctx_t sim;
    uint64_t       total_collisions;
    uint64_t       rigid_pyramid_hits;
    uint64_t       rigid_sphere_hits;
    uint64_t       particle_collisions;
    uint64_t       tunneling_escapes;
    uint64_t       lockstep_state_hash;
    uint32_t       active_rigid_bodies;
    uint32_t       active_crystal_nodes;
} ptrc_gc_world_t;

int      ptrc_gc_init(ptrc_gc_world_t *world, uint64_t seed);
int      ptrc_gc_step_tick(ptrc_gc_world_t *world);
uint64_t ptrc_gc_compute_lockstep_hash(const ptrc_gc_world_t *world);
int      ptrc_gc_render_rgb24(ptrc_gc_world_t *world, uint32_t width, uint32_t height, uint8_t *rgb_out);
void     ptrc_gc_wipe(ptrc_gc_world_t *world);

#ifdef __cplusplus
}
#endif

#endif /* PTRC_GAME_COLLISION_H */
