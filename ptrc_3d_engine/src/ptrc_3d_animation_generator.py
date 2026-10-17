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
pTRC Infinite Scale Core - Modular Metric Clock & Sieve Synchronization
100% Integer Z-Ontology | Module: Crystalline Flow Dynamics
Optimized: Fully open multi-axis crystal channels allowing node-level 1-bit interference filtering.
"""

import numpy as np

class PTRCModularClockEngine:
    def __init__(self, width=160, height=90, depth=64):
        self.width = width
        self.height = height
        self.depth = depth
        
        # The incorruptible p-adic modulo clock system
        self.PRIMORIAL_RING = 210  
        self.CLOCK_24 = 24         
        self.REFRESH_TAKTE = 137   
        
        self.global_master_clock = 0
        
        # Generate 144-facet crystalline axes (The true 1-bit data pipelines)
        self.crystal_axes = self._generate_144_facet_axes()
        
        # Space initialization via open crystalline flow intersections
        self.voxels = self._build_sieved_primorial_space()

    def _generate_144_facet_axes(self):
        flat_nodes = [
            2, 1, 0,   2, -1, 0,  -2, 1, 0,  -2, -1, 0,
            0, 2, 1,   0, 2, -1,   0, -2, 1,  0, -2, -1,
            1, 0, 2,  -1, 0, 2,    1, 0, -2, -1, 0, -2
        ]
        base_nodes = np.array(flat_nodes, dtype=np.int32).reshape(12, 3)
        axes = []
        for node in base_nodes:
            for factor in range(1, 13):
                axes.append(node * factor)
        return np.array(axes, dtype=np.int32)

    # ==========================================================================
    # !!! TARGET ZONE: PURE 1-BIT CRYSTAL INTERFERENCE MATRIX !!!
    # MARKER: PTRC_OPEN_CRYSTAL_INTERSECTION_2026
    # ==========================================================================
    def _build_sieved_primorial_space(self):
        """
        Errichtet das Interferenzfeld über die 144 offenen Achsen des Kristalls.
        Die Filterung der Flussbahnen geschieht deterministisch auf Knotenebene.
        Jeder Strahl ist starr 1 Bit breit.
        """
        space = np.zeros((self.depth, self.height, self.width), dtype=np.uint8)
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        
        # Die 8 erlaubten Hauptstrahlen der abelschen Symmetriegruppe modulo 24
        allowed_24_rays = {1, 5, 7, 11, 13, 17, 19, 23}
        
        # Alle 144 Achsen fließen als offene 1-Bit-Datenbahnen durch das Zentrum
        for axis in self.crystal_axes:
            ax, ay, az = axis[0], axis[1], axis[2]
            
            # Ein Strahl breitet sich entlang seiner ganzzahligen Metrik aus
            for step in range(-80, 80):
                x = cx + (ax * step) // 12
                y = cy + (ay * step) // 12
                z = cz + (az * step) // 12
                
                # Boundary Safety Check
                if 0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.depth:
                    # Berechne die Quadrance direkt bezogen auf das Kristallzentrum
                    quadrance = (x - cx)**2 + (y - cy)**2 + (z - cz)**2
                    
                    # 1. DAS MODULO-210 UHRSIEB
                    residuum_210 = quadrance % self.PRIMORIAL_RING
                    
                    if residuum_210 <= 156:  # Invarianter Grenzknoten
                        # 2. DER DISKRETE INTERFERENZ-TAKTERHALT AM KNOTENPUNKT
                        takt_check = (x * y + z) % self.CLOCK_24
                        
                        # Hier entscheidet sich am Kreuzungspunkt, ob Daten fließen!
                        if takt_check in allowed_24_rays:
                            space[z, y, x] = 2  # Aktiver Resonanz-Knoten (Datenübertragung aktiv)
                        elif takt_check == 12:
                            space[z, y, x] = 1  # Invarianter Massen-Knoten
                            
        return space
    # ==========================================================================
    # !!! END OF TARGET ZONE !!!
    # ==============================================================================

    def evolve_clock_one_takt(self):
        self.global_master_clock += 1
        current_hour = self.global_master_clock % self.CLOCK_24
        axis_to_roll = current_hour % 3
        shift_amount = 1 if (current_hour < 12) else -1
        self.voxels = np.roll(self.voxels, shift_amount, axis=axis_to_roll)

    def compute_integrated_density(self):
        return int(np.sum(self.voxels))

if __name__ == "__main__":
    core_engine = PTRCModularClockEngine()
    total_lattice_load = core_engine.compute_integrated_density()
    print(f"[ TEST ] Integrierte Voxel-Masse: {total_lattice_load}")
