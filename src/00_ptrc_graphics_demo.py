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

"""
3D-Raumkristall-Demo (v4.5.0) mit lastabhaengigem 137-Takt-Beobachter-Render
und optionaler nativer C11-Full-HD-Beschleunigung (1920x1080) ohne 0x00-Bytes.
"""

from __future__ import annotations

import ctypes
import sys
import tempfile
import time
from pathlib import Path

from ptrc_light_universe import PTRC_RENDER_READY, PTRC_RENDER_STALL, PtrcGfxContext

# Importiert die C11-Bridge aus dem Paritaetstest fuer Full-HD-Geschwindigkeit
from importlib import import_module

parity_mod = import_module("00_test_ptrc_graphics_parity")


def save_ppm_p6(path: Path, width: int, height: int, rgb_bytes: bytes) -> None:
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    path.write_bytes(header + rgb_bytes)


def run_demo(width: int = 1920, height: int = 1080, steps: int = 274) -> int:
    out_dir = Path(__file__).resolve().parent.parent / "build" / "observer_frames"
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        lib = parity_mod.build_shared_lib(Path(tmp))
        ctx = parity_mod.CPtrcGfxCtx()
        lib.ptrc_gfx_init(ctypes.byref(ctx), 137210144)

        frame_buf = (ctypes.c_uint8 * (width * height * 3))()
        rendered_frames = 0

        t0 = time.perf_counter()
        for _ in range(steps):
            lib.ptrc_gfx_step_takt(ctypes.byref(ctx))
            if ctx.render_status == PTRC_RENDER_READY:
                lib.ptrc_gfx_render_observer_rgb24(ctypes.byref(ctx), width, height, frame_buf)
                frame_path = out_dir / f"ptrc_crystal_takt_{ctx.last_render_takt:05d}.ppm"
                save_ppm_p6(frame_path, width, height, bytes(frame_buf))
                rendered_frames += 1
            elif ctx.render_status == PTRC_RENDER_STALL:
                print(f"[EVENT HORIZON] Takt {ctx.takt_counter}: Render-Stopp unter Volllast ({ctx.active_load})")

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        lib.ptrc_gfx_wipe(ctypes.byref(ctx))

        print(
            f"[DONE] {steps} Takte in {elapsed_ms:.2f} ms | Aufloesung={width}x{height} | "
            f"Gerenderte Beobachter-Frames={rendered_frames} -> {out_dir}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(run_demo())
