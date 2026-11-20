/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Observer Windtunnel v4.5.0
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

#include "ptrc_light_universe.h"
#include <stdlib.h>

static const uint32_t PTRC_GFX_RINGS[PTRC_GFX_PRIME_RINGS] = {
    11U, 13U, 17U, 19U, 23U, 29U, 37U, 41U,
    43U, 47U, 53U, 59U, 61U, 67U, 71U, 73U
};

static const int8_t PTRC_JUNCTION_DIRS_24[PTRC_GFX_JUNCTIONS] = {
    { 1,  1, -1}, { 1, -1, -1}, {-1,  1, -1}, {-1, -1, -1},
    { 1,  1,  1}, { 1, -1,  1}, {-1,  1,  1}, {-1, -1,  1},
    { 2,  1, -1}, { 2, -1, -1}, {-2,  1, -1}, {-2, -1, -1},
    {-1,  2,  1}, {-1,  2, -1}, {-1, -2,  1}, {-1, -2, -1},
    { 1, -1,  2}, {-1, -1,  2}, { 1, -1, -2}, {-1, -1, -2},
    { 2,  1,  1}, {-2, -1,  1}, { 1,  2,  1}, {-1, -2, -1}
};

static const int32_t PTRC_CLOCK24_U[PTRC_GFX_JUNCTIONS] = {
    1000,  966,  866,  707,  500,  259,
      -1, -259, -500, -707, -866, -966,
   -1000, -966, -866, -707, -500, -259,
       1,  259,  500,  707,  866,  966
};

static const int32_t PTRC_CLOCK24_V[PTRC_GFX_JUNCTIONS] = {
       1,  259,  500,  707,  866,  966,
    1000,  966,  866,  707,  500,  259,
      -1, -259, -500, -707, -866, -966,
   -1000, -966, -866, -707, -500, -259
};

static inline int32_t ptrc_z_no_zero(int32_t v) {
    return (v == 0) ? -1 : v;
}

/* Symmetrischer Plichta-Spiegel ohne Aufwaerts-Drift: wechselt zwischen -1 und +1 */
static inline int32_t ptrc_z_sym_no_zero(int32_t v, uint32_t parity) {
    if (v != 0) return v;
    return ((parity & 1U) == 0U) ? 1 : -1;
}

static inline uint8_t ptrc_u8_no_zero(uint8_t v) {
    return (v == 0U) ? 0xFFU : v;
}

static inline uint64_t ptrc_u64_no_zero(uint64_t v) {
    return (v == 0ULL) ? 1ULL : v;
}

static inline int32_t ptrc_abs32(int32_t x) {
    return (x < 0) ? -x : x;
}

static inline int32_t ptrc_plichta_move(int32_t pos, int32_t delta) {
    int32_t nxt = pos + delta;
    if (nxt == 0) {
        nxt = (delta >= 0) ? 1 : -1;
    }
    return nxt;
}

static inline uint32_t ptrc_fcc_slot_hash(int32_t x, int32_t y, int32_t z) {
    uint32_t qx = (uint32_t)((x + 1024) / 4);
    uint32_t qy = (uint32_t)((y + 1024) / 4);
    uint32_t qz = (uint32_t)((z + 1024) / 4);
    uint32_t h = (qx * 73856093U) ^ (qy * 19349663U) ^ (qz * 83492791U);
    return h & (PTRC_OCCUPANCY_SLOTS - 1U);
}

static inline uint8_t ptrc_encode_1byte_cascade(
    uint8_t cascade_anchor,
    uint8_t optics_mode,
    uint8_t wavelength_id
) {
    uint8_t wl = (uint8_t)(((wavelength_id - 1U) & 30U) + 1U);
    uint8_t opt = (uint8_t)(optics_mode & 3U);
    uint8_t anc = (uint8_t)(cascade_anchor & 1U);
    return ptrc_u8_no_zero((uint8_t)((anc << 7U) | (opt << 5U) | wl));
}

/* Exakte 4-seitige quadratische Pyramide (scharfe Spitze oben, ebene Basis unten)
 * Rotiert um die vertikale Y-Achse und leicht geneigt um X, raeumlich mittig bei Z = 1 */
