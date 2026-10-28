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

try:
    from experimental.ptrc_3d_engine.src.ptrc_3d_animation_generator import PTRC3DStereoEngine
except ImportError:
    # Standard-Fallback falls Pfadstrukturen im Standalone-Test abweichen
    class PTRC3DStereoEngine:
        def __init__(self, width=1920, height=1080):
            self.width = width
            self.height = height
            self.SCALE = 1000
            self.invariant_limit = 156
            self.state_flag_core = 1
            self.state_flag_wave = 2

        def project_coordinate_stereo(self, x, y, z, iod=30):
            scaled_depth = z * self.SCALE
            if scaled_depth + self.invariant_limit == 0:
                return 0, 0, 0
            proj_x_left = ((x - iod) * self.SCALE) // (scaled_depth + self.invariant_limit)
            proj_x_right = ((x + iod) * self.SCALE) // (scaled_depth + self.invariant_limit)
            proj_y = (y * self.SCALE) // (scaled_depth + self.invariant_limit)
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
        
        # Pfade festlegen
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.tmp_dir = os.path.join(self.base_dir, "ptrc_rendering_tmp")
        self.output_video = os.path.join(self.base_dir, "ptrc_mint_solver_demo.mp4")

    def run_realtime_solver_pipeline(self, iterations=120):
        print("[ START ] Initialisiere pTRC MINT-Solver mit MP4-Video-Kopplung...")
        
        # Temporären Ordner für Frames vorbereiten
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.makedirs(self.tmp_dir)

        # --- pTRC Schwarm-Generator (Erzeugt 200 mathematische Knoten) ---
        # Wir nutzen rein ganzzahlige Schritte, um Floats zu blockieren!
        base_indices = np.arange(1, 201, dtype=np.int64)
        
        # Startpositionen: Ein explodierender mathematischer Ring
        agents_x = ((base_indices * 7) % 600) - 300
        agents_y = ((base_indices * 11) % 400) - 200
        agents_z = ((base_indices * 13) % 150) + 30
        agents = np.column_stack((agents_x, agents_y, agents_z))

        # Zielkoordinaten: Kollaps in die Invarianten-Zentren (Grenzknoten 156)
        targets_x = ((base_indices * 17) % 210) - 105
        targets_y = ((base_indices * 19) % 210) - 105
        targets_z = ((base_indices * 23) % 100) + 50
        targets = np.column_stack((targets_x, targets_y, targets_z))

        
        # Simulierter Frame-Loop
        for step in range(iterations):
            # Frame-Buffer im RAM initialisieren
            frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

            # --- 1. MINT-Ganzzahl-Routing (O(1)) ---
            dx = (targets[:, 0] - agents[:, 0]) * self.SCALE
            dy = (targets[:, 1] - agents[:, 1]) * self.SCALE
            dz = (targets[:, 2] - agents[:, 2]) * self.SCALE

            allowed_x = np.where((dx // self.SCALE) % self.PRIMORIAL_MOD != 0, 1, 0)
            allowed_y = np.where((dy // self.SCALE) % self.PRIMORIAL_MOD != 0, 1, 0)
            allowed_z = np.where((dz // self.SCALE) % self.PRIMORIAL_MOD != 0, 1, 0)

            agents[:, 0] += np.sign(dx) * allowed_x
            agents[:, 1] += np.sign(dy) * allowed_y
            agents[:, 2] += np.sign(dz) * allowed_z

            # --- 2. 3D-Stereo-Retina-Projektion & Buffer-Mapping ---
            for i in range(len(agents)):
                ax, ay, az = agents[i, 0], agents[i, 1], agents[i, 2]
                xl, xr, yd = self.engine_3d.project_coordinate_stereo(ax, ay, az, iod=35)
                
                # Symmetrische Farbbestimmung über das Modulo-Sieb
                state_registry = (ax * ay * az) % self.PRIMORIAL_MOD
                if state_registry == (self.INVARIANT_LIMIT % self.PRIMORIAL_MOD):
                    color = [218, 165, 32]   # Spectral Gold (Kern)
                else:
                    color = [0, 255, 255]     # Spectral Blue / Cyan (Welle)

                # Zeichne Voxel-Knoten in den Stereo-Buffer
                for offset_x, offset_y in [(-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2)]:
                    for x_coord in [xl, xr]:
                        px = x_coord + offset_x
                        py = yd + offset_y
                        if 0 <= px < self.width and 0 <= py < self.height:
                            frame_buffer[py, px] = color

            # Rohdaten-Frame wegschreiben
            frame_path = os.path.join(self.tmp_dir, f"frame_{step:04d}.ppm")
            with open(frame_path, "wb") as f:
                f.write(f"P6\n{self.width} {self.height}\n255\n".encode())
                f.write(frame_buffer.tobytes())

        # --- 3. MP4-Kompilierung über ffmpeg ---
        print("        Kompiliere Frames zu ptrc_mint_solver_demo.mp4...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-f", "image2", "-framerate", "30",
            "-i", os.path.join(self.tmp_dir, "frame_%04d.ppm"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", self.output_video
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(f"[ OK ] Video erfolgreich exportiert: {self.output_video}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[ FEHLER ] ffmpeg-Aufruf fehlgeschlagen. Überprüfe die Binaries auf deinem System.")

        # --- 4. Automatisches Aufräumen ---
        print("        Bereinige temporäre Frame-Reste...")
        shutil.rmtree(self.tmp_dir)
        print("[ DONE ] System vollständig aufgeräumt.")

if __name__ == "__main__":
    orchestrator = PTRC3DMINTOrchestrator()
    orchestrator.run_realtime_solver_pipeline(iterations=60)
