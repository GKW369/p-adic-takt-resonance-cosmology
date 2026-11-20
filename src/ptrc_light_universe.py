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
PTRC_PYRAMID_RADIUS = 135

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


def ptrc_u8_no_zero(v: int) -> int:
    b = v & 0xFF
    return 0xFF if b == 0 else b


def ptrc_u64_no_zero(v: int) -> int:
    u = v & U64_MASK
    return 1 if u == 0 else u


def ptrc_plichta_move(pos: int, delta: int) -> int:
    nxt = pos + delta
    if nxt == 0:
        nxt = 1 if delta >= 0 else -1
    return nxt


def ptrc_fcc_slot_hash(x: int, y: int, z: int) -> int:
    qx = int((x + 1024) // 3) & 0xFFFFFFFF
    qy = int((y + 1024) // 3) & 0xFFFFFFFF
    qz = int((z + 1024) // 3) & 0xFFFFFFFF
    h = ((qx * 73856093) ^ (qy * 19349663) ^ (qz * 83492791)) & 0xFFFFFFFF
    return h & (PTRC_OCCUPANCY_SLOTS - 1)


def ptrc_encode_1byte_cascade(cascade_anchor: int, optics_mode: int, wavelength_id: int) -> int:
    wl = ((wavelength_id - 1) & 30) + 1
    opt = optics_mode & 3
    anc = cascade_anchor & 1
    return ptrc_u8_no_zero((anc << 7) | (opt << 5) | wl)


def ptrc_c_div(a: int, b: int) -> int:
    return int(a / b)


def ptrc_point_in_rotating_pyramid(px: int, py: int, pz: int, rot_u: int, rot_v: int) -> bool:
    dx = px - PTRC_PYRAMID_CENTER_X
    dy = py
    dz = pz
    if (dx * dx + dy * dy + dz * dz) > (PTRC_PYRAMID_RADIUS * PTRC_PYRAMID_RADIUS):
        return False

    lx = (dx * rot_u + dz * rot_v) >> 10
    lz = (-dx * rot_v + dz * rot_u) >> 10
    ly = (dy * rot_u + lz * rot_v) >> 10
    fz = (-dy * rot_v + lz * rot_u) >> 10

    lim = ptrc_c_div(PTRC_PYRAMID_RADIUS * 333, 1000)
    if fz < -lim:
        return False
    if (943 * lx - 333 * fz) > (PTRC_PYRAMID_RADIUS * 333):
        return False
    if (-471 * lx + 816 * ly - 333 * fz) > (PTRC_PYRAMID_RADIUS * 333):
        return False
    if (-471 * lx - 816 * ly - 333 * fz) > (PTRC_PYRAMID_RADIUS * 333):
        return False
    return True


def ptrc_transpose_wavelength_to_rgb(state_byte: int, depth_shade: int) -> Tuple[int, int, int]:
    wl = state_byte & 0x1F
    opt = (state_byte >> 5) & 3
    r = (((wl * 7 + opt * 41) & 0xFF) * depth_shade) >> 8
    g = ((((32 - wl) * 6 + opt * 37 + 40) & 0xFF) * depth_shade) >> 8
    b = (((110 + wl * 4 + opt * 23) & 0xFF) * depth_shade) >> 8
    return (1 if r == 0 else r, 1 if g == 0 else g, 1 if b == 0 else b)


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

        self.cell_impulse: List[int] = [1] * PTRC_OCCUPANCY_SLOTS
        self.cell_state: List[int] = [1] * PTRC_OCCUPANCY_SLOTS

        self.agents: List[PtrcWindAgent] = []
        span_x = PTRC_TUNNEL_HALF_X * 2
        span_y = PTRC_TUNNEL_HALF_Y * 2
        span_z = PTRC_TUNNEL_HALF_Z * 2

        for a in range(self.agent_count):
            rng = ptrc_u64_no_zero(rng * 6364136223846793005 + 1442695040888963407)
            rx = int(rng % span_x) - PTRC_TUNNEL_HALF_X
            ry = int((rng >> 16) % span_y) - PTRC_TUNNEL_HALF_Y
            rz = int((rng >> 32) % span_z) - PTRC_TUNNEL_HALF_Z

            x = ptrc_z_no_zero(rx)
            y = ptrc_z_no_zero(ry)
            z = ptrc_z_no_zero(rz)
            if ((x + y + z) & 1) != 0:
                x = ptrc_plichta_move(x, 1)

            wl = (a % 16) + 1
            opt = (a % 3) + 1
            self.agents.append(
                PtrcWindAgent(
                    x=x,
                    y=y,
                    z=z,
                    vx=6 + (a & 3),
                    vy=ptrc_z_no_zero(int((rng >> 48) % 3) - 1),
                    vz=ptrc_z_no_zero(int((rng >> 52) % 3) - 1),
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

        rot_idx = (self.takt_counter // 6) % PTRC_GFX_JUNCTIONS
        self.pyramid_angle_idx = rot_idx
        rot_u = PTRC_CLOCK24_U[rot_idx]
        rot_v = PTRC_CLOCK24_V[rot_idx]

        self.cell_impulse = [1] * PTRC_OCCUPANCY_SLOTS
        collisions = 0
        pyramid_hits = 0

        for a, ag in enumerate(self.agents):
            nx = ptrc_plichta_move(ag.x, ag.vx)
            ny = ptrc_plichta_move(ag.y, ag.vy)
            nz = ptrc_plichta_move(ag.z, ag.vz)

            if nx > PTRC_TUNNEL_HALF_X:
                nx = -PTRC_TUNNEL_HALF_X + int((a + self.takt_counter) & 15)
                if nx == 0:
                    nx = -1
                ag.vx = 6 + int((a + p_ring) & 3)
                ag.vy = ptrc_z_no_zero((a % 3) - 1)
                ag.vz = ptrc_z_no_zero(((a >> 2) % 3) - 1)
                ag.state_byte = ptrc_encode_1byte_cascade(a & 1, 1, (a % 12) + 1)
            elif nx < -PTRC_TUNNEL_HALF_X:
                nx = -PTRC_TUNNEL_HALF_X + 1
                ag.vx = 6

            if ny > PTRC_TUNNEL_HALF_Y:
                ny = PTRC_TUNNEL_HALF_Y - 1
                ag.vy = -abs(ag.vy)
            elif ny < -PTRC_TUNNEL_HALF_Y:
                ny = -PTRC_TUNNEL_HALF_Y + 1
                ag.vy = abs(ag.vy)

            if nz > PTRC_TUNNEL_HALF_Z:
                nz = PTRC_TUNNEL_HALF_Z - 1
                ag.vz = -abs(ag.vz)
            elif nz < -PTRC_TUNNEL_HALF_Z:
                nz = -PTRC_TUNNEL_HALF_Z + 1
                ag.vz = abs(ag.vz)

            if ptrc_point_in_rotating_pyramid(nx, ny, nz, rot_u, rot_v):
                pyramid_hits += 1
                collisions += 1
                j_dir = (a + rot_idx + self.takt_counter) % PTRC_GFX_JUNCTIONS
                jx, jy, jz = PTRC_JUNCTION_DIRS_24[j_dir]
                ag.vx = ptrc_z_no_zero(3 + abs(jx))
                ag.vy = ptrc_z_no_zero(jy * 3 + (2 if ny >= 0 else -2))
                ag.vz = ptrc_z_no_zero(jz * 3 + (2 if nz >= 0 else -2))
                nx = ptrc_plichta_move(ag.x, ag.vx)
                ny = ptrc_plichta_move(ag.y, ag.vy)
                nz = ptrc_plichta_move(ag.z, ag.vz)
                ag.state_byte = ptrc_encode_1byte_cascade(1, PTRC_OPTICS_FIELD_COUPLED, 20 + (a % 11))
            else:
                slot = ptrc_fcc_slot_hash(nx, ny, nz)
                occ_imp = self.cell_impulse[slot]
                if occ_imp == 1:
                    self.cell_impulse[slot] = ag.impulse
                    self.cell_state[slot] = ag.state_byte
                    if (a & 7) == (self.takt_counter & 7):
                        ag.vx = ptrc_z_no_zero((ag.vx * 3 + 7) >> 2)
                        ag.vy = ptrc_z_no_zero((ag.vy * 3) >> 2)
                        ag.vz = ptrc_z_no_zero((ag.vz * 3) >> 2)
                else:
                    collisions += 1
                    alt_dir = (a + occ_imp + self.takt_counter) % PTRC_GFX_JUNCTIONS
                    _, dy_j, dz_j = PTRC_JUNCTION_DIRS_24[alt_dir]
                    ag.vy = max(-8, min(8, ptrc_z_no_zero(ag.vy + dy_j)))
                    ag.vz = max(-8, min(8, ptrc_z_no_zero(ag.vz + dz_j)))
                    if ag.impulse > occ_imp:
                        self.cell_impulse[slot] = ag.impulse
                        self.cell_state[slot] = ag.state_byte

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
        z_buf = [1000] * total_pixels
        out = bytearray(b"\x01\x02\x06" * total_pixels)
        if self.render_status == PTRC_RENDER_STALL:
            return bytes(out)

        rot_idx = self.pyramid_angle_idx % PTRC_GFX_JUNCTIONS
        rot_u = PTRC_CLOCK24_U[rot_idx]
        rot_v = PTRC_CLOCK24_V[rot_idx]

        pyr_cx = ptrc_c_div((PTRC_PYRAMID_CENTER_X + PTRC_TUNNEL_HALF_X) * width, PTRC_TUNNEL_HALF_X * 2)
        pyr_cy = height >> 1
        pyr_r_px = ptrc_c_div(PTRC_PYRAMID_RADIUS * width, PTRC_TUNNEL_HALF_X * 2)

        for dy in range(-pyr_r_px, pyr_r_px + 1):
            py = pyr_cy + dy
            if py < 0 or py >= height:
                continue
            wy = ptrc_c_div((py - (height >> 1)) * (PTRC_TUNNEL_HALF_Y * 2), height)
            for dx in range(-pyr_r_px, pyr_r_px + 1):
                px = pyr_cx + dx
                if px < 0 or px >= width:
                    continue
                wx = ptrc_c_div((px - (width >> 1)) * (PTRC_TUNNEL_HALF_X * 2), width)
                for wz in range(-PTRC_PYRAMID_RADIUS, PTRC_PYRAMID_RADIUS + 1, 4):
                    if ptrc_point_in_rotating_pyramid(wx, wy, wz, rot_u, rot_v):
                        p_flat = py * width + px
                        z_buf[p_flat] = wz
                        shade = max(60, min(250, 230 - ((wz + PTRC_PYRAMID_RADIUS) >> 1)))
                        pix = p_flat * 3
                        out[pix + 0] = shade
                        out[pix + 1] = (shade * 3) >> 2
                        out[pix + 2] = (shade >> 2) + 20
                        break

        for ag in self.agents:
            z_depth = ag.z
            persp = 1414 + z_depth
            sx = ptrc_c_div(ag.x * 1414, persp)
            sy = ptrc_c_div(ag.y * 1414, persp)
            px = ptrc_c_div((sx + PTRC_TUNNEL_HALF_X) * width, PTRC_TUNNEL_HALF_X * 2)
            py = ptrc_c_div((sy + PTRC_TUNNEL_HALF_Y) * height, PTRC_TUNNEL_HALF_Y * 2)

            if 0 <= px < width and 0 <= py < height:
                p_flat = py * width + px
                if z_depth <= z_buf[p_flat]:
                    z_buf[p_flat] = z_depth
                    depth_shade = max(55, min(255, 240 - ((z_depth + PTRC_TUNNEL_HALF_Z) >> 2)))
                    r, g, b = ptrc_transpose_wavelength_to_rgb(ag.state_byte, depth_shade)
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
