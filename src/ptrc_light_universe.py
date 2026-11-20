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

from dataclasses import dataclass, field
from typing import List, Tuple

PTRC_GFX_FACETS = 144
PTRC_GFX_JUNCTIONS = 24
PTRC_GFX_MEM_FACETS = 120
PTRC_GFX_STABLE_ELEMENTS = 81
PTRC_GFX_PRIMORIAL_210 = 210
PTRC_GFX_TAKT_137 = 137
PTRC_GFX_INVARIANT_156 = 156
PTRC_GFX_DEPTH_1414 = 1414

PTRC_LATTICE_DIM = 16
PTRC_LATTICE_CELLS = PTRC_LATTICE_DIM ** 3
PTRC_MAX_IMPULSE_PACKETS = 1024

PTRC_GFX_OK = 1
PTRC_GFX_ERR = -1
PTRC_RENDER_READY = 1
PTRC_RENDER_WAIT = 2
PTRC_RENDER_STALL = -2

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


def ptrc_plichta_step_axis(pos: int, delta: int) -> int:
    nxt = pos + delta
    if nxt == 0:
        nxt = 1 if delta >= 0 else -1
    if nxt > 8:
        nxt = -8 + ((nxt - 9) & 7)
        if nxt == 0:
            nxt = -1
    elif nxt < -8:
        nxt = 8 - ((-nxt - 9) & 7)
        if nxt == 0:
            nxt = 1
    return nxt


def ptrc_coord_to_idx(c: int) -> int:
    return (c + 8) if c < 0 else (c + 7)


def ptrc_cell_linear_idx(x: int, y: int, z: int) -> int:
    ix = ptrc_coord_to_idx(x) & 15
    iy = ptrc_coord_to_idx(y) & 15
    iz = ptrc_coord_to_idx(z) & 15
    return (iz * PTRC_LATTICE_DIM + iy) * PTRC_LATTICE_DIM + ix


def ptrc_encode_1byte_state(element_id: int, wavelength_id: int) -> int:
    wl = ((wavelength_id - 1) & 30) + 1
    el_band = (element_id % 7) + 1
    return ptrc_u8_no_zero((el_band << 5) | (wl & 0x1F))


def ptrc_transpose_wavelength_to_rgb(state_byte: int, depth_shade: int) -> Tuple[int, int, int]:
    wl = state_byte & 0x1F
    band = (state_byte >> 5) & 7
    r = (((wl * 8 + band * 19) & 0xFF) * depth_shade) >> 8
    g = ((((32 - wl) * 7 + band * 29) & 0xFF) * depth_shade) >> 8
    b = ((((wl * 13) ^ (band * 41)) & 0xFF) * depth_shade) >> 8
    return (1 if r == 0 else r, 1 if g == 0 else g, 1 if b == 0 else b)


@dataclass
class PtrcCrystalCell:
    cx: int
    cy: int
    cz: int
    state_byte: int = 1
    impulse: int = 1
    observer_cluster: int = 1
    facet_mem: List[int] = field(default_factory=lambda: [1] * PTRC_GFX_MEM_FACETS)


@dataclass
class PtrcImpulsePacket:
    x: int
    y: int
    z: int
    dir_idx: int
    impulse: int
    wavelength_id: int
    element_id: int

