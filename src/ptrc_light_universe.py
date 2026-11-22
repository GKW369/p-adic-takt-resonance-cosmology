# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Observer Windtunnel v4.6.0
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
PTRC_GFX_SHELL_12 = 12
PTRC_GFX_CLUSTER_13 = 13
PTRC_GFX_STABLE_ELEMENTS = 81
PTRC_GFX_PRIME_RINGS = 16
PTRC_GFX_PRIMORIAL_210 = 210
PTRC_GFX_TAKT_137 = 137
PTRC_GFX_INVARIANT_156 = 156
PTRC_GFX_DEPTH_1414 = 1414

PTRC_MIN_ENGINES = 1
PTRC_DEFAULT_ENGINES = 4
PTRC_MAX_ENGINES = 8

PTRC_TUNNEL_HALF_X = 960
PTRC_TUNNEL_HALF_Y = 540
PTRC_TUNNEL_HALF_Z = 240

PTRC_PYRAMID_CENTER_X = -320
PTRC_PYRAMID_CENTER_Z = 55
PTRC_PYRAMID_HALF_BASE = 192
PTRC_PYRAMID_HEIGHT = 540
PTRC_PYRAMID_ROT_CYCLE = 3288

PTRC_SPHERE_CENTER_X = 320
PTRC_SPHERE_CENTER_Y = -170
PTRC_SPHERE_CENTER_Z = 5
PTRC_SPHERE_RADIUS = 230

PTRC_WIND_AGENTS = 30000
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

