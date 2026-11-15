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
Interactive Terminal Benchmark & HD Frame Export for pTRC Light Universe v4.0.
File: src/00_ptrc_graphics_demo.py
"""

from __future__ import annotations

import ctypes
import pathlib
import time

from ptrc_light_universe import (
    PTRC_GFX_FACETS,
    PTRC_GFX_JUNCTIONS,
    PTRC_GFX_OK,
    PTRC_GFX_PRIMORIAL_210,
    PTRC_GFX_TAKT_137,
    PtrcGfxContext,
    _CGfxCtx,
    load_c_gfx_library,
    write_ppm_rgb24,
)


def main() -> None:
    print("===============================================================================")
    print("  pTRC LIGHT UNIVERSE v4.0 — PURE INTEGER 1+12 RAY-MARCHING ENGINE")
    print(f"  Axioms   : Z \\ {{0}} (No Zero) | {PTRC_GFX_FACETS} Facets | {PTRC_GFX_JUNCTIONS}-Clock | {PTRC_GFX_TAKT_137}-Takt Mirror")
    print("===============================================================================")

    seed = 137210144
    lib = load_c_gfx_library()
    root = pathlib.Path(__file__).resolve().parent.parent
    out_dir = root / "build"
    out_dir.mkdir(parents=True, exist_ok=True)

    if lib is not None:
        c_ctx = _CGfxCtx()
        lib.ptrc_gfx_init(ctypes.byref(c_ctx), seed)
        for _ in range(18):
            lib.ptrc_gfx_step_takt(ctypes.byref(c_ctx))

        # Benchmark 120 frames at 640x360 in bare-metal C11
        bw, bh, frames = 640, 360, 120
        b_buf = (ctypes.c_uint8 * (bw * bh * 3))()
        t0 = time.perf_counter_ns()
        for _ in range(frames):
            lib.ptrc_gfx_step_takt(ctypes.byref(c_ctx))
            rc = lib.ptrc_gfx_render_frame_rgb24(ctypes.byref(c_ctx), bw, bh, b_buf)
            assert rc == PTRC_GFX_OK
        t1 = time.perf_counter_ns()

        elapsed_us = (t1 - t0) // 1000
        fps = (frames * 1_000_000) // (elapsed_us if elapsed_us >= 1 else 1)
        px_per_sec = (frames * bw * bh * 1_000_000) // (elapsed_us if elapsed_us >= 1 else 1)

        # Render 1280x720 HD showcase frame
        hd_w, hd_h = 1280, 720
        hd_buf = (ctypes.c_uint8 * (hd_w * hd_h * 3))()
        lib.ptrc_gfx_render_frame_rgb24(ctypes.byref(c_ctx), hd_w, hd_h, hd_buf)
        hd_bytes = bytes(hd_buf)
        ppm_path = out_dir / "ptrc_light_universe_720p.ppm"
        write_ppm_rgb24(ppm_path, hd_w, hd_h, hd_bytes)

        print(f" + Native C11 Kernel    : ACTIVE (sizeof(ctx)={ctypes.sizeof(c_ctx)} bytes, Zero malloc)")
        print(f" + 640x360 Throughput   : {frames} frames in {elapsed_us} us (~{fps} FPS | ~{px_per_sec} px/sec)")
        print(f" + HD Frame Export      : {ppm_path} ({hd_w}x{hd_h}, 0x00 bytes: {hd_bytes.count(0)})")
        print(f" + Active Crystal Hits  : {c_ctx.active_hits} | Base Primorial: {PTRC_GFX_PRIMORIAL_210}")
        lib.ptrc_gfx_wipe(ctypes.byref(c_ctx))
    else:
        py_ctx = PtrcGfxContext(seed=seed)
        for _ in range(18):
            py_ctx.step_takt()
        w, h = 320, 180
        t0 = time.perf_counter_ns()
        frame = py_ctx.render_frame_rgb24(w, h)
        t1 = time.perf_counter_ns()
        ppm_path = out_dir / "ptrc_light_universe_preview.ppm"
        write_ppm_rgb24(ppm_path, w, h, frame)
        print(f" + Python Reference     : {w}x{h} rendered in {(t1 - t0) // 1000} us -> {ppm_path}")

    print("===============================================================================")


if __name__ == "__main__":
    main()