class PtrcGfxContext:
    def __init__(self, seed: int = 137210144) -> None:
        rng = ptrc_u64_no_zero((seed ^ 614889782588491410) & U64_MASK)
        self.prime_rings: List[int] = list(PTRC_GFX_RINGS)
        self.sponge: List[int] = [1] * PTRC_GFX_FACETS

        for f in range(PTRC_GFX_FACETS):
            rng = ptrc_u64_no_zero(((rng * 137 + (f + 1) * 211) & U64_MASK) ^ (rng >> 13))
            raw = int(rng % PTRC_GFX_PRIMORIAL_210) - 105
            self.sponge[f] = ptrc_z_no_zero(raw)

        self.cells: List[PtrcCrystalCell] = []
        for iz in range(PTRC_LATTICE_DIM):
            cz = (iz - 8) if iz < 8 else (iz - 7)
            for iy in range(PTRC_LATTICE_DIM):
                cy = (iy - 8) if iy < 8 else (iy - 7)
                for ix in range(PTRC_LATTICE_DIM):
                    cx = (ix - 8) if ix < 8 else (ix - 7)
                    self.cells.append(
                        PtrcCrystalCell(
                            cx=cx,
                            cy=cy,
                            cz=cz,
                            observer_cluster=((ix + iy + iz) % 24) + 1,
                        )
                    )

        self.packets: List[PtrcImpulsePacket] = []
        for p in range(PTRC_MAX_IMPULSE_PACKETS):
            rng = ptrc_u64_no_zero(rng * 6364136223846793005 + 1442695040888963407)
            sx = int(rng % 16) - 8
            sy = int((rng >> 8) % 16) - 8
            sz = int((rng >> 16) % 16) - 8
            self.packets.append(
                PtrcImpulsePacket(
                    x=ptrc_z_no_zero(sx),
                    y=ptrc_z_no_zero(sy),
                    z=ptrc_z_no_zero(sz),
                    dir_idx=p % PTRC_GFX_JUNCTIONS,
                    impulse=(p % 240) + 10,
                    wavelength_id=(p % 31) + 1,
                    element_id=(p % PTRC_GFX_STABLE_ELEMENTS) + 1,
                )
            )

        self.takt_counter: int = 1
        self.clock_phase_24: int = 1
        self.active_load: int = PTRC_MAX_IMPULSE_PACKETS
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

        for cell in self.cells:
            cell.impulse = 1

        collisions = 0
        occupied_cells = 0

        for p_idx, pkt in enumerate(self.packets):
            d_idx = pkt.dir_idx % PTRC_GFX_JUNCTIONS
            dx, dy, dz = PTRC_JUNCTION_DIRS_24[d_idx]
            nx = ptrc_plichta_step_axis(pkt.x, dx)
            ny = ptrc_plichta_step_axis(pkt.y, dy)
            nz = ptrc_plichta_step_axis(pkt.z, dz)

            cell = self.cells[ptrc_cell_linear_idx(nx, ny, nz)]
            if cell.impulse == 1:
                cell.impulse = pkt.impulse
                cell.state_byte = ptrc_encode_1byte_state(pkt.element_id, pkt.wavelength_id)
                cell.facet_mem[(self.takt_counter + p_idx) % PTRC_GFX_MEM_FACETS] = pkt.element_id
                pkt.x, pkt.y, pkt.z = nx, ny, nz
                occupied_cells += 1
            else:
                collisions += 1
                weaker_imp = pkt.impulse
                weaker_wl = pkt.wavelength_id
                weaker_el = pkt.element_id

                if pkt.impulse > cell.impulse:
                    weaker_imp = cell.impulse
                    cell.impulse = pkt.impulse
                    cell.state_byte = ptrc_encode_1byte_state(pkt.element_id, pkt.wavelength_id)
                    pkt.x, pkt.y, pkt.z = nx, ny, nz

                alt_dir = (d_idx + (weaker_imp % 11) + 1) % PTRC_GFX_JUNCTIONS
                adx, ady, adz = PTRC_JUNCTION_DIRS_24[alt_dir]
                ax = ptrc_plichta_step_axis(nx, adx)
                ay = ptrc_plichta_step_axis(ny, ady)
                az = ptrc_plichta_step_axis(nz, adz)

                alt_cell = self.cells[ptrc_cell_linear_idx(ax, ay, az)]
                if alt_cell.impulse == 1:
                    alt_cell.impulse = ptrc_u8_no_zero(weaker_imp)
                    alt_cell.state_byte = ptrc_encode_1byte_state(weaker_el, weaker_wl)
                    occupied_cells += 1
                pkt.x, pkt.y, pkt.z = ax, ay, az
                pkt.dir_idx = alt_dir

        self.deflection_count += collisions
        self.active_load = occupied_cells + (collisions * 2)
        self.evaluate_observer_sync()

        self.takt_counter += 1
        self.clock_phase_24 = (self.clock_phase_24 % PTRC_GFX_JUNCTIONS) + 1
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
        out = bytearray(b"\x01\x02\x06" * (width * height))
        if self.render_status == PTRC_RENDER_STALL:
            return bytes(out)

        phase_idx = (self.clock_phase_24 - 1) % PTRC_GFX_JUNCTIONS
        rot_u = PTRC_CLOCK24_U[phase_idx]
        rot_v = PTRC_CLOCK24_V[phase_idx]

        for cell in self.cells:
            if cell.impulse == 1:
                continue
            x = cell.cx * 28
            y = cell.cy * 28
            z = cell.cz * 28

            rx = (x * rot_u - z * rot_v) >> 10
            rz = ((x * rot_v + z * rot_u) >> 10) + 320
            if rz <= 20:
                continue

            denom = int((rz * 1000) / PTRC_GFX_DEPTH_1414) + PTRC_GFX_INVARIANT_156
            px = int((rx * width) / denom) + (width >> 1)
            py = int((y * height) / denom) + (height >> 1)

            if 0 <= px < width and 0 <= py < height:
                depth_shade = max(48, min(255, 255 - ((rz - 100) >> 1)))
                r, g, b = ptrc_transpose_wavelength_to_rgb(cell.state_byte, depth_shade)
                pix = (py * width + px) * 3
                out[pix + 0] = r
                out[pix + 1] = g
                out[pix + 2] = b

        return bytes(out)
