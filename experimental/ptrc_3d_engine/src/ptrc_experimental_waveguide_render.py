# ==============================================================================
# pTRC Framework - Experimental Module: Invariant Kaleidoscope Rotator
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
pTRC Framework - Experimental Core: Holographic Voxel Projection Stabilizer
Operational Domain: Symmetrical Integer Translation Matrices (\mathbb{Z}^3).
Fixes coordinate jittering during clock-cycled multi-axis crystal transitions.
"""

import os
import sys
import numpy as np

class PTRCStabilizedRotator:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156
        self.SCALE = 1000
        
        # Vorab generierte, unbestechliche 144 Kristallachsen für den Richtungs-Lookup
        self.crystal_axes = self._build_invariant_axes()

    def _build_invariant_axes(self):
        """ Generiert 144 exakte, ganzzahlige Richtungs-Vektoren. """
        flat_nodes = [
            2, 1, 0,   2, -1, 0,  -2, 1, 0,  -2, -1, 0,
            0, 2, 1,   0, 2, -1,   0, -2, 1,  0, -2, -1,
            1, 0, 2,  -1, 0, 2,    1, 0, -2, -1, 0, -2
        ]
        base = np.array(flat_nodes, dtype=np.int32).reshape(12, 3)
        axes = []
        for node in base:
            for factor in range(1, 13):
                axes.append(node * factor)
        return np.array(axes, dtype=np.int32)

    def project_stabilized_frame(self, frame_idx, output_dir):
        """
        Rendert ein rauschfreies FullHD-Frame. Nutzt die Takt-Phase als 
        diskreten Achsen-Schalter, um Rotations-Jitter komplett zu eliminieren.
        """
        frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cx, cy = self.width // 2, self.height // 2
        z_offset = 65
        
        # Bestimme die aktuelle Projektionsachse über das Modulo-System
        axis_index = frame_idx % 144
        current_axis = self.crystal_axes[axis_index]
        
        # Duale Polaritäts-Oszillation (Plus/Minus Takt aus Modul 41)
        dual_polarity = 1 if (frame_idx % 2 == 0) else -1
        
        # Iteration durch den lokalen Planck-Raumblock
        for dx in range(-15, 16):
            for dy in range(-15, 16):
                for dz in range(-15, 16):
                    
                    quadrance = dx*dx + dy*dy + dz*dz
                    if quadrance == 0:
                        continue
                        
                    # 1. DAS MODULO-210 PHYSIK-SIEB
                    if (quadrance % self.primorial_base) > self.invariant_limit:
                        continue
                        
                    # Algebraische Achsen-Rotation ohne ungenaue Trigonometrie
                    # Wir projizieren die Raumpunkte entlang der invarianten Kristallachse
                    rx = dx + (current_axis[0] * dual_polarity) // 12
                    ry = dy + (current_axis[1] * dual_polarity) // 12
                    rz = dz + z_offset + (current_axis[2] * dual_polarity) // 12
                    
                    # Perspektivischer Teiler im reinen Ganzzahlraum
                    denom = ((rz * self.SCALE) // 1414) + self.invariant_limit
                    if denom <= 0:
                        continue
                        
                    out_x = (((int(rx) * 45 * self.SCALE) // denom) + cx) % self.width
                    out_y = (((int(ry) * 45 * self.SCALE) // denom) + cy) % self.height
                    
                    # Farb-Klassifizierung basierend auf der Modulo-24 Resonanz
                    takt_check = (dx * dy + frame_idx) % self.control_base
                    
                    if takt_check == 12:
                        r_c, g_c, b_c = 255, 210, 24  # Invarianter Massen-Knoten (Gold)
                        voxel_size = 4
                    elif takt_check in {1, 5, 7, 11, 13, 17, 19, 23}:
                        r_c, g_c, b_c = 0, 255, 210  # Aktiver Resonanz-Knoten (Cyan)
                        voxel_size = 3
                    else:
                        # Hintergrund-Vakuumgitter mit Tiefenglühen
                        glow = max(30, 180 - ((rz * 100) // 128))
                        r_c, g_c, b_c = 0, int(glow) // 2, int(glow)
                        voxel_size = 2
                        
                    # Sicheres Einzeichnen ins Pixel-Array
                    y1, y2 = max(0, out_y - voxel_size // 2), min(self.height - 1, out_y + voxel_size // 2)
                    x1, x2 = max(0, out_x - voxel_size // 2), min(self.width - 1, out_x + voxel_size // 2)
                    frame_buffer[y1:y2+1, x1:x2+1] = [r_c, g_c, b_c]
                    
        # Binärer P6-PPM-Export zur absoluten Vermeidung von Kompressions-Rauschen
        filename = os.path.join(output_dir, f"stabilized_frame_{frame_idx:04d}.ppm")
        header = f"P6\n{self.width} {self.height}\n255\n".encode('ascii')
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(frame_buffer.tobytes())

if __name__ == "__main__":
    print("[pTRC-ROTATOR] Initialisiere unbestechliche 3D-Rotations-Inferenz...")
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Stabilized_Cache")
    os.makedirs(output_path, exist_ok=True)
    
    rotator = PTRCStabilizedRotator()
    
    # Rendere eine Testsequenz von 48 Frames zum Abgleich des Interferenzmusters
    for frame in range(48):
        rotator.project_stabilized_frame(frame, output_path)
        if frame % 12 == 0:
            print(f"    + Invarianter Takt-Frame {frame:02d}/48 erfolgreich im Cache verankert.")
            
    print(f"\n[ OK ] 48 rauschfreie Interferenz-Frames in '{output_path}' abgelegt.")
