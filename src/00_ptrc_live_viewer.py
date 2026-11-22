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

"""
Full-HD (1920x1080) Echtzeit-Live-Viewer fuer den pTRC 3D-Windkanal v4.6.0
mit adaptiver Multi-Engine-Zuweisung (1..8 Engines), Kohaesions-Clustern
und automatischer int32-GPU/CPU-Erkennung.
"""

from __future__ import annotations

import os

import ctypes
import sys
import tempfile
import time
import tkinter as tk
from importlib import import_module
from pathlib import Path

from ptrc_light_universe import PTRC_RENDER_STALL

parity_mod = import_module("00_test_ptrc_graphics_parity")

FULL_HD_WIDTH = 1920
FULL_HD_HEIGHT = 1080


class PtrcFullHdLiveObserver:
    def __init__(self, width: int = FULL_HD_WIDTH, height: int = FULL_HD_HEIGHT) -> None:
        self.width = width
        self.height = height
        header_bytes = f"P6\n{self.width} {self.height}\n255\n".encode("ascii")
        self.header_len = len(header_bytes)
        self.rgb_len = self.width * self.height * 3

        self.ppm_buf = (ctypes.c_uint8 * (self.header_len + self.rgb_len))()
        ctypes.memmove(self.ppm_buf, header_bytes, self.header_len)
        self.rgb_ptr = ctypes.cast(
            ctypes.byref(self.ppm_buf, self.header_len), ctypes.POINTER(ctypes.c_uint8)
        )

        self.tmp_dir = tempfile.TemporaryDirectory()
        self.lib = parity_mod.build_shared_lib(Path(self.tmp_dir.name))
        self.ctx = parity_mod.CPtrcGfxCtx()
        self.seed = 137210144
        self.lib.ptrc_gfx_init(ctypes.byref(self.ctx), self.seed)

        self.paused = False
        self.closing = False
        self.after_id = None
        self.fullscreen = False
        self.sub_steps_per_frame = 2
        self.start_time = time.perf_counter()
        self.pause_started = 0.0
        self.paused_total = 0.0

        self.root = tk.Tk()
        self.root.title("pTRC 3D Space-Crystal Windtunnel v4.6.0 | Adaptive 1..8 Engines (1920x1080)")
        self.root.configure(bg="#010206")
        self.root.geometry(f"{self.width}x{self.height}")

        self.photo = tk.PhotoImage(width=self.width, height=self.height)
        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg="#010206",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        self.hud_bg = self.canvas.create_rectangle(14, 14, 1904, 56, fill="#08101E", outline="#1E3A5F")
        self.hud_text = self.canvas.create_text(
            24,
            35,
            anchor=tk.W,
            fill="#93C5FD",
            font=("Consolas", 10, "bold"),
            text="Initialisiere pTRC 3D-Raumkristall-Engine v4.6.0...",
        )

        self.root.bind("<space>", self.toggle_pause)
        self.root.bind("<plus>", self.speed_up)
        self.root.bind("<KP_Add>", self.speed_up)
        self.root.bind("<minus>", self.slow_down)
        self.root.bind("<KP_Subtract>", self.slow_down)
        self.root.bind("<r>", self.reset_universe)
        self.root.bind("<R>", self.reset_universe)
        self.root.bind("<f>", self.toggle_fullscreen)
        self.root.bind("<F>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.close)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def speed_up(self, _event: tk.Event | None = None) -> None:
        self.sub_steps_per_frame = min(137, self.sub_steps_per_frame + 1)

    def slow_down(self, _event: tk.Event | None = None) -> None:
        self.sub_steps_per_frame = max(1, self.sub_steps_per_frame - 1)

    def toggle_pause(self, _event: tk.Event | None = None) -> None:
        if not self.paused:
            self.paused = True
            self.pause_started = time.perf_counter()
        else:
            self.paused = False
            self.paused_total += time.perf_counter() - self.pause_started

    def toggle_fullscreen(self, _event: tk.Event | None = None) -> None:
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def reset_universe(self, _event: tk.Event | None = None) -> None:
        self.seed = (self.seed + 137210) ^ 0x5A5A137
        self.lib.ptrc_gfx_init(ctypes.byref(self.ctx), self.seed)
        self.start_time = time.perf_counter()
        self.paused_total = 0.0

    @staticmethod
    def _format_elapsed(seconds: float) -> str:
        total_s = int(seconds)
        hrs = total_s // 3600
        mins = (total_s % 3600) // 60
        secs = total_s % 60
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"

    def update_loop(self) -> None:
        if self.closing:
            return
        if not self.paused:
            t0 = time.perf_counter()
            elapsed = max(0.001, t0 - self.start_time - self.paused_total)

            load_divisor = 1
            if self.ctx.render_interval_takts > 137:
                load_divisor = self.ctx.render_interval_takts // 137
            effective_steps = max(1, self.sub_steps_per_frame // load_divisor)

            for _ in range(effective_steps):
                self.lib.ptrc_gfx_step_takt_adaptive(ctypes.byref(self.ctx))

            rc = self.lib.ptrc_gfx_render_observer_rgb24(
                ctypes.byref(self.ctx), self.width, self.height, self.rgb_ptr
            )

            new_photo = tk.PhotoImage(width=self.width, height=self.height, data=bytes(self.ppm_buf))
            self.canvas.itemconfigure(self.image_item, image=new_photo)
            self.photo = new_photo

            dt_ms = (time.perf_counter() - t0) * 1000.0
            fps = 1000.0 / dt_ms if dt_ms > 0.0 else 0.0
            takts_per_sec = self.ctx.takt_counter / elapsed
            hw_tag = "INT32-GPU" if self.ctx.gpu_int32_active == 1 else "CPU-INT"
            status_str = "STALL" if rc == PTRC_RENDER_STALL else f"INT:{self.ctx.render_interval_takts}T"

            self.canvas.itemconfigure(
                self.hud_text,
                text=(
                    f"ZEIT:{self._format_elapsed(elapsed)} | TAKTE:{self.ctx.takt_counter:,} ({takts_per_sec:.1f} T/s) | "
                    f"HW:{hw_tag} | ENG:{self.ctx.assigned_engines}/8 | KOHAESION:{self.ctx.bound_clusters:,} | "
                    f"LAST:{self.ctx.active_load} ({status_str}) | KOLL:{self.ctx.deflection_count:,} | {fps:.1f} FPS"
                ),
            )

        if not self.closing:
            elapsed_ms = int((time.perf_counter() - t0) * 1000.0)
            delay_ms = max(2, 16 - elapsed_ms)
            self.after_id = self.root.after(delay_ms, self.update_loop)

    def close(self, _event: tk.Event | None = None) -> None:
        self.lib.ptrc_gfx_wipe(ctypes.byref(self.ctx))
        self.tmp_dir.cleanup()
        self.closing = True
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass
        self.root.quit()
        os._exit(0)

    def run(self) -> int:
        self.after_id = self.root.after(5, self.update_loop)
        self.root.mainloop()
        return 0


if __name__ == "__main__":
    viewer = PtrcFullHdLiveObserver(FULL_HD_WIDTH, FULL_HD_HEIGHT)
    sys.exit(viewer.run())
