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
    """Erzeugt das unbestechliche Terminal-Visual ohne Float-Interpolation"""
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
    # Erzeuge das mathematische Triebwerk aus ptrc_clock_core.py
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
            
            time.sleep(0.045) # Kinotaktung für das menschliche Auge
