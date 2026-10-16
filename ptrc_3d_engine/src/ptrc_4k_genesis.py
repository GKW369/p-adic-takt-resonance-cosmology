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

import os
import sys

def generate_4k_crystal_genesis():
    WIDTH = 3840
    HEIGHT = 2160
    cx = WIDTH // 2
    cy = HEIGHT // 2
    
    CLOCK_210 = 210
    CLOCK_24  = 24
    ALPHA_137 = 137
    
    filename = "ptrc_4k_genesis.ppm"
    
    print("=" * 80)
    print(" [ pTRC 4K GENESIS ] RENDERING HIGH-RESOLUTION HOLOFRACTAL COHERENCE GRID")
    print(f" -> Target File: {filename} | Resolution: 3840x2160")
    print("=" * 80)
    
    # Wir schreiben die Bilddaten Zeile für Zeile direkt auf die Festplatte
    with open(filename, "wb") as f:
        # PPM-Header für ein unkomprimiertes 4K-RGB-Bild schreiben
        f.write(f"P6\n{WIDTH} {HEIGHT}\n255\n".encode())
        
        for y in range(HEIGHT):
            dy = y - cy
            dy_squared = dy * dy
            row_bytes = bytearray()
            
            for x in range(WIDTH):
                dx = x - cx
                dx_squared = dx * dx
                
                # 1. Reine Ganzzahl-Quadrance (Pythagoras ohne floats)
                quadrance = dx_squared + dy_squared
                
                # 2. Das Modulo-210 Raumsieb zünden
                residuum_210 = quadrance % CLOCK_210
                sieve_active = (residuum_210 <= 156)
                
                # 3. Den Modulo-24 Phasentakt berechnen
                ray_phase = (x * y + ALPHA_137) % CLOCK_24
                
                # Standard-Vakuumhintergrund (Moduliert über die 137er-Welle)
                bg_shading = ((quadrance % ALPHA_137) * 45) // ALPHA_137
                r = bg_shading // 3
                g = bg_shading // 4
                b = bg_shading // 2
                
                if sieve_active:
                    # KNOTEN-TYP 1: Invarianter Massen-Knoten (Takt 12) -> Bernstein-Gold
                    if ray_phase == 12:
                        r = min(255, 230 + (quadrance % 25))
                        g = min(255, 160 + (quadrance % 35))
                        b = 24
                    # KNOTEN-TYP 2: Die 8 erlaubten Energie-Strahlen -> Elektrisches Cyan
                    elif ray_phase in {1, 5, 7, 11, 13, 17, 19, 23}:
                        r = 0
                        g = min(255, 180 + (quadrance % 75))
                        b = min(255, 210 + (quadrance % 45))
                        
                row_bytes.append(r)
                row_bytes.append(g)
                row_bytes.append(b)
                
            f.write(row_bytes)
            
            # Fortschrittsanzeige im Terminal
            if (y + 1) % 200 == 0:
                percent = ((y + 1) * 100) // HEIGHT
                print(f" -> Progress Matrix: [ {percent:03d}% ] | Line {y+1}/{HEIGHT} computed.")
                
    print("=" * 80)
    print(f"[ SUCCESS ] 4K Spatial Crystal image baked successfully into {filename}")
    print("=" * 80)

if __name__ == "__main__":
    generate_4k_crystal_genesis()

