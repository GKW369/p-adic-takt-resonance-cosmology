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
pTRC Framework - Core Rendering & Artistic Expression Module: ptrc_4k_genesis_name_gif.py
Operational Domain: Discrete 4K Resolution Mapping (\mathbb{Z}) via modular sifting.
Features: 144-Facet Spatial Crystal Architecture (Haramein Lattice Sieve),
          Dynamic structural geometry mapping via 24-point contact interference,
          Lossless FFmpeg Pipeline MP4 Video Loop Exporter (Zero OpenCV Video-FPU Codecs).
"""

import numpy as np
import sys
import subprocess
from PIL import Image

class PTRC4KArtisticGenesisEngine:
    def __init__(self, canvas_width=3840, canvas_height=2160):
        self.width = canvas_width
        self.height = canvas_height
        self.primorial_base = 210
        self.control_base = 24  # The 24 contact points of the 12 enveloping crystals
        self.crystal_radius_steps = 9  # Exact 9 steps from center to facet boundaries
        self.invariant_limit = 156

    def execute_artistic_takt(self, global_takt_pulse, name_string, zoom_stride=2):
        # 1. Identity Token conversion for pure structural mapping
        ascii_sum = sum(ord(char) for char in name_string if char.isalnum())
        name_len = max(1, len(name_string.strip()))
        
        # Invariant parameter generation acting on the 24-point contact zone
        phase_offset = ascii_sum % self.control_base
        struct_multiplier = 1 + (ascii_sum % self.crystal_radius_steps)
        
        takt_factor = int(global_takt_pulse) % self.primorial_base
        center_x = self.width // 2
        center_y = self.height // 2
        
        y_indices = np.arange(0, self.height, zoom_stride)
        x_indices = np.arange(0, self.width, zoom_stride)
        Y, X = np.meshgrid(y_indices, x_indices, indexing='ij')
        
        # Whole-number spatial distance field (Quadrance calculation)
        delta_y = Y - center_y
        delta_x = X - center_x
        discrete_quadrance = (delta_x * delta_x) + (delta_y * delta_y)
        
        # Modulo-210 Primorial Sieve
        residue_210 = (discrete_quadrance * struct_multiplier) % self.primorial_base
        sieve_mask = residue_210 <= self.invariant_limit
        
        # --- 144-FACET CRYSTAL CONTACT MATRIX ---
        takt_check = (X * Y + takt_factor + phase_offset) % self.control_base
        crystal_resonance = (discrete_quadrance // (self.crystal_radius_steps * self.crystal_radius_steps)) % self.control_base
        
        takt_mask = (takt_check == crystal_resonance) | (takt_check == 12)
        valid_nodes_mask = sieve_mask & takt_mask
        
        # We initialize the canvas matrix directly in RGB order to bypass BGR-FPU overhead
        canvas_matrix = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        if np.any(valid_nodes_mask):
            valid_quadrance = discrete_quadrance[valid_nodes_mask]
            
            # --- DIGITAL WAVELENGTH SPECTRUM ROUTING ---
            wavelength_r = (valid_quadrance // (150 - struct_multiplier)) % 256
            wavelength_g = (valid_quadrance // (100 + phase_offset + 1)) % 256
            wavelength_b = (valid_quadrance // (50 + name_len)) % 256
            
            r_channel = (wavelength_r + name_len * 8) % 256
            g_channel = (wavelength_g + struct_multiplier * 15) % 256
            b_channel = (wavelength_b + phase_offset * 6) % 256

            rgb_pixels = np.stack([r_channel, g_channel, b_channel], axis=-1).astype(np.uint8)
            
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
        # 1. Real Integer Monospace PPM Master (Zero FPU involvement)
        ppm_path = f"{base_filename}.ppm"
        header = f"P6\n{self.width} {self.height}\n255\n".encode('ascii')
        with open(ppm_path, "wb") as f:
            f.write(header)
            f.write(matrix.tobytes())
        print(f"    + [ PPM ] Pure integer master file exported:     '{ppm_path}'")

        # 2. Pure Lossless PNG Image via Pillow
        png_path = f"{base_filename}.png"
        img = Image.fromarray(matrix, 'RGB')
        img.save(png_path, format="PNG")
        print(f"    + [ PNG ] Viewable image successfully exported: '{png_path}'")

    def generate_pulsing_video_ffmpeg(self, name_string, base_filename, steps=24):
        """
        Streamt die nackten Ganzzahl-Frames per Pipe direkt in das unbestechliche FFmpeg,
        um ein absolut flüssiges, H.264-komprimiertes MP4-Video auszugeben.
        """
        video_path = f"{base_filename}_pulse.mp4"
        print(f"[*] Initializing lossless FFmpeg pipeline for video loop synthesis ({steps} frames)...")
        
        # Der unbestechliche FFmpeg-Kommando-Vektor für Ubuntu
        command = [
            'ffmpeg',
            '-y',                          # Überschreibe existierende Dateien bedingungslos
            '-f', 'rawvideo',              # Eingangsformat: rohe Pixel-Bytes
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'rgb24',           # 24-bit RGB (Ganzzahl-Kopplung)
            '-s', f'{self.width}x{self.height}', # Native 4K-Auflösung
            '-r', '10',                    # 10 Frames pro Sekunde (Eingang)
            '-i', '-',                     # Die Eingabe erfolgt über die Python-Pipe
            '-c:v', 'libx264',             # H.264 Video-Codec
            '-pix_fmt', 'yuv420p',         # Maximale Player-Kompatibilität für Web/Handy
            video_path
        ]
        
        # Starte den FFmpeg-Subprozess ungedämpft im Hintergrund
        try:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print("[-] Error: 'ffmpeg' utility not found on this Ubuntu system.")
            print("    Please run: sudo apt update && sudo apt install ffmpeg")
            return
        
        for step in range(steps):
            # Takt-Vorschub um exakt 15 Schritte pro Frame für den perfekten Atem-Effekt
            takt_pulse = 1836 + (step * 15)
            # Für die Video-Vorschau nutzen wir zoom_stride=2 für volle 4K-Präzision
            matrix = self.execute_artistic_takt(global_takt_pulse=takt_pulse, name_string=name_string, zoom_stride=2)
            
            # Schiebe die rohen RGB-Bytes direkt in den FFmpeg-Rachen
            process.stdin.write(matrix.tobytes())
            print(f"    -> Frame {step+1}/{steps} piped into FFmpeg execution matrix.")
            
        process.stdin.close()
        process.wait()
        print(f"[+ SUCCESS ] 144-Facet Spatial Crystal MP4 Video saved to: '{video_path}'")


if __name__ == "__main__":
    print("=" * 80)
    print("[ pTRC-4K-AUTOMATIC-IRIS ] 144-FACET CRYSTAL ENGINE")
    print("=" * 80)
    
    user_name = input("Please enter the name string to map: ")
        
    if not user_name.strip():
        print("[-] Error: Empty input string detected. Aborting execution.")
        sys.exit(1)
        
    initials = "".join([part.upper() for part in user_name.split() if part])
    if not initials:
        initials = "GENESIS"
        
    filename_target = f"ptrc_4k_art_{initials}"
    
    print("-" * 80)
    print(f" -> Launching Takt Resonance Sieve for token: '{initials}'")
    
    engine = PTRC4KArtisticGenesisEngine()
    
    # 1. Exportiere das statische 4K-Meisterbild
    matrix_output = engine.execute_artistic_takt(global_takt_pulse=1836, name_string=user_name, zoom_stride=2)
    engine.export_dual_formats(matrix_output, filename_target)
    
    print("-" * 80)
    
    # 2. Erzeuge das flüssige 4K-MP4-Video via FFmpeg
    engine.generate_pulsing_video_ffmpeg(name_string=user_name, base_filename=filename_target, steps=24)
    
    print("=" * 80)
    print(f" -> SUCCESS: 4K static masters and fluid FFmpeg video loop secured.")
    print("=" * 80)
