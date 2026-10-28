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

import os
import sys
import shutil
import subprocess
import numpy as np

class PTRC3DStereoEngine:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.SCALE = 1000
        self.invariant_limit = 156
        self.state_flag_core = 1
        self.state_flag_wave = 2

    def project_coordinate_stereo(self, x, y, z, iod=140):
        # Tiefe konstant halten, um den Absturz in den Fluchtpunkt zu stoppen!
        scaled_depth = 40
        
        # Gigantischer Hebel für maximale Breitbild-Explosion auf der Leinwand
        proj_x_left = ((x - iod) * 160) // (scaled_depth + self.invariant_limit)
        proj_x_right = ((x + iod) * 160) // (scaled_depth + self.invariant_limit)
        proj_y = (y * 160) // (scaled_depth + self.invariant_limit)
        
        return proj_x_left + (self.width // 2), \
               proj_x_right + (self.width // 2), \
               proj_y + (self.height // 2)

class PTRC3DMINTOrchestrator:
    def __init__(self):
        self.width = 1920
        self.height = 1080
        self.engine_3d = PTRC3DStereoEngine(width=self.width, height=self.height)
        self.PRIMORIAL_MOD = 210
        self.CLOCK_MOD = 24
        self.INVARIANT_LIMIT = 156
        self.SCALE = 1000
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.tmp_dir = os.path.join(self.base_dir, "ptrc_rendering_tmp")
        self.output_video = os.path.join(self.base_dir, "ptrc_mint_solver_demo.mp4")

    def run_realtime_solver_pipeline(self, iterations=180): # DOPPELTE LÄNGE!
        print("[ START ] Initialisiere pTRC IMAX-Schwarm-Projektor...")
        
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.makedirs(self.tmp_dir)

 # --- pTRC Ganzzahl-Fibonacci-Spiralengenerator (Null Fließkomma-Trigonometrie!) ---
        base_indices = np.arange(1, 301, dtype=np.int64)
        
        # Der Goldene Schnitt im Ganzzahlfeld (Annäherung des Goldenen Winkels)
        # Über zyklische Modulo-Ringe simulieren wir den Rotations-Vorschub
        theta_steps = (base_indices * 144)  # 144 ist eine echte Fibonacci-Zahl!
        
        # Ganzzahlige Approximation von Richtungs-Vektoren ohne sin/cos
        # Wir nutzen die Modulo-Phasen deines Modulo-24-Takts zur Richtungszuweisung
        dir_x = ((theta_steps % 24) - 12)
        dir_y = (((theta_steps + 6) % 24) - 12)  # Um 90 Grad phasenverschoben
        
        # Radiales Wachstum: Der Radius wächst proportional zum Index (Archimedisch/Fibonacci)
        radius = base_indices * 3
        
        # Finale Ziel-Koordinaten im Breitbild verankern
        targets_x = (dir_x * radius) // 4
        targets_y = (dir_y * radius) // 4
        targets_z = np.ones(300, dtype=np.int64) * 100
        
        targets = np.column_stack((targets_x, targets_y, targets_z))
       
        for step in range(iterations):
            # Frame-Buffer initialisieren (Schwarz)
            frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

            # --- 1. MINT-Ganzzahl-Routing (O(1)) ---
            dx = (targets[:, 0] - agents[:, 0]) * self.SCALE
            dy = (targets[:, 1] - agents[:, 1]) * self.SCALE

            allowed_x = np.where((dx // self.SCALE) % self.PRIMORIAL_MOD != 0, 1, 0)
            allowed_y = np.where((dy // self.SCALE) % self.PRIMORIAL_MOD != 0, 1, 0)

            # Ultraschnelle Oszillation über den Bildschirm
            agents[:, 0] += np.sign(dx) * allowed_x * 18
            agents[:, 1] += np.sign(dy) * allowed_y * 11

            # --- 2. Vektorisierte Stereo-Projektions-Berechnung ---
            xl, xr, yd = self.engine_3d.project_coordinate_stereo(agents[:, 0], agents[:, 1], agents[:, 2], iod=70)

            # Mathematisches Sieb für alle Farben gleichzeitig
            state_registry = (agents[:, 0] * agents[:, 1]) % self.PRIMORIAL_MOD
            is_core = (state_registry == (self.INVARIANT_LIMIT % self.PRIMORIAL_MOD))

            # Zeichne die vergrößerten Voxel-Knoten in den Buffer
            for i in range(len(agents)):
                color = [218, 165, 32] if is_core[i] else [0, 255, 255] # Gold oder Cyan
                
                # Fette 3x3 Pixel-Kreuze für perfekte Sichtbarkeit im Video
                for offset_x, offset_y in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
                    for x_coord in [xl[i], xr[i]]:
                        px = x_coord + offset_x
                        py = yd[i] + offset_y
                        if 0 <= px < self.width and 0 <= py < self.height:
                            frame_buffer[py, px] = color

            # Unkomprimierten Frame wegschreiben
            frame_path = os.path.join(self.tmp_dir, f"frame_{step:04d}.ppm")
            with open(frame_path, "wb") as f:
                f.write(f"P6\n{self.width} {self.height}\n255\n".encode())
                f.write(frame_buffer.tobytes())

        print("        Kompiliere 180 IMAX-Frames via ffmpeg...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-f", "image2", "-framerate", "30",
            "-i", os.path.join(self.tmp_dir, "frame_%04d.ppm"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", self.output_video
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(f"[ OK ] Episches Video exportiert: {self.output_video}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[ FEHLER ] ffmpeg-Aufruf fehlgeschlagen.")

        shutil.rmtree(self.tmp_dir)
        print("[ DONE ] System vollständig bereinigt.")

if __name__ == "__main__":
    orchestrator = PTRC3DMINTOrchestrator()
    orchestrator.run_realtime_solver_pipeline(iterations=180)
