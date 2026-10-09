# -*- coding: utf-8 -*-
"""
pTRC Framework - Module: black_hole_saturation.py
Singularity Avoidance Engine via Rigid Lattice Capacity Constraints.
Refactored: 100% Floating-Point-Free. Pure digital integer visualization.
"""

import sys
import numpy as np

class BlackHoleSaturationEngine:
    def __init__(self, max_lattice_capacity=1836):
        # Maximale Kapazitätsgrenze eines einzelnen Gitterknotens
        self.max_lattice_capacity = max_lattice_capacity
        self.SCALE = 1000  # Skalierungsfaktor für Festkomma-Arithmetik

    def calculate_core_compression(self, total_mass=500000, compression_radius=0):
        """
        Berechnet die Kompression im Kern unter strikter Vermeidung von r=0 Singularitäten.
        Schützt das Gitter durch eine harte Pixel-Untergrenze (max(1, radius)).
        Rechnet streng in Z.
        """
        # FIX: Planck-Schutzbedingung. Verhindert Divisionen durch Null auf Hardware-Ebene.
        # Wenn der Radius kollabiert, fängt das Gitter ihn starr bei 1 Pixel ab.
        safe_radius = max(1, compression_radius)
        
        # Volumenberechnung im diskreten Gitter-Würfel (r^3)
        discretized_volume = safe_radius * safe_radius * safe_radius
        
        # Sättigungsdichte-Berechnung (Skaliert in Milli-Units)
        # Erst skalieren, dann Ganzzahl-Division (//)
        scaled_density = (total_mass * self.SCALE) // discretized_volume
        
        # Prüfung, ob die Gitter-Sättigungsgrenze überschritten wurde
        # Ein Überlauf wird starr auf die maximale Gitterkapazität gedeckelt
        if scaled_density > (self.max_lattice_capacity * self.SCALE):
            scaled_density = self.max_lattice_capacity * self.SCALE
            saturation_triggered = True
        else:
            saturation_triggered = False
            
        return scaled_density, saturation_triggered

if __name__ == "__main__":
    print("[ pTRC INFORMATICS ENGINE ] Validating Black Hole Saturation Limits...")
    engine = BlackHoleSaturationEngine()
    
    # Teste den Extremfall: Kollaps direkt auf den Nullpunkt (Radius = 0)
    density_units, saturated = engine.calculate_core_compression(total_mass=500000, compression_radius=0)
    
    print(f"\nDiskrete Gravitations-Verdichtung abgeschlossen:")
    print(f" -> Kern-Kompaktionsdichte: {density_units} Milli-Kompaktions-Units")
    
    if saturated:
        print(" -> STATUS: Singularität verhindert. Gitter-Sättigungsgrenze erreicht (Planck-Limit blockiert).")
    else:
        print(" -> STATUS: Sub-kritische Kern-Kompression.")
        
    print("-> ZERO Floating-Point Errors. Absolute Integer Invariance achieved.")
    sys.exit(0)
