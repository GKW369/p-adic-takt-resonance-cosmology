# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Light Universe Engine v4.0
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
pTRC v4.0 Discrete 1-Bit Integer Physics & Light Universe Engine (Python Reference).
File: src/ptrc_light_universe.py

Strictly pure integer (-1 adjacent to +1, no zero point), zero-trigonometry,
and bit-identical to embedded/graphics/ptrc_light_universe.c.
"""

from __future__ import annotations

import ctypes
import pathlib
from typing import List, Optional, Tuple

PTRC_GFX_FACETS = 144
PTRC_GFX_JUNCTIONS = 24
PTRC_GFX_PRIME_RINGS = 16
PTRC_GFX_PRIMORIAL_210 = 210
PTRC_GFX_TAKT_137 = 137
PTRC_GFX_LIMIT_156 = 156
PTRC_GFX_VOXEL_SHIFT = 16
PTRC_GFX_VOXEL_STEP = 65536
PTRC_GFX_MAX_STEPS = 28

PTRC_GFX_OK = 1
PTRC_GFX_ERR = -1

U64_MASK = 0xFFFFFFFFFFFFFFFF
U32_MASK = 0xFFFFFFFF

# 16 Coprime Non-Mersenne Prime Rings (gcd(p, 210) == 1)
PTRC_GFX_RINGS: Tuple[int, ...] = (
    11, 13, 17, 19, 23, 29, 37, 41,
    43, 47, 53, 59, 61, 67, 71, 73,
)

# 24-Clock Discrete Quadrance Orbit Table (u^2 + v^2 = 1000^2, zero trig)
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
    """Maps signed 32-bit integer into Z \\ {0}: 0 resolves directly to -1."""
    v32 = v & U32_MASK
    if v32 & 0x80000000:
        v32 -= 0x100000000
    return -1 if v32 == 0 else v32


def ptrc_gfx_u64_no_zero(v: int) -> int:
    """Maps unsigned 64-bit integer away from zero: 0 resolves to 1."""
    v64 = v & U64_MASK
    return 1 if v64 == 0 else v64


def _c_shr_i32(val: int, shift: int) -> int:
    """Arithmetic right shift matching signed 32-bit C11 semantics."""
    v32 = val & U32_MASK
    if v32 & 0x80000000:
        v32 -= 0x100000000
    return v32 >> shift


class PtrcGfxContext:
    """Pure Python reference matching ptrc_gfx_ctx_t in embedded/graphics/ptrc_light_universe.c."""

    def __init__(self, seed: int = 137210144) -> None:
        state = ptrc_gfx_u64_no_zero((seed ^ 614889782588491410) & U64_MASK)
        self.prime_rings: List[int] = list(PTRC_GFX_RINGS)
        self.sponge: List[int] = list((1,)) * PTRC_GFX_FACETS

        for f in range(PTRC_GFX_FACETS):
            state = (((state * 137 + (f + 1) * 211) & U64_MASK) ^ (state >> 13)) & U64_MASK
            state = ptrc_gfx_u64_no_zero(state)
            raw = int(state % PTRC_GFX_PRIMORIAL_210) - 105
            self.sponge.__setitem__(f, ptrc_gfx_z_no_zero(raw))

        self.takt_counter: int = 1
        self.clock_phase_24: int = 1
        u0 = PTRC_CLOCK24_U.__getitem__(0)
        v0 = PTRC_CLOCK24_V.__getitem__(0)
        self.cam_x: int = ptrc_gfx_z_no_zero(u0 * 920)
        self.cam_y: int = ptrc_gfx_z_no_zero(110000)
        self.cam_z: int = ptrc_gfx_z_no_zero(v0 * 920)
        self.active_hits: int = 1
        self.mirror_pulses: int = 1

    def step_takt(self) -> int:
        phase_idx = (self.clock_phase_24 - 1) % PTRC_GFX_JUNCTIONS
        u = PTRC_CLOCK24_U.__getitem__(phase_idx)
        v = PTRC_CLOCK24_V.__getitem__(phase_idx)

        self.cam_x = ptrc_gfx_z_no_zero(u * 920)
        self.cam_y = ptrc_gfx_z_no_zero(110000 + v * 16)
        self.cam_z = ptrc_gfx_z_no_zero(v * 920)

        if (self.takt_counter % PTRC_GFX_TAKT_137) == 0:
            for f in range(PTRC_GFX_FACETS):
                self.sponge.__setitem__(f, ptrc_gfx_z_no_zero(~self.sponge.__getitem__(f)))
            self.mirror_pulses += 1
        else:
            f0 = (self.takt_counter * 37) % PTRC_GFX_FACETS
            f1 = (f0 + 73) % PTRC_GFX_FACETS
            p_val = self.prime_rings.__getitem__(phase_idx & 15)
            self.sponge.__setitem__(f0, ptrc_gfx_z_no_zero(self.sponge.__getitem__(f0) + p_val))
            self.sponge.__setitem__(f1, ptrc_gfx_z_no_zero(self.sponge.__getitem__(f1) ^ p_val))

        self.takt_counter += 1
        self.clock_phase_24 = (self.clock_phase_24 % PTRC_GFX_JUNCTIONS) + 1
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
        cam_x = self.cam_x
        cam_y = self.cam_y
        cam_z = self.cam_z

        for py in range(height):
            dy = ptrc_gfx_z_no_zero((py - half_h) * scale_y)
            row_offset = py * width * 3

            for px in range(width):
                dx = ptrc_gfx_z_no_zero((px - half_w) * scale_x)

                dir_x = ptrc_gfx_z_no_zero(_c_shr_i32(-1024 * rot_u + dx * rot_v, 10) * 64)
                dir_y = ptrc_gfx_z_no_zero((-115 - dy) * 64)
                dir_z = ptrc_gfx_z_no_zero(_c_shr_i32(-1024 * rot_v - dx * rot_u, 10) * 64)

                ray_x = cam_x
                ray_y = cam_y
                ray_z = cam_z

                out_r = 1
                out_g = 1
                out_b = 3

                for step in range(1, PTRC_GFX_MAX_STEPS + 1):
                    ray_x += dir_x
                    ray_y += dir_y
                    ray_z += dir_z

                    vx = ptrc_gfx_z_no_zero(_c_shr_i32(ray_x, PTRC_GFX_VOXEL_SHIFT))
                    vy = ptrc_gfx_z_no_zero(_c_shr_i32(ray_y, PTRC_GFX_VOXEL_SHIFT))
                    vz = ptrc_gfx_z_no_zero(_c_shr_i32(ray_z, PTRC_GFX_VOXEL_SHIFT))

                    manhattan = abs(vx) + abs(vy) + abs(vz)
                    facet_idx = abs(vx * 3 + vy * 5 + vz * 7) % PTRC_GFX_FACETS
                    facet_val = sponge.__getitem__(facet_idx)

                    if manhattan <= 16 and (vy & 1) != 0 and ((abs(vx + vz + (facet_val & 7)) % 3) != 0):
                        shade = 250 - (step * 5)
                        if shade < 64:
                            shade = 64
                        out_r = shade
                        out_g = (shade * 195) >> 8
                        out_b = (shade * 52) >> 8
                        if out_b == 0:
                            out_b = 1
                        hit_counter += 1
                        break

                    sig = abs(vx * 137 + vy * 211 + vz * 157 + facet_val)
                    if (sig % 11) == 1 and (sig % 23) == 1:
                        ring_sel = sig % PTRC_GFX_PRIME_RINGS
                        lum = 240 - (step * 4)
                        if lum < 72:
                            lum = 72
                        if (ring_sel & 1) == 0:
                            out_r = 24
                            out_g = (lum * 220) >> 8
                            out_b = lum
                        else:
                            out_r = (lum * 210) >> 8
                            out_g = 42
                            out_b = lum
                        hit_counter += 1
                        break

                pix = row_offset + px * 3
                out.__setitem__(pix + 0, 1 if out_r == 0 else out_r)
                out.__setitem__(pix + 1, 1 if out_g == 0 else out_g)
                out.__setitem__(pix + 2, 1 if out_b == 0 else out_b)

        self.active_hits = hit_counter
        return bytes(out)
