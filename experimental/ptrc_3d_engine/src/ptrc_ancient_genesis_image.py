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
pTRC Framework - Genesis Core Image Generator: ptrc_ancient_genesis_image.py
Operational Domain: Baking Discrete Semitic Radical Vectors into a Single 4K Image.
Update: 100% Zero-Removal. Strict implementation of the \mathbb{Z} \setminus \{0\} space.
"""

import numpy as np
import cv2

def generate_genesis_matrix_image():
    print("=" * 80)
    print("[ pTRC GENESIS CORE ] Sifting Invariant Hebrew Word Geometry")
    print("=" * 80)

    # 4K-Leinwand starr festlegen
    width = 3840
    height = 2160
    center_x = width // 2
    center_y = height // 2

    # Das Uhrsieb-Fundament
    primorial_base = 210
    control_base = 24
    radius_steps = 9
    invariant_limit = 156
    takt_pulse = 1836  # Synchroner Basis-Takt

    # --- Die 3-Radikal-Vektoren von 'B-R-E-SH-I-TH' (Gematria-Firmware) ---
    v1_b, v1_r, v1_e = 2, 200, 1        # Erste Dreier-Wurzel (Beresch)
    v2_sh, v2_i, v2_th = 300, 10, 400   # Zweite Dreier-Wurzel (Ith)

    # Invariante Parameter-Generierung direkt aus der Wort-Substanz
    ascii_sum = v1_b + v1_r + v1_e + v2_sh + v2_i + v2_th
    phase_offset = ascii_sum % control_base
    struct_multiplier = 1 + (ascii_sum % radius_steps)

    print(f"[*] Gematria Sum: {ascii_sum} | Phase Offset: {phase_offset}")
    print(f"[*] Multiplier:  {struct_multiplier} | Matrix Rule: Modulo-210/24")
    print("[*] Calculating pixel lattice nodes branchless in Z \\ {0}...")

    # Zeilenweiser Zoom-Stride von 4 erzeugt die punktreine Braille-Struktur
    zoom_stride = 4
    y_indices = np.arange(0, height, zoom_stride)
    x_indices = np.arange(0, width, zoom_stride)
    Y, X = np.meshgrid(y_indices, x_indices, indexing='ij')

    # --- DER UNBESTECHLICHE pTRC-PHASENSPRUNG (ELIMINIERUNG DER NULL) ---
    # 1. Berechne den nackten Pixel-Abstand zur geometrischen Mitte (0 bis N)
    raw_dx = (X - center_x) // zoom_stride
    raw_dy = (Y - center_y) // zoom_stride

    # 2. Wenn der Abstand >= 0 ist, addieren wir 1 (Verschiebung in den positiven Raum)
    # Wenn der Abstand < 0 ist, bleibt er starr negativ (1, 2, 3... vs -1, -2, -3...)
    pTRC_x = np.where(raw_dx >= 0, raw_dx + 1, raw_dx)
    pTRC_y = np.where(raw_dy >= 0, raw_dy + 1, raw_dy)

    # 3. Die unbestechliche Abstands-Quadrance im reinen Z \ {0} Raum
    discrete_quadrance = (pTRC_x * pTRC_x) + (pTRC_y * pTRC_y)

    # Das Modulo-210 Uhrsieb
    residue_210 = (discrete_quadrance * struct_multiplier) % primorial_base
    sieve_mask = residue_210 <= invariant_limit

    # 144-Facetten Haramein-Kontakt-Matrix
    takt_factor = takt_pulse % primorial_base
    takt_check = (pTRC_x * pTRC_y + takt_factor + phase_offset) % control_base
    crystal_resonance = (discrete_quadrance // (radius_steps * radius_steps)) % control_base
    
    takt_mask = (takt_check == crystal_resonance) | (takt_check == 12)
    valid_nodes_mask = sieve_mask & takt_mask

    # Leere RGB-Leinwand initialisieren
    canvas_matrix = np.zeros((height, width, 3), dtype=np.uint8)

    if np.any(valid_nodes_mask):
        valid_quadrance = discrete_quadrance[valid_nodes_mask]

        # Verlustfreie Wellenlängen-Zuweisung über die kombinierten Vektoren
        wavelength_r = (valid_quadrance // (150 - struct_multiplier)) % 256
        wavelength_g = (valid_quadrance // (100 + phase_offset + 1)) % 256
        wavelength_b = (valid_quadrance // (50 + v1_b)) % 256

        # Kanäle mischen unter Einbeziehung der hebräischen End-Radikale (Resch und Taw)
        r_channel = (wavelength_r + v1_r * 8) % 256
        g_channel = (wavelength_g + struct_multiplier * 15) % 256
        b_channel = (wavelength_b + v2_th * 6) % 256

        # In OpenCV ist die Farbreihenfolge standardmäßig BGR (Blau, Grün, Rot)
        bgr_pixels = np.stack([b_channel, g_channel, r_channel], axis=-1).astype(np.uint8)

        valid_y, valid_x = np.where(valid_nodes_mask)
        for dy in range(zoom_stride):
            for dx in range(zoom_stride):
                canvas_matrix[valid_y * zoom_stride + dy, valid_x * zoom_stride + dx] = bgr_pixels

    # Speicher das unkomprimierte Bild direkt als PNG auf die Festplatte
    output_filename = "GKW369_genesis_core.png"
    cv2.imwrite(output_filename, canvas_matrix)
    
    print("-" * 80)
    print(f"[+ SUCCESS ] Genesis Core Image baked into: '{output_filename}'")
    print("=" * 80)

if __name__ == "__main__":
    generate_genesis_matrix_image()
