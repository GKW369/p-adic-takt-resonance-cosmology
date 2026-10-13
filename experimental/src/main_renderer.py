# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
#
# DUAL-LICENSING NOTICE:
# Non-commercial, academic, and open-source usage is strictly governed by 
# the GNU General Public License version 3 (GPLv3). Any commercial deployment,
# integration into proprietary, closed-source codebases, or corporate utilization
# explicitly requires a separate, individually negotiated commercial license.
# ==============================================================================
# -*- coding: utf-8 -*-
"""
pTRC Infinite Scale Core - Modular Metric Clock & Sieve Synchronization
100% Integer Z-Ontology | Module: Mathematics & Grid State
"""

import numpy as np

class PTRCModularClockEngine:
    def __init__(self, width=160, height=90, depth=64):
        self.width = width
        self.height = height
        self.depth = depth
        
        # Das unbestechliche p-adische Modulo-Uhrsystem
        self.PRIMORIAL_RING = 210  # Basis-Ring (2 * 3 * 5 * 7) -> Erweiterbar auf 2310
        self.CLOCK_24 = 24         # Symmetrische Steuer-Uhr
        self.REFRESH_TAKTE = 137   # Feynman-Vakuum-Limit
        
        self.global_master_clock = 0
        
        # 144-Facetten-Kristallachsen generieren
        self.crystal_axes = self._generate_144_facet_axes()
        
        # Initialisierung des Raums über das Modulo-Existenzsieb
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

    def _build_sieved_primorial_space(self):
        """Errichtet den 3D-Raum rein über die Restklassen des Uhrsystems"""
        space = np.zeros((self.depth, self.height, self.width), dtype=np.uint8)
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        
        # Die 8 erlaubten Hauptstrahlen der abelschen Symmetriegruppe modulo 24
        allowed_24_rays = {1, 5, 7, 11, 13, 17, 19, 23}
        
        for z in range(self.depth):
            dz2 = (z - cz) * (z - cz)
            for y in range(self.height):
                dy2 = (y - cy) * (y - cy)
                for x in range(self.width):
                    dx2 = (x - cx) * (x - cx)
                    quadrance = dx2 + dy2 + dz2
                    
                    # 1. DAS MODULO-210 UHRSIEB
                    residuum_210 = quadrance % self.PRIMORIAL_RING
                    
                    if residuum_210 <= 156: # Invarianter Grenzknoten
                        # 2. DER Z/24Z KONTROLLTAKT-CHECK
                        takt_check = (x * y + z) % self.CLOCK_24
                        
                        if takt_check in allowed_24_rays:
                            space[z, y, x] = 2  # Aktiver Resonanz-Knoten
                        elif takt_check == 12:
                            space[z, y, x] = 1  # Invarianter Massen-Knoten
                            
        return space

    def evolve_clock_one_takt(self):
        """Schaltet das gesamte Uhrsystem um einen Planck-Takt weiter (c = 1 px/takt)"""
        self.global_master_clock += 1
        
        current_hour = self.global_master_clock % self.CLOCK_24
        axis_to_roll = current_hour % 3
        shift_amount = 1 if (current_hour < 12) else -1
        
        self.voxels = np.roll(self.voxels, shift_amount, axis=axis_to_roll)
# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
#
# DUAL-LICENSING NOTICE:
# Non-commercial, academic, and open-source usage is strictly governed by 
# the GNU General Public License version 3 (GPLv3). Any commercial deployment,
# integration into proprietary, closed-source codebases, or corporate utilization
# explicitly requires a separate, individually negotiated commercial license.
# ==============================================================================
# -*- coding: utf-8 -*-
"""
pTRC Infinite Scale Core - 144-Facet Spatial Ray-Marching & Terminal Blitting
100% Integer Z-Ontology | c = 1 pixel/clock | Refresh on Takt 137
"""

import sys
import time
import numpy as np
from ptrc_clock_core import PTRCModularClockEngine

def render_144_facet_frame(engine):
    """Projiziert die Voxel entlang der 144 Symmetrieachsen ins flache Vision-Feld"""
    framebuffer = np.zeros((engine.height, engine.width), dtype=np.uint8)
    
    # Auswahl der Projektionsachse über den aktuellen Master-Takt
    axis_idx = engine.global_master_clock % 144
    axis = engine.crystal_axes[axis_idx]
    
    step_x = np.sign(axis)
    step_y = np.sign(axis)
    step_z = np.sign(axis) if axis != 0 else 1

    for y in range(engine.height):
        for x in range(engine.width):
            curr_x, curr_y, curr_z = x, y, 0
            for t in range(engine.depth):
                z_b = curr_z % engine.depth
                y_b = (curr_y + (t * step_y)) % engine.height
                x_b = (curr_x + (t * step_x)) % engine.width
                
                voxel_state = engine.voxels[z_b, y_b, x_b]
                if voxel_state > 0:
                    base_brightness = 200 if voxel_state == 2 else 120
                    framebuffer[y, x] = max(30, base_brightness - (t * 4))
                    break
                curr_z += step_z
    return framebuffer

def output_terminal_projection(engine, frame):
    ascii_chars = [" ", ".", "-", "+", "*", "X", "#", "@"]
    output = ["\033[H" + "="*160]
    output.append(f"[ pTRC MODULO CLOCK ENGINE ] TOTAL TAKT: {engine.global_master_clock} | RING Z/{engine.PRIMORIAL_RING}Z ACTIVE | REFRESH COHERENCE: 137".center(160))
    output.append("="*160)
    
    for y in range(0, engine.height, 2):
        row = []
        for x in range(engine.width):
            val = frame[y, x]
            char_idx = (val * (len(ascii_chars) - 1)) // 255
            row.append(ascii_chars[char_idx])
        output.append("".join(row))
    output.append("="*160)
    return "\n".join(output)

if __name__ == "__main__":
    # Erzeuge das mathematische Triebwerk
    engine = PTRCModularClockEngine()
    print("\033[2J", end="") # Einmaliger Terminal-Hard-Clear
    
    while True:
        # Die Engine taktet im Hintergrund permanent mit c=1 weiter
        engine.evolve_clock_one_takt()
        
        # Der unbestechliche Kollaps und Bildaufbau exakt alle 137 Takte
        if engine.global_master_clock % engine.REFRESH_TAKTE == 0:
            frame = render_144_facet_frame(engine)
            render_output = output_terminal_projection(engine, frame)
            print(render_output, flush=True)
            
            time.sleep(0.045) # Kinotaktung für das Auge