static int ptrc_point_in_square_pyramid(
    int32_t px,
    int32_t py,
    int32_t pz,
    int32_t rot_u,
    int32_t rot_v
) {
    int32_t dx = px - PTRC_PYRAMID_CENTER_X;
    int32_t dy = py;
    int32_t dz = pz;

    if (ptrc_abs32(dx) > 190 || ptrc_abs32(dy) > 190 || ptrc_abs32(dz) > 190) {
        return 0;
    }

    /* Leichte 3D-Kippung (ca. 15 Grad), damit man die Pyramide raeumlich plastisch sieht */
    int32_t ty = (dy * 966 - dz * 259) >> 10;
    int32_t tz = (dy * 259 + dz * 966) >> 10;

    /* Rotation um die Pyramiden-Hochachse */
    int32_t lx = (dx * rot_u - tz * rot_v) >> 10;
    int32_t lz = (dx * rot_v + tz * rot_u) >> 10;

    /* Pyramiden-Koordinaten: Spitze bei ty = -110 (oben), Basis bei ty = +110 (unten) */
    int32_t half_h = PTRC_PYRAMID_HEIGHT >> 1; /* 110 */
    if (ty < -half_h || ty > half_h) {
        return 0;
    }

    /* Lineare Verjuengung von der quadratischen Basis (120) bis zur scharfen Spitze (0) */
    int32_t allowed_half_width = ((ty + half_h) * PTRC_PYRAMID_HALF_BASE) / PTRC_PYRAMID_HEIGHT;
    if (ptrc_abs32(lx) <= allowed_half_width && ptrc_abs32(lz) <= allowed_half_width) {
        return 1;
    }
    return 0;
}

static void ptrc_transpose_wavelength_to_rgb(
    uint8_t state_byte,
    int32_t depth_shade,
    uint8_t *r_out,
    uint8_t *g_out,
    uint8_t *b_out
) {
    uint32_t wl = (uint32_t)(state_byte & 0x1FU);
    uint32_t opt = (uint32_t)((state_byte >> 5U) & 3U);

    uint32_t r = (((wl * 7U + opt * 41U) & 0xFFU) * (uint32_t)depth_shade) >> 8U;
    uint32_t g = ((((32U - wl) * 6U + opt * 37U + 40U) & 0xFFU) * (uint32_t)depth_shade) >> 8U;
    uint32_t b = (((110U + wl * 4U + opt * 23U) & 0xFFU) * (uint32_t)depth_shade) >> 8U;

    *r_out = (r == 0U) ? 1U : (uint8_t)r;
    *g_out = (g == 0U) ? 1U : (uint8_t)g;
    *b_out = (b == 0U) ? 1U : (uint8_t)b;
}

