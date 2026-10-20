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
pTRC Framework - Advanced Animation & Video Engine Pipeline
Filename: ptrc_3d_animation_generator.py
Operational Domain: Pure Discrete Memory Chains (\mathbb{Z}^3) representing 144-facet crystals.
"""

import os
import sys
import subprocess
import time
import numpy as np
import cv2

# Hardcoded Target-Namespace-Resolver für fehlerfreie Repository-Kopplung
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
for p in [os.path.dirname(script_dir), os.path.dirname(os.path.dirname(script_dir))]:
    if p:
        sys.path.insert(0, p)
        src_dir = os.path.join(p, "src")
        if os.path.exists(src_dir):
            sys.path.insert(0, src_dir)

try:
    from ptrc_3d_stereo_engine import PTRC3DStereoEngine
    from ptrc_clock_core import PTRCModularClockEngine
    from ptrc_geometry_sieve import PTRCGeometrySieve
except ImportError:
    from src.ptrc_3d_stereo_engine import PTRC3DStereoEngine
    from src.ptrc_clock_core import PTRCModularClockEngine
    from src.ptrc_geometry_sieve import PTRCGeometrySieve

class PTRC3DAnimationPipeline:
    """
    Rendert ruhig stehende Kugel- und Pyramidenformationen.
    Wartet den dezentralen Handshake-Takt ab, bevor das Sichtfeld kollabiert.
    """
    def __init__(self, total_frames=144):
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        
        self.width, self.height, self.depth = 320, 180, 128
        self.invariant_limit = 156
        self.FEYNMAN_LIMIT = 137  # 137 Takte Belichtungszeit pro Manifestationsframe
        self.SCALE = 1000
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.sieve = PTRCGeometrySieve(cx=self.width // 2, cy=self.height // 2, cz=self.depth // 2, v_scale=14)
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def generate_deterministic_video_sequence(self):
        print(f"[ PIPELINE ] Starte segmentierte Ganzzahl-Kompilierung...")
        self.total_generation_start = time.perf_counter()
        target_quadrance, sieve_tolerance = 196, 12

        for frame_idx in range(self.frames_limit):
            frame_start = time.perf_counter()
            frame_buffer = np.zeros((self.stereo_engine.height, self.stereo_engine.width, 3), dtype=np.uint8)
            
            # --- DEZENTRALE 137-TAKT BELICHTUNGSTIEFE ---
            for _ in range(self.FEYNMAN_LIMIT):
                self.clock_engine.evolve_clock_one_takt()
            
            # Abruf der absolut unbeweglichen Gitterpunkte
            kristall_zentren = self.sieve.generate_monolith_nodes(frame_idx)

            # --- KOLLAPS INS SICHTBARE LICHT ---
            for kx_obj, ky_obj, kz_obj in kristall_zentren:
                adjusted_z = 1 if (kz_obj % self.depth) <= 0 else (kz_obj % self.depth)
                denom = ((adjusted_z * self.SCALE) // 1414) + self.invariant_limit
                
                # Pi-Sieve-Abtastung für eine lückenlose Außenkontur-Hülle
                for dx in range(-16, 17):
                    for dy in range(-16, 17):
                        if abs((dx * dx) + (dy * dy) - target_quadrance) <= sieve_tolerance:
                            p_x = ((int(kx_obj - (self.width // 2) + dx) * 8) * self.SCALE) // denom
                            p_y = ((int(ky_obj - (self.height // 2) + dy) * 8) * self.SCALE) // denom
                            
                            out_x = (p_x + self.stereo_engine.width // 2) % self.stereo_engine.width
                            out_y = (p_y + self.stereo_engine.height // 2) % self.stereo_engine.height
                            
                            depth_glow = max(40, 255 - ((adjusted_z * 200) // self.depth))
                            frame_buffer[out_y, out_x] = [255, int(depth_glow // 2), 0]
            
            cv2.imwrite(os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png"), frame_buffer)
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Frame {frame_idx:03d}/{self.frames_limit} | Taktzeit: {(time.perf_counter() - frame_start)*1000:.2f} ms")

        self.total_generation_end = time.perf_counter()

    def compile_lossless_output_video(self):
        """Bündelt die Cache-Inhalte lückenlos als MP4-Video."""
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.png")
        target_video = os.path.join(script_dir, "ptrc_hologram_output.mp4")
        
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "1", "-preset", "slow", "-pix_fmt", "yuv420p", target_video
        ]
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            print(f"    + [ SUCCESS ] Statisches Monolith-Video exportiert: '{os.path.basename(target_video)}'")
            for frame_idx in range(self.frames_limit):
                p = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
                if os.path.exists(p): os.remove(p)
            os.rmdir(self.output_directory)
            return 1
        except Exception:
            print("    ! [ SYSTEM NOTICE ] Fehler bei der FFMPEG-Kompilierung.")
            return 0

if __name__ == "__main__":
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    pipeline.generate_deterministic_video_sequence()
    status = pipeline.compile_lossless_output_video()
    print(f" -> [ VALIDATION ] Pipeline erfolgreich beendet. Status: {status}")
