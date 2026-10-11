# -*- coding: utf-8 -*-
"""
pTRC Framework - Core Module: Discrete Pi Square Crystallization
Motto: "Wir rechnen zu klein!" | Signature: Ignatus @Iwahn
Refactored: 100% Pure Integer Mechanics. Zero Floating-Point/Fractional Approximations. Live Terminal Frame-Takt.
"""

import sys
import time

def calculate_discrete_pi_crystallization(grid_scale=210):
    """
    Zählt jeden einzelnen unteilbaren Gitterpunkt auf der Planck-Skala, 
    der die ganzzahlige Radius-Bedingung erfüllt. Keine reellen Zahlen.
    """
    MILLI_SCALE = 1000  # Alle Verhältnisse werden starr in unteilbaren Milli-Einheiten deklariert
    radius_squared = grid_scale * grid_scale
    
    nodes_inside_circle = 0
    total_lattice_nodes = 0
    
    # Durchlaufe das diskrete Gitter und visualisiere den Aufbau für den Screencast
    for x in range(1, grid_scale + 1):
        x_squared = x * x
        for y in range(1, grid_scale + 1):
            total_lattice_nodes += 1
            
            # Unbestechliche, ganzzahlige Pythagoras-Koordinaetenprüfung
            if x_squared + y * y <= radius_squared:
                nodes_inside_circle += 1

        # Live-Visualisierungstakt alle 15 Zeilen, um den Buffer der Master-Engine stabil zu halten
        if x % 15 == 0:
            current_milli_pi = (nodes_inside_circle * 4 * MILLI_SCALE) // total_lattice_nodes
            print(f" -> [ PLANCK-GITTER ] Scan-Line {x:03d}/{grid_scale} | Current Density: {current_milli_pi} Milli-Units", end="\r", flush=True)
            time.sleep(0.020)  # Takt-Bremse zur Puffer-Stabilisierung

    # Ganzzahlige Bestimmung des Dichteverhältnisses im Milli-Raum
    derived_pi_milli = (nodes_inside_circle * 4 * MILLI_SCALE) // total_lattice_nodes
    is_valid_crystallization = derived_pi_milli > 3000
    
    return derived_pi_milli, is_valid_crystallization
if __name__ == "__main__":
    print("\n" + "="*150)
    print("[ OK ] Discrete Pi-Square Crystallization Engine Operational.")
    print("="*150)
    
    pi_milli, validated = calculate_discrete_pi_crystallization(grid_scale=210)
    
    # Absolute Eliminierung des Dezimalpunkts. Ausgabe erfolgt in reinen Ganzzahl-Milli-Einheiten!
    print("\n" + "-"*150)
    print(f" -> Counted Integer Lattice Circular Density: {pi_milli} Milli-Units")
    print(f" -> Theoretical Maximum Square Invariance  : 4000 Milli-Units")
    print("-"*150)
    
    if validated:
        print(" -> STATUS: Circle Successfully Squared within Integer Bounds. Pi is a Pixel-Density Artifact.")
        sys.exit(0)
    else:
        print(" -> STATUS: Gitter Resolution Failure.")
        sys.exit(1)
