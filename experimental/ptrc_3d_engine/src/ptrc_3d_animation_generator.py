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
"""
pTRC Framework - Static Monolith Geometric Structures
Operational Domain: Pure Discrete Memory Chains (\mathbb{Z}^3) for zero-space formclosure.
"""

class PTRCMonolithStructures:
    """
    Stellt die unbeweglichen Raumgitter-Koordinaten für die Kugel- und
    Pyramiden-Formationen aus lückenlosen 144-seitigen Raumkristallen bereit.
    """
    def __init__(self, cx, cy, cz, v_scale=16):
        self.cx = int(cx)
        self.cy = int(cy)
        self.cz = int(cz)
        self.v_scale = int(v_scale)

    def get_static_centers(self, frame_idx):
        """
        Gibt die absolut ruhenden Kristallzentren basierend auf dem Frame-Index zurück.
        Keine kontinuierlichen Drifts oder Fließkomma-Verschiebungen.
        """
        kristall_zentren = []
        
        # Frames 0-71: Die unbewegliche Wirminghaus-Kugel
        if frame_idx < 72:
            fcc_sphere = [
                (0, 0, 0),
                (2, 2, 0), (-2, 2, 0), (2, -2, 0), (-2, -2, 0),
                (2, 0, 2), (2, 0, -2), (-2, 0, 2), (-2, 0, -2),
                (0, 2, 2), (0, 2, -2), (0, -2, 2), (0, -2, -2)
            ]
            for k_x, k_y, k_z in fcc_sphere:
                kx = self.cx + (k_x * self.v_scale)
                ky = self.cy + (k_y * self.v_scale)
                kz = self.cz + (k_z * self.v_scale)
                kristall_zentren.append((kx, ky, kz))
                
        # Frames 72-143: Die raumzentrierte, statische Pyramide
        else:
            pyramid_nodes = [
                # Basis (Z = -2)
                (-2, 2, -2), (2, 2, -2), (2, -2, -2), (-2, -2, -2),
                # Mitte (Z = 0)
                (-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0),
                # Absolute Spitze (Z = 2)
                (0, 0, 2)
            ]
            for k_x, k_y, k_z in pyramid_nodes:
                kx = self.cx + (k_x * self.v_scale)
                ky = self.cy + (k_y * self.v_scale) + 12  # Viewport-Zentrierung
                kz = self.cz + (k_z * self.v_scale)
                kristall_zentren.append((kx, ky, kz))
                
        return kristall_zentren

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
import platform
import numpy as np
import cv2

# Namespace-Resolver für die lokale Repository-Struktur
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
    from ptrc_monolith_structures import PTRCMonolithStructures
except ImportError:
    from src.ptrc_3d_stereo_engine import PTRC3DStereoEngine
    from src.ptrc_clock_core import PTRCModularClockEngine
    from src.ptrc_monolith_structures import PTRCMonolithStructures

class PTRC3DAnimationPipeline:
    def __init__(self, total_frames=144):
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        
        self.width, self.height, self.depth = 320, 180, 128
        self.invariant_limit = 156
        self.FEYNMAN_LIMIT = 137  # 137 Belichtungs-Takte für dezentrale Handshakes
        self.SCALE = 1000
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.structures = PTRCMonolithStructures(cx=self.width // 2, cy=self.height // 2, cz=self.depth // 2, v_scale=16)
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def generate_deterministic_video_sequence(self):
        print(f"[ PIPELINE ] Starte segmentierte Ganzzahl-Kompilierung...")
        self.total_generation_start = time.perf_counter()
        target_quadrance, sieve_tolerance = 196, 14

        for frame_idx in range(self.frames_limit):
            frame_start = time.perf_counter()
            frame_buffer = np.zeros((self.stereo_engine.height, self.stereo_engine.width, 3), dtype=np.uint8)
            
            # --- 137 TAKTE BACKGROUND-HANDSHAKE ---
            for _ in range(self.FEYNMAN_LIMIT):
                self.clock_engine.evolve_clock_one_takt()
            
            # Hole ruhende Gitter-Zentren aus dem neuen Struktur-Modul
            kristall_zentren = self.structures.get_static_centers(frame_idx)

            # --- TRANSPONIERUNG INS SICHTBARE LICHT ---
            for kx_obj, ky_obj, kz_obj in kristall_zentren:
                adjusted_z = 1 if (kz_obj % self.depth) <= 0 else (kz_obj % self.depth)
                denom = ((adjusted_z * self.SCALE) // 1414) + self.invariant_limit
                
                # Lokales Pi-Sieve für die Außenkontur des 144-Seiters
                for dx in range(-16, 17):
                    for dy in range(-16, 17):
                        if abs((dx * dx) + (dy * dy) - target_quadrance) <= sieve_tolerance:
                            p_x = ((int(kx_obj - (self.width // 2) + dx) * 8) * self.SCALE) // denom
                            p_y = ((int(ky_obj - (self.height // 2) + dy) * 8) * self.SCALE) // denom
                            
                            out_x = (p_x + self.stereo_engine.width // 2) % self.stereo_engine.width
                            out_y = (p_y + self.stereo_engine.height // 2) % self.stereo_engine.height
                            
                            depth_glow = max(50, 255 - ((adjusted_z * 180) // self.depth))
                            frame_buffer[out_y, out_x] = [255, int(depth_glow // 2), 0]
            
            cv2.imwrite(os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png"), frame_buffer)
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Frame {frame_idx:03d}/{self.frames_limit} | Taktzeit: {(time.perf_counter() - frame_start)*1000:.2f} ms")

        self.total_generation_end = time.perf_counter()

    def compile_lossless_output_video(self):
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.png")
        target_video = os.path.join(script_dir, "ptrc_wirminghaus_monolith.mp4")
        
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "1", "-preset", "slow", "-pix_fmt", "yuv420p", target_video
        ]
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            print(f"    + [ SUCCESS ] Video kompiliert: '{os.path.basename(target_video)}'")
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
    pipeline.compile_lossless_output_video()
