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

import numpy as np

class PTRCAncientGematriaSieveEngine:
    def __init__(self, canvas_width=3840, canvas_height=2160):
        self.width = canvas_width
        self.height = canvas_height
        self.primorial_base = 210
        self.control_base = 24  
        self.crystal_radius_steps = 9  
        self.invariant_limit = 156
        
        # Invariante Gematria-Tabelle der 22 hebräischen Ganzzahl-Knoten
        self.gematria_table = {
            'A': 1, 'B': 2, 'G': 3, 'D': 4, 'H': 5, 'V': 6, 'Z': 7, 'CH': 8, 'T': 9, 'I': 10,
            'K': 20, 'L': 30, 'M': 40, 'N': 50, 'S': 60, 'E': 70, 'P': 80, 'TZ': 90, 'Q': 100,
            'R': 200, 'SH': 300, 'TH': 400
        }

    def decode_text_to_integer_vectors(self, input_string):
        cleaned_tokens = []
        upper_text = input_string.upper()
        i = 0
        while i < len(upper_text):
            if upper_text[i:i+2] in ['CH', 'TZ', 'SH', 'TH']:
                cleaned_tokens.append(upper_text[i:i+2])
                i += 2
            elif upper_text[i] in self.gematria_table:
                cleaned_tokens.append(upper_text[i])
                i += 1
            else:
                i += 1
                
        vectors = []
        for index in range(0, len(cleaned_tokens), 3):
            block = cleaned_tokens[index:index+3]
            while len(block) < 3:
                block.append('A')  # Branchless Padding mit Aleph
                
            val_1 = self.gematria_table[block[0]]
            val_2 = self.gematria_table[block[1]]
            val_3 = self.gematria_table[block[2]]
            vectors.append((val_1, val_2, val_3))
            
        if not vectors:
            vectors.append((1, 2, 3))  
        return vectors

    def execute_crystal_sieve(self, global_takt_pulse, coordinate_vector):
        v1, v2, v3 = coordinate_vector
        ascii_sum = v1 + v2 + v3
        phase_offset = ascii_sum % self.control_base
        struct_multiplier = 1 + (ascii_sum % self.crystal_radius_steps)
        
        takt_factor = int(global_takt_pulse) % self.primorial_base
        center_x = self.width // 2
        center_y = self.height // 2
        
        zoom_stride = 4
        y_indices = np.arange(0, self.height, zoom_stride)
        x_indices = np.arange(0, self.width, zoom_stride)
        Y, X = np.meshgrid(y_indices, x_indices, indexing='ij')
        
        discrete_quadrance = ((X - center_x) ** 2) + ((Y - center_y) ** 2)
        residue_210 = (discrete_quadrance * struct_multiplier) % self.primorial_base
        sieve_mask = residue_210 <= self.invariant_limit
        
        takt_check = (X * Y + takt_factor + phase_offset) % self.control_base
        crystal_resonance = (discrete_quadrance // (self.crystal_radius_steps * self.crystal_radius_steps)) % self.control_base
        
        takt_mask = (takt_check == crystal_resonance) | (takt_check == 12)
        valid_nodes_mask = sieve_mask & takt_mask
        
        canvas_matrix = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        if np.any(valid_nodes_mask):
            valid_quadrance = discrete_quadrance[valid_nodes_mask]
            wavelength_r = (valid_quadrance // (150 - struct_multiplier)) % 256
            wavelength_g = (valid_quadrance // (100 + phase_offset + 1)) % 256
            wavelength_b = (valid_quadrance // (50 + v1)) % 256
            
            r_channel = (wavelength_r + v2 * 8) % 256
            g_channel = (wavelength_g + struct_multiplier * 15) % 256
            b_channel = (wavelength_b + v3 * 6) % 256
            rgb_pixels = np.stack([r_channel, g_channel, b_channel], axis=-1).astype(np.uint8)
            
            valid_y, valid_x = np.where(valid_nodes_mask)
            for dy in range(zoom_stride):
                for dx in range(zoom_stride):
                    canvas_matrix[valid_y * zoom_stride + dy, valid_x * zoom_stride + dx] = rgb_pixels
                        
        return canvas_matrix

# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
# Licensed under the terms of the GNU Affero General Public License v3 (AGPLv3)
# ==============================================================================

# -*- coding: utf-8 -*-
import sys
import subprocess
# Importiert die unbestechliche Basis-Engine aus dem selben Verzeichnis
from ptrc_gematria_core import PTRCAncientGematriaSieveEngine

def generate_ancient_resonance_video(input_text, base_filename):
    engine = PTRCAncientGematriaSieveEngine()
    radical_vectors = engine.decode_text_to_integer_vectors(input_text)
    steps = len(radical_vectors)
    video_path = f"{base_filename}_ancient_pulse.avi"
    
    print(f"[*] Initializing 100% FPU-clean Gematria Video Pipeline...")
    print(f"    Total text structural steps detected: {steps} radical blocks.")
    
    command = [
        'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{engine.width}x{engine.height}', '-framerate', '4', '-i', '-',
        '-c:v', 'huffyuv', '-pix_fmt', 'rgb24', '-vf', 'fps=4', video_path
    ]
    
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("[-] Error: 'ffmpeg' utility not found. Please install via apt.")
        return
        
    try:
        for step, vector in enumerate(radical_vectors):
            takt_pulse = 1836 + (step * 35)
            matrix = engine.execute_crystal_sieve(global_takt_pulse=takt_pulse, coordinate_vector=vector)
            process.stdin.write(matrix.tobytes())
            print(f"    -> Radical Block {step+1}/{steps} {vector} locked into Braille matrix plane.")
            
        process.stdin.close()
        process.wait()
        print(f"[+ SUCCESS ] Ancient Gematria HuffYUV Video saved to: '{video_path}'")
    except BrokenPipeError:
        print("[-] Critical Pipe Break: FFmpeg interface rejected text streams.")

if __name__ == "__main__":
    print("=" * 80)
    print("[ pTRC-ANCIENT-GEMATRIA-SIEVE ] 144-FACET TEXT MATRIX")
    print("=" * 80)
    print(" Please use Latin transliteration for the 22 ancient nodes.")
    print(" Example nodes: A B G D H V Z CH T I K L M N S E P TZ Q R SH TH")
    print("-" * 80)
    
    user_text = input("Please enter the ancient code sequence: ")
    if not user_text.strip():
        print("[-] Error: Empty sequence. Aborting computation.")
        sys.exit(1)
        
    generate_ancient_resonance_video(input_text=user_text, base_filename="ptrc_gematria_output")
    print("=" * 80)
    print(" -> SUCCESS: Text firmware successfully translated into invariant geometry.")
    print("=" * 80)
