# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
#
# DUAL-LICENSING NOTICE:
# Non-commercial, academic, and open-source usage is strictly governed by 
# the GNU Affero General Public License version 3 (AGPLv3). Any commercial deployment,
# integration into proprietary, closed-source codebases, or corporate utilization
# explicitly requires a separate, individually negotiated commercial license.
# ==============================================================================
# -*- coding: utf-8 -*-
"""
pTRC Framework - Core Module 20: Discrete Pi Square Crystallization
Strict Integer Ontology (Z) - Zero Fractional Approximations.
Optimized Layout: 90x44 Character Grid for a Native Quadratic Konsole Projection.
"""
import sys
import time

def render_native_quadratic_circle():
    """
    Renders a whole-number spatial circle directly onto a 90x44 grid.
    Eradicates oval distortion by restructuring the physical column width.
    """
    WIDTH = 90
    HEIGHT = 44
    cx = WIDTH // 2
    cy = HEIGHT // 2
    
    nodes_inside_circle = 0
    
    # Terminal-Inhalt hard löschen und Cursor nach oben links setzen
    print("\033[2J\033[H", end="", flush=True) 
    print("="*90)
    print(f"[ pTRC CORE ] NATIVE 90x44 QUADRATIC PROJECTION".center(90))
    print(f"[ LICENSED UNDER GNU AGPLv3 - SOURCE CODE ENTITLEMENT ACTIVE ]".center(90))
    print("="*90)
    
    # Der Radius wird starr an die neue vertikale Schmerzgrenze angepasst
    radius = 19
    radius_squared = radius * radius
    
    for y in range(HEIGHT):
        row_chars = []
        dy_squared = (y - cy) * (y - cy)
        
        for x in range(WIDTH):
            # Durch das Einkürzen der Breite auf 90 Spalten reicht ein flacher,
            # unkomplizierter Ganzzahl-Schritt, um die native Zeichenhöhe auszugleichen.
            dx_corrected = ((x - cx) * 50) // 100
            spatial_distance = (dx_corrected * dx_corrected) + dy_squared
            
            if spatial_distance <= radius_squared:
                nodes_inside_circle += 1
                
                # Symmetrische Kristallisation der Außenhülle
                if radius_squared - 35 <= spatial_distance <= radius_squared:
                    row_chars.append("O")
                else:
                    row_chars.append(".")
            else:
                row_chars.append("-")
                
        print("".join(row_chars), flush=True)
        time.sleep(0.035) # Takt-Delay für den Live-Aufbau im Video
        
    return nodes_inside_circle * 4
if __name__ == "__main__":
    total_units = render_native_quadratic_circle()
    
    print("="*90)
    print(f" -> Counted Integer Lattice Circular Density: {total_units} Quantum Units.")
    print(f" -> STATUS: Native 90x44 Circle Squared. Zero Floating-Point Pollution.")
    print("="*90)
    
    if total_units > 1000:
        sys.exit(0)
    else:
        sys.exit(1)
