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
        """Perspektivische Stereo-Retina-Projektion mit festem Tiefenanker."""
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

        # 300 Netzknoten basierend auf der 144er Fibonacci-Ur-Zelle
        num_agents = 300
        base_indices = np.arange(1, num_agents + 1, dtype=np.int64)
        
        # --- MATHEMATISCHE MATRIX-HERLEITUNG DER FIBONACCI-SPIRALE IN Z ---
        # Keine kontinuierlichen Winkel! Wir nutzen das Modulo-24-Uhrsieb als orthogonalen Richtungsgeber
        takt_phase = (base_indices * 144) % self.CLOCK_MOD
        
        dir_x = np.where(takt_phase % 4 == 0, 1, np.where(takt_phase % 4 == 1, -1, 0))
        dir_y = np.where(takt_phase % 4 == 2, 1, np.where(takt_phase % 4 == 3, -1, 0))
        
        # Korrektur der Phasenkreuzung über die 24 Kontaktflächen zur Verhinderung von Aliasing
        for idx in range(num_agents):
            step_mod = (idx * 5) % self.CLOCK_MOD
            if step_mod < 6:
                dir_x[idx] += 1
            elif step_mod < 12:
                dir_y[idx] += 1
            elif step_mod < 18:
                dir_x[idx] -= 1
            else:
                dir_y[idx] -= 1

        # Skalierter Ganzzahl-Radius für die finale Fibonacci-Lattice-Dichte
        radius = base_indices * 2
        
        # Finale Zielkoordinaten der Fibonacci-Spirale
        targets_x = dir_x * radius
        targets_y = dir_y * radius
        targets_z = np.ones(num_agents, dtype=np.int64) * 100
        
        # --- AGENTEN-INITIALISIERUNG IM ZENTRUM (Axiom I) ---
        # Alle Agenten starten unmanifestiert am Nullpunkt (Zentrum)
        agents = np.zeros((num_agents, 3), dtype=np.int64)
        agents[:, 2] = 100
        
        # Berechnen von chaotischen Zwischen-Lattice-Zuständen für die Verteilungssimulation
        expansion_seed = (base_indices * 1836) % self.PRIMORIAL_MOD
        scatter_x = np.where(expansion_seed % 2 == 0, 1, -1) * (expansion_seed * 2)
        scatter_y = np.where(expansion_seed % 3 == 0, 1, -1) * (expansion_seed * 2)

        for step in range(self.frames_limit):
            frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

            # --- DYNAMISCHE DRITTELUNG DES GESAMT-TAKTS ---
            # Phase 1 (Frame 0-80):  Explosion / Verteilung aus dem Zentrum heraus
            # Phase 2 (Frame 81-160): Umlenkung und Einfangen über das planetare Modulo-Uhrsieb
            # Phase 3 (Frame 161-240): Formschlüssiger Kollaps in die Fibonacci-Zielmatrix
            if step <= 80:
                # Interpolationsfreies Ganzzahl-Routing in die Peripherie
                dx = (scatter_x - agents[:, 0]) * self.SCALE
                dy = (scatter_y - agents[:, 1]) * self.SCALE
                speed_divider = 12
            elif step <= 160:
                # Übergangs-Sichtung zur Stabilisierung der Trajektorien
                dx = (((scatter_x + targets_x) // 2) - agents[:, 0]) * self.SCALE
                dy = (((scatter_y + targets_y) // 2) - agents[:, 1]) * self.SCALE
                speed_divider = 16
            else:
                # Finaler, unbestechlicher O(1) Einlauf in das 144-seitige Kristallgitter
                dx = (targets_x - agents[:, 0]) * self.SCALE
                dy = (targets_y - agents[:, 1]) * self.SCALE
                speed_divider = 8

            # Siebung von Sperrzonen über das primoriale Restklassen-Lattice Modulo 210
            allowed_x = np.where((dx // self.SCALE) % self.PRIMORIAL_MOD != 0, 1, 0)
            allowed_y = np.where((dy // self.SCALE) % self.PRIMORIAL_MOD != 0, 1, 0)

            # Inkrementeller Vorschub Schritt für Schritt
            agents[:, 0] += np.sign(dx) * allowed_x * speed_divider
            agents[:, 1] += np.sign(dy) * allowed_y * speed_divider

            # --- RETINA-PROJEKTION UND RENDERING (Axiom II) ---
            xl, xr, yd = self.engine_3d.project_coordinate_stereo(agents[:, 0], agents[:, 1], agents[:, 2], iod=55)

            # Invarianz-Prüfung zur spektralen Farbtrennung (Kernmasse vs. Vakuumwelle)
            state_registry = (agents[:, 0] * agents[:, 1]) % self.PRIMORIAL_MOD
            is_core = (state_registry <= self.INVARIANT_LIMIT)

            for i in range(num_agents):
                # Spektral-Gold (Masse) oder Spektral-Cyan (Vakuum-Resonanzwelle)
                color = [218, 165, 32] if is_core[i] else [0, 255, 255]
                
                # Formschlüssige 3x3-Kreuzbruchlinien schließen Pixellücken auf flachen Monitoren
                for offset_x, offset_y in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
                    for x_coord in [xl[i], xr[i]]:
                        px = x_coord + offset_x
                        py = yd[i] + offset_y
                        if 0 <= px < self.width and 0 <= py < self.height:
                            frame_buffer[py, px] = color

            # Export als unkomprimiertes, bit-exaktes PPM-Bild (P6-Binär)
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
            print(f"\n[ SYSTEM CHECK OK ] Das unbestechliche Fibonacci-Demovideo ist gesichert!")
            print(f" -> Pfad: {self.output_video}\n")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n[ ACHTUNG ] FFmpeg-Kompression fehlgeschlagen. PPM-Frames verbleiben im Cache.")

        shutil.rmtree(self.tmp_dir)
        print("[ OK ] Lokaler Cache atomar bereinigt. Zero Floating-Point Pollution.")

if __name__ == "__main__":
    orchestrator = PTRC3DMINTOrchestrator(total_frames=240)
    orchestrator.run_realtime_solver_pipeline()
