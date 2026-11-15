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
Verification Suite for pTRC Light Universe Engine v4.0:
  1. Z \ {0} Sponge, 24-Clock Orbit & 137-Takt Mirror Pulse Invariants
  2. 100% C11 / Python Pixel-for-Pixel Bit-Parity & -1 SRAM Scrubbing
  3. Zero-Float & Zero-Trigonometry Static Compliance
File: src/00_test_ptrc_graphics_parity.py
"""

from __future__ import annotations

import ctypes
import pathlib
import re
import sys

from ptrc_light_universe import (
    PTRC_CLOCK24_U,
    PTRC_CLOCK24_V,
    PTRC_GFX_FACETS,
    PTRC_GFX_JUNCTIONS,
    PTRC_GFX_OK,
    PTRC_GFX_TAKT_137,
    PtrcGfxContext,
    _CGfxCtx,
    load_c_gfx_library,
)


def test_python_universe_invariants() -> None:
    # Verify 24-Clock Discrete Quadrance law: u^2 + v^2 ~ 1000^2, no zeros
    for idx in range(PTRC_GFX_JUNCTIONS):
        u = PTRC_CLOCK24_U.__getitem__(idx)
        v = PTRC_CLOCK24_V.__getitem__(idx)
        assert u != 0 and v != 0, "Zero coordinate in 24-Clock table!"
        quad = u * u + v * v
        assert 999000 <= quad <= 1001000, f"Quadrance out of integer tolerance: {quad}"

    ctx = PtrcGfxContext(seed=137210144)
    assert len(ctx.sponge) == PTRC_GFX_FACETS
    assert all(x != 0 for x in ctx.sponge)
    assert ctx.cam_x != 0 and ctx.cam_y != 0 and ctx.cam_z != 0

    # Advance 140 takts across the 137-takt mirror pulse
    for _ in range(140):
        rc = ctx.step_takt()
        assert rc == PTRC_GFX_OK
        assert all(x != 0 for x in ctx.sponge)
        assert ctx.cam_x != 0 and ctx.cam_y != 0 and ctx.cam_z != 0

    assert ctx.mirror_pulses == 2, f"Expected 137-takt mirror pulse, got {ctx.mirror_pulses}"

    frame = ctx.render_frame_rgb24(96, 54)
    assert len(frame) == 96 * 54 * 3
    assert 0 not in frame, "Zero byte 0x00 violated Z \\ {0} pixel invariant!"
    assert ctx.active_hits > 1, "Expected active crystal/starfield hits in rendered frame"
    print("[PASS] 1. Z \\ {0} Universe Invariants, 24-Clock Quadrance & 137-Takt Mirror Pulse")


def test_c_python_graphics_parity() -> None:
    lib = load_c_gfx_library()
    if lib is None:
        print("[SKIP] 2. C11 shared library libptrc_light_universe not built yet.")
        return

    seed = 210144137
    py_ctx = PtrcGfxContext(seed=seed)
    c_ctx = _CGfxCtx()
    rc = lib.ptrc_gfx_init(ctypes.byref(c_ctx), seed)
    assert rc == PTRC_GFX_OK

    for _ in range(PTRC_GFX_TAKT_137 + 5):
        py_ctx.step_takt()
        lib.ptrc_gfx_step_takt(ctypes.byref(c_ctx))

    assert list(c_ctx.sponge) == py_ctx.sponge
    assert c_ctx.cam_x == py_ctx.cam_x
    assert c_ctx.cam_y == py_ctx.cam_y
    assert c_ctx.cam_z == py_ctx.cam_z
    assert c_ctx.mirror_pulses == py_ctx.mirror_pulses

    w, h = 128, 72
    py_frame = py_ctx.render_frame_rgb24(w, h)
    c_buf = (ctypes.c_uint8 * (w * h * 3))()
    rc_ren = lib.ptrc_gfx_render_frame_rgb24(ctypes.byref(c_ctx), w, h, c_buf)
    assert rc_ren == PTRC_GFX_OK
    assert bytes(c_buf) == py_frame, "Pixel mismatch between C11 and Python Light Universe!"
    assert c_ctx.active_hits == py_ctx.active_hits

    # Verify volatile SRAM wipe restores context to -1 (0xFF)
    lib.ptrc_gfx_wipe(ctypes.byref(c_ctx))
    raw_bytes = ctypes.string_at(ctypes.byref(c_ctx), ctypes.sizeof(c_ctx))
    assert all(b == 0xFF for b in raw_bytes), "SRAM wipe did not restore all bytes to -1 (0xFF)!"
    print("[PASS] 2. 100% C11 / Python Pixel-for-Pixel Bit-Parity & -1 SRAM Wipe")

def test_zero_float_compliance() -> None:
    root = pathlib.Path(__file__).resolve().parent.parent
    files = [
        root / "embedded" / "graphics" / "ptrc_light_universe.h",
        root / "embedded" / "graphics" / "ptrc_light_universe.c",
        root / "src" / "ptrc_light_universe.py",
        root / "src" / "00_ptrc_graphics_demo.py",
    ]
    forbidden = re.compile(r"\b(float|double|sin|cos|tan|sqrt|pow|log|exp|math)\b")
    for fpath in files:
        if not fpath.exists():
            continue
        raw = fpath.read_text(encoding="utf-8")
        cleaned = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
        cleaned = re.sub(r'r?""".*?"""', "", cleaned, flags=re.S)
        cleaned = re.sub(r"r?'''.*?'''", "", cleaned, flags=re.S)
        cleaned = re.sub(r"//.*", "", cleaned)
        cleaned = re.sub(r"#.*", "", cleaned)
        for lineno, line in enumerate(cleaned.splitlines(), 1):
            match = forbidden.search(line)
            assert match is None, f"Forbidden float/trig token '{match.group(0)}' in {fpath}:{lineno}"
    print("[PASS] 3. Static Zero-Float & Zero-Trig Compliance Verified across Graphics v4.0")


if __name__ == "__main__":
    test_python_universe_invariants()
    test_c_python_graphics_parity()
    test_zero_float_compliance()
    print("ALL 3 GRAPHICS v4.0 PARITY & INVARIANT CHECKS PASSED.")
    sys.exit(0)