int ptrc_gfx_init(ptrc_gfx_ctx_t *ctx, uint64_t seed) {
    if (!ctx) return PTRC_GFX_ERR;

    uint64_t rng = ptrc_u64_no_zero(seed ^ 614889782588491410ULL);

    for (uint32_t r = 0U; r < PTRC_GFX_PRIME_RINGS; r++) {
        ctx->prime_rings[r] = PTRC_GFX_RINGS[r];
    }

    for (uint32_t f = 0U; f < PTRC_GFX_FACETS; f++) {
        rng = ptrc_u64_no_zero((rng * 137ULL + (uint64_t)(f + 1U) * 211ULL) ^ (rng >> 13U));
        int32_t raw = (int32_t)(rng % PTRC_GFX_PRIMORIAL_210) - 105;
        ctx->sponge[f] = ptrc_z_no_zero(raw);
    }

    for (uint32_t s = 0U; s < PTRC_OCCUPANCY_SLOTS; s++) {
        ctx->cell_impulse[s] = 1U;
        ctx->cell_density[s] = 1U;
    }

    /* 60.000 Luftmolekuel-Agenten gleichmaessig im gesamten 32x18x8cm Kanal verteilen */
    for (uint32_t a = 0U; a < PTRC_WIND_AGENTS; a++) {
        rng = ptrc_u64_no_zero(rng * 6364136223846793005ULL + 1442695040888963407ULL);
        int32_t rx = (int32_t)(rng % (uint64_t)(PTRC_TUNNEL_HALF_X * 2)) - PTRC_TUNNEL_HALF_X;
        int32_t ry = (int32_t)((rng >> 16U) % (uint64_t)(PTRC_TUNNEL_HALF_Y * 2)) - PTRC_TUNNEL_HALF_Y;
        int32_t rz = (int32_t)((rng >> 32U) % (uint64_t)(PTRC_TUNNEL_HALF_Z * 2)) - PTRC_TUNNEL_HALF_Z;

        int32_t x = ptrc_z_sym_no_zero(rx, a);
        int32_t y = ptrc_z_sym_no_zero(ry, a >> 1U);
        int32_t z = ptrc_z_sym_no_zero(rz, a >> 2U);
        if (((x + y + z) & 1) != 0) {
            x = ptrc_plichta_move(x, 1);
        }

        uint8_t wl = (uint8_t)((a % 16U) + 1U);
        uint8_t opt = (uint8_t)((a % 3U) + 1U);

        ctx->agents[a].x = (int16_t)x;
        ctx->agents[a].y = (int16_t)y;
        ctx->agents[a].z = (int16_t)z;
        /* Laminare Hauptstroemung exakt horizontal nach rechts (+X), Y/Z im Mittel 0 */
        ctx->agents[a].vx = (int16_t)(7 + (int32_t)(a & 3U));
        ctx->agents[a].vy = (int16_t)(((a & 1U) == 0U) ? 1 : -1);
        ctx->agents[a].vz = (int16_t)((((a >> 1U) & 1U) == 0U) ? 1 : -1);
        ctx->agents[a].impulse = (uint8_t)(40U + (a % 180U));
        ctx->agents[a].state_byte = ptrc_encode_1byte_cascade((uint8_t)(a & 1U), opt, wl);
    }

    ctx->takt_counter = 1ULL;
    ctx->clock_phase_24 = 1U;
    ctx->observer_sub_takt = 1U;
    ctx->pyramid_angle_idx = 0U;
    ctx->active_load = 1024U;
    ctx->render_interval_takts = PTRC_GFX_TAKT_137;
    ctx->last_render_takt = 1U;
    ctx->deflection_count = 1U;
    ctx->mirror_pulses = 1U;
    ctx->render_status = PTRC_RENDER_READY;
    return PTRC_GFX_OK;
}

