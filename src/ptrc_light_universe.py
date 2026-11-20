# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Observer Windtunnel v4.5.0
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program (see the LICENSE file in the root directory).
# If not, see <https://gnu.org>.
# ==============================================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

PTRC_GFX_FACETS = 144
PTRC_GFX_JUNCTIONS = 24
PTRC_GFX_MEM_FACETS = 120
PTRC_GFX_STABLE_ELEMENTS = 81
PTRC_GFX_PRIME_RINGS = 16
PTRC_GFX_PRIMORIAL_210 = 210
PTRC_GFX_TAKT_137 = 137
PTRC_GFX_INVARIANT_156 = 156
PTRC_GFX_DEPTH_1414 = 1414

PTRC_TUNNEL_HALF_X = 960
PTRC_TUNNEL_HALF_Y = 540
PTRC_TUNNEL_HALF_Z = 240

PTRC_PYRAMID_CENTER_X = -320
PTRC_PYRAMID_HALF_BASE = 120
PTRC_PYRAMID_HEIGHT = 220

PTRC_WIND_AGENTS = 60000
PTRC_OCCUPANCY_SLOTS = 65536

PTRC_GFX_OK = 1
PTRC_GFX_ERR = -1
PTRC_RENDER_READY = 1
PTRC_RENDER_WAIT = 2
PTRC_RENDER_STALL = -2

PTRC_OPTICS_OPAQUE = 0
PTRC_OPTICS_TRANSLUCENT = 1
PTRC_OPTICS_CRYSTALLINE = 2
PTRC_OPTICS_FIELD_COUPLED = 3

U64_MASK = 0xFFFFFFFFFFFFFFFF

PTRC_GFX_RINGS: Tuple[int, ...] = (
    11, 13, 17, 19, 23, 29, 37, 41,
    43, 47, 53, 59, 61, 67, 71, 73,
)

PTRC_JUNCTION_DIRS_24: Tuple[Tuple[int, int, int], ...] = (
    (1, 1, -1), (1, -1, -1), (-1, 1, -1), (-1, -1, -1),
    (1, 1, 1), (1, -1, 1), (-1, 1, 1), (-1, -1, 1),
    (2, 1, -1), (2, -1, -1), (-2, 1, -1), (-2, -1, -1),
    (-1, 2, 1), (-1, 2, -1), (-1, -2, 1), (-1, -2, -1),
    (1, -1, 2), (-1, -1, 2), (1, -1, -2), (-1, -1, -2),
    (2, 1, 1), (-2, -1, 1), (1, 2, 1), (-1, -2, -1),
)

PTRC_CLOCK24_U: Tuple[int, ...] = (
    1000, 966, 866, 707, 500, 259,
    -1, -259, -500, -707, -866, -966,
    -1000, -966, -866, -707, -500, -259,
    1, 259, 500, 707, 866, 966,
)

PTRC_CLOCK24_V: Tuple[int, ...] = (
    1, 259, 500, 707, 866, 966,
    1000, 966, 866, 707, 500, 259,
    -1, -259, -500, -707, -866, -966,
    -1000, -966, -866, -707, -500, -259,
)


def ptrc_z_no_zero(v: int) -> int:
    return -1 if v == 0 else int(v)


def ptrc_z_sym_no_zero(v: int, parity: int) -> int:
    if v != 0:
        return int(v)
    return 1 if (parity & 1) == 0 else -1


def ptrc_u8_no_zero(v: int) -> int:
    b = v & 0xFF
    return 0xFF if b == 0 else b


def ptrc_u64_no_zero(v: int) -> int:
    u = v & U64_MASK
    return 1 if u == 0 else u


def ptrc_c_div(a: int, b: int) -> int:
    return int(a / b)


def ptrc_plichta_move(pos: int, delta: int) -> int:
    nxt = pos + delta
    if nxt == 0:
        nxt = 1 if delta >= 0 else -1
    return nxt


