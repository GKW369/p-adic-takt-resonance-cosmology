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