int ptrc_gfx_step_takt(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) return PTRC_GFX_ERR;

    uint32_t phase_idx = (ctx->clock_phase_24 - 1U) % PTRC_GFX_JUNCTIONS;
    uint32_t p_ring = ctx->prime_rings[phase_idx & 15U];

    for (uint32_t j = 0U; j < PTRC_GFX_JUNCTIONS; j++) {
        uint32_t jf = PTRC_GFX_MEM_FACETS + j;
        uint32_t mf = (j * 5U + phase_idx) % PTRC_GFX_MEM_FACETS;
        int32_t coupled = ctx->sponge[jf] ^ ctx->sponge[mf];
        ctx->sponge[jf] = ptrc_z_no_zero(coupled + (int32_t)p_ring);
    }

    if ((ctx->takt_counter % PTRC_GFX_TAKT_137) == 0ULL) {
        for (uint32_t f = 0U; f < PTRC_GFX_FACETS; f++) {
            ctx->sponge[f] = ptrc_z_no_zero(~ctx->sponge[f]);
        }
        ctx->mirror_pulses++;
    }

    uint32_t rot_idx = (uint32_t)((ctx->takt_counter / 4ULL) % PTRC_GFX_JUNCTIONS);
    ctx->pyramid_angle_idx = rot_idx;
    int32_t rot_u = PTRC_CLOCK24_U[rot_idx];
    int32_t rot_v = PTRC_CLOCK24_V[rot_idx];

    for (uint32_t s = 0U; s < PTRC_OCCUPANCY_SLOTS; s++) {
        ctx->cell_impulse[s] = 1U;
        ctx->cell_density[s] = 1U;
    }

    uint32_t collisions = 0U;
    uint32_t pyramid_hits = 0U;

    for (uint32_t a = 0U; a < PTRC_WIND_AGENTS; a++) {
        ptrc_wind_agent_t *ag = &ctx->agents[a];
        uint32_t sym_bit = a + (uint32_t)ctx->takt_counter;

        int32_t nx = ptrc_plichta_move((int32_t)ag->x, (int32_t)ag->vx);
        int32_t ny = ptrc_plichta_move((int32_t)ag->y, (int32_t)ag->vy);
        int32_t nz = ptrc_plichta_move((int32_t)ag->z, (int32_t)ag->vz);

        /* Kontinuierlicher Ausstrom rechts (+960) & frischer laminarer Einstrom links (-960) */
        if (nx > PTRC_TUNNEL_HALF_X) {
            uint64_t mix = (uint64_t)a * 2654435761ULL + ctx->takt_counter * 137ULL;
            nx = -PTRC_TUNNEL_HALF_X + (int32_t)(mix & 7ULL) + 1;
            ny = ptrc_z_sym_no_zero((int32_t)((mix >> 8U) % (uint64_t)(PTRC_TUNNEL_HALF_Y * 2)) - PTRC_TUNNEL_HALF_Y, a);
            nz = ptrc_z_sym_no_zero((int32_t)((mix >> 24U) % (uint64_t)(PTRC_TUNNEL_HALF_Z * 2)) - PTRC_TUNNEL_HALF_Z, a >> 1U);
            ag->vx = (int16_t)(7 + (int32_t)((a + p_ring) & 3U));
            ag->vy = (int16_t)(((sym_bit & 1U) == 0U) ? 1 : -1);
            ag->vz = (int16_t)((((sym_bit >> 1U) & 1U) == 0U) ? 1 : -1);
            ag->state_byte = ptrc_encode_1byte_cascade((uint8_t)(a & 1U), 1U, (uint8_t)((a % 12U) + 1U));
        } else if (nx < -PTRC_TUNNEL_HALF_X) {
            nx = -PTRC_TUNNEL_HALF_X + 1;
            ag->vx = 7;
        }

        /* Wand-Einfluss (Decke/Boden +-540, Vorder-/Rueckwand +-240): Grenzschicht-Reibung + Reflexion */
        if (ny > (PTRC_TUNNEL_HALF_Y - 12)) {
            if (ny > PTRC_TUNNEL_HALF_Y) {
                ny = PTRC_TUNNEL_HALF_Y - 1;
                ag->vy = (int16_t)-ptrc_abs32((int32_t)ag->vy);
            }
            if (ag->vx > 3) ag->vx--; /* Wandreibung bremst Luft an der Kanalwand ab */
        } else if (ny < (-PTRC_TUNNEL_HALF_Y + 12)) {
            if (ny < -PTRC_TUNNEL_HALF_Y) {
                ny = -PTRC_TUNNEL_HALF_Y + 1;
                ag->vy = (int16_t)ptrc_abs32((int32_t)ag->vy);
            }
            if (ag->vx > 3) ag->vx--;
        }

        if (nz > (PTRC_TUNNEL_HALF_Z - 10)) {
            if (nz > PTRC_TUNNEL_HALF_Z) {
                nz = PTRC_TUNNEL_HALF_Z - 1;
                ag->vz = (int16_t)-ptrc_abs32((int32_t)ag->vz);
            }
            if (ag->vx > 3) ag->vx--;
        } else if (nz < (-PTRC_TUNNEL_HALF_Z + 10)) {
            if (nz < -PTRC_TUNNEL_HALF_Z) {
                nz = -PTRC_TUNNEL_HALF_Z + 1;
                ag->vz = (int16_t)ptrc_abs32((int32_t)ag->vz);
            }
            if (ag->vx > 3) ag->vx--;
        }

        /* Kollision mit der scharfkantigen 3D-Pyramide (X = -320, Z = 1) */
        if (ptrc_point_in_square_pyramid(nx, ny, nz, rot_u, rot_v)) {
            pyramid_hits++;
            collisions++;
            uint32_t j_dir = (a + rot_idx + (uint32_t)ctx->takt_counter) % PTRC_GFX_JUNCTIONS;
            int32_t jy = PTRC_JUNCTION_DIRS_24[j_dir];
            int32_t jz = PTRC_JUNCTION_DIRS_24[j_dir];

            /* Staudruck vor der Pyramide: Vorwaertstempo sinkt, Luft stroemt symmetrisch aussen vorbei */
            ag->vx = 2;
            ag->vy = ptrc_z_sym_no_zero(jy * 3 + ((ny >= 0) ? 3 : -3), sym_bit);
            ag->vz = ptrc_z_sym_no_zero(jz * 3 + ((nz >= 0) ? 3 : -3), sym_bit >> 1U);
            nx = ptrc_plichta_move((int32_t)ag->x, -2); /* Zurueckprallen vor die Pyramidenflaeche */
            ny = ptrc_plichta_move((int32_t)ag->y, (int32_t)ag->vy);
            nz = ptrc_plichta_move((int32_t)ag->z, (int32_t)ag->vz);
            ag->state_byte = ptrc_encode_1byte_cascade(1U, PTRC_OPTICS_FIELD_COUPLED, (uint8_t)(22U + (a % 9U)));
        } else {
            uint32_t slot = ptrc_fcc_slot_hash(nx, ny, nz);
            uint8_t occ_imp = ctx->cell_impulse[slot];
            uint8_t dens = ctx->cell_density[slot];
            if (dens < 250U) ctx->cell_density[slot] = (uint8_t)(dens + 1U);

            if (occ_imp == 1U) {
                ctx->cell_impulse[slot] = ag->impulse;
                /* Symmetrische Relaxation zur horizontalen Grundstroemung (kein Drift nach oben!) */
                if ((a & 3U) == (uint32_t)(ctx->takt_counter & 3ULL)) {
                    if (ag->vx < 7) ag->vx++;
                    if (ag->vx > 9) ag->vx--;
                    if (ag->vy > 1) ag->vy--;
                    else if (ag->vy < -1) ag->vy++;
                    else ag->vy = ((sym_bit & 1U) == 0U) ? 1 : -1;

                    if (ag->vz > 1) ag->vz--;
                    else if (ag->vz < -1) ag->vz++;
                    else ag->vz = (((sym_bit >> 1U) & 1U) == 0U) ? 1 : -1;
                }
            } else {
                collisions++;
                /* Teilchenstau-Effekt: Hohe Dichte vor der Pyramide bremst nachfolgende Teilchen ab */
                if (dens >= 3U && nx < (PTRC_PYRAMID_CENTER_X + 60) && ptrc_abs32(ny) < 180) {
                    if (ag->vx > 2) ag->vx--;
                    ag->state_byte = ptrc_encode_1byte_cascade(1U, PTRC_OPTICS_CRYSTALLINE, 18U);
                }
                uint32_t alt_dir = (a + occ_imp + (uint32_t)ctx->takt_counter) % PTRC_GFX_JUNCTIONS;
                int32_t nvy = (int32_t)ag->vy + PTRC_JUNCTION_DIRS_24[alt_dir];
                int32_t nvz = (int32_t)ag->vz + PTRC_JUNCTION_DIRS_24[alt_dir];
                ag->vy = (int16_t)ptrc_z_sym_no_zero(nvy, sym_bit);
                ag->vz = (int16_t)ptrc_z_sym_no_zero(nvz, sym_bit >> 1U);
                if (ag->vy > 7) ag->vy = 7;
                if (ag->vy < -7) ag->vy = -7;
                if (ag->vz > 7) ag->vz = 7;
                if (ag->vz < -7) ag->vz = -7;

                if (ag->impulse > occ_imp) {
                    ctx->cell_impulse[slot] = ag->impulse;
                }
            }
        }

        ag->x = (int16_t)nx;
        ag->y = (int16_t)ny;
        ag->z = (int16_t)nz;
    }

    ctx->deflection_count += collisions;
    ctx->active_load = (collisions >> 4U) + (pyramid_hits >> 2U) + 600U;
    (void)ptrc_gfx_evaluate_observer_sync(ctx);

    ctx->takt_counter++;
    if (ctx->observer_sub_takt >= PTRC_GFX_TAKT_137) {
        ctx->observer_sub_takt = 1U;
        ctx->clock_phase_24 = (ctx->clock_phase_24 % PTRC_GFX_JUNCTIONS) + 1U;
    } else {
        ctx->observer_sub_takt++;
    }
    return PTRC_GFX_OK;
}

