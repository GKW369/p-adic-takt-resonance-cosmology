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
Optimized: Keyboard-controlled interactive engine with instant live window projection.
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
    """
    Transforms the sequential frame compiler into an interactive real-time
    game engine environment governed entirely by whole-number keyboard vectors.
    """
    def __init__(self):
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        
        # Harmonische Spielauflösung der Planck-Ebene
        self.width = 1680
        self.height = 1050
        self.depth = 420
        self.primorial_base = 210
        self.control_base = 24
        
        # Lade die 1-Bit-Flusskanäle des Kristalls
        self.clock_engine = PTRCModularClockEngine(width=160, height=90, depth=64)
        self.crystal_axes = self.clock_engine.crystal_axes
        
        # Interaktive Positions-Koordinaten des Beobachters (Start im Zentrum)
        self.pos_x_offset = 0
        self.pos_y_offset = 0
        self.pos_z_offset = 0

    def run_interactive_loop(self):
        """
        Launches the interactive game loop. Listens to keyboard controls and
        renders the 1-bit crystal sieve streams on-the-fly directly to the window.
        """
        window_name = "pTRC Quantum Crystal Engine v1.0"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        allowed_24_rays = {1, 5, 7, 11, 13, 17, 19, 23}
        
        print("\n[ INTERAKTIV ] Spielschleife gestartet!")
        print(" -> Steuerung: W/S (Vor/Zurück) | A/D (Links/Rechts) | Q/E (Hoch/Runter) | ESC (Beenden)\n")
        
        while True:
            start_time = time.perf_counter()
            
            # 1. Puffer für den aktuellen Frame komplett leeren
            self.stereo_engine.left_eye_buffer.fill(0)
            self.stereo_engine.right_eye_buffer.fill(0)
            
            # 2. ON-THE-FLY INTERFERENZ BERECHNUNG (Unter Berücksichtigung der Spielerposition)
            for axis in self.crystal_axes:
                ax, ay, az = axis, axis, axis
                
                for step in range(-120, 120):
                    # Inkorporiere die interaktiven Tastatur-Verschiebungen direkt im Fluss
                    x_g = cx + (ax * step) // 6 + self.pos_x_offset
                    y_g = cy + (ay * step) // 6 + self.pos_y_offset
                    z_g = cz + (az * step) // 6
                    
                    if 0 <= x_g < self.width and 0 <= y_g < self.height and 0 <= z_g < self.depth:
                        quadrance = (x_g - cx)**2 + (y_g - cy)**2 + (z_g - cz)**2
                        
                        if quadrance % self.primorial_base <= 156:
                            takt_check = (x_g * y_g + z_g) % self.control_base
                            
                            if takt_check in allowed_24_rays:
                                # Berechne den Tiefenabstand bezogen auf den Vorwärtsflug (Z-Offset)
                                raw_z = int(z_g - self.pos_z_offset)
                                while raw_z <= 0:
                                    raw_z += self.depth
                                raw_z = (raw_z % self.depth) or 1
                                
                                raw_x = int(x_g - cx)
                                raw_y = int(y_g - cy)
                                
                                self.stereo_engine.project_spatial_voxel_node(
                                    coord_x=raw_x,
                                    coord_y=raw_y,
                                    coord_z=raw_z,
                                    focal_offset=14
                                )
            
            # Takte die Hintergrund-Uhr-Engine im Hintergrund permanent mit
            self.clock_engine.evolve_clock_one_takt()
            
            # Signalkonvertierung in 8-Bit Sichtfeld
            live_view = self.stereo_engine.left_eye_buffer * 255
            
            # Performance-Metriken im Live-Bild einblenden
            end_time = time.perf_counter()
            fps = 1.0 / (end_time - start_time)
            active_nodes = int(np.sum(self.stereo_engine.left_eye_buffer))
            
            cv2.putText(live_view, f"FPS: {fps:.1f} | NODES: {active_nodes:,} | POS: ({self.pos_x_offset},{self.pos_y_offset},{self.pos_z_offset})", 
                        (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2, cv2.LINE_AA)
            
            # Zeige das Bild direkt im Vollbildfenster an
            cv2.imshow(window_name, live_view)
            
            # 3. INTERAKTIVE TASTATUR-ABFRAGE (Wartet 1 ms auf Input)
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC-Taste gedrückt
                print("[ GAME ] Universum über ESC sicher geschlossen.")
                break
            elif key == ord('w') or key == ord('W'):
                self.pos_z_offset = (self.pos_z_offset + 4) % self.depth  # Vorwärts fliegen
            elif key == ord('s') or key == ord('S'):
                self.pos_z_offset = (self.pos_z_offset - 4) % self.depth  # Rückwärts fliegen
            elif key == ord('a') or key == ord('A'):
                self.pos_x_offset -= 8  # Nach links steuern
            elif key == ord('d') or key == ord('D'):
                self.pos_x_offset += 8  # Nach rechts steuern
            elif key == ord('q') or key == ord('Q'):
                self.pos_y_offset -= 8  # Nach oben fliegen
            elif key == ord('e') or key == ord('E'):
                self.pos_y_offset += 8  # Nach unten fliegen

        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = PTRC3DGameEngine()
    game.run_interactive_loop()
