python3 -c '
code = """# ==============================================================================
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
r\"\"\"
pTRC Framework - Interactive Game Engine Pipeline: Real-Time Crystal Flight
Operational Domain: Live 3D Whole-Number Projections (\\mathbb{Z}) into the Primorial Sieve.
Optimized: 100% Vectorized Matrix Projection with a solid RGB observer sphere.
\"\"\"

import os
import sys
import time
import numpy as np
import cv2

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

parent_1 = os.path.dirname(script_dir)
parent_2 = os.path.dirname(parent_1)

for p in [parent_1, parent_2]:
    if p:
        sys.path.insert(0, p)
        src_dir = os.path.join(p, "src")
        if os.path.exists(src_dir):
            sys.path.insert(0, src_dir)

try:
    from ptrc_3d_stereo_engine import PTRC3DStereoEngine
except ImportError:
    from src.ptrc_3d_stereo_engine import PTRC3DStereoEngine

try:
    from ptrc_clock_core import PTRCModularClockEngine
except ImportError:
    from src.ptrc_clock_core import PTRCModularClockEngine

print(" -> [ PATH ] Erfolgreich mit der Kern-Engine \x27ptrc_clock_core.py\x27 synchronisiert.")

class PTRC3DGameEngine:
    def __init__(self):
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        self.width = 320
        self.height = 180
        self.depth = 128
        self.primorial_base = 210
        self.control_base = 24
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.pos_x_offset = 0
        self.pos_y_offset = 0
        self.pos_z_offset = 0
        self.last_valid_view = np.zeros((1080, 1920), dtype=np.uint8)

    def run_interactive_loop(self):
        window_name = "pTRC Quantum Crystal Engine v1.0"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        print("\n[ INTERAKTIV ] Vektorisiertes Gitter geladen!")
        print(" -> Steuerung: W/S (Vor/Zurück) | A/D (Links/Rechts) | Q/E (Hoch/Runter) | ESC (Beenden)\n")
        
        while True:
            start_time = time.perf_counter()
            self.stereo_engine.left_eye_buffer.fill(0)
            self.stereo_engine.right_eye_buffer.fill(0)
            z_indices, y_indices, x_indices = np.where(self.clock_engine.voxels == 2)
            total_active_nodes = len(x_indices)
            
            if total_active_nodes > 0:
                z_flight_offset = self.pos_z_offset % self.depth
                raw_z = (z_indices - z_flight_offset)
                raw_z[raw_z <= 0] += self.depth
                raw_z = np.clip(raw_z, 1, self.depth)
                raw_x = (x_indices - cx) + self.pos_x_offset
                raw_y = (y_indices - cy) + self.pos_y_offset
                scaled_depth = (raw_z * 1000) // 1414
                denominator = scaled_depth + 156
                proj_x_left = ((raw_x * 8 - 12) * 1000) // denominator
                proj_x_right = ((raw_x * 8 + 12) * 1000) // denominator
                proj_y = ((raw_y * 8) * 1000) // denominator
                out_x_left = (proj_x_left + self.stereo_engine.width // 2) % self.stereo_engine.width
                out_x_right = (proj_x_right + self.stereo_engine.width // 2) % self.stereo_engine.width
                out_y = (proj_y + self.stereo_engine.height // 2) % self.stereo_engine.height
                takt_check = (raw_x * raw_y + raw_z) % self.control_base
                valid_mask = (takt_check == 1) | (takt_check == 5) | (takt_check == 7) | \
                             (takt_check == 11) | (takt_check == 12) | (takt_check == 13) | \
                             (takt_check == 17) | (takt_check == 19) | (takt_check == 23)
                if np.any(valid_mask):
                    self.stereo_engine.left_eye_buffer[out_y[valid_mask], out_x_left[valid_mask]] = 1
                    self.stereo_engine.right_eye_buffer[out_y[valid_mask], out_x_right[valid_mask]] = 1
            
            self.clock_engine.evolve_clock_one_takt()
            active_nodes = int(np.sum(self.stereo_engine.left_eye_buffer))
            if active_nodes > 2:
                self.last_valid_view = self.stereo_engine.left_eye_buffer * 255
                bw_matrix = self.last_valid_view.copy()
            else:
                bw_matrix = self.last_valid_view.copy()
                
            color_scene = cv2.cvtColor(bw_matrix, cv2.COLOR_GRAY2BGR)
            center_point = (self.stereo_engine.width // 2, self.stereo_engine.height // 2)
            sphere_radius = 80
            sphere_color = (255, 180, 0)
            cv2.circle(color_scene, center_point, sphere_radius, sphere_color, thickness=-1)
            cv2.circle(color_scene, center_point, sphere_radius, (0, 0, 0), thickness=2)
            
            end_time = time.perf_counter()
            dt = end_time - start_time
            fps = 1.0 / dt if dt > 0 else 999.0
            cv2.putText(color_scene, f"FPS: {fps:.1f} | ACTIVE NODES: {active_nodes:,} | SOLID OBSERVER SPHERE", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(color_scene, f"VECTORS: X_SHIFT: {self.pos_x_offset} | Y_SHIFT: {self.pos_y_offset} | Z_TACT: {self.pos_z_offset}", (30, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 1, cv2.LINE_AA)
            cv2.imshow(window_name, color_scene)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                print("[ GAME ] Universum über ESC sicher geschlossen.")
                break
            elif key == ord(\x27w\x27) or key == ord(\x27W\x27):
                self.pos_z_offset = (self.pos_z_offset + 1) % self.depth
            elif key == ord(\x27s\x27) or key == ord(\x27S\x27):
                self.pos_z_offset = (self.pos_z_offset - 1) % self.depth
            elif key == ord(\x27a\x27) or key == ord(\x27A\x27):
                self.pos_x_offset -= 2
            elif key == ord(\x27d\x27) or key == ord(\x27D\x27):
                self.pos_x_offset += 2
            elif key == ord(\x27q\x27) or key == ord(\x27Q\x27):
                self.pos_y_offset -= 2
            elif key == ord(\x27e\x27) or key == ord(\x27E\x27):
                self.pos_y_offset += 2
        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = PTRC3DGameEngine()
    game.run_interactive_loop()
"""
path = "/home/ignatus/Downloads/p-adic-takt-resonance-cosmology_002/p-adic-takt-resonance-cosmology-main(4)/p-adic-takt-resonance-cosmology-main/ptrc_3d_engine/src/ptrc_3d_animation_generator.py"
with open(path, "w", encoding="utf-8") as f:
    f.write(code)
print("[ LOCAL FIXED ] Die Datei wurde lokal auf Beißebene vollständig repariert.")
'
