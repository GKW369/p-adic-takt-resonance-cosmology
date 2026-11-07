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
pTRC Framework - Core Rendering & Artistic Expression Module: ptrc_4k_genesis_name.py
Operational Domain: Discrete 4K Resolution Mapping (\mathbb{Z}) via modular sifting.
Features: 100% Automatic Irisating Chromaticity based on digital wavelengths,
          Single-prompt interactive terminal input (Zero Nerd-Overhead),
          Initials-only anonymized dual-format file exporter (PNG + PPM).
"""

import numpy as np
import cv2
import sys

class PTRC4KArtisticGenesisEngine:
    def __init__(self, canvas_width=3840, canvas_height=2160):
        self.width = canvas_width
        self.height = canvas_height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156

    def execute_artistic_takt(self, global_takt_pulse, name_string, zoom_stride=2):
        # 1. Namens-Vertonung für den initialen Phasen-Offset
        ascii_sum = sum(ord(char) for char in name_string if char.isalnum())
        name_phase_offset = ascii_sum % self.control_base
        
        takt_factor = int(global_takt_pulse) % self.primorial_base
        center_x = self.width // 2
        center_y = self.height // 2
        
        y_indices = np.arange(0, self.height, zoom_stride)
        x_indices = np.arange(0, self.width, zoom_stride)
        Y, X = np.meshgrid(y_indices, x_indices, indexing='ij')
        
        discrete_quadrance = ((X - center_x) ** 2) + ((Y - center_y) ** 2)
        
        residue_210 = discrete_quadrance % self.primorial_base
        sieve_mask = residue_210 <= self.invariant_limit
        
        # Automatischer Phasen-Suchlauf gegen "schwarze Löcher"
        valid_nodes_mask = None
        for phase_shift in range(self.control_base):
            target_phase = (12 + name_phase_offset + phase_shift) % self.control_base
            takt_mask = ((X * Y + takt_factor) % self.control_base) == target_phase
            
            test_mask = sieve_mask & takt_mask
            if np.sum(test_mask) > 100:
                valid_nodes_mask = test_mask
                break
                
        if valid_nodes_mask is None:
            valid_nodes_mask = sieve_mask & ((X * Y + takt_factor) % self.control_base == 12)
        
        canvas_matrix = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        if np.any(valid_nodes_mask):
            valid_quadrance = discrete_quadrance[valid_nodes_mask]
            
            # --- DIE DIGITALE WELLENLÄNGE ---
            # Wir nutzen die Quadrance direkt als unbestechlichen Taktgeber für die Spektralfarben.
            # Durch die Modulo-Schleifen bricht sich das Licht vollautomatisch irisierend.
            wavelength_b = (valid_quadrance // 60) % 256
            wavelength_g = (valid_quadrance // 120) % 256
            wavelength_r = (valid_quadrance // 180) % 256
            
            # Zusätzliche Phasenverschiebung basierend auf dem Namen einweben, 
            # damit jeder Name sein individuelles Farbspektrum entfaltet
            b_channel = (wavelength_b + name_phase_offset * 5) % 256
            g_channel = (wavelength_g + name_phase_offset * 10) % 256
            r_channel = (wavelength_r + name_phase_offset * 15) % 256

            rgb_pixels = np.stack([b_channel, g_channel, r_channel], axis=-1).astype(np.uint8)
            
            valid_y, valid_x = np.where(valid_nodes_mask)
            for dy in range(zoom_stride):
                for dx in range(zoom_stride):
                    y_target = valid_y * zoom_stride + dy
                    x_target = valid_x * zoom_stride + dx
                    in_bounds = (y_target < self.height) & (x_target < self.width)
                    if np.any(in_bounds):
                        canvas_matrix[y_target[in_bounds], x_target[in_bounds]] = rgb_pixels[in_bounds]
                        
        return canvas_matrix

    def export_dual_formats(self, matrix, base_filename):
        png_path = f"{base_filename}.png"
        cv2.imwrite(png_path, matrix)
        print(f"    + [ PNG ] Sichtbares Bild gespeichert:  '{png_path}'")
        
        ppm_path = f"{base_filename}.ppm"
        rgb_matrix = cv2.cvtColor(matrix, cv2.COLOR_BGR2RGB)
        header = f"P6\n{self.width} {self.height}\n255\n".encode('ascii')
        with open(ppm_path, "wb") as f:
            f.write(header)
            f.write(rgb_matrix.tobytes())
        print(f"    + [ PPM ] Unbestechlicher Ganzzahl-Master: '{ppm_path}'")


if __name__ == "__main__":
    print("=" * 80)
    print("[ pTRC-4K-AUTOMATIC-IRIS ] DIGITAL WAVELENGTH ENGINE")
    print("=" * 80)
    
    # Bereinigter, nativer Python 3 Input ohne fehleranfällige Typenprüfung
    user_name = input("Bitte den Namen eingeben: ")
        
    if not user_name.strip():
        print("[-] Fehler: Keine Eingabe erkannt. Abbruch.")
        sys.exit(1)
        
    # Absolute Anonymisierung der Dateinamen über die Initialen der Eingabe
    initials = "".join([part.upper() for part in user_name.split() if part])
    if not initials:
        initials = "GENESIS"
        
    filename_target = f"ptrc_4k_art_{initials}"
    
    print("-" * 80)
    print(f" -> Starte Takt-Resonanz für: '{initials}' (Irisierung aktiv)")
    
    engine = PTRC4KArtisticGenesisEngine()
    matrix_output = engine.execute_artistic_takt(global_takt_pulse=1836, name_string=user_name, zoom_stride=2)
    engine.export_dual_formats(matrix_output, filename_target)
    
    print("=" * 80)
    print(f" -> FERTIG: Bilder erfolgreich exportiert als '{filename_target}.png/.ppm'")
    print("=" * 80)
