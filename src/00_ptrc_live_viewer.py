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
Full-HD (1920x1080) Echtzeit-Live-Viewer fuer das pTRC 3D-Raumkristall-Universum v4.5.0.
Nutzt direkt die kompilierte C11-Engine (libptrc_light_universe.so) und zeigt
Takt-Fortschritt, Informationslast, Render-Intervall (137 -> Verlangsamung -> STALL)
sowie Impuls-Kollisionsumlenkungen live ohne externe Abhaengigkeiten an.

Steuerung im Fenster:
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

from ptrc_light_universe import PTRC_RENDER_STALL

parity_mod = import_module("00_test_ptrc_graphics_parity")

FULL_HD_WIDTH = 1920
FULL_HD_HEIGHT = 1080


class PtrcFullHdLiveObserver:
    def __init__(self, width: int = FULL_HD_WIDTH, height: int = FULL_HD_HEIGHT) -> None:
        self.width = width
        self.height = height
        self.ppm_header = f"P6\n{self.width} {self.height}\n255\n".encode("ascii")

        self.tmp_dir = tempfile.TemporaryDirectory()
        self.lib = parity_mod.build_shared_lib(Path(self.tmp_dir.name))
        self.ctx = parity_mod.CPtrcGfxCtx()
        self.seed = 137210144
        self.lib.ptrc_gfx_init(ctypes.byref(self.ctx), self.seed)

        self.rgb_buf = (ctypes.c_uint8 * (self.width * self.height * 3))()
        self.paused = False
        self.fullscreen = False
        self.takts_per_frame = 137

        self.root = tk.Tk()
        self.root.title("pTRC 3D Space-Crystal Universe v4.5.0 | Full-HD Observer Retina (1920x1080)")
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

        self.hud_bg = self.canvas.create_rectangle(16, 16, 1140, 56, fill="#08101E", outline="#1E3A5F")
        self.hud_text = self.canvas.create_text(
            28,
            36,
            anchor=tk.W,
            fill="#93C5FD",
            font=("Consolas", 12, "bold"),
            text="Initialisiere 3D-Raumkristall-Gitter (1920x1080)...",
        )

        self.root.bind("<space>", self.toggle_pause)
        self.root.bind("<r>", self.reset_universe)
        self.root.bind("<R>", self.reset_universe)
        self.root.bind("<f>", self.toggle_fullscreen)
        self.root.bind("<F>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.close)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

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

            # Berechne einen kompletten Beobachter-Zyklus (137 Grundtakte pro Render-Schritt)
            steps = self.ctx.render_interval_takts if self.ctx.render_interval_takts > 0 else 137
            for _ in range(steps):
                self.lib.ptrc_gfx_step_takt(ctypes.byref(self.ctx))

            rc = self.lib.ptrc_gfx_render_observer_rgb24(
                ctypes.byref(self.ctx), self.width, self.height, self.rgb_buf
            )
            ppm_frame = self.ppm_header + bytes(self.rgb_buf)
            self.photo.configure(data=ppm_frame)

            dt_ms = (time.perf_counter() - t0) * 1000.0
            fps = 1000.0 / dt_ms if dt_ms > 0.0 else 0.0
            status_str = "EVENT-HORIZON STALL" if rc == PTRC_RENDER_STALL else f"INTERVALL {self.ctx.render_interval_takts}T"

            self.canvas.itemconfigure(
                self.hud_text,
                text=(
                    f"FULL-HD 1920x1080 | TAKT: {self.ctx.takt_counter:,} | "
                    f"LAST: {self.ctx.active_load} | {status_str} | "
                    f"UMLENKUNGEN: {self.ctx.deflection_count:,} | {dt_ms:.1f} ms ({fps:.1f} FPS)"
                ),
            )

        self.root.after(16, self.update_loop)

    def close(self, _event: tk.Event | None = None) -> None:
        self.lib.ptrc_gfx_wipe(ctypes.byref(self.ctx))
        self.tmp_dir.cleanup()
        self.root.destroy()

    def run(self) -> int:
        self.root.after(10, self.update_loop)
        self.root.mainloop()
        return 0


if __name__ == "__main__":
    viewer = PtrcFullHdLiveObserver(FULL_HD_WIDTH, FULL_HD_HEIGHT)
    sys.exit(viewer.run())
