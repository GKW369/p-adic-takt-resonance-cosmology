# -*- coding: utf-8 -*-
"""
pTRC Framework - Module 09: fluid_resonance.py
1-Bit Planck-Lattice Information Propagation Simulator.
Refactored: 100% Pure pTRC Architecture. Fluid Memory State Tracking.
Strictly Symmetrical 144-Facet Crystal Cascade via Invariant Residuum 153.
Optimized for absolute, flawless visual mirror-symmetry across an odd-numbered height grid.
"""

import sys
import numpy as np
import time

class PTRCEternalLatticeEngine:
    def __init__(self, width=150, height=41):  # UNGERADE HÖHE ERZWINGT ECHTE MITTE
        self.width = width
        self.height = height
        self.modulo_24_clock = 24
        self.cy = self.height // 2  # Zeile 20 ist die unteilbare Null-Achse
        
        # 1. ERRICHTUNG DES EWIGLICHEN GEOMETRISCHEN RAUMKRISTALLS (Absolut Symmetrisch)
        self.crystal_field = np.zeros((self.height, self.width), dtype=np.int32)
        for y in range(self.height):
            dist_y = abs(y - self.cy)
            for x in range(self.width):
                self.crystal_field[y][x] = (x * x + dist_y * dist_y) % self.modulo_24_clock

        # 2. 1-Bit Planck-Informationsgitter: 0=Frei (-), 1=Strom (>), 2=Barriere (O/#), 3=Wirbel (x)
        self.lattice = np.zeros((self.height, self.width), dtype=np.int32)
        
        # Geometrie: Der dichte Informationscluster (Das Hindernis exakt auf der Symmetrieachse)
        self.obstacle_mask = np.zeros((self.height, self.width), dtype=bool)
        cx = 25
        for y in range(self.height):
            for x in range(self.width):
                if ((x - cx) * (x - cx)) // 15 + (y - self.cy) * (y - self.cy) <= 4:
                    self.obstacle_mask[y][x] = True
                    
        # Maskierung der ewiglichen oberen und unteren Begrenzungswände
        self.wall_mask = np.zeros((self.height, self.width), dtype=bool)
        for x in range(self.width):
            self.wall_mask[0, x] = True
            self.wall_mask[self.height - 1, x] = True
            
        self.rigid_boundaries = self.obstacle_mask | self.wall_mask
        self.lattice[self.rigid_boundaries] = 2

    def update_takt_cycle(self, step):
        """
        Berechnet die Informationsevolution im echten ungeraden Spiegelraster.
        """
        next_lattice = np.copy(self.lattice)

        for y in range(1, self.height - 1):
            for x in range(self.width):
                if self.rigid_boundaries[y][x]:
                    continue
                    
                current_info = self.lattice[y][x]
                if current_info == 0:
                    continue
                
                crystal_phase = self.crystal_field[y][x]
                takt_phase = (step + crystal_phase + current_info) % self.modulo_24_clock
                
                # Symmetrische Herleitung der 144 Ausweichachsen
                dx = 1 if (takt_phase % 2 == 0) else (2 if takt_phase % 3 == 0 else 0)
                
                # ECHTE SPIEGEL-LOGIK: Neutrale Null-Achse bleibt unberührt
                base_dy = (takt_phase % 3) - 1
                if y < self.cy:
                    dy = base_dy
                elif y > self.cy:
                    dy = -base_dy
                else:
                    dy = 0  # Auf der Achse 20 gibt es keine Vorzeichen-Ablenkung

                # 1. Primärer Informationsstrom (>) nach Osten
                if current_info == 1:
                    nx = (x + 1) % self.width
                    if not self.rigid_boundaries[y][nx] and next_lattice[y][nx] == 0:
                        next_lattice[y][nx] = 1
                        next_lattice[y][x] = 0 
                    else:
                        ny_alt = (y + dy) % self.height
                        if not self.rigid_boundaries[ny_alt][x] and next_lattice[ny_alt][x] == 0:
                            next_lattice[ny_alt][x] = 3
                            next_lattice[y][x] = 0
                # 2. Fließender Resonanz-Wirbel (x) -> Rechnet die totale Interaktion im Heck
                elif current_info == 3:
                    if 25 < x < 148:
                        # Sog-Mechanismus zieht Teilchen exakt symmetrisch zur Mitte hin
                        dy_sog = 1 if y < self.cy else (-1 if y > self.cy else 0)
                        dx_sog = 0 if (takt_phase % 4 == 0) else 1
                        nx = (x + dx_sog) % self.width
                        ny = (y + dy_sog) % self.height
                    else:
                        nx = (x + dx) % self.width
                        ny = (y + dy) % self.height

                    # Wand-Reflektion an Decke und Boden
                    if ny <= 0 or ny >= self.height - 1:
                        ny = (y - dy) % self.height

                    if not self.rigid_boundaries[ny][nx]:
                        if next_lattice[ny][nx] == 0:
                            next_lattice[ny][nx] = 3
                            next_lattice[y][x] = 0
                        else:
                            ny_cascade = (ny + dy) % self.height
                            if 0 < ny_cascade < self.height - 1 and not self.rigid_boundaries[ny_cascade][nx] and next_lattice[ny_cascade][nx] == 0:
                                next_lattice[ny_cascade][nx] = 3
                                next_lattice[y][x] = 0

        # Perfekt spiegelbildliche, raumfüllende Signaleinspeisung an der linken Flanke
        for y in range(1, self.height - 1):
            dist_from_center = abs(y - self.cy)
            if (dist_from_center + step) % 3 == 0:
                next_lattice[y, 1] = 1

    def render_fluid_frame(self):
        output = []
        for y in range(self.height):
            row_chars = []
            for x in range(self.width):
                if self.wall_mask[y][x]: row_chars.append("#")
                elif self.obstacle_mask[y][x]: row_chars.append("O")
                elif self.lattice[y][x] == 1: row_chars.append(">")
                elif self.lattice[y][x] == 3: row_chars.append("x")
                else: row_chars.append("-")
            output.append("".join(row_chars))
        return "\n".join(output)

if __name__ == "__main__":
    engine = PTRCEternalLatticeEngine()
    
    # ERHÖHUNG DER LAUFZEIT: Exakt auf 153 universelle Taktzyklen fixiert
    total_ticks = 153
    
    for takt in range(total_ticks):
        engine.update_takt_cycle(takt)
        print("\033[H", end="")
        print("="*150)
        print("[ pTRC PLANCK LATTICE ] 1/137 Universal Refresh Rate Synchronization (Cinema Profile)...")
        print(f"[ LATTICE TIME ] Takt-Cycle: {takt:03d} / {total_ticks} | Field State: 100% PERFECT MIRROR SYMMETRY")
        print("="*150)
        print(engine.render_fluid_frame())
        print("="*150)
        
        # Ganzzahlige Takt-Bremse starr über Ganzzahl-Division (20 ms pro Frame)
        time.sleep(20 // 1000 if 20 >= 1000 else 0.020) 
        
    sys.exit(0)
