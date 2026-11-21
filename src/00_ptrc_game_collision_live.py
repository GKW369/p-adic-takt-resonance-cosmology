# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
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
Full-HD (1920x1080) Game-Collision Showcase & Lockstep-Determinismus-Audit
auf Basis der pTRC Light-Universe Engine v4.6.0.
"""

from __future__ import annotations

import argparse
import ctypes
import subprocess
import sys
import tempfile
import time
import tkinter as tk
from importlib import import_module
from pathlib import Path

from ptrc_light_universe import PTRC_RENDER_STALL

parity_mod = import_module("00_test_ptrc_graphics_parity")

REPO_ROOT = Path(__file__).resolve().parent.parent
GC_DIR = REPO_ROOT / "embedded" / "game_collision"
GFX_DIR = REPO_ROOT / "embedded" / "graphics"


class CPtrcGcWorld(ctypes.Structure):
    _fields_ = [
        ("sim", parity_mod.CPtrcGfxCtx),
        ("total_collisions", ctypes.c_uint64),
        ("rigid_pyramid_hits", ctypes.c_uint64),
        ("rigid_sphere_hits", ctypes.c_uint64),
        ("particle_collisions", ctypes.c_uint64),
        ("tunneling_escapes", ctypes.c_uint64),
        ("lockstep_state_hash", ctypes.c_uint64),
        ("active_rigid_bodies", ctypes.c_uint32),
        ("active_crystal_nodes", ctypes.c_uint32),
    ]


def build_gc_lib(build_dir: Path) -> ctypes.CDLL:
    so_path = build_dir / "libptrc_game_collision.so"
    cmd = [
        "gcc",
        "-std=c11",
        "-O2",
        "-pthread",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-shared",
        "-fPIC",
        f"-I{GC_DIR}",
        f"-I{GFX_DIR}",
        str(GC_DIR / "ptrc_game_collision.c"),
        str(GFX_DIR / "ptrc_light_universe.c"),
        "-ldl",
        "-o",
        str(so_path),
    ]
    subprocess.run(cmd, check=True)
    lib = ctypes.CDLL(str(so_path))

    lib.ptrc_gc_init.argtypes = [ctypes.POINTER(CPtrcGcWorld), ctypes.c_uint64]
    lib.ptrc_gc_init.restype = ctypes.c_int

    lib.ptrc_gc_step_tick.argtypes = [ctypes.POINTER(CPtrcGcWorld)]
    lib.ptrc_gc_step_tick.restype = ctypes.c_int

    lib.ptrc_gc_render_rgb24.argtypes = [
        ctypes.POINTER(CPtrcGcWorld),
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint8),
    ]
    lib.ptrc_gc_render_rgb24.restype = ctypes.c_int

    lib.ptrc_gc_wipe.argtypes = [ctypes.POINTER(CPtrcGcWorld)]
    lib.ptrc_gc_wipe.restype = None
    return lib


def run_lockstep_audit() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        lib = build_gc_lib(Path(tmp))
        w1 = CPtrcGcWorld()
        w2 = CPtrcGcWorld()
        assert lib.ptrc_gc_init(ctypes.byref(w1), 137210144) == 1
        assert lib.ptrc_gc_init(ctypes.byref(w2), 137210144) == 1

        for _ in range(10):
            assert lib.ptrc_gc_step_tick(ctypes.byref(w1)) == 1
            assert lib.ptrc_gc_step_tick(ctypes.byref(w2)) == 1
            assert w1.lockstep_state_hash == w2.lockstep_state_hash
            assert w1.tunneling_escapes == 0

        print(
            f"[PASS] Game-Collision Lockstep Hash=0x{w1.lockstep_state_hash:016X} | "
            f"Kollisionen={w1.total_collisions:,} (Pyr={w1.rigid_pyramid_hits:,}, "
            f"Kugel={w1.rigid_sphere_hits:,}) | Tunneling=0"
        )
        lib.ptrc_gc_wipe(ctypes.byref(w1))
        lib.ptrc_gc_wipe(ctypes.byref(w2))
    return 0

class PtrcGameCollisionLiveViewer:
    def __init__(self, width: int = 1920, height: int = 1080) -> None:
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
        self.lib = build_gc_lib(Path(self.tmp_dir.name))
        self.world = CPtrcGcWorld()
        self.seed = 137210144
        self.lib.ptrc_gc_init(ctypes.byref(self.world), self.seed)

        self.paused = False
        self.fullscreen = False
        self.steps_per_frame = 2
        self.start_time = time.perf_counter()

        self.root = tk.Tk()
        self.root.title("pTRC Game-Collision Engine v4.6.0 — Zero-Tunneling & Lockstep Showcase (1920x1080)")
        self.root.configure(bg="#010206")
        self.root.geometry(f"{self.width}x{self.height}")

        self.photo = tk.PhotoImage(width=self.width, height=self.height)
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#010206", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        self.hud_top = self.canvas.create_rectangle(14, 14, 1904, 54, fill="#08101E", outline="#2563EB")
        self.hud_top_txt = self.canvas.create_text(
            24, 34, anchor=tk.W, fill="#93C5FD", font=("Consolas", 10, "bold"), text="Initialisiere..."
        )

        self.hud_bot = self.canvas.create_rectangle(14, 1026, 1904, 1066, fill="#08101E", outline="#10B981")
        self.hud_bot_txt = self.canvas.create_text(
            24, 1046, anchor=tk.W, fill="#6EE7B7", font=("Consolas", 10, "bold"), text="Berechne Lockstep..."
        )

        self.root.bind("<space>", lambda _e: setattr(self, "paused", not self.paused))
        self.root.bind("<plus>", lambda _e: setattr(self, "steps_per_frame", min(137, self.steps_per_frame + 1)))
        self.root.bind("<minus>", lambda _e: setattr(self, "steps_per_frame", max(1, self.steps_per_frame - 1)))
        self.root.bind("<f>", lambda _e: self._toggle_fs())
        self.root.bind("<F>", lambda _e: self._toggle_fs())
        self.root.bind("<Escape>", lambda _e: self.close())
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _toggle_fs(self) -> None:
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def update_loop(self) -> None:
        if not self.paused:
            t0 = time.perf_counter()
            for _ in range(self.steps_per_frame):
                self.lib.ptrc_gc_step_tick(ctypes.byref(self.world))
            t_phys = time.perf_counter()

            rc = self.lib.ptrc_gc_render_rgb24(ctypes.byref(self.world), self.width, self.height, self.rgb_ptr)
            t_rend = time.perf_counter()

            new_photo = tk.PhotoImage(width=self.width, height=self.height, data=bytes(self.ppm_buf))
            self.canvas.itemconfigure(self.image_item, image=new_photo)
            self.photo = new_photo

            phys_ms = ((t_phys - t0) * 1000.0) / self.steps_per_frame
            rend_ms = (t_rend - t_phys) * 1000.0
            c_total_ms = (t_rend - t0) * 1000.0
            c_fps = 1000.0 / c_total_ms if c_total_ms > 0.0 else 0.0
            elapsed = max(0.001, time.perf_counter() - self.start_time)
            w = self.world

            self.canvas.itemconfigure(
                self.hud_top_txt,
                text=(
                    f"ZEIT:{elapsed:06.1f}s | TICK:{w.sim.takt_counter:,} | KRISTALLE:{w.active_crystal_nodes:,} | "
                    f"ENG:{w.sim.assigned_engines}/8 | C11-PHYS:{phys_ms:.2f}ms | ZBUF:{rend_ms:.1f}ms | C11-MAX:{c_fps:.1f} FPS"
                ),
            )
            stall_info = "STALL" if rc == PTRC_RENDER_STALL else "LOCKSTEP-OK"
            self.canvas.itemconfigure(
                self.hud_bot_txt,
                text=(
                    f"KOLLISIONEN GESAMT:{w.total_collisions:,} | RIGID-PYRAMIDE:{w.rigid_pyramid_hits:,} | "
                    f"RIGID-KUGEL:{w.rigid_sphere_hits:,} | PARTIKEL:{w.particle_collisions:,} | "
                    f"TUNNELING:{w.tunneling_escapes} | HASH:0x{w.lockstep_state_hash:016X} [{stall_info}]"
                ),
            )
        self.root.after(1, self.update_loop)

    def close(self) -> None:
        self.lib.ptrc_gc_wipe(ctypes.byref(self.world))
        self.tmp_dir.cleanup()
        self.root.destroy()

    def run(self) -> int:
        self.root.after(5, self.update_loop)
        self.root.mainloop()
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="pTRC Game-Collision Live Showcase & Audit")
    parser.add_argument("--audit-only", action="store_true", help="Nur Lockstep- & 0-Tunneling-Audit ausfuehren")
    args = parser.parse_args()
    if args.audit_only:
        return run_lockstep_audit()
    return PtrcGameCollisionLiveViewer().run()


if __name__ == "__main__":
    sys.exit(main())