int ptrc_gfx_evaluate_observer_sync(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) return PTRC_GFX_ERR;

    if (ctx->active_load >= 2600U) {
        ctx->render_interval_takts = 0U;
        ctx->render_status = PTRC_RENDER_STALL;
        return PTRC_RENDER_STALL;
    } else if (ctx->active_load >= 1900U) {
        ctx->render_interval_takts = PTRC_GFX_TAKT_137 * 4U;
    } else if (ctx->active_load >= 1350U) {
        ctx->render_interval_takts = PTRC_GFX_TAKT_137 * 2U;
    } else {
        ctx->render_interval_takts = PTRC_GFX_TAKT_137;
    }

    if ((ctx->takt_counter % (uint64_t)ctx->render_interval_takts) == 0ULL) {
        ctx->last_render_takt = (uint32_t)ctx->takt_counter;
        ctx->render_status = PTRC_RENDER_READY;
    } else {
        ctx->render_status = PTRC_RENDER_WAIT;
    }
    return ctx->render_status;
}

static inline int32_t ptrc_edge_fn(int32_t ax, int32_t ay, int32_t bx, int32_t by, int32_t cx, int32_t cy) {
    return (cx - ax) * (by - ay) - (cy - ay) * (bx - ax);
}

/* Rastert ein scharfkantiges 3D-Dreieck der Pyramide mit exakter Z-Tiefen-Interpolation */
static void ptrc_raster_pyramid_triangle(
    uint8_t *rgb_out,
    int16_t *z_buf,
    uint32_t width,
    uint32_t height,
    int32_t x0, int32_t y0, int32_t z0,
    int32_t x1, int32_t y1, int32_t z1,
    int32_t x2, int32_t y2, int32_t z2,
    uint8_t r, uint8_t g, uint8_t b
) {
    int32_t area = ptrc_edge_fn(x0, y0, x1, y1, x2, y2);
    if (area == 0) return;

    int32_t min_x = x0 < x1 ? (x0 < x2 ? x0 : x2) : (x1 < x2 ? x1 : x2);
    int32_t max_x = x0 > x1 ? (x0 > x2 ? x0 : x2) : (x1 > x2 ? x1 : x2);
    int32_t min_y = y0 < y1 ? (y0 < y2 ? y0 : y2) : (y1 < y2 ? y1 : y2);
    int32_t max_y = y0 > y1 ? (y0 > y2 ? y0 : y2) : (y1 > y2 ? y1 : y2);

    if (min_x < 0) min_x = 0;
    if (min_y < 0) min_y = 0;
    if (max_x >= (int32_t)width) max_x = (int32_t)width - 1;
    if (max_y >= (int32_t)height) max_y = (int32_t)height - 1;

    for (int32_t py = min_y; py <= max_y; py++) {
        for (int32_t px = min_x; px <= max_x; px++) {
            int32_t w0 = ptrc_edge_fn(x1, y1, x2, y2, px, py);
            int32_t w1 = ptrc_edge_fn(x2, y2, x0, y0, px, py);
            int32_t w2 = ptrc_edge_fn(x0, y0, x1, y1, px, py);

            if ((area > 0 && w0 >= 0 && w1 >= 0 && w2 >= 0) ||
                (area < 0 && w0 <= 0 && w1 <= 0 && w2 <= 0)) {
                int32_t pz = (w0 * z0 + w1 * z1 + w2 * z2) / area;
                size_t p_flat = (size_t)py * (size_t)width + (size_t)px;
                if (pz <= (int32_t)z_buf[p_flat]) {
                    z_buf[p_flat] = (int16_t)pz;
                    size_t pix = p_flat * 3U;
                    /* Kanten-Highlighting fuer kristallklare Pyramidengeometrie */
                    int32_t abs_a = ptrc_abs32(area);
                    int32_t edge_thresh = abs_a >> 5;
                    if (ptrc_abs32(w0) < edge_thresh || ptrc_abs32(w1) < edge_thresh || ptrc_abs32(w2) < edge_thresh) {
                        rgb_out[pix + 0U] = 250U;
                        rgb_out[pix + 1U] = 215U;
                        rgb_out[pix + 2U] = 110U;
                    } else {
                        rgb_out[pix + 0U] = r;
                        rgb_out[pix + 1U] = g;
                        rgb_out[pix + 2U] = b;
                    }
                }
            }
        }
    }
}

