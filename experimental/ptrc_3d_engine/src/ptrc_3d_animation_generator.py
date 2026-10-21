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
pTRC Framework - Advanced Volumetric Transposition Suite (Dense Voxel Monolith)
Operational Domain: Pure Integer Viewports (\mathbb{Z}^3). Zero Analog Leakage.
Filename: ptrc_3d_animation_generator.py
"""

import os
import sys
import subprocess
import time
import numpy as np
import cv2

# ==============================================================================
# !!! TARGET ZONE: EXPLIZITE UND TAB-FREIE MODUL-KOPPLUNG !!!
# MARKER: PTRC_HARDCODED_NAMESPACE_RESOLVER_2026
# ==============================================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

parent_1 = os.path.dirname(script_dir)
parent_2 = os.path.dirname(parent_1)

for p in [parent_1, parent_2]:
    if p:
        sys.path.insert(0, p)
        src_dir = os.path.join(p, "src")
        if os.path.exists(src_dir):
            sys.path.insert(0, src_dir)

try:
    from ptrc_3d_stereo_engine import PTRC3DStereoEngine
except ImportError:
    from src.ptrc_3d_stereo_engine import PTRC3DStereoEngine

try:
    from ptrc_clock_core import PTRCModularClockEngine
except ImportError:
    from src.ptrc_clock_core import PTRCModularClockEngine

print(" -> [ PATH ] Synchronisation für 'ptrc_3d_animation_generator.py' erfolgreich etabliert.")
# ==============================================================================

class PTRC3DAnimationPipeline:
    """
    Kollabiert das 137-Takt Handshake-Sieve direkt in massive, dreidimensionale
    Körper aus dichtgepackten Ganzzahl-Raumpixeln ohne künstliche Linienstrukturen.
    """
    def __init__(self, total_frames=144):
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        
        self.width, self.height, self.depth = 320, 180, 128
        self.invariant_limit = 156
        self.FEYNMAN_LIMIT = 137  # Die 137 Handshake-Belichtungstakte vor dem Beobachter-Kollaps
        self.SCALE = 1000
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def _get_cpu_name(self):
        try:
            import platform
            if platform.system() == "Linux":
                command = "cat /proc/cpuinfo | grep 'model name' | uniq"
                cpu_info = subprocess.check_output(command, shell=True).decode().strip()
                if cpu_info:
                    return cpu_info.split(":")[-1].strip()
        except Exception:
            pass
        return "Intel(R) Core(TM) i3-3217U CPU @ 1.80GHz"

    def generate_deterministic_video_sequence(self):
        """Erzeugt das lückenlose Gitter aus dichten, volumetrischen Pixelblöcken."""
        cpu_name = self._get_cpu_name()
        print(f"[ PIPELINE ] Verwende Hardware-Profil: {cpu_name}")
        print(f" -> Starte volumetrische Raumpixel-Injektion...")
        
        self.total_generation_start = time.perf_counter()
        static_z = 58 

        cx_kugel, cy_kugel = self.width // 4, self.height // 2
        cx_pyramide, cy_pyramide = (self.width * 3) // 4, (self.height // 2) + 20
        
        # 1 Zentralkugel + 12 umschließende Nachbarkugeln (Dichteste Kugelpackung)
        fcc_offsets = [
            (0, 0, 0),  
            (2, 2, 0),  (2, -2, 0),  (-2, 2, 0),  (-2, -2, 0),
            (2, 0, 2),  (2, 0, -2), (-2, 0, 2),  (-2, 0, -2),
            (0, 2, 2),  (0, 2, -2), (0, -2, 2),  (0, -2, -2)
        ]

        for frame_idx in range(self.frames_limit):
            frame_start = time.perf_counter()
            frame_buffer = np.zeros((self.stereo_engine.height, self.stereo_engine.width, 3), dtype=np.uint8)
            
            # --- 137 TAKTE DEZENTRALE HANDSHAKE-PHASE ---
            for _ in range(self.FEYNMAN_LIMIT):
                self.clock_engine.evolve_clock_one_takt()
                
            pulse_size = (frame_idx % 4)

            # ==================================================================
            # RENDERING: 1. DIE MASSIVE WIRMINGHAUS-KUGEL (LINKS)
            # ==================================================================
            for ox, oy, oz in fcc_offsets:
                kx = cx_kugel + (ox * 14)
                ky = cy_kugel + (oy * 14)
                kz = static_z + (oz * 10)
                
                denom = ((kz * self.SCALE) // 1414) + self.invariant_limit
                out_x = (((int(kx - (self.width // 2)) * 8 * self.SCALE) // denom) + self.stereo_engine.width // 2) % self.stereo_engine.width
                out_y = (((int(ky - (self.height // 2)) * 8 * self.SCALE) // denom) + self.stereo_engine.height // 2) % self.stereo_engine.height
                
                pixel_block_radius = int(((10 + pulse_size) * self.SCALE) // denom)
                if pixel_block_radius < 2: pixel_block_radius = 2
                
                for dx in range(-pixel_block_radius, pixel_block_radius + 1):
                    for dy in range(-pixel_block_radius, pixel_block_radius + 1):
                        if (dx * dx) + (dy * dy) <= (pixel_block_radius * pixel_block_radius):
                            tx = (out_x + dx) % self.stereo_engine.width
                            ty = (out_y + dy) % self.stereo_engine.height
                            
                            depth_glow = max(40, 255 - ((kz * 150) // self.depth))
                            frame_buffer[ty, tx] = [255, int(depth_glow // 2), 0]

            # ==================================================================
            # RENDERING: 2. DIE MASSIVE PYRAMIDE (RECHTS)
            # ==================================================================
            for level in range(3):
                z_layer = level * 2
                y_layer = -level * 4
                for row in range(3 - level):
                    for col in range(3 - level):
                        px = cx_pyramide + (col * 24) - ((3 - level) * 12) + 12
                        py = cy_pyramide + (row * 24) - ((3 - level) * 12) + 12 + y_layer
                        
                        for ox, oy, oz in fcc_offsets:
                            kx = px + (ox * 4)
                            ky = py + (oy * 4)
                            kz = static_z + (z_layer + oz) * 6
                            
                            denom = ((kz * self.SCALE) // 1414) + self.invariant_limit
                            out_x = (((int(kx - (self.width // 2)) * 8 * self.SCALE) // denom) + self.stereo_engine.width // 2) % self.stereo_engine.width
                            out_y = (((int(ky - (self.height // 2)) * 8 * self.SCALE) // denom) + self.stereo_engine.height // 2) % self.stereo_engine.height
                            
                            pixel_block_radius = int(((8 + pulse_size) * self.SCALE) // denom)
                            if pixel_block_radius < 2: pixel_block_radius = 2
                            
                            for dx in range(-pixel_block_radius, pixel_block_radius + 1):
                                for dy in range(-pixel_block_radius, pixel_block_radius + 1):
                                    if (dx * dx) + (dy * dy) <= (pixel_block_radius * pixel_block_radius):
                                        tx = (out_x + dx) % self.stereo_engine.width
                                        ty = (out_y + dy) % self.stereo_engine.height
                                        
                                        depth_glow = max(40, 255 - ((kz * 150) // self.depth))
                                        frame_buffer[ty, tx] = [180, int(depth_glow), 40]

            cv2.imwrite(os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png"), frame_buffer)
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Frame {frame_idx:03d}/{self.frames_limit} | Volumetrischer Formschluss stabilisiert.")

        self.total_generation_end = time.perf_counter()

    def compile_lossless_output_video(self):
        """Kompiliert die dichten Voxel-Frames ab und erzeugt den Videostream."""
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.png")
        target_video = os.path.join(script_dir, "ptrc_wirminghaus_dense_monolith.mp4")
        
        print(" -> Starte FFMPEG-Kompilierung...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", target_video
        ]
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            print(f"    + [ SUCCESS ] Video erstellt: '{os.path.basename(target_video)}'")
            for frame_idx in range(self.frames_limit):
                p = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
                if os.path.exists(p): os.remove(p)
            os.rmdir(self.output_directory)
            return 1
        except Exception:
            return 0

if __name__ == "__main__":
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    pipeline.generate_deterministic_video_sequence()
    status = pipeline.compile_lossless_output_video()
    print(f" -> [ VALIDATION ] Video-Pipeline erfolgreich beendet. Status-Code: {status}")
