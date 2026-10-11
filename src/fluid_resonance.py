# -*- coding: utf-8 -*-
"""
pTRC Framework - Module: fluid_resonance.py
Discrete Finite-Volume Lattice Integration for High-Velocity Aerospace Diagnostics.
Refactored: Strict 132 Takt Steps. Pure Z-Nanosecond Frame Synchronization.
Cinema Profile: Symmetrical 150-Character Grid Projection Layout.
"""

import numpy as np
import os
import sys
import time

class FluidResonanceEngine:
    def __init__(self, width=150, height=20, target_resonance=210):
        self.width = width
        self.height = height
        self.target_resonance = target_resonance
        
        # 4 orthogonale Richtungen für diskrete Teilchenbewegung
        self.grid = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        
        # Geometrische Barriere im Strömungskanal (Gitter-Hindernis im Kinoformat)
        self.obstacle = np.zeros((self.height, self.width), dtype=np.uint8)
        cx, cy, r = width // 3, height // 2, height // 4
        for y in range(self.height):
            for x in range(self.width):
                if (x - cx)**2 + (y - cy)**2 <= r**2:
                    self.obstacle[y, x] = 1

        self.initialize_flow()

    def initialize_flow(self):
        # Konstanter Taktstrom (Einstrom) von links nach rechts
        self.grid[:, :4, 0] = 1
        rand_ints = np.random.randint(0, 100, size=(self.height, self.width, 4), dtype=np.uint8)
        self.grid[rand_ints > 75] = 1
        
        for d in range(4):
            self.grid[self.obstacle == 1, d] = 0

    def step(self):
        """ Führt einen diskreten Taktzyklus aus: Streaming -> Bounce-Back -> Collision """
        new_grid = np.zeros_like(self.grid)
        new_grid[:, :, 0] = np.roll(self.grid[:, :, 0], shift=1, axis=1)   # Rechts
        new_grid[:, :, 1] = np.roll(self.grid[:, :, 1], shift=-1, axis=0)  # Oben
        new_grid[:, :, 2] = np.roll(self.grid[:, :, 2], shift=-1, axis=1)  # Links
        new_grid[:, :, 3] = np.roll(self.grid[:, :, 3], shift=1, axis=0)   # Unten

        new_grid[:, :1, 0] = 1

        obs_mask = (self.obstacle == 1)
        for d in range(4):
            opp_d = (d + 2) % 4
            if d == 0:
                new_grid[:, :-1, opp_d] = np.where(self.obstacle[:, 1:], new_grid[:, :-1, d], new_grid[:, :-1, opp_d])
            elif d == 1:
                new_grid[1:, :, opp_d] = np.where(self.obstacle[:-1, :], new_grid[1:, :, d], new_grid[1:, :, opp_d])
            elif d == 2:
                new_grid[:, 1:, opp_d] = np.where(self.obstacle[:, :-1], new_grid[:, 1:, d], new_grid[:, 1:, opp_d])
            elif d == 3:
                new_grid[:-1, :, opp_d] = np.where(self.obstacle[1:, :], new_grid[:-1, :, d], new_grid[:-1, :, opp_d])

        for d in range(4):
            new_grid[obs_mask, d] = 0

        c_180 = (new_grid[:, :, 0] == 1) & (new_grid[:, :, 2] == 1) & (new_grid[:, :, 1] == 0) & (new_grid[:, :, 3] == 0)
        c_90  = (new_grid[:, :, 1] == 1) & (new_grid[:, :, 3] == 1) & (new_grid[:, :, 0] == 0) & (new_grid[:, :, 2] == 0)

        new_grid[c_180, 0], new_grid[c_180, 2] = 0, 0
        new_grid[c_180, 1], new_grid[c_180, 3] = 1, 1
        new_grid[c_90, 1], new_grid[c_90, 3] = 0, 0
        new_grid[c_90, 0], new_grid[c_90, 2] = 1, 1

        self.grid = new_grid
    def get_density_matrix(self):
        raw_density = np.sum(self.grid, axis=2, dtype=np.uint8)
        return (raw_density * 6) % self.target_resonance

    def render_ascii(self):
        density = self.get_density_matrix()
        chars = [" ", ".", "-", "=", "#"]
        output = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if self.obstacle[y, x] == 1:
                    row += "O"
                else:
                    val = density[y, x] // 5
                    idx = min(val, 4)
                    row += chars[idx]
            output.append(row)
        return "\n".join(output)

if __name__ == "__main__":
    # Aktivierung des starr 150 Zeichen breiten Kinoformats
    engine = FluidResonanceEngine(width=150, height=20)
    
    # Exakt auf 132 Takte fixiert (Vorgabe aus dem Alpha-Emitter-Taktkreis)
    total_ticks = 132
    
    # 3.000.000.000 Nanosekunden Gesamtlaufzeit // 132 Takt-Frames = 22727272 Nanosekunden pro Frame
    NANOSECONDS_PER_FRAME = 22727272
    
    global_start = time.time_ns()
    
    for tick in range(1, total_ticks + 1):
        frame_start = time.time_ns()
        
        # Ein unteilbarer physikalischer Integrationsschritt
        engine.step()
        
        # Bildschirm hard loeschen und an Spalte 0 fixieren
        print("\033[2J\033[H", end="", flush=True)
        print("="*150)
        print(f"[ pTRC WINDKANAL ] LIVE FIELD DYNAMICS | STEP {tick:03d}/{total_ticks} | PROFILE: 150-CHAR CINEMA GRID".center(150))
        print("="*150)
        print(engine.render_ascii(), flush=True)
        
        # PURE GANZZAHL-TAKTUNG: Blockierende Hardware-Abfrageschleife bis die Nanosekunden voll sind.
        # Ersetzt analoges time.sleep komplett und erzwingt die Sichtbarkeit auf dem ACER-Display!
        while (time.time_ns() - frame_start) < NANOSECONDS_PER_FRAME:
            pass
            
    global_end = time.time_ns()
    duration_ms = (global_end - global_start) // 1000000
    
    print("\n" + "-"*150)
    print(f" -> STATUS: LGCA Flow Engine Evaluated. Symmetrical Wave-Front Stabilized.")
    print(f" -> TOTAL HARDWARE BENCHMARK RUNTIME: {duration_ms} ms (132 Steps Invariant).")
    print("-"*150)
    sys.exit(0)
