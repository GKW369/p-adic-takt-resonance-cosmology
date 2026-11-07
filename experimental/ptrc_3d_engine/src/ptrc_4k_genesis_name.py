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
Features: Interactive Terminal Input prompt for universal name mapping,
          Automated phase-stabilization loop against dark-state collapse,
          Initials-only anonymized dual-format file exporter (PNG + PPM).
Optimized: 100% Vectorized Matrix Computations for Acer Aspire Dual-Core architectures.
"""

import numpy as np
import cv2
import sys

class PTRC4KArtisticGenesisEngine:
    """
    Erzeugt hochauflösende 3840x2160 Raumgitter-Strukturen, modifiziert durch 
    interaktive Namens-Rhythmen, automatische Phasen-Stabilisierung und Irisdruck-Farbpaletten.
    """
    def __init__(self, canvas_width=3840, canvas_height=2160):
        self.width = canvas_width
        self.height = canvas_height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156

    def execute_artistic_takt(self, global_takt_pulse, name_string, zoom_stride=2, color_vibe="cyan"):
        """
        Koppelt den textbasierten Namens-Rhythmus direkt in die divisionsfreie Matrix-Rasterung ein.
        Stabilisiert die Phase automatisch, damit keine leeren oder schwarzen Bilder entstehen.
        """
        # 1. Namens-Vertonung & Phasen-Gewichtung
        ascii_sum = sum(ord(char) for char in name_string if char.isalnum())
        name_phase_offset = ascii_sum % self.control_base
        
        takt_factor = int(global_takt_pulse) % self.primorial_base
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Erzeuge die Koordinaten-Gitter im diskreten Raum
        y_indices = np.arange(0, self.height, zoom_stride)
        x_indices = np.arange(0, self.width, zoom_stride)
        Y, X = np.meshgrid(y_indices, x_indices, indexing='ij')
        
        # Quadrance-Berechnung (Z-Raum Transformation)
        delta_y = Y - center_y
        delta_x = X - center_x
        discrete_quadrance = (delta_x * delta_x) + (delta_y * delta_y)
        
        # Das Modulo-210 Uhrsieb (Raumgitter-Basis)
        residue_210 = discrete_quadrance % self.primorial_base
        sieve_mask = residue_210 <= self.invariant_limit
        
        # Universeller Phasen-Suchlauf: Verhindert die "schwarze Seele", falls ein Offset ins Leere läuft
        valid_nodes_mask = None
        for phase_shift in range(self.control_base):
            target_phase = (12 + name_phase_offset + phase_shift) % self.control_base
            takt_check = (X * Y + takt_factor) % self.control_base
            takt_mask = takt_check == target_phase
            
            test_mask = sieve_mask & takt_mask
            if np.sum(test_mask) > 100:  # Mindestknotendichte für ein stabiles Bildgefüge
                valid_nodes_mask = test_mask
                break
                
        # Fallback, falls der Suchlauf extrem restriktiv ist
        if valid_nodes_mask is None:
            valid_nodes_mask = sieve_mask & ((X * Y + takt_factor) % self.control_base == 12)
        
        # Initialisiere die BGR-Farbmatrix komplett in Schwarz
        canvas_matrix = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        if np.any(valid_nodes_mask):
            valid_quadrance = discrete_quadrance[valid_nodes_mask]
            
            # Zero-Float Irisierung: Modulo-Wellen auf der Quadrance erzeugen rhythmische Farb-Bänder
            color_wave = (valid_quadrance // 80) % 256
            color_wave_alt = (valid_quadrance // 200) % 256
            
            if color_vibe == "bonbon":
                # Bonbon-Palette: Kristallines Magenta, feuriges Violett und weiche Töne
                b_channel = (130 + color_wave // 2) % 256
                g_channel = (color_wave_alt) % 120
                r_channel = (220 + color_wave // 3) % 256
            else:
                # pTRC-Signatur-Palette: Irisierendes Cyan, elektrisches Türkis und Smaragd
                b_channel = (190 + color_wave // 2) % 256
                g_channel = (160 + color_wave_alt) % 256
                r_channel = (color_wave // 5) % 80

            rgb_pixels = np.stack([b_channel, g_channel, r_channel], axis=-1).astype(np.uint8)
            
            # Fülle die Matrix unter Berücksichtigung des Zoom-Strides (Faden-Effekt)
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
        """
        Gibt das Bild gleichzeitig in PNG (universell) und PPM (rein ganzzahlig) aus.
        """
        png_path = f"{base_filename}.png"
        cv2.imwrite(png_path, matrix)
        print(f"    + [ PNG EXPORT ] Viewable image written: '{png_path}'")
        
        ppm_path = f"{base_filename}.ppm"
        rgb_matrix = cv2.cvtColor(matrix, cv2.COLOR_BGR2RGB)
        header = f"P6\n{self.width} {self.height}\n255\n".encode('ascii')
        with open(ppm_path, "wb") as f:
            f.write(header)
            f.write(rgb_matrix.tobytes())
        print(f"    + [ PPM EXPORT ] Pure integer master written:  '{ppm_path}'")


if __name__ == "__main__":
    print("=" * 80)
    print("[ pTRC-4K-UNIVERSAL-GENESIS ] INTERACTIVE MATRIX INITIALIZER")
    print("=" * 80)
    
    # Interaktive Abfrage im Terminal
    if sys.version_info[0] < 3:
        user_name = raw_input("Bitte den gewünschten Namen eingeben: ")
    else:
        user_name = input("Bitte den gewünschten Namen eingeben: ")
        
    if not user_name.strip():
        user_name = "ANONYMOUS REVOLUTION"
        
    # Extrahiere die Initialen für die absolut anonyme Dateibenennung auf GitHub
    initials = "".join([part[0].upper() for part in user_name.split() if part])
    if not initials:
        initials = "XYZ"
        
    # Bestimme die Farbpalette anhand der Namens-Eingabe (Automatisches Bonbon für Anke)
    vibe = "cyan"
    if "anke" in user_name.lower():
        vibe = "bonbon"
        
    filename_target = f"ptrc_4k_art_{initials}"
    
    print("-" * 80)
    print(f" -> Starting Engine for Identity Token: '{initials}' | Mode: {vibe}")
    
    engine = PTRC4KArtisticGenesisEngine()
    matrix_output = engine.execute_artistic_takt(global_takt_pulse=1836, name_string=user_name, zoom_stride=2, color_vibe=vibe)
    engine.export_dual_formats(matrix_output, filename_target)
    
    print("=" * 80)
    print(f" -> SUCCESS: Files saved anonymously as '{filename_target}.png/.ppm'")
    print("=" * 80)
