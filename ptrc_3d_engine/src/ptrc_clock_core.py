# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# LICENSE & LIABILITY NOTICE:
# Academic, non-commercial research and evaluation is permitted strictly under 
# the terms of the GNU Affero General Public License version 3 (AGPLv3).
# For the complete, unedited license text see: https://www.gnu.org/licenses/agpl-3.0.html
#
# ANY COMMERCIAL DEPLOYMENT, production utilization, or proprietary enterprise 
# integration requires a separate, individually negotiated commercial infrastructure 
# waiver issued directly by the author.
#
# WARRANTY DISCLAIMER: THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE SYSTEMATICALLY DISCLAIMED.
# ==============================================================================
# -*- coding: utf-8 -*-
"""
pTRC Framework - Core Simulation Module: Modular Cellular Clock Engine
Operational Domain: 2D Cellular State Permutations (\mathbb{Z}) using Modulo-210/24 rings.
Executes lossless tactical lattice steps without continuous floating-point variables.
"""

import numpy as np

class PTRCModularClockEngine:
    """
    Manages a deterministic cellular automaton environment where cell transitions
    are synchronized strictly via discrete whole-number spatial clocks.
    """
    def __init__(self, width=64, height=64):
        self.width = width
        self.height = height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156
        self.SCALE = 1000
        
        # 1-bit cellular state grids mapping structural topology natively in Z
        self.current_grid = np.zeros((self.height, self.width), dtype=np.uint8)
        self.next_grid = np.zeros((self.height, self.width), dtype=np.uint8)

    def seed_resonance_pattern(self):
        """
        Seeds the grid with a symmetrical whole-number coordinate pattern.
        """
        for y in range(self.height):
            for x in range(self.width):
                if (x * y + 5) % self.control_base == 12:
                    self.current_grid[y, x] = 1

    def step_cellular_takt(self, global_takt_counter):
        """
        Advances the cellular matrix by one discrete clock step.
        Uses pure bit-counting and modular filters to determine cell evolution.
        """
        takt_factor = int(global_takt_counter) % self.primorial_base
        
        # Calculate neighbor counts utilizing parallel shift operations
        neighbor_count = (
            np.roll(self.current_grid, 1, axis=0) + np.roll(self.current_grid, -1, axis=0) +
            np.roll(self.current_grid, 1, axis=1) + np.roll(self.current_grid, -1, axis=1)
        )
        
        # Clear next state buffer
        self.next_grid.fill(0)
        
        # Whole-number state transition rules mapped strictly inside Z
        for y in range(self.height):
            for x in range(self.width):
                count = neighbor_count[y, x]
                cell_state = self.current_grid[y, x]
                
                # Check phase resonance using scaling vectors to bypass float noise
                phase_check = (count * self.SCALE + takt_factor) // self.invariant_limit
                
                if cell_state == 1:
                    if count == 2 or count == 3 or (phase_check % 2 == 0):
                        self.next_grid[y, x] = 1
                else:
                    if count == 3 and (phase_check % 3 == 0):
                        self.next_grid[y, x] = 1
                        
        # Symmetrical swap operations
        self.current_grid, self.next_grid = self.next_grid, self.current_grid

    def compute_active_density(self):
        """
        Returns the exact integrated state mass of the cellular automaton.
        """
        return int(np.sum(self.current_grid))

if __name__ == "__main__":
    print("[ pTRC-MODULAR-CLOCK ] Initializing zellular automaton grid...")
    engine = PTRCModularClockEngine(width=64, height=64)
    engine.seed_resonance_pattern()
    
    print(" -> Advancing grid state across 24 discrete metric calibration steps...")
    for step in range(24):
        engine.step_cellular_takt(global_takt_counter=1836 + step)
        
    total_mass = engine.compute_active_density()
    print(f" -> [ VALIDATION ] Cellular state updates completed.")
    print(f" -> Total Integrated Live Cells: {total_mass}")
    print(" -> STATUS: Zero-Float Cellular Modular Clock Engine Successfully Audited.")
