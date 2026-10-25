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
pTRC Framework - Core Graphics: Unified 3D Game Viewport & Rasterizer Engine
Operational Domain: Symmetrical Integer Translation Matrices (\mathbb{Z}^3).
Converts the abstract modulo interference matrix into a human-readable 2D
monitor projection. Implements a whole-number Z-buffer and physical fluid boundaries.
"""

import os
import sys
import subprocess
import numpy as np

class PTRCGameWorld:
    """ Defines the physical game space: walls, pyramid, and flowing fluid. """
    def __init__(self, size=64):
        self.size = size
        # 3D spatial grid: 0 = vacuum, 1 = pipe wall, 2 = pyramid, 3 = active fluid
        self.voxels = np.zeros((size, size, size), dtype=np.uint8)
        self._build_world_geometry()

    def _build_world_geometry(self):
        mid = self.size // 2
        
        # 1. BUILDING THE PIPE / RIVERBED (Physical boundary along the X-axis)
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    dy = y - mid
                    dz = z - mid
                    if (dy*dy + dz*dz) >= 256 and (dy*dy + dz*dz) <= 289:
                        self.voxels[x, y, z] = 1

        # 2. BUILDING THE MASSIVE PYRAMID (Anchored within the riverbed using space crystals)
        for h in range(12):
            span = 12 - h
            for dy in range(-span, span + 1):
                for dx in range(-span, span + 1):
                    px = mid + dx - 10
                    py = mid + dy
                    pz = (mid - 12) + h
                    if 0 <= px < self.size and 0 <= py < self.size and 0 <= pz < self.size:
                        if self.voxels[px, py, pz] == 0:
                            self.voxels[px, py, pz] = 2

    def update_fluid_flow(self, frame_idx):
        """ Clocks the fluid resonance strictly within the pipe boundaries. """
        mid = self.size // 2
        
        # Fluid injection at the pipe start (x = 0) in the center of the riverbed
        takt_step = frame_idx % 4
        if takt_step == 0:
            self.voxels[2:5, mid-3:mid+4, mid-3:mid+4] = 3

        # Conservation of momentum via index shift along the pipe longitudinal axis (X-axis)
        fluid_mask = (self.voxels == 3)
        if np.any(fluid_mask):
            moved_fluid = np.roll(fluid_mask, shift=1, axis=0)
            allowed_move = moved_fluid & (self.voxels != 1) & (self.voxels != 2)
            self.voxels[fluid_mask] = 0
            self.voxels[allowed_move] = 3

class PTRCTrueCrystalSieve:
    def __init__(self, v_scale=9):
        self.v_scale = int(v_scale)
        self.crystal_axes = self._build_144_facet_vectors()

    def _build_144_facet_vectors(self):
        flat_nodes = [
            2, 1, 0,  2, -1, 0, -2,  1, 0, -2, -1, 0,
            0, 2, 1,  0,  2, -1,  0, -2, 1,  0, -2, -1,
            1, 0, 2, -1,  0,  2,  1,  0, -2, -1,  0, -2
        ]
        base_tensors = np.array(flat_nodes, dtype=np.int32).reshape(12, 3)
        axes = []
        for node in base_tensors:
            for factor in range(1, 13):
                axes.append(node * factor)
        return np.array(axes, dtype=np.int32)

class PTRCGameViewport:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.SCALE = 1000

    def render_to_screen(self, world_instance, frame_idx):
        """ Projects the 3D space with high-contrast color mapping for human vision. """
        frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        z_buffer = np.full((self.height, self.width), fill_value=999999, dtype=np.int32)
        
        cx, cy = self.width // 2, self.height // 2
        w_size = world_instance.size
        w_mid = w_size // 2

        # Camera rotation remains anchored to the control clock counter
        angle_takt = int((frame_idx % 24) - 12)

        for x in range(w_size):
            for y in range(w_size):
                for z in range(w_size):
                    voxel_type = world_instance.voxels[x, y, z]
                    if voxel_type == 0:
                        continue

                    # STRICT NO-SCALE MAPPING (1:1 Planck Steps)
                    rx = (x - w_mid)
                    ry = (y - w_mid)
                    rz = (z - w_mid)

                    # RIGID MATRIX INTERCEPT
                    rotated_x = rx + (ry * angle_takt) // 24
                    rotated_y = ry - (rx * angle_takt) // 24
                    rotated_z = rz + 120

                    if rotated_z <= 10:
                        continue

                    # Perspective whole-number division
                    out_x = (((rotated_x * 700 * self.SCALE) // ((rotated_z * self.SCALE) // 1414)) + cx) % self.width
                    out_y = (((rotated_y * 700 * self.SCALE) // ((rotated_z * self.SCALE) // 1414)) + cy) % self.height

                    if rotated_z < z_buffer[out_y, out_x]:
                        z_buffer[out_y, out_x] = rotated_z

                        # HIGH-CONTRAST COLOR ASSIGNMENT FOR OPTIMIZED VISUAL DIFFERENTIATION
                        if voxel_type == 1:
                            # Bound walls: Dense Industrial Metallic Gray
                            r, g, b = 140, 145, 160     
                        elif voxel_type == 2:
                            # Monolithic Pyramid: Pure Radiant Gold (Invariant Core)
                            r, g, b = 255, 200, 0      
                        else:
                            # Flowing Fluid: Ultra-Luminous Electric Cyan (Hydrodynamics)
                            r, g, b = 0, 255, 220      

                        # CRYSTAL-STRUCTURE COMPOSITION (Formclosure pixel arrangement)
                        crystal_structure = [
                            (0, 0), (0, -1), (0, 1), (-1, 0), (1, 0),
                            (0, -2), (0, 2), (-2, 0), (2, 0),
                            (-1, -1), (1, -1), (-1, 1), (1, 1),
                            (-2, -1), (2, -1), (-2, 1), (2, 1),
                            (-1, -2), (1, -2), (-1, 2), (1, 2)
                        ]
                        
                        for ox, oy in crystal_structure:
                            px = (out_x + ox) % self.width
                            py = (out_y + oy) % self.height
                            
                            # Fixed-point shading logic mapping depth to brightness
                            shading_factor = max(50, 255 - (rotated_z * 2))
                            
                            if ox == 0 and oy == 0:
                                # Core crystal node (Full emission)
                                frame_buffer[py, px] = [
                                    (r * shading_factor) // 255,
                                    (g * shading_factor) // 255,
                                    (b * shading_factor) // 255
                                ]
                            else:
                                # Phase-shifted secondary facets (Emphasizes 3D volume depths)
                                frame_buffer[py, px] = [
                                    (r * shading_factor) // 380,
                                    (g * shading_factor) // 380,
                                    (b * shading_factor) // 380
                                ]

        return frame_buffer

if __name__ == "__main__":
    print("[pTRC-VIEWPORT] Switching graphics pipeline to 2D monitor projection (Demo Mode)...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_dir, "Stabilized_Cache")
    os.makedirs(cache_dir, exist_ok=True)

    android_download_dir = "/storage/emulated/0/Download"
    video_output_dir = android_download_dir if os.path.exists(android_download_dir) else base_dir
    os.makedirs(video_output_dir, exist_ok=True)

    total_frames = 144
    world = PTRCGameWorld(size=64)
    viewport = PTRCGameViewport(width=1920, height=1080)

    for frame in range(total_frames):
        world.update_fluid_flow(frame)
        frame_matrix = viewport.render_to_screen(world, frame)
        
        filename = os.path.join(cache_dir, f"game_frame_{frame:04d}.ppm")
        header = f"P6\n{viewport.width} {viewport.height}\n255\n".encode('ascii')
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(frame_matrix.tobytes())

        if frame % 24 == 0 or frame == total_frames - 1:
            print(f" + Viewport frame {frame:03d}/{total_frames} z-buffered and rasterized.")

    input_pattern = os.path.join(cache_dir, "game_frame_%04d.ppm")
    video_target_path = os.path.join(video_output_dir, "ptrc_game_simulation_v001.mp4")

    version = 1
    while os.path.exists(video_target_path):
        video_target_path = os.path.join(video_output_dir, f"ptrc_game_simulation_v{version:03d}.mp4")
        version += 1

    print("\n -> Compiling plastic 2D monitor stream via FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
        "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", video_target_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        print(f"\n[ SYSTEM CHECK OK ] The unified game video has been successfully secured!")
        print(f" -> File: {video_target_path}")

        for frame in range(total_frames):
            ppm_file = os.path.join(cache_dir, f"game_frame_{frame:04d}.ppm")
            if os.path.exists(ppm_file): os.remove(ppm_file)
        os.rmdir(cache_dir)
        print(" + Viewport cache atomically cleared. Invariance fully preserved.")
        sys.exit(0)

    except Exception as e:
        print(f"\n[ WARNING ] FFmpeg video compilation failed: {e}")
        sys.exit(1)
