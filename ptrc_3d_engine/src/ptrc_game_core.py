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
r"""
pTRC Framework - Interactive Game Engine Pipeline: Real-Time Crystal Flight
Operational Domain: Live 3D Whole-Number Projections (\mathbb{Z}) into the Primorial Sieve.
Optimized: Pure Vectorized Holographic Matrix Projection with fixed attribute links.
"""

import os
import sys
import time
import numpy as np
import cv2

# ==============================================================================
# !!! TARGET ZONE: EXPLIZITE UND TAB-FREIE MODUL-KOPPLUNG !!!
# MARKER: PTRC_HARDCODED_NAMESPACE_RESOLVER_2026
# ==============================================================================
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

print(" -> [ PATH ] Erfolgreich mit der Kern-Engine 'ptrc_clock_core.py' synchronisiert.")
# ==============================================================================
# !!! END OF TARGET ZONE !!!
# ==============================================================================

class PTRC3DGameEngine:
    def __init__(self):
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        
        # Performante Triebwerks-Auflösung
        self.width = 320
        self.height = 180
        self.depth = 128
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156  # Als echtes Klassenattribut fixiert
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        
        # Interaktive Reiseparameter des Beobachters
        self.pos_x_offset = 0
        self.pos_y_offset = 0
        self.pos_z_offset = 0
        
        self.last_valid_view = np.zeros((1080, 1920), dtype=np.uint8)

    def run_interactive_loop(self):
        window_name = "pTRC Quantum Crystal Engine v1.0"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        allowed_24_list = [1, 5, 7, 11, 12, 13, 17, 19, 23]
        
        print("\n[ HOLOGRAMM ] Reine holografische Spiegel-Interferenz aktiv!")
        print(" -> Steuerung: W/S (Vor/Zurück) | A/D (Links/Rechts) | Q/E (Hoch/Runter) | ESC (Beenden)\n")
        
        while True:
            start_time = time.perf_counter()
            
            # Retina-Puffer leeren
            self.stereo_engine.left_eye_buffer.fill(0)
            self.stereo_engine.right_eye_buffer.fill(0)
            
            # VEKTORISIERTE EXTRAKTION DES HINTERGRUNDS
            z_indices, y_indices, x_indices = np.where(self.clock_engine.voxels == 2)
            total_active_nodes = len(x_indices)
            
            if total_active_nodes > 0:
                z_flight_offset = self.pos_z_offset % self.depth
                
                raw_z = (z_indices - z_flight_offset)
                raw_z[raw_z <= 0] += self.depth
                raw_z = np.clip(raw_z, 1, self.depth)
                
                raw_x = (x_indices - cx) + self.pos_x_offset
                raw_y = (y_indices - cy) + self.pos_y_offset
                
                # Perspektiv-Transformation des Hintergrunds
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

            # ==================================================================
            # !!! TARGET ZONE: HOLOGRAFISCHE MATRIX-SPIEGEL-KUGEL !!!
            # ==================================================================
            grid_y, grid_x = np.indices((self.stereo_engine.height, self.stereo_engine.width))
            
            screen_cx = self.stereo_engine.width // 2
            screen_cy = self.stereo_engine.height // 2
            
            dx_left = grid_x - (screen_cx - 8)
            dx_right = grid_x - (screen_cx + 8)
            dy = grid_y - screen_cy
            
            quadrance_left = (dx_left * dx_left) + (dy * dy)
            quadrance_right = (dx_right * dx_right) + (dy * dy)
            
            # Fehlerkorrektur: Nutzt jetzt self.invariant_limit fehlerfrei
            mask_takt_left = np.isin(quadrance_left % self.control_base, allowed_24_list)
            mask_prim_left = (quadrance_left % self.primorial_base) <= self.invariant_limit
            sphere_mask_left = (quadrance_left < 7000) & (mask_takt_left | mask_prim_left)
            
            mask_takt_right = np.isin(quadrance_right % self.control_base, allowed_24_list)
            mask_prim_right = (quadrance_right % self.primorial_base) <= self.invariant_limit
            sphere_mask_right = (quadrance_right < 7000) & (mask_takt_right | mask_prim_right)
            
            # Zuweisung an die 1-Bit Stereo-Buffer
            self.stereo_engine.left_eye_buffer[sphere_mask_left] = 1
            self.stereo_engine.right_eye_buffer[sphere_mask_right] = 1
            # ==================================================================

            # Uhr-Engine weitertakten
            self.clock_engine.evolve_clock_one_takt()
            
            # Flacker-Schutz (Coherence Hold)
            active_nodes = int(np.sum(self.stereo_engine.left_eye_buffer))
            if active_nodes > 2:
                self.last_valid_view = self.stereo_engine.left_eye_buffer * 255
                bw_scene = self.last_valid_view.copy()
            else:
                bw_scene = self.last_valid_view.copy()
            
            # Diagnostik
            end_time = time.perf_counter()
            dt = end_time - start_time
            fps = 1.0 / dt if dt > 0 else 999.0
            
            # HUD-Anzeige
            cv2.putText(bw_scene, f"FPS: {fps:.1f} | NODES: {active_nodes:,} | HOLOGRAPHIC RECONSTRUCTION ACTIVE", 
                        (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2, cv2.LINE_AA)
            cv2.putText(bw_scene, f"VECTORS: X_SHIFT: {self.pos_x_offset} | Y_SHIFT: {self.pos_y_offset} | Z_TACT: {self.pos_z_offset}", 
                        (30, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 200, 1, cv2.LINE_AA)
            
            cv2.imshow(window_name, bw_scene)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                print("[ GAME ] Universum über ESC sicher geschlossen.")
                break
            elif key == ord('w') or key == ord('W'):
                self.pos_z_offset = (self.pos_z_offset + 1) % self.depth
            elif key == ord('s') or key == ord('S'):
                self.pos_z_offset = (self.pos_z_offset - 1) % self.depth
            elif key == ord('a') or key == ord('A'):
                self.pos_x_offset -= 2
            elif key == ord('d') or key == ord('D'):
                self.pos_x_offset += 2
            elif key == ord('q') or key == ord('Q'):
                self.pos_y_offset -= 2
            elif key == ord('e') or key == ord('E'):
                self.pos_y_offset += 2

        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = PTRC3DGameEngine()
    game.run_interactive_loop()
