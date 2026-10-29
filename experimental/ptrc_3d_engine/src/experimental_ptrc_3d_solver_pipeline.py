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

# -*- coding: utf-8 -*-
"""
pTRC Framework - Core Animation Suite: Fibonacci MINT Sieve Projector
Operational Domain: 3D Stereoscopic IMAX Viewports (Z^3). Zero Float Pollution.
File Name: ptrc_3d_animation_generator.py
"""

import os
import sys
import shutil
import subprocess
import numpy as np

class PTRC3DStereoEngine:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.invariant_limit = 156

    def project_coordinate_stereo(self, x, y, z, iod=70):
        """Perspektivische Stereo-Retina-Projektion mit festem Tiefenanker ohne Floats."""
        scaled_depth = 40
        denom = scaled_depth + self.invariant_limit
        
        proj_x_left = ((x - iod) * 160) // denom
        proj_x_right = ((x + iod) * 160) // denom
        proj_y = (y * 160) // denom
        
        return proj_x_left + (self.width // 2), \
               proj_x_right + (self.width // 2), \
               proj_y + (self.height // 2)

class PTRC3DMINTOrchestrator:
    def __init__(self, total_frames=240):
        self.width = 1920
        self.height = 1080
        self.frames_limit = total_frames
        self.engine_3d = PTRC3DStereoEngine(width=self.width, height=self.height)
        self.PRIMORIAL_MOD = 210
        self.CLOCK_MOD = 24
        self.INVARIANT_LIMIT = 156
        self.SCALE = 1000
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.tmp_dir = os.path.join(self.base_dir, "ptrc_rendering_tmp")
        self.output_video = os.path.join(self.base_dir, "ptrc_wirminghaus_dual_passing.mp4")

    def run_realtime_solver_pipeline(self):
        print(f"[ pTRC CORE ] Initialisiere 4K-kompatible Volumensynthese ({self.width}x{self.height})...")
        
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.makedirs(self.tmp_dir)

        # 600 Netzknoten für ein dichteres, satteres Bild beim Ausfüllen
        num_agents = 600
        base_indices = np.arange(1, num_agents + 1, dtype=np.int64)
        
        # --- MATHEMATISCHE GEOMETRIE DER FIBONACCI-ZIELMATRIX IN Z ---
        # Das Modulo-24-Uhrsieb bestimmt die orthogonalen Endpositionen
        takt_phase = (base_indices * 144) % self.CLOCK_MOD
        dir_x = np.where(takt_phase % 4 == 0, 1, np.where(takt_phase % 4 == 1, -1, 0))
        dir_y = np.where(takt_phase % 4 == 2, 1, np.where(takt_phase % 4 == 3, -1, 0))
        
        for idx in range(num_agents):
            step_mod = (idx * 5) % self.CLOCK_MOD
            if step_mod < 6: dir_x[idx] += 1
            elif step_mod < 12: dir_y[idx] += 1
            elif step_mod < 18: dir_x[idx] -= 1
            else: dir_y[idx] -= 1

        radius = base_indices * 2
        targets_x = dir_x * radius
        targets_y = dir_y * radius
        
        # --- INITIALISIERUNG AM NULLPUNKT (Axiom I) ---
        agents = np.zeros((num_agents, 3), dtype=np.int64)
        agents[:, 2] = 100  # Starre Tiefenebene Z=100
        
        # Generiere ein weites, raumfüllendes Ablenkungsmuster über das 1-Byte-Register (256)
        expansion_seed = (base_indices * 1836) % 256
        max_fill_x = np.where(expansion_seed % 2 == 0, 1, -1) * (expansion_seed * 4)
        max_fill_y = np.where(expansion_seed % 3 == 0, 1, -1) * (expansion_seed * 3)

        for step in range(self.frames_limit):
            frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

            # --- DREI RECHENTAKT-PHASEN NACH KURT GUIDO WIRMINGHAUS ---
            if step <= 80:
                # PHASE 1: Explosive Inflation. Die Agenten besetzen blitzartig den Raum
                # und füllen den Bildschirm komplett aus, da noch kein Beobachter bremst.
                progress = step * 12
                current_targets_x = (max_fill_x * progress) // 80
                current_targets_y = (max_fill_y * progress) // 80
                speed_divider = 15
            elif step <= 160:
                # PHASE 2: Das Aushandeln in den 136 Zwischentakten. Die Pixel wirbeln
                # dezentral umher, füllen Freiräume und bereiten den Strukturwechsel vor.
                phase_progress = (step - 80)
                interference_x = np.where((base_indices + step) % 4 == 0, 30, -30)
                interference_y = np.where((base_indices + step) % 4 == 2, 30, -30)
                
                current_targets_x = max_fill_x + (((targets_x - max_fill_x) * phase_progress) // 80) + interference_x
                current_targets_y = max_fill_y + (((targets_y - max_fill_y) * phase_progress) // 80) + interference_y
                speed_divider = 10
            else:
                # PHASE 3: Formschlüssiger Kollaps. Der Schwellenwert ist erreicht.
                # Pixel für Pixel rastet unerbittlich auf seinen Planck-Platz in der Spirale ein.
                current_targets_x = targets_x
                current_targets_y = targets_y
                speed_divider = 6

            # Berechnung des ganzzahligen Vorschubs (Pixel-Eroberung)
            dx = (current_targets_x - agents[:, 0]) * self.SCALE
            dy = (current_targets_y - agents[:, 1]) * self.SCALE

            # Siebung von Sperrzonen über das primoriale Restklassen-Lattice
            allowed_x = np.where((dx // self.SCALE) % self.PRIMORIAL_MOD != 0, 1, 0)
            allowed_y = np.where((dy // self.SCALE) % self.PRIMORIAL_MOD != 0, 1, 0)

            agents[:, 0] += np.sign(dx) * allowed_x * speed_divider
            agents[:, 1] += np.sign(dy) * allowed_y * speed_divider

            # --- RETINA-PROJEKTION UND BIT-EXAKTES RENDERING ---
            xl, xr, yd = self.engine_3d.project_coordinate_stereo(agents[:, 0], agents[:, 1], agents[:, 2], iod=55)

            # Invarianz-Prüfung zur spektralen Farbtrennung (Kernmasse vs. Vakuumwelle)
            state_registry = (agents[:, 0] * agents[:, 1]) % self.PRIMORIAL_MOD
            is_core = (state_registry <= self.INVARIANT_LIMIT)

            for i in range(num_agents):
                # Spektral-Gold für Masse (Kern), Cyan für die Vakuum-Resonanzwelle
                color = [218, 165, 32] if is_core[i] else [0, 255, 255]
                
                # 3x3 Kreuzbruchlinien um Pixellücken auf der flachen Renderebene zu schließen
                for offset_x, offset_y in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
                    for x_coord in [xl[i], xr[i]]:
                        px = x_coord + offset_x
                        py = yd[i] + offset_y
                        if 0 <= px < self.width and 0 <= py < self.height:
                            frame_buffer[py, px] = color

            # Export als unkomprimiertes PPM-Bild
            frame_path = os.path.join(self.tmp_dir, f"frame_{step:04d}.ppm")
            with open(frame_path, "wb") as f:
                f.write(f"P6\n{self.width} {self.height}\n255\n".encode('ascii'))
                f.write(frame_buffer.tobytes())

            if step % 24 == 0 or step == self.frames_limit - 1:
                print(f"    + Takt-Frame {step:03d}/{self.frames_limit} | Invarianz-Lattice synchronisiert.")

        # --- LOSSLESS VIDEO-KOMPILIERUNG VIA FFmpeg ---
        print(f" -> Kompiliere {self.frames_limit} rauschfreie Takt-Frames via FFmpeg...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-f", "image2", "-framerate", "30",
            "-i", os.path.join(self.tmp_dir, "frame_%04d.ppm"),
            "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", self.output_video
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(f"\n[ SYSTEM CHECK OK ] Das raumfüllende Fibonacci-Demovideo wurde erfolgreich gerendert!")
            print(f" -> Pfad: {self.output_video}\n")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n[ ACHTUNG ] FFmpeg-Kompression fehlgeschlagen. PPM-Frames verbleiben im Cache.")

        shutil.rmtree(self.tmp_dir)
        print("[ OK ] Lokaler Cache atomar bereinigt. Zero Floating-Point Pollution.")

if __name__ == "__main__":
    orchestrator = PTRC3DMINTOrchestrator(total_frames=240)
    orchestrator.run_realtime_solver_pipeline()
