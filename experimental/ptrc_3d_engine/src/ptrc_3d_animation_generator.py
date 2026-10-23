# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://gnu.org>.
# ==============================================================================

# -*- coding: utf-8 -*-
r"""
pTRC Framework - Advanced Volumetric Transposition Suite (Relativistic Passing Engine)
Operational Domain: Pure Integer Viewports (\mathbb{Z}^3). Zero Analog Leakage.
Beschreibung: Generiert eine dichte, prä-physikalische Kristallmatrix basierend auf 
              dem Modulo-210-Sieb und der Radius-9-Symmetrie der Ur-Zelle.
"""

import os
import sys
import subprocess
import time
import numpy as np

# Dynamische Pfad-Ermittlung fuer Termux/Android Umgebung
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

for depth in [script_dir, os.path.dirname(script_dir), os.path.dirname(os.path.dirname(script_dir))]:
    if depth:
        sys.path.insert(0, depth)
        src_path = os.path.join(depth, "src")
        if os.path.exists(src_path):
            sys.path.insert(0, src_path)

try:
    from ptrc_3d_stereo_engine import PTRC3DStereoEngine
except ImportError:
    class PTRC3DStereoEngine:
        def __init__(self, viewport_width=1920, viewport_height=1080):
            self.width = viewport_width
            self.height = viewport_height

class PTRC3DAnimationPipeline:
    def __init__(self, total_frames=144):
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        
        self.width = self.stereo_engine.width
        self.height = self.stereo_engine.height
        self.invariant_limit = 156
        self.SCALE = 1000
        
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def write_ppm_image(self, filename, buffer_matrix):
        """Schreibt ein unkomprimiertes Ganzzahl-PPM-Bild (P6-Binär)."""
        h, w, _ = buffer_matrix.shape
        header = f"P6\n{w} {h}\n255\n".encode('ascii')
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(buffer_matrix.tobytes())

    def draw_integer_rectangle(self, buffer, x1, y1, x2, y2, color):
        """Sicheres Ganzzahl-Pixel-Clipping im Matrixraster."""
        x1 = max(0, min(int(x1), self.width - 1))
        x2 = max(0, min(int(x2), self.width - 1))
        y1 = max(0, min(int(y1), self.height - 1))
        y2 = max(0, min(int(y2), self.height - 1))
        if x1 > x2: x1, x2 = x2, x1
        if y1 > y2: y1, y2 = y2, y1
        buffer[y1:y2+1, x1:x2+1] = color

    def generate_deterministic_video_sequence(self):
        print(f"[ pTRC CORE ] Starte dichte FullHD-Volumensynthese (1920x1080)...")
        cx = self.width // 2
        cy = self.height // 2
        z_offset = 65 

        for frame_idx in range(self.frames_limit):
            frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            phase_shift = (frame_idx * 1) % 24

            # ABTASTUNG DES REINEN GANZZAHL-RAUMS
            for dx in range(-18, 19):
                for dy in range(-18, 19):
                    for dz in range(-18, 19):
                        
                        Q = dx**2 + dy**2 + dz**2
                        if Q == 0:
                            continue
                            
                        # Modulo-210 Primorial-Raumsieb
                        if (Q % 210) > self.invariant_limit:
                            continue
                            
                        rx = dx
                        ry = dy
                        rz = dz + z_offset
                        
                        if (Q + phase_shift) % 2 == 0:
                            ry += 1
                        
                        # Perspektivische Integer-Projektion
                        denom = ((rz * self.SCALE) // 1414) + self.invariant_limit
                        if denom <= 0:
                            continue
                            
                        out_x = (((int(rx) * 45 * self.SCALE) // denom) + cx) % self.width
                        out_y = (((int(ry) * 45 * self.SCALE) // denom) + cy) % self.height
                        
                        # Geometrische Farb- und Symmetrie-Klassifizierung
                        if Q == 9 or Q == 18 or Q == 36:
                            r_c, g_c, b_c = 0, 255, 255
                            voxel_size = 5
                        elif Q == 144:
                            r_c, g_c, b_c = 255, 255, 255
                            voxel_size = 4
                        else:
                            depth_glow = max(40, 255 - ((rz * 120) // 128))
                            r_c, g_c, b_c = 40, int(depth_glow), 160
                            voxel_size = 3
                            
                        color_vector = [r_c, g_c, b_c]
                        
                        self.draw_integer_rectangle(
                            frame_buffer, 
                            out_x - voxel_size // 2, out_y - voxel_size // 2, 
                            out_x + voxel_size // 2, out_y + voxel_size // 2, 
                            color_vector
                        )

            frame_filename = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.ppm")
            self.write_ppm_image(frame_filename, frame_buffer)
            
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Synced Takt-Frame {frame_idx:03d}/{self.frames_limit} | Matrix-Cluster written.")

    def compile_lossless_output_video(self):
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.ppm")
        android_download_path = "/storage/emulated/0/Download/ptrc_wirminghaus_dual_passing.mp4"
        
        print(" -> Starte FFMPEG Kompression...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", android_download_path
        ]
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            print(f"\n[ SYSTEM CHECK OK ] Kristall-Video im Download-Ordner verankert!")
            print(f" -> Datei: {android_download_path}\n")
            
            for frame_idx in range(self.frames_limit):
                p = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.ppm")
                if os.path.exists(p): os.remove(p)
            os.rmdir(self.output_directory)
        except Exception as e:
            print(f"\n[ ACHTUNG ] FFmpeg-Kompression fehlgeschlagen: {e}")
            print(f" -> Die PPM-Bilder verbleiben im Cache-Ordner: {self.output_directory}")

if __name__ == "__main__":
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    pipeline.generate_deterministic_video_sequence()
    pipeline.compile_lossless_output_video()
