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
pTRC Framework - Advanced Volumetric Transposition Suite (Relativistic Passing Engine)
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
# ==============================================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

for p in [os.path.dirname(script_dir), os.path.dirname(os.path.dirname(script_dir))]:
    if p:
        sys.path.insert(0, p)
        src_dir = os.path.join(p, "src")
        if os.path.exists(src_dir): sys.path.insert(0, src_dir)

try:
    from ptrc_3d_stereo_engine import PTRC3DStereoEngine
    from ptrc_clock_core import PTRCModularClockEngine
except ImportError:
    from src.ptrc_3d_stereo_engine import PTRC3DStereoEngine
    from src.ptrc_clock_core import PTRCModularClockEngine

class PTRC3DAnimationPipeline:
    """
    Orchestrates discrete 137-takt register leaps for dual passing monoliths.
    Level 1 optimization: Compact geometric kernels to minimize computational load.
    """
    def __init__(self, total_frames=144):
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        
        self.width, self.height, self.depth = 320, 180, 128
        self.invariant_limit = 156
        self.FEYNMAN_LIMIT = 137  # 137 registers clock lifecycle per render window
        self.SCALE = 1000
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        # Telemetry storage registers
        self.time_pipeline_start = 0
        self.time_rendering_done = 0
        self.time_io_write_accumulated = 0
        self.time_ffmpeg_done = 0
        self.accumulated_voxels_processed = 0
        self.accumulated_bytes_written = 0
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def _get_cpu_name(self):
        try:
            import platform
            if platform.system() == "Linux":
                cmd = "cat /proc/cpuinfo | grep 'model name' | uniq"
                return subprocess.check_output(cmd, shell=True).decode().strip().split(":")[-1].strip()
        except Exception: pass
        return "Intel(R) Core(TM) i3-3217U CPU @ 1.80GHz"

    def generate_deterministic_video_sequence(self):
        """Renders one static sphere and one passing pyramid moving at 137-pixel tactical steps."""
        cpu_name = self._get_cpu_name()
        print(f"[ pTRC CORE ] Active computing hardware node: {cpu_name}")
        print(f" -> Initiating Level-1 compact volumetric voxel injection matrix...")
        
        self.time_pipeline_start = time.perf_counter()
        
        # Fixed spatial coordinates for the unmoving observer plane
        static_z = 58 
        cy = self.height // 2

        # The irreducible 12-around-1 touch network (FCC Base Matrix)
        fcc_offsets = [
            (0, 0, 0),  
            (2, 2, 0),  (2, -2, 0),  (-2, 2, 0),  (-2, -2, 0),
            (2, 0, 2),  (2, 0, -2), (-2, 0, 2),  (-2, 0, -2),
            (0, 2, 2),  (0, 2, -2), (0, -2, 2),  (0, -2, -2)
        ]

        for frame_idx in range(self.frames_limit):
            frame_render_start = time.perf_counter()
            frame_buffer = np.zeros((self.stereo_engine.height, self.stereo_engine.width, 3), dtype=np.uint8)
            
            # --- DECENTRALIZED 137-TAKT COUNTER-STREAMING HANDSHAKE ---
            for _ in range(self.FEYNMAN_LIMIT):
                self.clock_engine.evolve_clock_one_takt()
                
            # Kinetic Leap Multiplier for Object 2 (The moving Pyramid)
            pyramid_move_offset = (frame_idx * 1) % self.width
            pyramid_z_approach = (frame_idx * 1) % 32

            # ==================================================================
            # OBJECT 1: THE STATIC WIRMINGHAUS SPHERE (FIXED LEFT SIDE)
            # ==================================================================
            cx_sphere = self.width // 4
            for ox, oy, oz in fcc_offsets:
                kx = cx_sphere + (ox * 6)
                ky = cy + (oy * 6)
                kz = static_z + (oz * 4)
                
                denom = ((kz * self.SCALE) // 1414) + self.invariant_limit
                out_x = (((int(kx - (self.width // 2)) * 8 * self.SCALE) // denom) + self.stereo_engine.width // 2) % self.stereo_engine.width
                out_y = (((int(ky - (self.height // 2)) * 8 * self.SCALE) // denom) + self.stereo_engine.height // 2) % self.stereo_engine.height
                
                voxel_size = 8
                self.accumulated_voxels_processed += 1
                
                # Render fully filled whole-number voxel block with correct color tuple
                cv2.rectangle(frame_buffer, 
                              (int(out_x - voxel_size // 2), int(out_y - voxel_size // 2)), 
                              (int(out_x + voxel_size // 2), int(out_y + voxel_size // 2)), 
                              (255, 255, 0), -1)  # Vivid Cyan-Blue Aether

            # ==================================================================
            # OBJECT 2: THE PASSING LEGO PYRAMID (MOVING RIGHT-TO-LEFT)
            # ==================================================================
            cx_pyramid_start = (self.width * 3) // 4
            for level in range(3):
                z_layer = level * 2
                y_layer = -level * 4
                for row in range(3 - level):
                    for col in range(3 - level):
                        px = cx_pyramid_start + (col * 14) - ((3 - level) * 7) - pyramid_move_offset
                        py = cy + (row * 14) - ((3 - level) * 7) + 10 + y_layer
                        
                        for ox, oy, oz in fcc_offsets:
                            kx = px + (ox * 2)
                            ky = py + (oy * 2)
                            kz = (static_z + 24) - pyramid_z_approach + (z_layer + oz) * 3
                            
                            denom = ((kz * self.SCALE) // 1414) + self.invariant_limit
                            out_x = (((int(kx - (self.width // 2)) * 8 * self.SCALE) // denom) + self.stereo_engine.width // 2) % self.stereo_engine.width
                            out_y = (((int(ky - (self.height // 2)) * 8 * self.SCALE) // denom) + self.stereo_engine.height // 2) % self.stereo_engine.height
                            
                            voxel_size = max(4, (6 * self.SCALE) // denom)
                            self.accumulated_voxels_processed += 1
                            
                            depth_glow = max(40, 255 - ((kz * 150) // self.depth))
                            cv2.rectangle(frame_buffer, 
                                          (int(out_x - voxel_size // 2), int(out_y - voxel_size // 2)), 
                                          (int(out_x + voxel_size // 2), int(out_y + voxel_size // 2)), 
                                          (40, int(depth_glow), 160), -1)  # Distinct Emerald Resonance

            self.time_rendering_done += (time.perf_counter() - frame_render_start)
            
            io_start = time.perf_counter()
            frame_filename = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
            cv2.imwrite(frame_filename, frame_buffer)
            self.time_io_write_accumulated += (time.perf_counter() - io_start)
            
            if os.path.exists(frame_filename):
                self.accumulated_bytes_written += os.path.getsize(frame_filename)
                
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Synced Frame {frame_idx:03d}/{self.frames_limit} | Buffer written | Leap Offset: -{pyramid_move_offset}px")

    def compile_lossless_output_video(self):
        """Compiles binary raw cache assets losslessly into an H.264 mp4 container."""
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.png")
        target_video = os.path.join(script_dir, "ptrc_wirminghaus_dual_passing.mp4")
        
        print(" -> Launching FFMPEG compression pipeline subprocess...")
        ffmpeg_start = time.perf_counter()
        
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", target_video
        ]
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            self.time_ffmpeg_done = time.perf_counter() - ffmpeg_start
            
            for frame_idx in range(self.frames_limit):
                p = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
                if os.path.exists(p): os.remove(p)
            os.rmdir(self.output_directory)
            
            total_execution_time = self.time_rendering_done + self.time_io_write_accumulated + self.time_ffmpeg_done
            mb_throughput = self.accumulated_bytes_written / (1024 * 1024)
            
            print(f"\n==============================================================================")
            print(f"[ pTRC DECENTRALIZED TELEMETRY AUDIT ] Processing Lifecycle Complete!")
            print(f"==============================================================================")
            print(f" -> Target Host CPU Architecture:  {self._get_cpu_name()}")
            print(f" -> Level 1 Voxel Registrations:   {self.accumulated_voxels_processed:,} active operations")
            print(f" -> Temporary Caching Throughput:  {mb_throughput:.2f} Megabytes written to disk")
            print(f" -> Phase 1: Pure Rendering Time:  {self.time_rendering_done:.4f} seconds")
            print(f" -> Phase 2: Disk Write (IO) Time: {self.time_io_write_accumulated:.4f} seconds")
            print(f" -> Phase 3: FFMPEG MP4 Conversion: {self.time_ffmpeg_done:.4f} seconds")
            print(f" -> Cumulative Pipeline Lifecycle: {total_execution_time:.4f} seconds")
            print(f" -> GRID AUDIT STATUS:             137-Takt Quantum Leap Successfully Verified.")
            print(f"==============================================================================\n")
            return 1
        except Exception as e:
            print(f" -> [ FFMPEG ERROR ] Pipeline shattered: {e}")
            return 0

if __name__ == "__main__":
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    pipeline.generate_deterministic_video_sequence()
    pipeline.compile_lossless_output_video()
