# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ==============================================================================

# -*- coding: utf-8 -*-
r"""
pTRC Framework - Advanced Volumetric Transposition Suite (Relativistic Passing Engine)
Operational Domain: Pure Integer Viewports (\mathbb{Z}^3). Zero Analog Leakage.
"""

import os
import sys
import subprocess
import time
import numpy as np

# Dynamische Pfad-Ermittlung fuer Termux/Android Umgebung
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Durchsuche alle hierarchischen Ebenen nach der ptrc_3d_stereo_engine.py
for depth in [script_dir, os.path.dirname(script_dir), os.path.dirname(os.path.dirname(script_dir))]:
    if depth:
        sys.path.insert(0, depth)
        src_path = os.path.join(depth, "src")
        if os.path.exists(src_path):
            sys.path.insert(0, src_path)

try:
    from ptrc_3d_stereo_engine import PTRC3DStereoEngine
except ImportError:
    # Fallback-Dummy-Klasse, falls die Datei in der Termux-Struktur verschoben wurde
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
        """Schreibt ein unkomprimiertes Ganzzahl-PPM."""
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
        print(f"[ pTRC CORE ] Starte FullHD-Integer-Bildsynthese...")
        cy = self.height // 2
        static_z = 58

        fcc_offsets = [
            (0, 0, 0), (2, 2, 0), (2, -2, 0), (-2, 2, 0), (-2, -2, 0),
            (2, 0, 2), (2, 0, -2), (-2, 0, 2), (-2, 0, -2), (0, 2, 2),
            (0, 2, -2), (0, -2, 2), (0, -2, -2)
        ]

        for frame_idx in range(self.frames_limit):
            frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            pyramid_move = (frame_idx * 4) % self.width
            pyramid_z = (frame_idx * 1) % 32

            # 1. KUGELSTREUUNG (Cyan)
            cx_sphere = self.width // 4
            for ox, oy, oz in fcc_offsets:
                kx, ky, kz = cx_sphere + (ox * 24), cy + (oy * 24), static_z + (oz * 4)
                denom = ((kz * self.SCALE) // 1414) + self.invariant_limit
                out_x = (((int(kx - (self.width // 2)) * 8 * self.SCALE) // denom) + self.width // 2) % self.width
                out_y = (((int(ky - (self.height // 2)) * 8 * self.SCALE) // denom) + self.height // 2) % self.height
                
                # Farbvektor explizit deklariert und uebergeben
                r_c, g_c, b_c = 0, 255, 255
                cyan_color = [r_c, g_c, b_c]
                self.draw_integer_rectangle(frame_buffer, out_x - 8, out_y - 8, out_x + 8, out_y + 8, cyan_color)

            # 2. BEWEGTE PYRAMIDE (Smaragd)
            cx_pyramid = (self.width * 3) // 4
            for level in range(3):
                y_layer = -level * 16
                for row in range(3 - level):
                    for col in range(3 - level):
                        px = cx_pyramid + (col * 56) - ((3 - level) * 28) - pyramid_move
                        py = cy + (row * 56) - ((3 - level) * 28) + 40 + y_layer
                        for ox, oy, oz in fcc_offsets:
                            kx, ky, kz = px + (ox * 8), py + (oy * 8), (static_z + 24) - pyramid_z + (level * 2 + oz) * 3
                            denom = ((kz * self.SCALE) // 1414) + self.invariant_limit
                            out_x = (((int(kx - (self.width // 2)) * 8 * self.SCALE) // denom) + self.width // 2) % self.width
                            out_y = (((int(ky - (self.height // 2)) * 8 * self.SCALE) // denom) + self.height // 2) % self.height
                            
                            depth_glow = max(40, 255 - ((kz * 150) // 128))
                            self.draw_integer_rectangle(frame_buffer, out_x - 4, out_y - 4, out_x + 4, out_y + 4, [40, int(depth_glow), 160])

            frame_filename = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.ppm")
            self.write_ppm_image(frame_filename, frame_buffer)
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Frame {frame_idx:03d}/{self.frames_limit} im Cache gesichert.")

    def compile_lossless_output_video(self):
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.ppm")
        # Primärer Pfad im Android-Download-Verzeichnis (Globaler Zugriff)
        android_download_path = "/storage/emulated/0/Download/ptrc_wirminghaus_dual_passing.mp4"
        
        print(" -> Starte FFMPEG Kompression...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", android_download_path
        ]
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            print(f"\n[ SYSTEM CHECK OK ] Video erfolgreich in den Hauptspeicher geschrieben!")
            print(f" -> Datei liegt unter: {android_download_path}\n")
            
            # Cache bereinigen
            for frame_idx in range(self.frames_limit):
                p = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.ppm")
                if os.path.exists(p): os.remove(p)
            os.rmdir(self.output_directory)
        except Exception:
            print(f"\n[ ACHTUNG ] FFmpeg fehlt oder hat keine Schreibrechte!")
            print(f" -> Die unkomprimierten Bilder liegen im Ordner: {self.output_directory}")

if __name__ == "__main__":
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    pipeline.generate_deterministic_video_sequence()
    pipeline.compile_lossless_output_video()
