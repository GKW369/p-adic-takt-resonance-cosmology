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
        # Tiefe konstant auf 40 Takt-Einheiten halten, um FPU-Fluchtpunktdrift zu eliminieren
        scaled_depth = 40
        
        # Ganzzahliger Skalierungshebel für das IMAX-Breitbildraster
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

    def run_realtime_solver_pipeline(self, iterations=180):
        print("[ START ] Initialisiere pTRC IMAX-Schwarm-Projektor...")
        
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.makedirs(self.tmp_dir)

        # --- Pure Integer Fibonacci Sieve Architecture ---
        # 300 Netzknoten basierend auf der 144er Fibonacci-Ur-Zelle
        base_indices = np.arange(1, 301, dtype=np.int64)
        
        # Herleitung der gekrümmten Spiraltrajektorie ohne Pi oder analoge Trigonometrie:
        # Wir nutzen die Restklassen-Schritte des Modulo-24-Takts als Rotations-Vorschub.
        # Um die Drift zu eliminieren, werden die Achsen komplementär gespiegelt.
        takt_phase = (base_indices * 144) % self.CLOCK_MOD
        
        # Quadrance-basierte Richtungsauflösung analog zu deinem Kreis-Schnitt
        # Durch die Multiplikation mit wechselnden Modulo-Schritten erzeugen wir
        # eine raumzentrierte Rotation im unmanifestierten Ganzzahlraum.
        dir_x = np.where(takt_phase % 4 == 0, 1, np.where(takt_phase % 4 == 1, -1, 0))
        dir_y = np.where(takt_phase % 4 == 2, 1, np.where(takt_phase % 4 == 3, -1, 0))
        
        # Korrektur der 90-Grad-Phasenkreuzung über die 24 Kontaktflächen
        for idx in range(300):
            step_mod = (idx * 5) % self.CLOCK_MOD
            if step_mod < 6:
                dir_x[idx] += 1
            elif step_mod < 12:
                dir_y[idx] += 1
            elif step_mod < 18:
                dir_x[idx] -= 1
            else:
                dir_y[idx] -= 1

        # Radiales Wachstum: Der Radius skaliert formschlüssig mit dem Index
        radius = base_indices * 2
        
        # Absolute Zentrierung: Keine Kommazahlen, exakte Begrenzung im Sichtfeld
        targets_x = (dir_x * radius)
        targets_y = (dir_y * radius)
        targets_z = np.ones(300, dtype=np.int64) * 100
        
        targets = np.column_stack((targets_x, targets_y, targets_z))
       
        # --- Etablierung des 3D-Agentenregisters ---
        # Alle Agenten starten perfekt synchronisiert im Kernzentrum (0, 0, 100)
        agents = np.zeros((300, 3), dtype=np.int64)
        agents[:, 2] = 100
        
        for step in range(iterations):
            frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

            # --- 1. Verlustfreies MINT-Ganzzahl-Routing (O(1)) ---
            dx = (targets[:, 0] - agents[:, 0]) * self.SCALE
            dy = (targets[:, 1] - agents[:, 1]) * self.SCALE

            # Siebung komplementärer Sperrzonen über das Modulo-210-Lattice
            allowed_x = np.where((dx // self.SCALE) % self.PRIMORIAL_MOD != 0, 1, 0)
            allowed_y = np.where((dy // self.SCALE) % self.PRIMORIAL_MOD != 0, 1, 0)

            # Inkrementelle Bewegung zum Spiral-Zielzustand (Dämpfung der Ausreißer)
            agents[:, 0] += np.sign(dx) * allowed_x * 4
            agents[:, 1] += np.sign(dy) * allowed_y * 3

            # --- 2. Vektorisierte Stereo-Retina-Projektion ---
            xl, xr, yd = self.engine_3d.project_coordinate_stereo(agents[:, 0], agents[:, 1], agents[:, 2], iod=70)

            # Invarianz-Sichtung zur spektralen Trennung (Masse-Kern vs. Feldwelle)
            state_registry = (agents[:, 0] * agents[:, 1]) % self.PRIMORIAL_MOD
            is_core = (state_registry == (self.INVARIANT_LIMIT % self.PRIMORIAL_MOD))

            # Ganzzahl-Mapping im Bild-Speicherraster
            for i in range(len(agents)):
                # Spektral-Gold (Masse) oder Spektral-Cyan (Resonanz-Welle)
                color = [218, 165, 32] if is_core[i] else [0, 255, 255]
                
                # Formschlüssige 3x3-Kreuzbruchlinien zur Schließung der Monitor-Lücken
                for offset_x, offset_y in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
                    for x_coord in [xl[i], xr[i]]:
                        px = x_coord + offset_x
                        py = yd[i] + offset_y
                        if 0 <= px < self.width and 0 <= py < self.height:
                            frame_buffer[py, px] = color

            # Export als unkomprimiertes P6-PPM-Format (100% rauschfrei)
            frame_path = os.path.join(self.tmp_dir, f"frame_{step:04d}.ppm")
            with open(frame_path, "wb") as f:
                f.write(f"P6\n{self.width} {self.height}\n255\n".encode())
                f.write(frame_buffer.tobytes())

        print(f"        Kompiliere {iterations} IMAX-Frames via ffmpeg...")
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
