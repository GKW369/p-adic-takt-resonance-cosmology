# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Observer Universe v4.0
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

r"""
pTRC v4.0 Discrete 1-Bit Integer Physics & Observer Universe (Python Reference).
File: src/ptrc_light_universe.py

Pure information-state lattice in Z \ {0}: 144-facet integer crystals (radius 9),
1+12 cuboctahedral topology, 24 contact junctions, 120 free memory facets,
1 takt = 1 light-speed step, Observer View rendered every 137 takts.
"""

from __future__ import annotations

import ctypes
import pathlib
from typing import List, Optional, Tuple

PTRC_GFX_FACETS = 144
PTRC_GFX_FREE_FACETS = 120
PTRC_GFX_JUNCTIONS = 24
PTRC_GFX_NEIGHBORS = 12
PTRC_GFX_CRYSTAL_RAD = 9
PTRC_GFX_CRYSTAL_STEP = 18
PTRC_GFX_PRIME_RINGS = 16
PTRC_GFX_PRIMORIAL_210 = 210
PTRC_GFX_TAKT_137 = 137
PTRC_GFX_LIMIT_156 = 156
PTRC_GFX_VOXEL_SHIFT = 16
PTRC_GFX_MAX_STEPS = 44

PTRC_GFX_OK = 1
PTRC_GFX_ERR = -1

U64_MASK = 0xFFFFFFFFFFFFFFFF
U32_MASK = 0xFFFFFFFF

PTRC_GFX_RINGS: Tuple[int, ...] = (
    11, 13, 17, 19, 23, 29, 37, 41,
    43, 47, 53, 59, 61, 67, 71, 73,
)

PTRC_NEIGHBOR_DX: Tuple[int, ...] = (18, 18, -18, -18, 18, 18, -18, -18, 0, 0, 0, 0)
PTRC_NEIGHBOR_DY: Tuple[int, ...] = (18, -18, 18, -18, 0, 0, 0, 0, 18, 18, -18, -18)
PTRC_NEIGHBOR_DZ: Tuple[int, ...] = (0, 0, 0, 0, 18, -18, 18, -18, 18, -18, 18, -18)

PTRC_JUNCTION_X: Tuple[int, ...] = (
     9,  9,  9,  9, -9, -9, -9, -9,  9,  9,  9,  9,
    -9, -9, -9, -9,  1, -1,  1, -1,  1, -1,  1, -1,
)
PTRC_JUNCTION_Y: Tuple[int, ...] = (
     9,  9, -9, -9,  9,  9, -9, -9,  1, -1,  1, -1,
     1, -1,  1, -1,  9,  9,  9,  9, -9, -9, -9, -9,
)
PTRC_JUNCTION_Z: Tuple[int, ...] = (
     1, -1,  1, -1,  1, -1,  1, -1,  9,  9, -9, -9,
     9,  9, -9, -9,  9,  9, -9, -9,  9,  9, -9, -9,
)

PTRC_CLOCK24_U: Tuple[int, ...] = (
    1000,  966,  866,  707,  500,  259,
      -1, -259, -500, -707, -866, -966,
   -1000, -966, -866, -707, -500, -259,
       1,  259,  500,  707,  866,  966,
)

PTRC_CLOCK24_V: Tuple[int, ...] = (
       1,  259,  500,  707,  866,  966,
    1000,  966,  866,  707,  500,  259,
      -1, -259, -500, -707, -866, -966,
   -1000, -966, -866, -707, -500, -259,
)


def ptrc_gfx_z_no_zero(v: int) -> int:
    v32 = v & U32_MASK
    if v32 & 0x80000000:
        v32 -= 0x100000000
    return -1 if v32 == 0 else v32


def ptrc_gfx_u64_no_zero(v: int) -> int:
    v64 = v & U64_MASK
    return 1 if v64 == 0 else v64


def _c_shr_i32(val: int, shift: int) -> int:
    v32 = val & U32_MASK
    if v32 & 0x80000000:
        v32 -= 0x100000000
    return v32 >> shift


def _crystal_facet_metric(lx: int, ly: int, lz: int) -> int:
    ax = abs(lx)
    ay = abs(ly)
    az = abs(lz)
    max_axis = max(ax, ay, az)
    oct_val = (ax + ay + az) >> 1
    return max_axis if max_axis > oct_val else oct_val