int ptrc_gfx_render_observer_rgb24(
    ptrc_gfx_ctx_t *ctx,
    uint32_t width,
    uint32_t height,
    uint8_t *rgb_out
) {
    if (!ctx || !rgb_out || width < 2U || height < 2U) return PTRC_GFX_ERR;

    size_t total_pixels = (size_t)width * (size_t)height;
    int16_t *z_buf = (int16_t *)malloc(total_pixels * sizeof(int16_t));
    if (!z_buf) return PTRC_GFX_ERR;

    for (size_t p = 0U; p < total_pixels; p++) {
        z_buf[p] = 1000;
        size_t idx = p * 3U;
        rgb_out[idx + 0U] = 1U;
        rgb_out[idx + 1U] = 2U;
        rgb_out[idx + 2U] = 6U;
    }

    if (ctx->render_status == PTRC_RENDER_STALL) {
        free(z_buf);
        return PTRC_RENDER_STALL;
    }

    uint32_t rot_idx = ctx->pyramid_angle_idx % PTRC_GFX_JUNCTIONS;
    int32_t rot_u = PTRC_CLOCK24_U[rot_idx];
    int32_t rot_v = PTRC_CLOCK24_V[rot_idx];

    /* 1. Scharfkantige 4-seitige 3D-Pyramide mittig bei (X=-320, Y=1, Z=1) projizieren */
    int32_t half_b = PTRC_PYRAMID_HALF_BASE;
    int32_t half_h = PTRC_PYRAMID_HEIGHT >> 1;
    int32_t local_verts = {
        {       1, -half_h,       1 }, /* 0: Scharfe Spitze oben */
        { -half_b,  half_h, -half_b }, /* 1: Basis vorne-links */
        {  half_b,  half_h, -half_b }, /* 2: Basis vorne-rechts */
        {  half_b,  half_h,  half_b }, /* 3: Basis hinten-rechts */
        { -half_b,  half_h,  half_b }  /* 4: Basis hinten-links */
    };

    int32_t scr_x, scr_y, scr_z;
    for (int v = 0; v < 5; v++) {
        int32_t vx = local_verts[v];
        int32_t vy = local_verts[v];
        int32_t vz = local_verts[v];

        /* Inverse Kippung + Rotation passend zu ptrc_point_in_square_pyramid */
        int32_t rx = (vx * rot_u + vz * rot_v) >> 10;
        int32_t rz = (-vx * rot_v + vz * rot_u) >> 10;
        int32_t wy = (vy * 966 + rz * 259) >> 10;
        int32_t wz = (-vy * 259 + rz * 966) >> 10;
        int32_t wx = rx + PTRC_PYRAMID_CENTER_X;

        int32_t persp = 1414 + wz;
        int32_t sx = (wx * 1414) / persp;
        int32_t sy = (wy * 1414) / persp;

        scr_x[v] = ((sx + PTRC_TUNNEL_HALF_X) * (int32_t)width) / (PTRC_TUNNEL_HALF_X * 2);
        scr_y[v] = ((sy + PTRC_TUNNEL_HALF_Y) * (int32_t)height) / (PTRC_TUNNEL_HALF_Y * 2);
        scr_z[v] = wz;
    }

    /* 4 Seitenflaechen + 2 Basis-Dreiecke mit geraden Kanten rastern */
    const int faces = {
        {0, 1, 2, 215, 165,  55},
        {0, 2, 3, 185, 138,  45},
        {0, 3, 4, 145, 105,  35},
        {0, 4, 1, 175, 130,  42},
        {1, 3, 2, 110,  80,  28},
        {1, 4, 3, 110,  80,  28}
    };
    for (int f = 0; f < 6; f++) {
        int i0 = faces[f], i1 = faces[f], i2 = faces[f];
        ptrc_raster_pyramid_triangle(
            rgb_out, z_buf, width, height,
            scr_x[i0], scr_y[i0], scr_z[i0],
            scr_x[i1], scr_y[i1], scr_z[i1],
            scr_x[i2], scr_y[i2], scr_z[i2],
            (uint8_t)faces[f], (uint8_t)faces[f], (uint8_t)faces[f]
        );
    }

    /* 2. Alle 60.000 Luftmolekuel-Cluster mit Tiefen-Groessenskalierung (Vordergrund groesser, Hintergrund kleiner) */
    for (uint32_t a = 0U; a < PTRC_WIND_AGENTS; a++) {
        const ptrc_wind_agent_t *ag = &ctx->agents[a];

        int32_t z_depth = (int32_t)ag->z;
        int32_t persp = 1414 + z_depth;
        int32_t sx = ((int32_t)ag->x * 1414) / persp;
        int32_t sy = ((int32_t)ag->y * 1414) / persp;

        int32_t px = ((sx + PTRC_TUNNEL_HALF_X) * (int32_t)width) / (PTRC_TUNNEL_HALF_X * 2);
        int32_t py = ((sy + PTRC_TUNNEL_HALF_Y) * (int32_t)height) / (PTRC_TUNNEL_HALF_Y * 2);

        /* Tiefen-abhaengige Agentengroesse: Vorne (-240..-80) = 2x2 Pixel, Mitte/Hinten = 1x1 Pixel */
        int32_t dot_size = (z_depth < -80) ? 2 : 1;

        int32_t depth_shade = 245 - ((z_depth + PTRC_TUNNEL_HALF_Z) >> 2);
        if (depth_shade < 50) depth_shade = 50;
        if (depth_shade > 255) depth_shade = 255;

        uint8_t r, g, b;
        ptrc_transpose_wavelength_to_rgb(ag->state_byte, depth_shade, &r, &g, &b);

        for (int32_t oy = 0; oy < dot_size; oy++) {
            int32_t fpy = py + oy;
            if (fpy < 0 || fpy >= (int32_t)height) continue;
            for (int32_t ox = 0; ox < dot_size; ox++) {
                int32_t fpx = px + ox;
                if (fpx < 0 || fpx >= (int32_t)width) continue;

                size_t p_flat = (size_t)fpy * (size_t)width + (size_t)fpx;
                if (z_depth <= (int32_t)z_buf[p_flat]) {
                    z_buf[p_flat] = (int16_t)z_depth;
                    size_t pix = p_flat * 3U;
                    if (rgb_out[pix + 0U] == 1U && rgb_out[pix + 1U] == 2U) {
                        rgb_out[pix + 0U] = r;
                        rgb_out[pix + 1U] = g;
                        rgb_out[pix + 2U] = b;
                    } else {
                        uint8_t mr = (uint8_t)((rgb_out[pix + 0U] + r) >> 1U);
                        uint8_t mg = (uint8_t)((rgb_out[pix + 1U] + g) >> 1U);
                        uint8_t mb = (uint8_t)((rgb_out[pix + 2U] + b) >> 1U);
                        rgb_out[pix + 0U] = (mr == 0U) ? 1U : mr;
                        rgb_out[pix + 1U] = (mg == 0U) ? 1U : mg;
                        rgb_out[pix + 2U] = (mb == 0U) ? 1U : mb;
                    }
                }
            }
        }
    }

    free(z_buf);
    return PTRC_GFX_OK;
}

void ptrc_gfx_wipe(ptrc_gfx_ctx_t *ctx) {
    if (!ctx) return;
    volatile uint8_t *p = (volatile uint8_t *)ctx;
    for (size_t i = 0U; i < sizeof(*ctx); i++) {
        p[i] = 0xFFU;
    }
}
