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
Full-HD (1920x1080) 3D-Windkanal Live-Viewer (32cm x 18cm x 8cm, 60.000 Molekuel-Cluster,
scharfkantige rotierende 3D-Pyramide mittig im linken Drittel, Z-Occlusion & Tiefenskalierung).

Steuerung im Fenster:
  [+] / [-]   : Stroemungs-Takte pro Frame (1..8)
  [LEERTASTE] : Pause / Weiter
  [R]         : Reset mit neuem Primzahl-Seed
  [F]         : Vollbild (1920x1080) umschalten
  [ESC]       : Beenden
"""

from __future__ import annotations

import ctypes
import sys
import tempfile
import time
import tkinter as tk
from importlib import import_module
from pathlib import Path

from ptrc_light_universe import PTRC_RENDER_STALL, PTRC_WIND_AGENTS

parity_mod = import_module("00_test_ptrc_graphics_parity")

FULL_HD_WIDTH = 1920
FULL_HD_HEIGHT = 1080


class PtrcWindtunnelLiveViewer:
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
        self.fullscreen = False
        self.steps_per_frame = 1

        self.root = tk.Tk()
        self.root.title("pTRC 3D-Windkanal v4.5.0 | 32x18x8 cm | 60.000 1+12-Cluster | Full-HD")
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

        self.hud_bg = self.canvas.create_rectangle(16, 16, 1460, 56, fill="#08101E", outline="#1E3A5F")
        self.hud_text = self.canvas.create_text(
            28,
            36,
            anchor=tk.W,
            fill="#93C5FD",
            font=("Consolas", 11, "bold"),
            text="Initialisiere 3D-Windkanal (32x18x8 cm, 60.000 Molekuel-Cluster)...",
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
        self.steps_per_frame = min(8, self.steps_per_frame + 1)

    def slow_down(self, _event: tk.Event | None = None) -> None:
        self.steps_per_frame = max(1, self.steps_per_frame - 1)

    def toggle_pause(self, _event: tk.Event | None = None) -> None:
        self.paused = not self.paused

    def toggle_fullscreen(self, _event: tk.Event | None = None) -> None:
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def reset_universe(self, _event: tk.Event | None = None) -> None:
        self.seed = (self.seed + 137210) ^ 0x5A5A137
        self.lib.ptrc_gfx_init(ctypes.byref(self.ctx), self.seed)

    def update_loop(self) -> None:
        if not self.paused:
            t0 = time.perf_counter()

            for _ in range(self.steps_per_frame):
                self.lib.ptrc_gfx_step_takt(ctypes.byref(self.ctx))

            rc = self.lib.ptrc_gfx_render_observer_rgb24(
                ctypes.byref(self.ctx), self.width, self.height, self.rgb_ptr
            )
            self.photo.configure(data=bytes(self.ppm_buf))

            dt_ms = (time.perf_counter() - t0) * 1000.0
            fps = 1000.0 / dt_ms if dt_ms > 0.0 else 0.0
            status_str = "EVENT-HORIZON STALL" if rc == PTRC_RENDER_STALL else f"INTERVALL {self.ctx.render_interval_takts}T"

            self.canvas.itemconfigure(
                self.hud_text,
                text=(
                    f"3D-WINDKANAL 32x18x8cm | {PTRC_WIND_AGENTS:,} AGENTEN | "
                    f"TAKT: {self.ctx.takt_counter:,} ({self.steps_per_frame}x) | "
                    f"LAST: {self.ctx.active_load} | {status_str} | "
                    f"KOLLISIONEN: {self.ctx.deflection_count:,} | {dt_ms:.1f} ms ({fps:.1f} FPS)"
                ),
            )

        self.root.after(1, self.update_loop)

    def close(self, _event: tk.Event | None = None) -> None:
        self.lib.ptrc_gfx_wipe(ctypes.byref(self.ctx))
        self.tmp_dir.cleanup()
        self.root.destroy()

    def run(self) -> int:
        self.root.after(5, self.update_loop)
        self.root.mainloop()
        return 0


if __name__ == "__main__":
    viewer = PtrcWindtunnelLiveViewer(FULL_HD_WIDTH, FULL_HD_HEIGHT)
    sys.exit(viewer.run())