class PtrcGfxContext:
    """Bit-exact Python reference for ptrc_gfx_ctx_t in embedded/graphics/ptrc_light_universe.c."""

    def __init__(self, seed: int = 137210144) -> None:
        state = ptrc_gfx_u64_no_zero((seed ^ 614889782588491410) & U64_MASK)
        self.prime_rings: List[int] = list(PTRC_GFX_RINGS)
        self.sponge: List[int] = list((1,)) * PTRC_GFX_FACETS
        self.crystal_state: List[int] = list((1,)) * PTRC_GFX_FACETS

        for f in range(PTRC_GFX_FACETS):
            state = (((state * 137 + (f + 1) * 211) & U64_MASK) ^ (state >> 13)) & U64_MASK
            state = ptrc_gfx_u64_no_zero(state)
            raw = int(state % PTRC_GFX_PRIMORIAL_210) - 105
            self.sponge.__setitem__(f, ptrc_gfx_z_no_zero(raw))
            st8 = int(state & 0xFF)
            self.crystal_state.__setitem__(f, 0xFF if st8 == 0 else st8)

        self.takt_counter: int = 1
        self.clock_phase_24: int = 1
        u0 = PTRC_CLOCK24_U.__getitem__(0)
        v0 = PTRC_CLOCK24_V.__getitem__(0)
        self.cam_x: int = ptrc_gfx_z_no_zero(u0 * 2750)
        self.cam_y: int = ptrc_gfx_z_no_zero(780000)
        self.cam_z: int = ptrc_gfx_z_no_zero(v0 * 2750)
        self.active_hits: int = 1
        self.mirror_pulses: int = 1

    def step_takt(self) -> int:
        phase_idx = (self.clock_phase_24 - 1) % PTRC_GFX_JUNCTIONS
        p_ring = self.prime_rings.__getitem__(phase_idx & 15)

        for j in range(PTRC_GFX_JUNCTIONS):
            j_facet = PTRC_GFX_FREE_FACETS + j
            mem_facet = (j * 5 + phase_idx) % PTRC_GFX_FREE_FACETS
            coupled = self.sponge.__getitem__(j_facet) ^ self.sponge.__getitem__(mem_facet)
            self.sponge.__setitem__(j_facet, ptrc_gfx_z_no_zero(coupled + p_ring))

            s_prev = self.crystal_state.__getitem__(mem_facet)
            s_next = ((s_prev ^ (coupled & 0xFF)) + p_ring) & 0xFF
            self.crystal_state.__setitem__(mem_facet, 0xFF if s_next == 0 else s_next)

        if (self.takt_counter % PTRC_GFX_TAKT_137) == 0:
            for f in range(PTRC_GFX_FACETS):
                self.sponge.__setitem__(f, ptrc_gfx_z_no_zero(~self.sponge.__getitem__(f)))
                inv = (~self.crystal_state.__getitem__(f)) & 0xFF
                self.crystal_state.__setitem__(f, 0xFF if inv == 0 else inv)
            self.mirror_pulses += 1

        u = PTRC_CLOCK24_U.__getitem__(phase_idx)
        v = PTRC_CLOCK24_V.__getitem__(phase_idx)
        self.cam_x = ptrc_gfx_z_no_zero(u * 2750)
        self.cam_y = ptrc_gfx_z_no_zero(780000 + v * 120)
        self.cam_z = ptrc_gfx_z_no_zero(v * 2750)

        self.takt_counter += 1
        self.clock_phase_24 = (self.clock_phase_24 % PTRC_GFX_JUNCTIONS) + 1
        return PTRC_GFX_OK

    def advance_observer_epoch(self) -> int:
        for _ in range(PTRC_GFX_TAKT_137):
            self.step_takt()
        return PTRC_GFX_OK

    def render_frame_rgb24(self, width: int, height: int) -> bytes:
        if width < 2 or height < 2:
            raise ValueError("Width and height must be >= 2")

        half_w = width >> 1
        half_h = height >> 1
        phase_idx = (self.clock_phase_24 - 1) % PTRC_GFX_JUNCTIONS
        rot_u = PTRC_CLOCK24_U.__getitem__(phase_idx)
        rot_v = PTRC_CLOCK24_V.__getitem__(phase_idx)
        hit_counter = 1

        scale_x = (1024 // half_w) if (1024 // half_w) >= 1 else 1
        scale_y = (576 // half_h) if (576 // half_h) >= 1 else 1

        out = bytearray(width * height * 3)
        sponge = self.sponge
        cstate = self.crystal_state
        cam_x = self.cam_x
        cam_y = self.cam_y
        cam_z = self.cam_z

        for py in range(height):
            dy = ptrc_gfx_z_no_zero((py - half_h) * scale_y)
            row_offset = py * width * 3

            for px in range(width):
                dx = ptrc_gfx_z_no_zero((px - half_w) * scale_x)

                dir_x = ptrc_gfx_z_no_zero(_c_shr_i32(-1024 * rot_u + dx * rot_v, 10) * 84)
                dir_y = ptrc_gfx_z_no_zero((-280 - dy) * 84)
                dir_z = ptrc_gfx_z_no_zero(_c_shr_i32(-1024 * rot_v - dx * rot_u, 10) * 84)

                ray_x = cam_x
                ray_y = cam_y
                ray_z = cam_z

                out_r = 2
                out_g = 2
                out_b = 5

                for _ in range(1, PTRC_GFX_MAX_STEPS + 1):
                    ray_x += dir_x
                    ray_y += dir_y
                    ray_z += dir_z

                    vx = ptrc_gfx_z_no_zero(_c_shr_i32(ray_x, PTRC_GFX_VOXEL_SHIFT))
                    vy = ptrc_gfx_z_no_zero(_c_shr_i32(ray_y, PTRC_GFX_VOXEL_SHIFT))
                    vz = ptrc_gfx_z_no_zero(_c_shr_i32(ray_z, PTRC_GFX_VOXEL_SHIFT))

                    # A. 24 Contact Junctions (Active Information Bridges)
                    hit_junction = False
                    for j in range(PTRC_GFX_JUNCTIONS):
                        jdx = abs(vx - PTRC_JUNCTION_X.__getitem__(j))
                        jdy = abs(vy - PTRC_JUNCTION_Y.__getitem__(j))
                        jdz = abs(vz - PTRC_JUNCTION_Z.__getitem__(j))
                        if (jdx + jdy + jdz) <= 2:
                            jf = PTRC_GFX_FREE_FACETS + j
                            jstate = cstate.__getitem__(jf)
                            out_r = 252
                            out_g = (180 + (jstate & 0x3F)) & 0xFF
                            out_b = (64 + (jstate & 0x3F)) & 0xFF
                            hit_junction = True
                            hit_counter += 1
                            break
                    if hit_junction:
                        break

                    # B. Central 144-Facet Crystal (Radius = 9 units to each facet center)
                    m_center = _crystal_facet_metric(vx, vy, vz)
                    if m_center <= PTRC_GFX_CRYSTAL_RAD:
                        facet_id = abs(vx * 7 + vy * 11 + vz * 13) % PTRC_GFX_FREE_FACETS
                        elem_state = cstate.__getitem__(facet_id)
                        sp_val = sponge.__getitem__(facet_id)
                        edge = (abs(vx + vy) + abs(vy + vz)) % 3
                        base_lum = 250 if edge == 0 else (155 + (elem_state & 0x3F))
                        out_r = base_lum & 0xFF
                        out_g = ((base_lum * 198) >> 8) & 0xFF
                        out_b = (((base_lum * 64) >> 8) + (sp_val & 0x1F)) & 0xFF
                        hit_counter += 1
                        break

                    # C. 12 Surrounding 144-Facet Crystals enclosing the Central Crystal
                    hit_shell = False
                    for n in range(PTRC_GFX_NEIGHBORS):
                        lx = vx - PTRC_NEIGHBOR_DX.__getitem__(n)
                        ly = vy - PTRC_NEIGHBOR_DY.__getitem__(n)
                        lz = vz - PTRC_NEIGHBOR_DZ.__getitem__(n)
                        mn = _crystal_facet_metric(lx, ly, lz)
                        if mn == PTRC_GFX_CRYSTAL_RAD or mn == (PTRC_GFX_CRYSTAL_RAD - 1):
                            if ((abs(lx) + abs(ly) + abs(lz)) & 1) != 0:
                                facet_id = (n * 10 + abs(lx + ly * 3 + lz * 5)) % PTRC_GFX_FREE_FACETS
                                fstate = cstate.__getitem__(facet_id)
                                lum = 150 + (fstate & 0x3F)
                                if (n & 1) == 0:
                                    out_r = 32
                                    out_g = ((lum * 215) >> 8) & 0xFF
                                    out_b = lum & 0xFF
                                else:
                                    out_r = ((lum * 195) >> 8) & 0xFF
                                    out_g = 68
                                    out_b = lum & 0xFF
                                hit_shell = True
                                hit_counter += 1
                                break
                    if hit_shell:
                        break

                    # D. Far-Field 120-Facet Isotropic Lattice Background Nodes
                    sig = abs(vx * 137 + vy * 211 + vz * 157)
                    if (sig % 17) == 1 and (sig % 29) == 1:
                        fid = sig % PTRC_GFX_FREE_FACETS
                        st = cstate.__getitem__(fid)
                        out_r = (40 + (st & 0x7F)) & 0xFF
                        out_g = (90 + ((st >> 1) & 0x7F)) & 0xFF
                        out_b = (160 + (st & 0x5F)) & 0xFF
                        hit_counter += 1
                        break

                pix = row_offset + px * 3
                out.__setitem__(pix + 0, 1 if out_r == 0 else out_r)
                out.__setitem__(pix + 1, 1 if out_g == 0 else out_g)
                out.__setitem__(pix + 2, 1 if out_b == 0 else out_b)

        self.active_hits = hit_counter
        return bytes(out)


def write_ppm_rgb24(filepath: pathlib.Path, width: int, height: int, rgb_bytes: bytes) -> None:
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    filepath.write_bytes(header + rgb_bytes)


class _CGfxCtx(ctypes.Structure):
    _fields_ = [
        ("sponge", ctypes.c_int32 * PTRC_GFX_FACETS),
        ("crystal_state", ctypes.c_uint8 * PTRC_GFX_FACETS),
        ("prime_rings", ctypes.c_uint32 * PTRC_GFX_PRIME_RINGS),
        ("takt_counter", ctypes.c_uint64),
        ("clock_phase_24", ctypes.c_uint32),
        ("cam_x", ctypes.c_int32),
        ("cam_y", ctypes.c_int32),
        ("cam_z", ctypes.c_int32),
        ("active_hits", ctypes.c_uint32),
        ("mirror_pulses", ctypes.c_uint32),
    ]


def load_c_gfx_library(search_root: Optional[pathlib.Path] = None) -> Optional[ctypes.CDLL]:
    root = search_root or pathlib.Path(__file__).resolve().parent.parent
    candidates = [
        root / "build" / "libptrc_light_universe.so",
        root / "build" / "libptrc_light_universe.dylib",
        root / "build" / "ptrc_light_universe.dll",
        root / "build" / "Release" / "ptrc_light_universe.dll",
    ]
    for cand in candidates:
        if cand.exists():
            lib = ctypes.CDLL(str(cand))
            lib.ptrc_gfx_init.argtypes = [ctypes.POINTER(_CGfxCtx), ctypes.c_uint64]
            lib.ptrc_gfx_init.restype = ctypes.c_int

            lib.ptrc_gfx_step_takt.argtypes = [ctypes.POINTER(_CGfxCtx)]
            lib.ptrc_gfx_step_takt.restype = ctypes.c_int

            lib.ptrc_gfx_advance_observer_epoch.argtypes = [ctypes.POINTER(_CGfxCtx)]
            lib.ptrc_gfx_advance_observer_epoch.restype = ctypes.c_int

            lib.ptrc_gfx_render_frame_rgb24.argtypes = [
                ctypes.POINTER(_CGfxCtx),
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.POINTER(ctypes.c_uint8),
            ]
            lib.ptrc_gfx_render_frame_rgb24.restype = ctypes.c_int

            lib.ptrc_gfx_wipe.argtypes = [ctypes.POINTER(_CGfxCtx)]
            lib.ptrc_gfx_wipe.restype = None
            return lib
    return None
