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
pTRC Framework - Advanced Volumetric Transposition Suite (Universal Master Engine)
Operational Domain: Pure Integer Viewports (\mathbb{Z}^3). Zero Analog Leakage.
Description: Unified core tracking 144-facet spatial crystal matrices with absolute
integrated memory cleanup and -1 Plichta mirror delegation.
File Name: ptrc_3d_animation_generator.py
"""

import os
import sys
import subprocess
import time
import shutil
import numpy as np

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
        
        # Absolute storage routing for Samsung Galaxy S21 FE Download scope
        self.android_download_path = "/storage/emulated/0/Download"
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
        print(f"[ pTRC CORE ] Starte universelle MINT-Volumensynthese (1920x1080)...")
        cx = self.width // 2
        cy = self.height // 2
        z_offset = 65 

        # Exact linear indices to save precisely 5 control frames out to the Download folder
        control_frames_indices = set(np.linspace(0, self.frames_limit - 1, 5, dtype=int))

        for frame_idx in range(self.frames_limit):
            frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            phase_shift = (frame_idx * 1) % 24

            # --- PRESERVED NATIVE PURE INTEGER SPACE SCANNING ---
            for dx in range(-18, 19):
                for dy in range(-18, 19):
                    for dz in range(-18, 19):
                        
                        # --- THE CROSSED PLICHTA-MIRROR OPERATION (Z \ {0}) ---
                        # Eliminates spatial null stagnation by non-zero shift transposition
                        ptrc_dx = -1 if dx == 0 else dx
                        ptrc_dy = -1 if dy == 0 else dy
                        ptrc_dz = -1 if dz == 0 else dz
                        
                        Q = ptrc_dx**2 + ptrc_dy**2 + ptrc_dz**2
                        
                        # Modulo-210 Primorial-Raumsieb (Symmetry lock condition)
                        if (Q % 210) > self.invariant_limit:
                            continue
                            
                        rx = dx
                        ry = dy
                        rz = dz + z_offset
                        
                        if (Q + phase_shift) % 2 == 0:
                            ry += 1
                        
                        # --- COHERENT MONOLITH CORE (Pyramid integration condition) ---
                        # Injecting rotating central crystal values directly into the space array
                        if frame_idx > 72 and abs(dx) + abs(dy) <= (144 - (frame_idx % 24)):
                            # Force Golden Core coloration parameters dynamically
                            r_c, g_c, b_c = 218, 165, 32
                            voxel_size = 4
                        else:
                            # Standard multi-domain spectral classification
                            if Q == 9 or Q == 18 or Q == 36:
                                r_c, g_c, b_c = 0, 255, 255  # Active Wave / Fluid (Cyan)
                                voxel_size = 5
                            elif Q == 144:
                                r_c, g_c, b_c = 255, 255, 255  # Matrix Hull (White)
                                voxel_size = 4
                            else:
                                depth_glow = max(40, 255 - ((rz * 120) // 128))
                                r_c, g_c, b_c = 40, int(depth_glow), 160  # Background Space (Blue)
                                voxel_size = 3
                        
                        # --- DATA DELEGATION VIA -1 PHASE INVERSION ---
                        # Shading contours shifted dynamically via the Modulo-24 clock cross
                        mirror_shading = 255 - (phase_shift * 4)
                        color_vector = [
                            (r_c * mirror_shading) // 255,
                            (g_c * mirror_shading) // 255,
                            (b_c * mirror_shading) // 255
                        ]
                        
                        # Perspective projection
                        denom = ((rz * self.SCALE) // 1414) + self.invariant_limit
                        if denom <= 0:
                            continue
                            
                        out_x = (((int(rx) * 45 * self.SCALE) // denom) + cx) % self.width
                        out_y = (((int(ry) * 45 * self.SCALE) // denom) + cy) % self.height
                        
                        self.draw_integer_rectangle(
                            frame_buffer, 
                            out_x - voxel_size // 2, out_y - voxel_size // 2, 
                            out_x + voxel_size // 2, out_y + voxel_size // 2, 
                            color_vector
                        )

            frame_filename = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.ppm")
            self.write_ppm_image(frame_filename, frame_buffer)
            
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Synced Takt-Frame {frame_idx:03d}/{self.frames_limit} | Structural Matrix secured.")

    def compile_lossless_output_video(self):
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.ppm")
        video_target = os.path.join(self.android_download_path, "ptrc_wirminghaus_dual_passing.mp4")
        control_frames_set = set(np.linspace(0, self.frames_limit - 1, 5, dtype=int))
        
        print(" -> Starte FFMPEG Kompression...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", video_target
        ]
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            print(f"\n[ SYSTEM CHECK OK ] Universal Master Video saved to Downloads!")
            print(f" -> Path: {video_target}\n")
            
            # Autarkic Storage Cleanup Layer: Preserves exactly 5 control frames inside /Download/
            for frame_idx in range(self.frames_limit):
                p = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.ppm")
                if os.path.exists(p):
                    if frame_idx in control_frames_set:
                        dest_img = os.path.join(self.android_download_path, f"control_takt_frame_{frame_idx:03d}.ppm")
                        shutil.move(p, dest_img)
                    else:
                        os.remove(p)
            os.rmdir(self.output_directory)
            print("[ OK ] Transient cache cleared completely. 5 verification images exported to Downloads.")
        except Exception as e:
            print(f"\n[ ACHTUNG ] Transmission failed: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    pipeline.generate_deterministic_video_sequence()
    pipeline.compile_lossless_output_video()
