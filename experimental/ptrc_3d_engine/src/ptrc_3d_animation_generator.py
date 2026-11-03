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
pTRC Framework - Unified Master Space & Resonance Engine
Operational Domain: Pure Integer Viewports (Z^3). Zero Float Pollution.
Description: Universal look-up processor merging 144-facet vector equilibrium hulls,
the branchless Plichta crossed-mirror engine, and -1 phase-inversion data delegation.
File Name: ptrc_3d_animation_generator.py
"""

import os
import sys
import shutil
import subprocess
import time
import numpy as np

class PTRCTrueCrystalSieve:
    def __init__(self, v_scale=9):
        self.v_scale = int(v_scale)  # Theoretical baseline limit radius = 9
        self.crystal_axes = self._build_144_facet_vectors()

    def _build_144_facet_vectors(self):
        """Generates 144 discrete directional axes from modular symmetry conditions."""
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

class PTRCUniversalGraphicsProcessor:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.invariant_limit = 156
        self.SCALE = 1000

    def project_observer_retina(self, x, y, z, iod=55):
        """Perspective 3D whole-number projection without analog leakage."""
        scaled_depth = (z * self.SCALE) // 1414
        denom = scaled_depth + self.invariant_limit
        if denom <= 0:
            denom = 1
            
        proj_x_left = ((x - iod) * 45 * self.SCALE) // denom
        proj_x_right = ((x + iod) * 45 * self.SCALE) // denom
        proj_y = (y * 45 * self.SCALE) // denom
        
        return (proj_x_left + self.width // 2) % self.width, \
               (proj_x_right + self.width // 2) % self.width, \
               (proj_y + self.height // 2) % self.height

class PTRCUniversalOrchestrator:
    def __init__(self, total_frames=240):
        self.width = 1920
        self.height = 1080
        self.frames_limit = total_frames
        self.processor = PTRCUniversalGraphicsProcessor(width=self.width, height=self.height)
        self.sieve = PTRCTrueCrystalSieve(v_scale=9)
        
        self.PRIMORIAL_MOD = 210
        self.CLOCK_MOD = 24
        self.REFRESH_TAKTE = 137  # Structural 1/137 lightspeed collapse interval
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.tmp_dir = os.path.join(self.base_dir, "ptrc_rendering_tmp")
        self.output_video = os.path.join(self.base_dir, "ptrc_universal_cosmology_master.mp4")

    def run_multi_domain_pipeline(self):
        print(f"[ pTRC MASTER ENGINE ] Commencing 1080p structural volume synthesis...")
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.makedirs(self.tmp_dir)

        num_agents = 300
        base_indices = np.arange(1, num_agents + 1, dtype=np.int64)
        
        # --- FIBONACCI TARGET FORMATION MATRIX IN Z ---
        step_mod = (base_indices * 5) % self.CLOCK_MOD
        radius = (base_indices * 3) // 2
        dir_x = np.where(step_mod < 6, 1, np.where(step_mod < 12, 0, np.where(step_mod < 18, -1, 0)))
        dir_y = np.where(step_mod < 6, 0, np.where(step_mod < 12, 1, np.where(step_mod < 18, 0, -1)))
        spiral_twist = (base_indices * 8) % self.CLOCK_MOD
        targets_x = dir_x * radius + (np.where(spiral_twist % 2 == 0, 1, -1) * (base_indices // 4))
        targets_y = dir_y * radius + (np.where(spiral_twist % 3 == 0, 1, -1) * (base_indices // 4))
        
        agents = np.zeros((num_agents, 3), dtype=np.int64)
        agents[:, 2] = 60 + ((base_indices * 80) // num_agents)
        
        # --- VARIABLE ATOM / OBSERVER CONFIGURATION LAYER ---
        # Mono-Signal (Base DNA) separated from cosmetic mutations via (-1) phase transposition
        base_dna_mono_signal = 1836
        cosmetic_mutation_hair_color = 5  # Variable parameter to alter phenotypic output
        
        expansion_seed = ((base_indices * base_dna_mono_signal) ^ cosmetic_mutation_hair_color) % 256
        max_fill_x = np.where(base_indices % 4 == 0, 1, np.where(base_indices % 4 == 1, -1, np.where(base_indices % 4 == 2, 1, -1))) * (expansion_seed * 3)
        max_fill_y = np.where(base_indices % 4 == 0, 1, np.where(base_indices % 4 == 1, 1, np.where(base_indices % 4 == 2, -1, -1))) * (expansion_seed * 2)

        # Invariant indices for saving exactly 5 evenly spaced control frames
        control_frames = set(np.linspace(0, self.frames_limit - 1, 5, dtype=int))

        for step in range(self.frames_limit):
            frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            angle_takt = (step % self.CLOCK_MOD) - 12

            if step <= 80:
                progress = step * 12
                current_targets_x = (max_fill_x * progress) // 80
                current_targets_y = (max_fill_y * progress) // 80
                speed_divider = 12
            elif step <= 160:
                phase_progress = (step - 80)
                interference_x = np.where((base_indices + step) % 4 == 0, 15, -15)
                interference_y = np.where((base_indices + step) % 4 == 2, 15, -15)
                current_targets_x = max_fill_x + (((targets_x - max_fill_x) * phase_progress) // 80) + interference_x
                current_targets_y = max_fill_y + (((targets_y - max_fill_y) * phase_progress) // 80) + interference_y
                speed_divider = 10
            else:
                current_targets_x = targets_x
                current_targets_y = targets_y
                speed_divider = 6

            dx = (current_targets_x - agents[:, 0]) * self.processor.SCALE
            dy = (current_targets_y - agents[:, 1]) * self.processor.SCALE

            # --- PLICHTA CROSSED-MIRROR TRANSPOSITION (Z \ {0}) ---
            raw_dx = dx // self.processor.SCALE
            raw_dy = dy // self.processor.SCALE
            ptrc_dx = np.where(raw_dx == 0, -1, raw_dx)
            ptrc_dy = np.where(raw_dy == 0, -1, raw_dy)

            allowed_x = np.where((ptrc_dx % self.PRIMORIAL_MOD != 0) | (step % 3 == 0), 1, 0)
            allowed_y = np.where((ptrc_dy % self.PRIMORIAL_MOD != 0) | (step % 3 == 0), 1, 0)

            agents[:, 0] += np.sign(dx) * allowed_x * speed_divider
            agents[:, 1] += np.sign(dy) * allowed_y * speed_divider

            # --- CENTRAL ROTATING CRYSTAL PYRAMID ---
            pyramid_buffer = []
            if step > 160:
                pyramid_heights = np.arange(-10, 11, 2)
                for h in pyramid_heights:
                    span = 10 - abs(h)
                    for px in range(-span, span + 1, 2):
                        # Apply pure whole-number rotation onto the central monolith core
                        rx = (px * angle_takt) // 12
                        ry = (h * angle_takt) // 12
                        pyramid_buffer.append([rx, ry, 100])

            # --- RETINA VISUALIZATION LAYER (Axiom II / 137 Lightspeed Collapse) ---
            mirror_shading = 255 - ((step % self.CLOCK_MOD) * 8)
            
            # Render Agents
            xl, xr, yd = self.processor.project_observer_retina(agents[:, 0], agents[:, 1] + ((agents[:, 2] * 3) // 4), agents[:, 2])
            for i in range(num_agents):
                # Color segmentation: Coherent Mono-Signal (Gold) vs Wave Bounds (Cyan)
                color = [255, 215, 0] if (base_indices[i] % 2 == 0) else [0, 255, 240]
                for ox, oy in [(0,0), (-1,0), (1,0), (0,-1), (0,1)]: # Complete 144-facet hull fill
                    for xc in [xl[i], xr[i]]:
                        px, py = (xc + ox) % self.width, (yd[i] + oy) % self.height
                        frame_buffer[py, px] = [(color[c] * mirror_shading) // 255 for c in range(3)]

            # Render Central Core Pyramid
            for p_node in pyramid_buffer:
                x_p, y_p, z_p = p_node[0], p_node[1], p_node[2]
                xl_p, xr_p, yd_p = self.processor.project_observer_retina(x_p, y_p, z_p)
                for xc in [xl_p, xr_p]:
                    if 0 <= xc < self.width and 0 <= yd_p < self.height:
                        frame_buffer[yd_p, xc] = [218, 165, 32] # Coherent Monolith Core (Spectral Gold)

            frame_path = os.path.join(self.tmp_dir, f"frame_{step:04d}.ppm")
            with open(frame_path, "wb") as f:
                f.write(f"P6\n{self.width} {self.height}\n255\n".encode('ascii'))
                f.write(frame_buffer.tobytes())

        # --- LOSSLESS COMPRESSION & STORAGE CLEANuP ---
        print(f" -> Compiling progress stream via FFmpeg...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-f", "image2", "-framerate", "30",
            "-i", os.path.join(self.tmp_dir, "frame_%04d.ppm"),
            "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", self.output_video
        ]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"\n[ SYSTEM CHECK OK ] Master video secured at: {self.output_video}")

        # Atomic cleanup layer: deletes all cache files except the 5 evenly spaced control frames
        for step in range(self.frames_limit):
            p = os.path.join(self.tmp_dir, f"frame_{step:04d}.ppm")
            if os.path.exists(p):
                if step in control_frames:
                    # Move control frames out of the transient temp path for validation
                    shutil.move(p, os.path.join(self.base_dir, f"control_takt_frame_{step:03d}.ppm"))
                else:
                    os.remove(p)
        shutil.rmtree(self.tmp_dir)
        print(f"[ OK ] Transient cache atomically purged. 5 control frames preserved in root.")

if __name__ == "__main__":
    orchestrator = PTRCUniversalOrchestrator(total_frames=240)
    orchestrator.run_multi_domain_pipeline()
