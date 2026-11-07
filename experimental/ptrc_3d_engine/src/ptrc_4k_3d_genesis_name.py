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
pTRC Framework - Core 3D Volume Suite: ptrc_4k_genesis_3d_fly.py
Operational Domain: 3D Perspective Integer Space (Z^3). Zero Float Pollution.
Features: Interactive Terminal Name prompt for deep-space 3D immersion,
          Perspective integer projection without trigonometric pollution,
          Anonymized dual-format file exporter (PNG + PPM).
"""

import numpy as np
import cv2
import sys

class PTRC3DImmersionEngine:
    def __init__(self, canvas_width=3840, canvas_height=2160):
        self.width = canvas_width
        self.height = canvas_height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156

    def project_3d_to_retina(self, x, y, z):
        """
        Ganzzahlige, perspektivische Projektion aus dem Z^3-Raum auf den 4K-Bildschirm.
        Verwendet deinen Tiefenanker-Ansatz, komplett ohne Floats oder Sinus/Cosinus.
        """
        # Verhindert Division durch Null im Zentrum des Beobachters
        denom = 50 + self.invariant_limit + (z // 2)
        if denom <= 0:
            denom = 1
            
        # Skalierungs-Faktor 120 für raumfüllende 4K-Spreizung
        proj_x = (x * 120) // denom + (self.width // 2)
        proj_y = (y * 120) // denom + (self.height // 2)
        return proj_x, proj_y

    def render_deep_space(self, global_takt_pulse, name_string):
        print(f" -> Computing 3D Resonances inside the crystal lattice...")
        
        # 1. Namens-Einspeisung für die Phasen-Verschiebung im Raum
        ascii_sum = sum(ord(char) for char in name_string if char.isalnum())
        name_phase_offset = ascii_sum % self.control_base
        takt_factor = int(global_takt_pulse) % self.primorial_base

        canvas_matrix = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # 2. Definiere den diskreten 3D-Raumblock vor dem Beobachter
        # Wir tasten Würfel-Schichten in der Tiefe (Z) ab
        x_range = np.arange(-300, 300, 6)
        y_range = np.arange(-200, 200, 6)
        z_range = np.arange(10, 400, 8)  # Tiefenschichten von nah (10) bis fern (400)

        # Schleifenfreie Vektorberechnung über die Tiefen-Ebenen
        for z_layer in z_range:
            X, Y = np.meshgrid(x_range, y_range)
            
            # Die echte dreidimensionale Quadrance zum Vorwärts-Vektor
            # Wir weben den Takt und den Namen als "Flug-Vorschub" direkt in den Z-Raum ein!
            dynamic_z = z_layer + name_phase_offset
            discrete_quadrance_3d = (X * X) + (Y * Y) + (dynamic_z * dynamic_z)

            # Das Modulo-210 Uhrsieb im 3D-Volumen
            residue_210 = discrete_quadrance_3d % self.primorial_base
            sieve_mask = residue_210 <= self.invariant_limit

            # Der Z/24Z Phasencheck im Raumgefüge
            target_phase = (12 + name_phase_offset) % self.control_base
            takt_check = (X * Y + dynamic_z + takt_factor) % self.control_base
            takt_mask = takt_check == target_phase

            valid_nodes = sieve_mask & takt_mask
            
            if np.any(valid_nodes):
                valid_x = X[valid_nodes]
                valid_y = Y[valid_nodes]
                
                # Perspektivische Transformation der gültigen 3D-Knoten auf die 2D-Retina
                proj_x, proj_y = self.project_3d_to_retina(valid_x, valid_y, z_layer)

                # Die digitale Wellenlänge ist im 3D-Raum abhängig von der Tiefe (Verlaufseffekt)
                color_wave = (discrete_quadrance_3d[valid_nodes] // 100) % 256
                
                # Weiche Tiefenabdunklung: Je weiter weg (größeres z), desto schwächer das Licht
                depth_damping = max(10, 255 - (z_layer * 230 // 400))
                
                b_channel = ((180 + color_wave // 2) * depth_damping // 255) % 256
                g_channel = ((140 + color_wave + name_phase_offset) * depth_damping // 255) % 256
                r_channel = ((color_wave // 3) * depth_damping // 255) % 256

                # Zeichne die Raumpunkte mit formschlüssigen 2x2-Blöcken gegen Pixellücken
                for i in range(len(proj_x)):
                    px = proj_x[i]
                    py = proj_y[i]
                    
                    # Boundary Check auf dem 4K-Bildschirm
                    if 0 <= px < self.width - 1 and 0 <= py < self.height - 1:
                        color = [b_channel[i], g_channel[i], r_channel[i]]
                        canvas_matrix[py, px] = color
                        canvas_matrix[py+1, px] = color
                        canvas_matrix[py, px+1] = color
                        canvas_matrix[py+1, px+1] = color

        return canvas_matrix

    def export_dual_formats(self, matrix, base_filename):
        png_path = f"{base_filename}.png"
        cv2.imwrite(png_path, matrix)
        print(f"    + [ PNG ] 3D-Szenenansicht gesichert: '{png_path}'")
        
        ppm_path = f"{base_filename}.ppm"
        rgb_matrix = cv2.cvtColor(matrix, cv2.COLOR_BGR2RGB)
        header = f"P6\n{self.width} {self.height}\n255\n".encode('ascii')
        with open(ppm_path, "wb") as f:
            f.write(header)
            f.write(rgb_matrix.tobytes())
        print(f"    + [ PPM ] Unbestechlicher 3D-Master:  '{ppm_path}'")


if __name__ == "__main__":
    print("=" * 80)
    print("[ pTRC-4K-3D-IMMERSION ] MITTENDERIN IM RAUMGITTER")
    print("=" * 80)
    
    user_name = input("Bitte den Namen für den 3D-Flugraum eingeben: ")
        
    if not user_name.strip():
        print("[-] Fehler: Keine Eingabe erkannt. Abbruch.")
        sys.exit(1)
        
    initials = "".join([part.upper() for part in user_name.split() if part])
    if not initials:
        initials = "SPACE"
        
    filename_target = f"ptrc_4k_art_3d_{initials}"
    
    print("-" * 80)
    print(f" -> Starte 3D-Volumensynthese für: '{initials}'")
    
    engine = PTRC3DImmersionEngine()
    matrix_output = engine.render_deep_space(global_takt_pulse=1836, name_string=user_name)
    engine.export_dual_formats(matrix_output, filename_target)
    
    print("=" * 80)
    print(f" -> SUCCESS: Du stehst jetzt mitten drin! Dateien: '{filename_target}.png/.ppm'")
    print("=" * 80)