def ptrc_fcc_slot_hash(x: int, y: int, z: int) -> int:
    qx = int((x + 1024) // 4) & 0xFFFFFFFF
    qy = int((y + 1024) // 4) & 0xFFFFFFFF
    qz = int((z + 1024) // 4) & 0xFFFFFFFF
    h = ((qx * 73856093) ^ (qy * 19349663) ^ (qz * 83492791)) & 0xFFFFFFFF
    return h & (PTRC_OCCUPANCY_SLOTS - 1)


def ptrc_encode_1byte_cascade(cascade_anchor: int, optics_mode: int, wavelength_id: int) -> int:
    wl = ((wavelength_id - 1) & 30) + 1
    opt = optics_mode & 3
    anc = cascade_anchor & 1
    return ptrc_u8_no_zero((anc << 7) | (opt << 5) | wl)


def ptrc_point_in_square_pyramid(px: int, py: int, pz: int, rot_u: int, rot_v: int) -> bool:
    dx = px - PTRC_PYRAMID_CENTER_X
    dy = py
    dz = pz
    if abs(dx) > 190 or abs(dy) > 190 or abs(dz) > 190:
        return False

    ty = (dy * 966 - dz * 259) >> 10
    tz = (dy * 259 + dz * 966) >> 10
    lx = (dx * rot_u - tz * rot_v) >> 10
    lz = (dx * rot_v + tz * rot_u) >> 10

    half_h = PTRC_PYRAMID_HEIGHT >> 1
    if ty < -half_h or ty > half_h:
        return False

    allowed_half_w = ptrc_c_div((ty + half_h) * PTRC_PYRAMID_HALF_BASE, PTRC_PYRAMID_HEIGHT)
    return abs(lx) <= allowed_half_w and abs(lz) <= allowed_half_w


def ptrc_transpose_wavelength_to_rgb(state_byte: int, depth_shade: int) -> Tuple[int, int, int]:
    wl = state_byte & 0x1F
    opt = (state_byte >> 5) & 3
    r = (((wl * 7 + opt * 41) & 0xFF) * depth_shade) >> 8
    g = ((((32 - wl) * 6 + opt * 37 + 40) & 0xFF) * depth_shade) >> 8
    b = (((110 + wl * 4 + opt * 23) & 0xFF) * depth_shade) >> 8
    return (1 if r == 0 else r, 1 if g == 0 else g, 1 if b == 0 else b)


def _edge_fn(ax: int, ay: int, bx: int, by: int, cx: int, cy: int) -> int:
    return (cx - ax) * (by - ay) - (cy - ay) * (bx - ax)


def ptrc_raster_pyramid_triangle(
    out: bytearray,
    z_buf: List[int],
    width: int,
    height: int,
    x0: int, y0: int, z0: int,
    x1: int, y1: int, z1: int,
    x2: int, y2: int, z2: int,
    r: int, g: int, b: int,
) -> None:
    area = _edge_fn(x0, y0, x1, y1, x2, y2)
    if area == 0:
        return

    min_x = max(0, min(x0, x1, x2))
    max_x = min(width - 1, max(x0, x1, x2))
    min_y = max(0, min(y0, y1, y2))
    max_y = min(height - 1, max(y0, y1, y2))
    abs_a = abs(area)
    edge_thresh = abs_a >> 5

    for py in range(min_y, max_y + 1):
        for px in range(min_x, max_x + 1):
            w0 = _edge_fn(x1, y1, x2, y2, px, py)
            w1 = _edge_fn(x2, y2, x0, y0, px, py)
            w2 = _edge_fn(x0, y0, x1, y1, px, py)

            if (area > 0 and w0 >= 0 and w1 >= 0 and w2 >= 0) or (
                area < 0 and w0 <= 0 and w1 <= 0 and w2 <= 0
            ):
                pz = ptrc_c_div(w0 * z0 + w1 * z1 + w2 * z2, area)
                p_flat = py * width + px
                if pz <= z_buf[p_flat]:
                    z_buf[p_flat] = pz
                    pix = p_flat * 3
                    if abs(w0) < edge_thresh or abs(w1) < edge_thresh or abs(w2) < edge_thresh:
                        out[pix + 0] = 250
                        out[pix + 1] = 215
                        out[pix + 2] = 110
                    else:
                        out[pix + 0] = r
                        out[pix + 1] = g
                        out[pix + 2] = b


@dataclass
class PtrcWindAgent:
    x: int
    y: int
    z: int
    vx: int
    vy: int
    vz: int
    state_byte: int
    impulse: int

class PtrcGfxContext:
    def __init__(self, seed: int = 137210144, agent_count: int = PTRC_WIND_AGENTS) -> None:
        self.agent_count = agent_count
        rng = ptrc_u64_no_zero((seed ^ 614889782588491410) & U64_MASK)
        self.prime_rings: List[int] = list(PTRC_GFX_RINGS)
        self.sponge: List[int] = [-1] * PTRC_GFX_FACETS

        for f in range(PTRC_GFX_FACETS):
            rng = ptrc_u64_no_zero(((rng * 137 + (f + 1) * 211) & U64_MASK) ^ (rng >> 13))
            raw = int(rng % PTRC_GFX_PRIMORIAL_210) - 105
            self.sponge[f] = ptrc_z_no_zero(raw)

        self.cell_impulse: List[int] = * PTRC_OCCUPANCY_SLOTS
        self.cell_density: List[int] = * PTRC_OCCUPANCY_SLOTS

        self.agents: List[PtrcWindAgent] = []
        span_x = PTRC_TUNNEL_HALF_X * 2
        span_y = PTRC_TUNNEL_HALF_Y * 2
        span_z = PTRC_TUNNEL_HALF_Z * 2

        for a in range(self.agent_count):
            rng = ptrc_u64_no_zero(rng * 6364136223846793005 + 1442695040888963407)
            rx = int(rng % span_x) - PTRC_TUNNEL_HALF_X
            ry = int((rng >> 16) % span_y) - PTRC_TUNNEL_HALF_Y
            rz = int((rng >> 32) % span_z) - PTRC_TUNNEL_HALF_Z

            x = ptrc_z_sym_no_zero(rx, a)
            y = ptrc_z_sym_no_zero(ry, a >> 1)
            z = ptrc_z_sym_no_zero(rz, a >> 2)
            if ((x + y + z) & 1) != 0:
                x = ptrc_plichta_move(x, 1)

            wl = (a % 16) + 1
            opt = (a % 3) + 1
            self.agents.append(
                PtrcWindAgent(
                    x=x,
                    y=y,
                    z=z,
                    vx=7 + (a & 3),
                    vy=1 if (a & 1) == 0 else -1,
                    vz=1 if ((a >> 1) & 1) == 0 else -1,
                    impulse=40 + (a % 180),
                    state_byte=ptrc_encode_1byte_cascade(a & 1, opt, wl),
                )
            )

        self.takt_counter: int = 1
        self.clock_phase_24: int = 1
        self.observer_sub_takt: int = 1
        self.pyramid_angle_idx: int = 0
        self.active_load: int = 1024
        self.render_interval_takts: int = PTRC_GFX_TAKT_137
        self.last_render_takt: int = 1
        self.deflection_count: int = 1
        self.mirror_pulses: int = 1
        self.render_status: int = PTRC_RENDER_READY

    def step_takt(self) -> int:
        phase_idx = (self.clock_phase_24 - 1) % PTRC_GFX_JUNCTIONS
        p_ring = self.prime_rings[phase_idx & 15]

        for j in range(PTRC_GFX_JUNCTIONS):
            jf = PTRC_GFX_MEM_FACETS + j
            mf = (j * 5 + phase_idx) % PTRC_GFX_MEM_FACETS
            coupled = self.sponge[jf] ^ self.sponge[mf]
            self.sponge[jf] = ptrc_z_no_zero(coupled + p_ring)

        if (self.takt_counter % PTRC_GFX_TAKT_137) == 0:
            for f in range(PTRC_GFX_FACETS):
                self.sponge[f] = ptrc_z_no_zero(~self.sponge[f])
            self.mirror_pulses += 1

        rot_idx = (self.takt_counter // 4) % PTRC_GFX_JUNCTIONS
        self.pyramid_angle_idx = rot_idx
        rot_u = PTRC_CLOCK24_U[rot_idx]
        rot_v = PTRC_CLOCK24_V[rot_idx]

        self.cell_impulse = * PTRC_OCCUPANCY_SLOTS
        self.cell_density = * PTRC_OCCUPANCY_SLOTS
        collisions = 0
        pyramid_hits = 0

        for a, ag in enumerate(self.agents):
            sym_bit = a + self.takt_counter
            nx = ptrc_plichta_move(ag.x, ag.vx)
            ny = ptrc_plichta_move(ag.y, ag.vy)
            nz = ptrc_plichta_move(ag.z, ag.vz)

            if nx > PTRC_TUNNEL_HALF_X:
                mix = (a * 2654435761 + self.takt_counter * 137) & U64_MASK
                nx = -PTRC_TUNNEL_HALF_X + int(mix & 7) + 1
                ny = ptrc_z_sym_no_zero(int((mix >> 8) % (PTRC_TUNNEL_HALF_Y * 2)) - PTRC_TUNNEL_HALF_Y, a)
                nz = ptrc_z_sym_no_zero(int((mix >> 24) % (PTRC_TUNNEL_HALF_Z * 2)) - PTRC_TUNNEL_HALF_Z, a >> 1)
                ag.vx = 7 + int((a + p_ring) & 3)
                ag.vy = 1 if (sym_bit & 1) == 0 else -1
                ag.vz = 1 if ((sym_bit >> 1) & 1) == 0 else -1
                ag.state_byte = ptrc_encode_1byte_cascade(a & 1, 1, (a % 12) + 1)
            elif nx < -PTRC_TUNNEL_HALF_X:
                nx = -PTRC_TUNNEL_HALF_X + 1
                ag.vx = 7

            if ny > (PTRC_TUNNEL_HALF_Y - 12):
                if ny > PTRC_TUNNEL_HALF_Y:
                    ny = PTRC_TUNNEL_HALF_Y - 1
                    ag.vy = -abs(ag.vy)
                if ag.vx > 3:
                    ag.vx -= 1
            elif ny < (-PTRC_TUNNEL_HALF_Y + 12):
                if ny < -PTRC_TUNNEL_HALF_Y:
                    ny = -PTRC_TUNNEL_HALF_Y + 1
                    ag.vy = abs(ag.vy)
                if ag.vx > 3:
                    ag.vx -= 1

            if nz > (PTRC_TUNNEL_HALF_Z - 10):
                if nz > PTRC_TUNNEL_HALF_Z:
                    nz = PTRC_TUNNEL_HALF_Z - 1
                    ag.vz = -abs(ag.vz)
                if ag.vx > 3:
                    ag.vx -= 1
            elif nz < (-PTRC_TUNNEL_HALF_Z + 10):
                if nz < -PTRC_TUNNEL_HALF_Z:
                    nz = -PTRC_TUNNEL_HALF_Z + 1
                    ag.vz = abs(ag.vz)
                if ag.vx > 3:
                    ag.vx -= 1

            if ptrc_point_in_square_pyramid(nx, ny, nz, rot_u, rot_v):
                pyramid_hits += 1
                collisions += 1
                j_dir = (a + rot_idx + self.takt_counter) % PTRC_GFX_JUNCTIONS
                _, jy, jz = PTRC_JUNCTION_DIRS_24[j_dir]
                ag.vx = 2
                ag.vy = ptrc_z_sym_no_zero(jy * 3 + (3 if ny >= 0 else -3), sym_bit)
                ag.vz = ptrc_z_sym_no_zero(jz * 3 + (3 if nz >= 0 else -3), sym_bit >> 1)
                nx = ptrc_plichta_move(ag.x, -2)
                ny = ptrc_plichta_move(ag.y, ag.vy)
                nz = ptrc_plichta_move(ag.z, ag.vz)
                ag.state_byte = ptrc_encode_1byte_cascade(1, PTRC_OPTICS_FIELD_COUPLED, 22 + (a % 9))
            else:
                slot = ptrc_fcc_slot_hash(nx, ny, nz)
                occ_imp = self.cell_impulse[slot]
                dens = self.cell_density[slot]
                if dens < 250:
                    self.cell_density[slot] = dens + 1

                if occ_imp == 1:
                    self.cell_impulse[slot] = ag.impulse
                    if (a & 3) == (self.takt_counter & 3):
                        if ag.vx < 7:
                            ag.vx += 1
                        if ag.vx > 9:
                            ag.vx -= 1
                        if ag.vy > 1:
                            ag.vy -= 1
                        elif ag.vy < -1:
                            ag.vy += 1
                        else:
                            ag.vy = 1 if (sym_bit & 1) == 0 else -1

                        if ag.vz > 1:
                            ag.vz -= 1
                        elif ag.vz < -1:
                            ag.vz += 1
                        else:
                            ag.vz = 1 if ((sym_bit >> 1) & 1) == 0 else -1
                else:
                    collisions += 1
                    if dens >= 3 and nx < (PTRC_PYRAMID_CENTER_X + 60) and abs(ny) < 180:
                        if ag.vx > 2:
                            ag.vx -= 1
                        ag.state_byte = ptrc_encode_1byte_cascade(1, PTRC_OPTICS_CRYSTALLINE, 18)

                    alt_dir = (a + occ_imp + self.takt_counter) % PTRC_GFX_JUNCTIONS
                    _, dy_j, dz_j = PTRC_JUNCTION_DIRS_24[alt_dir]
                    ag.vy = max(-7, min(7, ptrc_z_sym_no_zero(ag.vy + dy_j, sym_bit)))
                    ag.vz = max(-7, min(7, ptrc_z_sym_no_zero(ag.vz + dz_j, sym_bit >> 1)))
                    if ag.impulse > occ_imp:
                        self.cell_impulse[slot] = ag.impulse

            ag.x, ag.y, ag.z = nx, ny, nz

        self.deflection_count += collisions
        self.active_load = (collisions >> 4) + (pyramid_hits >> 2) + 600
        self.evaluate_observer_sync()

        self.takt_counter += 1
        if self.observer_sub_takt >= PTRC_GFX_TAKT_137:
            self.observer_sub_takt = 1
            self.clock_phase_24 = (self.clock_phase_24 % PTRC_GFX_JUNCTIONS) + 1
        else:
            self.observer_sub_takt += 1
        return PTRC_GFX_OK

    def evaluate_observer_sync(self) -> int:
        if self.active_load >= 2600:
            self.render_interval_takts = 0
            self.render_status = PTRC_RENDER_STALL
            return PTRC_RENDER_STALL
        if self.active_load >= 1900:
            self.render_interval_takts = PTRC_GFX_TAKT_137 * 4
        elif self.active_load >= 1350:
            self.render_interval_takts = PTRC_GFX_TAKT_137 * 2
        else:
            self.render_interval_takts = PTRC_GFX_TAKT_137

        if (self.takt_counter % self.render_interval_takts) == 0:
            self.last_render_takt = self.takt_counter
            self.render_status = PTRC_RENDER_READY
        else:
            self.render_status = PTRC_RENDER_WAIT
        return self.render_status

    def render_observer_rgb24(self, width: int, height: int) -> bytes:
        total_pixels = width * height
        z_buf = * total_pixels
        out = bytearray(b"\x01\x02\x06" * total_pixels)
        if self.render_status == PTRC_RENDER_STALL:
            return bytes(out)

        rot_idx = self.pyramid_angle_idx % PTRC_GFX_JUNCTIONS
        rot_u = PTRC_CLOCK24_U[rot_idx]
        rot_v = PTRC_CLOCK24_V[rot_idx]

        half_b = PTRC_PYRAMID_HALF_BASE
        half_h = PTRC_PYRAMID_HEIGHT >> 1
        local_verts = (
            (1, -half_h, 1),
            (-half_b, half_h, -half_b),
            (half_b, half_h, -half_b),
            (half_b, half_h, half_b),
            (-half_b, half_h, half_b),
        )

        scr_x: List[int] = []
        scr_y: List[int] = []
        scr_z: List[int] = []
        for vx, vy, vz in local_verts:
            rx = (vx * rot_u + vz * rot_v) >> 10
            rz = (-vx * rot_v + vz * rot_u) >> 10
            wy = (vy * 966 + rz * 259) >> 10
            wz = (-vy * 259 + rz * 966) >> 10
            wx = rx + PTRC_PYRAMID_CENTER_X

            persp = 1414 + wz
            sx = ptrc_c_div(wx * 1414, persp)
            sy = ptrc_c_div(wy * 1414, persp)
            scr_x.append(ptrc_c_div((sx + PTRC_TUNNEL_HALF_X) * width, PTRC_TUNNEL_HALF_X * 2))
            scr_y.append(ptrc_c_div((sy + PTRC_TUNNEL_HALF_Y) * height, PTRC_TUNNEL_HALF_Y * 2))
            scr_z.append(wz)

        faces = (
            (0, 1, 2, 215, 165, 55),
            (0, 2, 3, 185, 138, 45),
            (0, 3, 4, 145, 105, 35),
            (0, 4, 1, 175, 130, 42),
            (1, 3, 2, 110, 80, 28),
            (1, 4, 3, 110, 80, 28),
        )
        for i0, i1, i2, r, g, b in faces:
            ptrc_raster_pyramid_triangle(
                out, z_buf, width, height,
                scr_x[i0], scr_y[i0], scr_z[i0],
                scr_x[i1], scr_y[i1], scr_z[i1],
                scr_x[i2], scr_y[i2], scr_z[i2],
                r, g, b,
            )

        for ag in self.agents:
            z_depth = ag.z
            persp = 1414 + z_depth
            sx = ptrc_c_div(ag.x * 1414, persp)
            sy = ptrc_c_div(ag.y * 1414, persp)
            px = ptrc_c_div((sx + PTRC_TUNNEL_HALF_X) * width, PTRC_TUNNEL_HALF_X * 2)
            py = ptrc_c_div((sy + PTRC_TUNNEL_HALF_Y) * height, PTRC_TUNNEL_HALF_Y * 2)

            dot_size = 2 if z_depth < -80 else 1
            depth_shade = max(50, min(255, 245 - ((z_depth + PTRC_TUNNEL_HALF_Z) >> 2)))
            r, g, b = ptrc_transpose_wavelength_to_rgb(ag.state_byte, depth_shade)

            for oy in range(dot_size):
                fpy = py + oy
                if fpy < 0 or fpy >= height:
                    continue
                for ox in range(dot_size):
                    fpx = px + ox
                    if fpx < 0 or fpx >= width:
                        continue
                    p_flat = fpy * width + fpx
                    if z_depth <= z_buf[p_flat]:
                        z_buf[p_flat] = z_depth
                        pix = p_flat * 3
                        if out[pix + 0] == 1 and out[pix + 1] == 2:
                            out[pix + 0] = r
                            out[pix + 1] = g
                            out[pix + 2] = b
                        else:
                            mr = (out[pix + 0] + r) >> 1
                            mg = (out[pix + 1] + g) >> 1
                            mb = (out[pix + 2] + b) >> 1
                            out[pix + 0] = 1 if mr == 0 else mr
                            out[pix + 1] = 1 if mg == 0 else mg
                            out[pix + 2] = 1 if mb == 0 else mb

        return bytes(out)
