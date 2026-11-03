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
Operational Domain: Pure Integer Viewports (\mathbb{Z}^3). Zero Float Noise.
Fix: Corrected voxel raster-stepping to ensure structural aircraft/pyramid preservation.
File Name: ptrc_3d_animation_generator.py
"""

import os
import sys
import subprocess
import time
import shutil
import numpy as np

class PTRCUniversalGraphicsProcessor:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.invariant_limit = 156
        self.SCALE = 1000

    def project_observer_retina(self, x, y, z, iod=60):
        """Perspective 3D whole-number projection mimicking true observer distance."""
        scaled_depth = (z * self.SCALE) // 1414
        denom = scaled_depth + self.invariant_limit
        if denom <= 0:
            denom = 1
            
        proj_x_left = ((x - iod) * 55 * self.SCALE) // denom
        proj_x_right = ((x + iod) * 55 * self.SCALE) // denom
        proj_y = (y * 55 * self.SCALE) // denom
        
        return (proj_x_left + self.width // 2) % self.width, \
               (proj_x_right + self.width // 2) % self.width, \
               (proj_y + self.height // 2) % self.height

class PTRC3DAnimationPipeline:
    def __init__(self, total_frames=144):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.frames_limit = total_frames
        self.processor = PTRCUniversalGraphicsProcessor(width=1920, height=1080)
        
        self.width = self.processor.width
        self.height = self.processor.height
        self.invariant_limit = 156
        self.SCALE = 1000
        
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

    def draw_integer_voxel(self, buffer, cx, cy, size, color):
        """Zeichnet ein formschlüssiges Voxel-Quadrat auf der wahren Renderebene."""
        half = size // 2
        x1 = max(0, min(int(cx - half), self.width - 1))
        x2 = max(0, min(int(cx + half), self.width - 1))
        y1 = max(0, min(int(cy - half), self.height - 1))
        y2 = max(0, min(int(cy + half), self.height - 1))
        buffer[y1:y2+1, x1:x2+1] = color

    def generate_deterministic_video_sequence(self):
        print(f"[ pTRC CORE ] Synthesizing 1080p structural volume (Preserving Aircraft Geometry)...")
        cx = self.width // 2
        cy = self.height // 2
        z_offset = 75 

        control_frames_indices = set(np.linspace(0, self.frames_limit - 1, 5, dtype=int))

        for frame_idx in range(self.frames_limit):
            frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            phase_shift = (frame_idx * 1) % 24

            # --- PRESERVED NATIVE PURE INTEGER SPACE SCANNING ---
            for dx in range(-16, 17):
                for dy in range(-16, 17):
                    for dz in range(-16, 17):
                        
                        # --- THE CROSSED PLICHTA-MIRROR OPERATION (Z \ {0}) ---
                        ptrc_dx = -1 if dx == 0 else dx
                        ptrc_dy = -1 if dy == 0 else dy
                        ptrc_dz = -1 if dz == 0 else dz
                        
                        Q = ptrc_dx**2 + ptrc_dy**2 + ptrc_dz**2
                        
                        # Invarianz-Prüfung gegen unkontrollierte Bildüberflutung
                        if (Q % 210) > self.invariant_limit:
                            continue
                            
                        # --- COHERENT STRUCTURE ENGINE (The Aircraft & Pyramid Lattice) ---
                        # Geometrischer Bedingungsanker für den formschlüssigen Körper
                        is_aircraft_hull = (abs(dx) < 3 and abs(dz) < 12 and dy == 0) or \
                                           (abs(dz) < 2 and abs(dx) < 14 and dy == 0) or \
                                           (abs(dx) == abs(dz) and abs(dy) < 2 and Q < 150)
                                           
                        is_central_pyramid = (frame_idx > 72) and (abs(dx) + abs(dy) + abs(dz) <= (18 - (phase_shift // 2)))

                        if is_central_pyramid:
                            # Central rotating crystal pyramid core (Spectral Gold)
                            r_c, g_c, b_c = 218, 165, 32
                            voxel_size = 5
                        elif is_aircraft_hull:
                            # Invariant Core Structure (Pure Matrix Hull / White)
                            r_c, g_c, b_c = 255, 255, 255
                            voxel_size = 4
                        elif Q in:
                            # Active Wave Nodes / Fluid Fields (Cyan)
                            r_c, g_c, b_c = 0, 255, 255
                            voxel_size = 3
                        else:
                            # Suppressed noise backgrounds (Deep Cosmic Indigo)
                            r_c, g_c, b_c = 25, 40, 110
                            voxel_size = 2

                        # --- PHASE INVERSION DATA DELEGATION ---
                        mirror_shading = 255 - (phase_shift * 5)
                        color_vector = [
                            (r_c * mirror_shading) // 255,
                            (g_c * mirror_shading) // 255,
                            (b_c * mirror_shading) // 255
                        ]
                        
                        # Target transformation onto the observer perspective
                        rx = dx
                        ry = dy
                        rz = dz + z_offset
                        
                        xl_p, xr_p, yd_p = self.processor.project_observer_retina(rx, ry, rz)
                        
                        # Render dual stereo points to the viewport
                        for xc in [xl_p, xr_p]:
                            self.draw_integer_voxel(frame_buffer, xc, yd_p, voxel_size, color_vector)

            frame_filename = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.ppm")
            self.write_ppm_image(frame_filename, frame_buffer)
            
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Synced Takt-Frame {frame_idx:03d}/{self.frames_limit} | Aircraft Structure locked.")

    def compile_lossless_output_video(self):
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.ppm")
        video_target = os.path.join(self.android_download_path, "ptrc_wirminghaus_dual_passing.mp4")
        control_frames_set = set(np.linspace(0, self.frames_limit - 1, 5, dtype=int))
        
        print(" -> Starting FFmpeg Compression layer...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", video_target
        ]
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            print(f"\n[ SYSTEM CHECK OK ] Universal Master Video saved to Downloads!")
            print(f" -> Path: {video_target}\n")
            
            # Export exactly 5 cleanly distributed control frames directly to the Android Download directory
            for frame_idx in range(self.frames_limit):
                p = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.ppm")
                if os.path.exists(p):
                    if frame_idx in control_frames_set:
                        dest_img = os.path.join(self.android_download_path, f"control_takt_frame_{frame_idx:03d}.ppm")
                        shutil.move(p, dest_img)
                    else:
                        os.remove(p)
            os.rmdir(self.output_directory)
            print("[ OK ] Transient cache cleared. 5 verification images exported to Downloads.")
        except Exception as e:
            print(f"\n[ SYSTEM TRUNCATION ERROR ] Transmission failed: {e}")

if __name__ == "__main__":
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    pipeline.generate_deterministic_video_sequence()
    pipeline.compile_lossless_output_video()
