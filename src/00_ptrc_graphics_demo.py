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
Observer Universe Windtunnel Full-HD 1080p Render & 137-Takt Epoch Demo.
File: src/00_ptrc_graphics_demo.py
"""

from __future__ import annotations

import ctypes
import pathlib
import time

from ptrc_light_universe import (
    PTRC_GFX_AGENT_COUNT,
    PTRC_GFX_CRYSTAL_RAD,
    PTRC_GFX_FACETS,
    PTRC_GFX_FREE_FACETS,
    PTRC_GFX_JUNCTIONS,
    PTRC_GFX_OK,
    PTRC_GFX_TAKT_137,
    PtrcGfxContext,
    _CGfxCtx,
    load_c_gfx_library,
    write_ppm_rgb24,
)


def main() -> None:
    print("===============================================================================")
    print("  pTRC OBSERVER WINDTUNNEL v4.1 — 60,000-AGENT 1+12 CRYSTAL LATTICE (Z \\ {0})")
    print(f"  Crystal  : {PTRC_GFX_FACETS} Facets (Radius {PTRC_GFX_CRYSTAL_RAD}) | {PTRC_GFX_JUNCTIONS} Junctions | {PTRC_GFX_FREE_FACETS} Memory")
    print(f"  Dynamics : {PTRC_GFX_AGENT_COUNT} Agents | 1 Takt = Light Speed | Render Every {PTRC_GFX_TAKT_137} Takts")
    print("===============================================================================")

    seed = 137210144
    lib = load_c_gfx_library()
    root = pathlib.Path(__file__).resolve().parent.parent
    out_dir = root / "build"
    out_dir.mkdir(parents=True, exist_ok=True)

    if lib is not None:
        c_ctx = _CGfxCtx()
        lib.ptrc_gfx_init(ctypes.byref(c_ctx), seed)

        # Advance 1 full Observer Epoch (137 light-speed takts)
        t_ep0 = time.perf_counter_ns()
        rc_ep = lib.ptrc_gfx_advance_observer_epoch(ctypes.byref(c_ctx))
        t_ep1 = time.perf_counter_ns()
        assert rc_ep == PTRC_GFX_OK
        epoch_us = (t_ep1 - t_ep0) // 1000

        # Render Full-HD 1920x1080 Observer View at 137-Takt Pulse
        fhd_w, fhd_h = 1920, 1080
        fhd_buf = (ctypes.c_uint8 * (fhd_w * fhd_h * 3))()
        t_ren0 = time.perf_counter_ns()
        rc_ren = lib.ptrc_gfx_render_frame_rgb24(ctypes.byref(c_ctx), fhd_w, fhd_h, fhd_buf)
        t_ren1 = time.perf_counter_ns()
        assert rc_ren == PTRC_GFX_OK

        ren_us = (t_ren1 - t_ren0) // 1000
        fhd_bytes = bytes(fhd_buf)
        ppm_path = out_dir / "ptrc_light_universe_1080p.ppm"
        write_ppm_rgb24(ppm_path, fhd_w, fhd_h, fhd_bytes)

        print(f" + Native C11 Kernel    : ACTIVE (sizeof(ctx)={ctypes.sizeof(c_ctx)} bytes, Zero malloc)")
        print(f" + 137-Takt Light Epoch : {PTRC_GFX_AGENT_COUNT} agents x 137 takts in {epoch_us} us (Pulses: {c_ctx.mirror_pulses})")
        print(f" + Full-HD 1080p Render : {fhd_w}x{fhd_h} in {ren_us} us -> {ppm_path} (0x00 bytes: {fhd_bytes.count(0)})")
        print(f" + Active Lattice Hits  : {c_ctx.active_hits} (60,000 Agents + Rotating 1+12 Pyramid)")
        lib.ptrc_gfx_wipe(ctypes.byref(c_ctx))
    else:
        py_ctx = PtrcGfxContext(seed=seed)
        py_ctx.advance_observer_epoch()
        w, h = 640, 360
        frame = py_ctx.render_frame_rgb24(w, h)
        ppm_path = out_dir / "ptrc_light_universe_preview.ppm"
        write_ppm_rgb24(ppm_path, w, h, frame)
        print(f" + Python Reference     : 137-Takt Epoch -> {ppm_path}")

    print("===============================================================================")


if __name__ == "__main__":
    main()
