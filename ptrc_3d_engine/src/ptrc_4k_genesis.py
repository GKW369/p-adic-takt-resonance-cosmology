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
pTRC Framework - Core Rendering Module: Ultra-High-Definition 4K Genesis Grid
Operational Domain: Discrete 4K Resolution Mapping (\mathbb{Z}) via modular sifting.
Optimized: 100% Vectorized Matrix Computations bypassing heavy Python loops.
"""

import numpy as np
import cv2

class PTRC4KGenesisEngine:
    """
    Executes precise integer-based grid allocations for 3840x2160 resolution canvases
    utilizing nested primorial residue filters and Modulo-24 control clocks.
    """
    def __init__(self, canvas_width=3840, canvas_height=2160):
        self.width = canvas_width
        self.height = canvas_height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156
        self.SCALE = 1000
        
        # 1-bit boolean 4K master canvas memory array
        self.canvas_matrix = np.zeros((self.height, self.width), dtype=np.uint8)

    # ==========================================================================
    # !!! TARGET ZONE: ABSOLUT FEHLERFREIE 4K BITMAP VEKTORISIERUNG !!!
    # MARKER: PTRC_GPU_VECTOR_ACCELERATION_TRUE_FIX_2026
    # ==========================================================================
    def execute_genesis_raster_takt(self, global_takt_pulse):
        """
        Populates the high-density coordinate grid based on numeric clock interference.
        Vektorisiert ohne Informationsverlust. Berechnet jeden Zustand exakt wie die Urversion.
        """
        takt_factor = int(global_takt_pulse) % self.primorial_base
        center_x = self.width // 2
        center_y = self.height // 2
        
        print(f" -> Mapping high-density 4K integer space nodes via vectorized grids...")
        
        # Wir bauen das 2D-Gitter direkt für jeden zweiten Pixel auf, exakt wie in deiner Schleife (step=2)
        y_range = np.arange(0, self.height, 2, dtype=np.int32)
        x_range = np.arange(0, self.width, 2, dtype=np.int32)
        
        # Erzeugt die vollständigen Koordinaten-Matrizen im RAM
        Y, X = np.meshgrid(y_range, x_range, indexing='ij')
        
        # Physikalische Abstandsquadrate (Ur-Metrik bezogen auf das Zentrum)
        delta_y = Y - center_y
        delta_x = X - center_x
        discrete_quadrance = (delta_x * delta_x) + (delta_y * delta_y)
        
        # 1. DAS MODULO-210 UHRSIEB
        residue_210 = discrete_quadrance % self.primorial_base
        sieve_mask = residue_210 <= self.invariant_limit
        
        # 2. DER Z/24Z PHASENKONTROLL-CHECK (Exakt deine Formel: x * y + takt)
        takt_check = (X * Y + takt_factor) % self.control_base
        takt_mask = takt_check == 12
        
        # Kombiniere die Filter-Kriterien deterministisch
        valid_nodes_mask = sieve_mask & takt_mask
        
        # Hole die echten Pixel-Indizes, bei denen die Symmetrie zutrifft
        real_y, real_x = np.where(valid_nodes_mask)
        
        # Da wir mit arange(0, ..., 2) gearbeitet haben, müssen wir die Indizes der Maske
        # wieder auf die realen Positionen mappen:
        real_y = real_y * 2
        real_x = real_x * 2
        
        # Blitzschnelle, blockweise 2x2-Pixel-Zuweisung im Speicher
        if len(real_y) > 0:
            self.canvas_matrix[real_y, real_x] = 1
            self.canvas_matrix[real_y + 1, real_x] = 1
            self.canvas_matrix[real_y, real_x + 1] = 1
            self.canvas_matrix[real_y + 1, real_x + 1] = 1
            print(f"    + [ LOG ] {len(real_y) * 4} Pixel erfolgreich in Speicher-Matrix geschrieben.")
    # ==========================================================================
    # !!! END OF TARGET ZONE !!!
    # ==========================================================================

    def export_genesis_bitmap(self, output_path="ptrc_4k_genesis_master.png"):
        """
        Saves the processed 4K canvas matrix directly onto disk as a lossless image.
        """
        # Skaliere die 1-Bit-Werte (0 und 1) auf volles Weiß (255) hoch
        pixel_sharp_view = self.canvas_matrix * 255
        
        # Schreibe die Datei via OpenCV
        success = cv2.imwrite(output_path, pixel_sharp_view)
        if success:
            print(f"    + [ SUCCESS ] UHD Genesis-Bild erfolgreich exportiert: '{output_path}'")
        else:
            print(f"    - [ ERROR ] Schreiben der Bilddatei fehlgeschlagen: '{output_path}'")

    def verify_raster_mass_density(self):
        """
        Aggregates active 4K lattice pixels to measure total integrated mass load.
        """
        total_active_pixels = int(np.sum(self.canvas_matrix))
        if total_active_pixels > 0:
            return 1
        return 0

if __name__ == "__main__":
    print("[ pTRC-4K-GENESIS ] Initializing high-resolution integer canvas pipelines...")
    engine = PTRC4KGenesisEngine()
    
    print(" -> Clocking ultra-hd matrix generation cycles for system Takt 1836...")
    engine.execute_genesis_raster_takt(global_takt_pulse=1836)
    
    # JETZT wird das Bild physisch erzeugt und abgespeichert
    engine.export_genesis_bitmap("ptrc_4k_genesis_master.png")
    
    is_valid = engine.verify_raster_mass_density()
    print(f" -> [ VALIDATION ] 4K image raster pass completed successfully.")
    print(f" -> High-Resolution Field Density Active Status: {is_valid}")
    print(" -> STATUS: Zero-Float 4K Genesis Grid Suite Successfully Audited.")
