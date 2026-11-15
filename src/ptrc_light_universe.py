# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Observer Windtunnel v4.1
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
pTRC v4.1 Discrete 1-Bit Integer Physics & Observer Windtunnel (Python Reference).
File: src/ptrc_light_universe.py

Bit-exact match to embedded/graphics/ptrc_light_universe.c:
  - 144-facet integer crystals (radius 9, 24 contact junctions, 120 memory facets)
  - 60,000 freely distributed 1-bit information agents flowing left -> right
  - Rotating 1+12 golden pyramid floating up/down in the front third (1/5 screen width)
  - 1 takt = 1 light-speed step, Observer View rendered every 137 takts
"""

from __future__ import annotations

import ctypes
import pathlib
from typing import List, Optional, Tuple

PTRC_GFX_FACETS = 144
PTRC_GFX_FREE_FACETS = 120
PTRC_GFX_JUNCTIONS = 24
PTRC_GFX_CRYSTAL_RAD = 9
PTRC_GFX_PRIME_RINGS = 16
PTRC_GFX_PRIMORIAL_210 = 210
PTRC_GFX_TAKT_137 = 137
PTRC_GFX_AGENT_COUNT = 60000

VIRT_W = 16384
VIRT_H = 9216

PTRC_GFX_OK = 1
PTRC_GFX_ERR = -1

U64_MASK = 0xFFFFFFFFFFFFFFFF
U32_MASK = 0xFFFFFFFF

PTRC_GFX_RINGS: Tuple[int, ...] = (
    11, 13, 17, 19, 23, 29, 37, 41,
    43, 47, 53, 59, 61, 67, 71, 73,
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


def _c_div_trunc(num: int, den: int) -> int:
    q = abs(num) // abs(den)
    return -q if (num < 0) ^ (den < 0) else q


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

        self.agent_x: List[int] = list((1,)) * PTRC_GFX_AGENT_COUNT
        self.agent_y: List[int] = list((1,)) * PTRC_GFX_AGENT_COUNT
        self.agent_vx: List[int] = list((1,)) * PTRC_GFX_AGENT_COUNT
        self.agent_vy: List[int] = list((1,)) * PTRC_GFX_AGENT_COUNT
        self.agent_state: List[int] = list((1,)) * PTRC_GFX_AGENT_COUNT

        for i in range(PTRC_GFX_AGENT_COUNT):
            state = (state * 6364136223846793005 + 1442695040888963407) & U64_MASK
            state = ptrc_gfx_u64_no_zero(state)
            ax = int(state % VIRT_W) + 1
            state = (((state ^ (state >> 17)) * 211) + 137) & U64_MASK
            state = ptrc_gfx_u64_no_zero(state)
            ay = int(state % VIRT_H) + 1

            self.agent_x.__setitem__(i, ptrc_gfx_z_no_zero(ax))
            self.agent_y.__setitem__(i, ptrc_gfx_z_no_zero(ay))
            self.agent_vx.__setitem__(i, ptrc_gfx_z_no_zero(44 + (i % 19)))
            self.agent_vy.__setitem__(i, ptrc_gfx_z_no_zero((i % 5) - 2))
            ast = int((state >> 8) & 0xFF)
            self.agent_state.__setitem__(i, 0xFF if ast == 0 else ast)

        self.takt_counter: int = 1
        self.clock_phase_24: int = 1
        self.pyramid_cx: int = ptrc_gfx_z_no_zero(4600)
        self.pyramid_cy: int = ptrc_gfx_z_no_zero(VIRT_H >> 1)
        self.active_hits: int = 1
        self.mirror_pulses: int = 1

    def step_takt(self) -> int:
        phase_idx = (self.clock_phase_24 - 1) % PTRC_GFX_JUNCTIONS
        rot_u = PTRC_CLOCK24_U.__getitem__(phase_idx)
        rot_v = PTRC_CLOCK24_V.__getitem__(phase_idx)
        p_ring = self.prime_rings.__getitem__(phase_idx & 15)

        for j in range(PTRC_GFX_JUNCTIONS):
            jf = PTRC_GFX_FREE_FACETS + j
            mf = (j * 5 + phase_idx) % PTRC_GFX_FREE_FACETS
            coupled = self.sponge.__getitem__(jf) ^ self.sponge.__getitem__(mf)
            self.sponge.__setitem__(jf, ptrc_gfx_z_no_zero(coupled + p_ring))
            sn = ((self.crystal_state.__getitem__(mf) ^ (coupled & 0xFF)) + p_ring) & 0xFF
            self.crystal_state.__setitem__(mf, 0xFF if sn == 0 else sn)

        if (self.takt_counter % PTRC_GFX_TAKT_137) == 0:
            for f in range(PTRC_GFX_FACETS):
                self.sponge.__setitem__(f, ptrc_gfx_z_no_zero(~self.sponge.__getitem__(f)))
                inv = (~self.crystal_state.__getitem__(f)) & 0xFF
                self.crystal_state.__setitem__(f, 0xFF if inv == 0 else inv)
            self.mirror_pulses += 1

        py_center = (VIRT_H >> 1) + _c_shr_i32(rot_v * 680, 10)
        self.pyramid_cx = ptrc_gfx_z_no_zero(4600 + _c_shr_i32(rot_u * 180, 10))
        self.pyramid_cy = ptrc_gfx_z_no_zero(py_center)

        pyr_rad = 1638
        pyr_cx = self.pyramid_cx
        pyr_cy = self.pyramid_cy
        takt_u32 = self.takt_counter & U32_MASK

        ax_list = self.agent_x
        ay_list = self.agent_y
        vx_list = self.agent_vx
        vy_list = self.agent_vy
        st_list = self.agent_state

        for i in range(PTRC_GFX_AGENT_COUNT):
            ax = ax_list.__getitem__(i) + vx_list.__getitem__(i)
            ay = ay_list.__getitem__(i) + vy_list.__getitem__(i)

            if ax > VIRT_W:
                ax = ptrc_gfx_z_no_zero((ax % 64) + 1)
                ay = ptrc_gfx_z_no_zero((((i * 137 + takt_u32 * 31) & U32_MASK) % VIRT_H) + 1)
                vx_list.__setitem__(i, ptrc_gfx_z_no_zero(44 + (i % 19)))
                vy_list.__setitem__(i, ptrc_gfx_z_no_zero((i % 5) - 2))

            if ay < 1:
                ay = 1
                vy_list.__setitem__(i, abs(vy_list.__getitem__(i)))
            elif ay > VIRT_H:
                ay = VIRT_H
                vy_list.__setitem__(i, -abs(vy_list.__getitem__(i)))

            dx = ax - pyr_cx
            dy = ay - pyr_cy
            manhattan = abs(dx) + abs(dy)

            if manhattan <= (pyr_rad + 420):
                push_y = 18 if dy >= 0 else -18
                if manhattan <= pyr_rad:
                    offset = pyr_rad - abs(dx) + 24
                    ay = ptrc_gfx_z_no_zero(pyr_cy + (offset if dy >= 0 else -offset))
                    vx_list.__setitem__(i, ptrc_gfx_z_no_zero(36 + (rot_u & 15)))
                    vy_list.__setitem__(i, ptrc_gfx_z_no_zero(push_y + _c_shr_i32(rot_v, 7)))
                    st = (st_list.__getitem__(i) ^ 0xA5) & 0xFF
                    st_list.__setitem__(i, 0xFF if st == 0 else st)
                else:
                    delta_vy = (_c_shr_i32(rot_v, 8) * (1 if (i & 1) else -1)) if dx > 0 else _c_shr_i32(push_y, 2)
                    vy_list.__setitem__(i, ptrc_gfx_z_no_zero(vy_list.__getitem__(i) + delta_vy))
            else:
                cur_vy = vy_list.__getitem__(i)
                if cur_vy > 3:
                    vy_list.__setitem__(i, cur_vy - 1)
                elif cur_vy < -3:
                    vy_list.__setitem__(i, cur_vy + 1)

            ax_list.__setitem__(i, ptrc_gfx_z_no_zero(ax))
            ay_list.__setitem__(i, ptrc_gfx_z_no_zero(ay))

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

        total_pixels = width * height
        out = bytearray(b"\x01\x02\x06" * total_pixels)

        phase_idx = (self.clock_phase_24 - 1) % PTRC_GFX_JUNCTIONS
        rot_u = PTRC_CLOCK24_U.__getitem__(phase_idx)
        rot_v = PTRC_CLOCK24_V.__getitem__(phase_idx)
        hit_counter = 1

        ax_list = self.agent_x
        ay_list = self.agent_y
        vy_list = self.agent_vy
        st_list = self.agent_state

        for i in range(PTRC_GFX_AGENT_COUNT):
            ax = ax_list.__getitem__(i)
            ay = ay_list.__getitem__(i)
            if ax < 1 or ax > VIRT_W or ay < 1 or ay > VIRT_H:
                continue
            px = ((ax - 1) * width) >> 14
            py = ((ay - 1) * height) // VIRT_H
            if px >= width:
                px = width - 1
            if py >= height:
                py = height - 1

            st = st_list.__getitem__(i)
            vy_abs = abs(vy_list.__getitem__(i))

            if vy_abs > 10:
                r_val = (185 + (st & 0x3F)) & 0xFF
                g_val = 58
                b_val = (210 + (st & 0x2A)) & 0xFF
            elif (st & 1) == 0:
                r_val = 28
                g_val = (175 + (st & 0x4F)) & 0xFF
                b_val = (215 + (st & 0x27)) & 0xFF
            else:
                r_val = 42
                g_val = (120 + (st & 0x5F)) & 0xFF
                b_val = (195 + (st & 0x3B)) & 0xFF

            pix = (py * width + px) * 3
            out.__setitem__(pix + 0, 1 if r_val == 0 else r_val)
            out.__setitem__(pix + 1, 1 if g_val == 0 else g_val)
            out.__setitem__(pix + 2, 1 if b_val == 0 else b_val)
            hit_counter += 1

        pyr_cx_px = (self.pyramid_cx * width) >> 14
        pyr_cy_px = (self.pyramid_cy * height) // VIRT_H
        pyr_half_w = width // 10
        if pyr_half_w < 8:
            pyr_half_w = 8

        y_min = max(0, pyr_cy_px - pyr_half_w)
        y_max = min(height - 1, pyr_cy_px + pyr_half_w)
        x_min = max(0, pyr_cx_px - pyr_half_w)
        x_max = min(width - 1, pyr_cx_px + pyr_half_w)
        sponge = self.sponge

        for py in range(y_min, y_max + 1):
            dy = py - pyr_cy_px
            row_off = py * width * 3

            for px in range(x_min, x_max + 1):
                dx = px - pyr_cx_px
                rx = _c_shr_i32(dx * rot_u - dy * rot_v, 10)
                ry = _c_shr_i32(dx * rot_v + dy * rot_u, 10)

                dist = abs(rx) + abs(ry)
                if dist <= pyr_half_w:
                    facet_id = abs(rx * 3 + ry * 5) % PTRC_GFX_FACETS
                    fval = sponge.__getitem__(facet_id)
                    facet_border = 1 if ((abs(rx) % 9) == 0 or (abs(ry) % 9) == 0) else 0

                    shade = 215 - _c_div_trunc((rx + ry) * 65, pyr_half_w) + (fval & 15)
                    if facet_border:
                        shade += 32
                    if shade > 255:
                        shade = 255
                    if shade < 85:
                        shade = 85

                    gr = shade & 0xFF
                    gg = ((shade * 198) >> 8) & 0xFF
                    gb = ((shade * 54) >> 8) & 0xFF
                    if gb == 0:
                        gb = 1

                    pix = row_off + px * 3
                    out.__setitem__(pix + 0, gr)
                    out.__setitem__(pix + 1, gg)
                    out.__setitem__(pix + 2, gb)
                    hit_counter += 1

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
        ("agent_x", ctypes.c_int32 * PTRC_GFX_AGENT_COUNT),
        ("agent_y", ctypes.c_int32 * PTRC_GFX_AGENT_COUNT),
        ("agent_vx", ctypes.c_int32 * PTRC_GFX_AGENT_COUNT),
        ("agent_vy", ctypes.c_int32 * PTRC_GFX_AGENT_COUNT),
        ("agent_state", ctypes.c_uint8 * PTRC_GFX_AGENT_COUNT),
        ("takt_counter", ctypes.c_uint64),
        ("clock_phase_24", ctypes.c_uint32),
        ("pyramid_cx", ctypes.c_int32),
        ("pyramid_cy", ctypes.c_int32),
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