PTRC_SHELL_12_DIRS: Tuple[Tuple[int, int, int], ...] = (
    (1, 1, -1), (1, -1, -1), (-1, 1, -1), (-1, -1, -1),
    (1, 1, 1), (1, -1, 1), (-1, 1, 1), (-1, -1, 1),
    (2, 1, -1), (-2, -1, 1), (-1, 2, 1), (1, -2, -1),
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

def ptrc_c_div(num: int, den: int) -> int:
    return int(num / den)


def ptrc_c_rshift(val: int, shift: int) -> int:
    return val >> shift


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


def ptrc_plichta_move(pos: int, delta: int) -> int:
    nxt = pos + delta
    if nxt == 0:
        nxt = 1 if delta >= 0 else -1
    return nxt


def ptrc_get_smooth_rotation(angle_step: int) -> Tuple[int, int]:
    step = angle_step % PTRC_PYRAMID_ROT_CYCLE
    phase = (step // PTRC_GFX_TAKT_137) % PTRC_GFX_JUNCTIONS
    next_phase = (phase + 1) % PTRC_GFX_JUNCTIONS
    sub = step % PTRC_GFX_TAKT_137
    inv_sub = PTRC_GFX_TAKT_137 - sub

    rot_u = ptrc_c_div(PTRC_CLOCK24_U[phase] * inv_sub + PTRC_CLOCK24_U[next_phase] * sub, PTRC_GFX_TAKT_137)
    rot_v = ptrc_c_div(PTRC_CLOCK24_V[phase] * inv_sub + PTRC_CLOCK24_V[next_phase] * sub, PTRC_GFX_TAKT_137)
    return rot_u, rot_v


def ptrc_fcc_slot_hash(x: int, y: int, z: int) -> int:
    qx = ptrc_c_div(x + 1024, 4) & 0xFFFFFFFF
    qy = ptrc_c_div(y + 1024, 4) & 0xFFFFFFFF
    qz = ptrc_c_div(z + 1024, 4) & 0xFFFFFFFF
    h = ((qx * 73856093) ^ (qy * 19349663) ^ (qz * 83492791)) & 0xFFFFFFFF
    return h & (PTRC_OCCUPANCY_SLOTS - 1)


def ptrc_encode_1byte_cascade(cohesion_anchor: int, optics_mode: int, wavelength_id: int) -> int:
    wl = ((wavelength_id - 1) & 30) + 1
    opt = optics_mode & 3
    anc = cohesion_anchor & 1
    return ptrc_u8_no_zero((anc << 7) | (opt << 5) | wl)


def ptrc_get_pyramid_dual_axes(angle_idx: int) -> Tuple[int, int, int, int]:
    norm_idx = angle_idx % PTRC_PYRAMID_ROT_CYCLE
    rev_idx = (PTRC_PYRAMID_ROT_CYCLE - norm_idx) % PTRC_PYRAMID_ROT_CYCLE
    tilt_u, tilt_v = ptrc_get_smooth_rotation(rev_idx)
    pitch_idx = (norm_idx + (PTRC_PYRAMID_ROT_CYCLE >> 2)) % PTRC_PYRAMID_ROT_CYCLE
    raw_pu, raw_pv = ptrc_get_smooth_rotation(pitch_idx)
    mod_u = 1018 + ptrc_c_rshift(raw_pu - 1024, 7)
    mod_v = ptrc_c_rshift(raw_pv, 3)
    rot_u = ptrc_c_rshift(316 * mod_u - 974 * mod_v, 10)
    rot_v = ptrc_c_rshift(316 * mod_v + 974 * mod_u, 10)
    return rot_u, rot_v, tilt_u, tilt_v


def ptrc_point_in_square_pyramid(px: int, py: int, pz: int, rot_u: int, rot_v: int, tilt_u: int, tilt_v: int) -> bool:
    dx = px - PTRC_PYRAMID_CENTER_X
    dy = py
    dz = pz - PTRC_PYRAMID_CENTER_Z
    if abs(dx) > 350 or abs(dy) > 350 or abs(dz) > 350:
        return False

    ty = ptrc_c_rshift(dy * tilt_u - dz * tilt_v, 10)
    tz = ptrc_c_rshift(dy * tilt_v + dz * tilt_u, 10)
    lx = ptrc_c_rshift(dx * rot_u - tz * rot_v, 10)
    lz = ptrc_c_rshift(dx * rot_v + tz * rot_u, 10)

    half_h = PTRC_PYRAMID_HEIGHT >> 1
    if ty < -half_h or ty > half_h:
        return False

    allowed_half_width = ptrc_c_div((ty + half_h) * PTRC_PYRAMID_HALF_BASE, PTRC_PYRAMID_HEIGHT)
    return abs(lx) <= allowed_half_width and abs(lz) <= allowed_half_width


def ptrc_point_in_crystal_sphere(px: int, py: int, pz: int) -> bool:
    dx = px - PTRC_SPHERE_CENTER_X
    dy = py - PTRC_SPHERE_CENTER_Y
    dz = pz - PTRC_SPHERE_CENTER_Z
    if abs(dx) > PTRC_SPHERE_RADIUS or abs(dy) > PTRC_SPHERE_RADIUS or abs(dz) > PTRC_SPHERE_RADIUS:
        return False
    return (dx * dx + dy * dy + dz * dz) <= (PTRC_SPHERE_RADIUS * PTRC_SPHERE_RADIUS)


def ptrc_transpose_wavelength_to_rgb(state_byte: int, depth_shade: int) -> Tuple[int, int, int]:
    wl = state_byte & 0x1F
    opt = (state_byte >> 5) & 3
    if opt == PTRC_OPTICS_CRYSTALLINE or opt == PTRC_OPTICS_FIELD_COUPLED:
        br = 255
        bg = 65 + (wl & 31)
        bb = 195 + (wl & 31)
    else:
        br = 68 + (wl & 15)
        bg = 152 + (wl & 31)
        bb = 235 + (wl & 15)

    r = (br * depth_shade) >> 8
    g = (bg * depth_shade) >> 8
    b = (bb * depth_shade) >> 8
    return (1 if r == 0 else r, 1 if g == 0 else g, 1 if b == 0 else b)


def _project_single_crystal(
    out: bytearray, z_buf: List[int], width: int, height: int,
    wx: int, wy: int, wz: int, r: int, g: int, b: int, blend_mode: int,
) -> None:
    persp = 1414 + wz
    if persp <= 100:
        return
    sx = ptrc_c_div(wx * 1414, persp)
    sy = ptrc_c_div(wy * 1414, persp)
    px = ptrc_c_div((sx + PTRC_TUNNEL_HALF_X) * width, PTRC_TUNNEL_HALF_X * 2)
    py = ptrc_c_div((sy + PTRC_TUNNEL_HALF_Y) * height, PTRC_TUNNEL_HALF_Y * 2)

    if px < 0 or px >= width or py < 0 or py >= height:
        return

    p_flat = py * width + px
    if wz <= z_buf[p_flat]:
        z_buf[p_flat] = wz
        pix = p_flat * 3
        if blend_mode == 0 or (out[pix + 0] == 1 and out[pix + 1] == 2):
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


def _splat_cluster_1_plus_12(
    out: bytearray, z_buf: List[int], width: int, height: int,
    wx: int, wy: int, wz: int, r: int, g: int, b: int, blend_mode: int,
) -> None:
    _project_single_crystal(out, z_buf, width, height, wx, wy, wz, r, g, b, blend_mode)
    obs_dist = PTRC_GFX_DEPTH_1414 + wz
    if obs_dist <= 100:
        return
    shell_span = 1 if blend_mode == 0 else ptrc_c_div(PTRC_GFX_DEPTH_1414 * 5, obs_dist * 3)
    if shell_span > 0:
        sr = max(1, (r * 7) >> 3)
        sg = max(1, (g * 7) >> 3)
        sb = max(1, (b * 7) >> 3)
        dirs = PTRC_SHELL_12_DIRS[:6] if blend_mode == 0 else PTRC_SHELL_12_DIRS
        for ring in range(1, shell_span + 1):
            for dx, dy, dz in dirs:
                _project_single_crystal(
                    out, z_buf, width, height,
                    wx + ((dx * ring + 1) >> 1), wy + ((dy * ring + 1) >> 1), wz + ((dz * ring + 1) >> 1),
                    sr, sg, sb, blend_mode,
                )


@dataclass
class PtrcWindAgent:
    x: int
    y: int
    z: int
    vx: int
    vy: int
    vz: int
    impulse: int
    state_byte: int

class PtrcGfxContext:
    def __init__(self, seed: int = 137210144, agent_count: int = PTRC_WIND_AGENTS) -> None:
        self.agent_count = agent_count
        rng = ptrc_u64_no_zero((seed ^ 614889782588491410) & U64_MASK)
        self.prime_rings: List[int] = list(PTRC_GFX_RINGS)
        self.sponge: List[int] = [-1 for _ in range(PTRC_GFX_FACETS)]

        for f in range(PTRC_GFX_FACETS):
            rng = ptrc_u64_no_zero(((rng * 137 + (f + 1) * 211) & U64_MASK) ^ (rng >> 13))
            raw = int(rng % PTRC_GFX_PRIMORIAL_210) - 105
            self.sponge[f] = ptrc_z_no_zero(raw)

        self.cell_impulse: List[int] = [1 for _ in range(PTRC_OCCUPANCY_SLOTS)]
        self.cell_density: List[int] = [1 for _ in range(PTRC_OCCUPANCY_SLOTS)]
        self.cell_cohesion: List[int] = [1 for _ in range(PTRC_OCCUPANCY_SLOTS)]

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
            opt = PTRC_OPTICS_TRANSLUCENT
            coh = 1 if (a % 5) == 0 else 0
            self.agents.append(
                PtrcWindAgent(
                    x=x, y=y, z=z,
                    vx = 1,
                    vy=1 if (a & 1) == 0 else -1,
                    vz=1 if ((a >> 1) & 1) == 0 else -1,
                    impulse=40 + (a % 180),
                    state_byte=ptrc_encode_1byte_cascade(coh, PTRC_OPTICS_TRANSLUCENT, wl),
                )
            )

        self.takt_counter: int = 1
        self.clock_phase_24: int = 1
        self.observer_sub_takt: int = 1
        self.pyramid_angle_idx: int = 0
        self.active_load: int = 1024
        self.assigned_engines: int = PTRC_DEFAULT_ENGINES
        self.bound_clusters: int = 1
        self.gpu_int32_active: int = 0
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

        self.pyramid_angle_idx = (self.takt_counter * 3) % PTRC_PYRAMID_ROT_CYCLE
        rot_u, rot_v, tilt_u, tilt_v = ptrc_get_pyramid_dual_axes(self.pyramid_angle_idx)

        self.cell_impulse = [1 for _ in range(PTRC_OCCUPANCY_SLOTS)]
        self.cell_density = [1 for _ in range(PTRC_OCCUPANCY_SLOTS)]
        self.cell_cohesion = [1 for _ in range(PTRC_OCCUPANCY_SLOTS)]
        collisions = 0
        obstacle_hits = 0
        bound_cnt = 0
        phase_24 = self.clock_phase_24

        for a, ag in enumerate(self.agents):
            sym_bit = a + self.takt_counter
            is_cohesive = (ag.state_byte >> 7) & 1
            if is_cohesive != 0:
                bound_cnt += 1

            nx = ptrc_plichta_move(ag.x, ag.vx)
            ny = ptrc_plichta_move(ag.y, ag.vy)
            nz = ptrc_plichta_move(ag.z, ag.vz)

            if nx > PTRC_TUNNEL_HALF_X:
                mix = (a * 2654435761 + self.takt_counter * 137) & U64_MASK
                nx = -PTRC_TUNNEL_HALF_X + int(mix & 7) + 1
                ny = ptrc_z_sym_no_zero(int((mix >> 8) % (PTRC_TUNNEL_HALF_Y * 2)) - PTRC_TUNNEL_HALF_Y, a)
                nz = ptrc_z_sym_no_zero(int((mix >> 24) % (PTRC_TUNNEL_HALF_Z * 2)) - PTRC_TUNNEL_HALF_Z, a >> 1)
                ag.vx = 1
                ag.vy = 1 if (sym_bit & 1) == 0 else -1
                ag.vz = 1 if ((sym_bit >> 1) & 1) == 0 else -1
                ag.state_byte = ptrc_encode_1byte_cascade(is_cohesive, 1, (a % 12) + 1)
            elif nx < -PTRC_TUNNEL_HALF_X:
                nx = -PTRC_TUNNEL_HALF_X + 1
                ag.vx = 1

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

            if ptrc_point_in_square_pyramid(nx, ny, nz, rot_u, rot_v, tilt_u, tilt_v):
                obstacle_hits += 1
                collisions += 1
                facet_144 = (a + (self.pyramid_angle_idx // 137) * 6 + phase_24) % PTRC_GFX_FACETS
                aniso_bias = 1 if self.sponge[facet_144] >= 0 else -1
                j_dir = (facet_144 + self.takt_counter) % PTRC_GFX_JUNCTIONS
                _, jy, jz = PTRC_JUNCTION_DIRS_24[j_dir]

                ag.vx = 1
                ag.vy = ptrc_z_sym_no_zero(jy + (1 if ny >= 0 else -1) + aniso_bias, sym_bit)
                ag.vz = ptrc_z_sym_no_zero(jz + (1 if nz >= 0 else -1) - aniso_bias, sym_bit >> 1)
                nx = ptrc_plichta_move(ag.x, -2)
                ny = ptrc_plichta_move(ag.y, ag.vy)
                nz = ptrc_plichta_move(ag.z, ag.vz)
                ag.state_byte = ptrc_encode_1byte_cascade(1, PTRC_OPTICS_FIELD_COUPLED, 22 + (a % 9))
            elif ptrc_point_in_crystal_sphere(nx, ny, nz):
                obstacle_hits += 1
                collisions += 1
                facet_144 = (a * 3 + phase_24) % PTRC_GFX_FACETS
                aniso_bias = 1 if self.sponge[facet_144] >= 0 else -1
                sdy = ny - PTRC_SPHERE_CENTER_Y
                sdz = nz - PTRC_SPHERE_CENTER_Z
                ag.vx = 1
                ag.vy = ptrc_z_sym_no_zero((1 if sdy >= 0 else -1) + aniso_bias, sym_bit)
                ag.vz = ptrc_z_sym_no_zero((1 if sdz >= 0 else -1) - aniso_bias, sym_bit >> 1)
                nx = ptrc_plichta_move(ag.x, -2)
                ny = ptrc_plichta_move(ag.y, ag.vy)
                nz = ptrc_plichta_move(ag.z, ag.vz)
                ag.state_byte = ptrc_encode_1byte_cascade(1, PTRC_OPTICS_CRYSTALLINE, 25 + (a % 6))
            else:
                slot = ptrc_fcc_slot_hash(nx, ny, nz)
                occ_imp = self.cell_impulse[slot]
                dens = self.cell_density[slot]
                slot_coh = self.cell_cohesion[slot]
                if dens < 250:
                    self.cell_density[slot] = dens + 1
                if is_cohesive != 0 and slot_coh < 250:
                    self.cell_cohesion[slot] = slot_coh + 1

                if occ_imp == 1:
                    self.cell_impulse[slot] = ag.impulse
                    ag.vx = 1
                    ag.vy = -1 if ag.vy > 0 else 1
                    ag.vz = -1 if ag.vz > 0 else 1
                else:
                    collisions += 1
                    if (is_cohesive != 0 or slot_coh >= 2) and dens >= 3:
                        if ag.vx > 2:
                            ag.vx -= 1
                        ag.state_byte = ptrc_encode_1byte_cascade(1, PTRC_OPTICS_TRANSLUCENT, 19)
                    else:
                        facet_144 = (slot + occ_imp + phase_24) % PTRC_GFX_FACETS
                        alt_dir = (facet_144 + abs(self.sponge[facet_144])) % PTRC_GFX_JUNCTIONS
                        _, dy_j, dz_j = PTRC_JUNCTION_DIRS_24[alt_dir]
                        ag.vy = 1 if ptrc_z_sym_no_zero(ag.vy + dy_j, sym_bit) >= 0 else -1
                        ag.vz = 1 if ptrc_z_sym_no_zero(ag.vz + dz_j, sym_bit >> 1) >= 0 else -1
                    if ag.impulse > occ_imp:
                        self.cell_impulse[slot] = ag.impulse

            nx = max(-PTRC_TUNNEL_HALF_X, min(PTRC_TUNNEL_HALF_X, nx))
            ny = max(-PTRC_TUNNEL_HALF_Y, min(PTRC_TUNNEL_HALF_Y, ny))
            nz = max(-PTRC_TUNNEL_HALF_Z, min(PTRC_TUNNEL_HALF_Z, nz))
            ag.vx = 1
            ag.vy = 1 if ag.vy >= 0 else -1
            ag.vz = 1 if ag.vz >= 0 else -1
            ag.x, ag.y, ag.z = ptrc_z_no_zero(nx), ptrc_z_no_zero(ny), ptrc_z_no_zero(nz)

        self.deflection_count += collisions
        self.bound_clusters = bound_cnt
        self.active_load = (collisions >> 4) + (obstacle_hits >> 2) + (bound_cnt >> 8) + 600
        eff = self.active_load + (bound_cnt >> 7)
        self.assigned_engines = 8 if eff >= 1900 else (4 if eff >= 1350 else (2 if eff >= 950 else 1))
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
        z_buf = [1000 for _ in range(total_pixels)]
        out = bytearray(b"\x01\x02\x06" * total_pixels)
        if self.render_status == PTRC_RENDER_STALL:
            return bytes(out)

        rot_u, rot_v, tilt_u, tilt_v = ptrc_get_pyramid_dual_axes(self.pyramid_angle_idx)
        half_h = PTRC_PYRAMID_HEIGHT >> 1
        step = 2

        for ty in range(-half_h, half_h + 1, step):
            ny = ptrc_z_no_zero(ty)
            hw = max(1, ptrc_c_div((ty + half_h) * PTRC_PYRAMID_HALF_BASE, PTRC_PYRAMID_HEIGHT))
            fcc_shift = (ty >> 1) & 1
            for s in range(-hw + fcc_shift, hw + 1, step):
                ns = ptrc_z_no_zero(s)
                is_edge = abs(abs(s) - hw) <= step or ty <= (-half_h + step) or ty >= (half_h - step)
                for wall in range(4):
                    if wall == 0:
                        lx, lz, wr, wg, wb = ns, -hw, 215, 165, 55
                    elif wall == 1:
                        lx, lz, wr, wg, wb = hw, ns, 185, 138, 45
                    elif wall == 2:
                        lx, lz, wr, wg, wb = ns, hw, 145, 105, 35
                    else:
                        lx, lz, wr, wg, wb = -hw, ns, 175, 130, 42
                    if is_edge:
                        wr, wg, wb = 252, 220, 115

                    rx = ptrc_c_rshift(lx * rot_u + lz * rot_v, 10)
                    rz = ptrc_c_rshift(-lx * rot_v + lz * rot_u, 10)
                    wy = ptrc_c_rshift(ny * tilt_u + rz * tilt_v, 10)
                    wz = ptrc_c_rshift(-ny * tilt_v + rz * tilt_u, 10) + PTRC_PYRAMID_CENTER_Z
                    wx = rx + PTRC_PYRAMID_CENTER_X
                    _splat_cluster_1_plus_12(out, z_buf, width, height, wx, wy, wz, wr, wg, wb, 0)

        base_hw = PTRC_PYRAMID_HALF_BASE
        for bz in range(-base_hw, base_hw + 1, step):
            nbz = ptrc_z_no_zero(bz)
            fcc_shift = (bz >> 1) & 1
            for bx in range(-base_hw + fcc_shift, base_hw + 1, step):
                nbx = ptrc_z_no_zero(bx)
                is_border = abs(abs(bx) - base_hw) <= step or abs(abs(bz) - base_hw) <= step
                br, bg, bb = (252, 220, 115) if is_border else (115, 84, 30)
                rx = ptrc_c_rshift(nbx * rot_u + nbz * rot_v, 10)
                rz = ptrc_c_rshift(-nbx * rot_v + nbz * rot_u, 10)
                wy = ptrc_c_rshift(half_h * tilt_u + rz * tilt_v, 10)
                wz = ptrc_c_rshift(-half_h * tilt_v + rz * tilt_u, 10) + PTRC_PYRAMID_CENTER_Z
                wx = rx + PTRC_PYRAMID_CENTER_X
                _splat_cluster_1_plus_12(out, z_buf, width, height, wx, wy, wz, br, bg, bb, 0)

        r_sph = PTRC_SPHERE_RADIUS
        r_sq = r_sph * r_sph
        r_inner_sq = (r_sph - 4) * (r_sph - 4)
        for ly in range(-r_sph, r_sph + 1, 2):
            ny = ptrc_z_no_zero(ly)
            fcc_y = (ly >> 1) & 1
            for lz in range(-r_sph + fcc_y, r_sph + 1, 2):
                nz = ptrc_z_no_zero(lz)
                yz_sq = ny * ny + nz * nz
                if yz_sq > r_sq:
                    continue
                for lx in range(-r_sph, r_sph + 1, 2):
                    nx = ptrc_z_no_zero(lx)
                    q = yz_sq + nx * nx
                    if q > r_sq or q < r_inner_sq:
                        continue

                    rx = ptrc_c_rshift(nx * rot_u - nz * rot_v, 10)
                    rz = ptrc_c_rshift(nx * rot_v + nz * rot_u, 10)
                    light = max(55, min(250, 155 - ptrc_c_rshift(rx + ny - rz, 3)))
                    is_ring = abs(ny) <= 4 or abs(nx) <= 4
                    cr = 140 if is_ring else ((light * 3) >> 3)
                    cg = 245 if is_ring else ((light * 7) >> 3)
                    cb = 255 if is_ring else light

                    _splat_cluster_1_plus_12(
                        out, z_buf, width, height,
                        rx + PTRC_SPHERE_CENTER_X,
                        ny + PTRC_SPHERE_CENTER_Y,
                        rz + PTRC_SPHERE_CENTER_Z,
                        cr, cg, cb, 0,
                    )

        for ag in self.agents:
            z_depth = ag.z
            depth_shade = max(50, min(255, 245 - ((z_depth + PTRC_TUNNEL_HALF_Z) >> 2)))
            r, g, b = ptrc_transpose_wavelength_to_rgb(ag.state_byte, depth_shade)
            _splat_cluster_1_plus_12(out, z_buf, width, height, ag.x, ag.y, z_depth, r, g, b, 1)

        return bytes(out)
