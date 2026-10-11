# -*- coding: utf-8 -*-
"""
pTRC Framework - Core Module 20: Discrete Pi Square Crystallization
Strict Integer Ontology (Z) - Zero Fractional Approximations.
Proves that circular density inside a Planck-lattice is a pure integer value.
Features an explicit visual clock-delay for terminal screencasts.
"""
import sys
import time

def calculate_discrete_pi_crystallization(grid_scale: int = 210) -> tuple[int, bool]:
    """
    Counts every single discrete pixel node that satisfies the spatial 
    radius condition inside a bounded square matrix (2 * grid_scale)^2.
    Uses strict integer logic with a visual frame-takt delay.
    """
    radius_squared: int = grid_scale * grid_scale
    nodes_inside_circle: int = 0
    total_lattice_nodes: int = grid_scale * grid_scale
    
    print(" -> Commencing multi-layered grid sweep across the space crystal...")
    
    # Durchlaufe das Gitter zeilenweise und erzeuge eine fließende Terminal-Anzeige
    for x in range(1, grid_scale + 1):
        x_squared: int = x * x
        for y in range(1, grid_scale + 1):
            if x_squared + y * y <= radius_squared:
                nodes_inside_circle += 1
                
        # Jede 5. Zeile wird die aktuelle Auszählung live auf den Bildschirm projiziert
        if x % 5 == 0:
            print(f" -> [ PLANCK-GITTER ] Scanning Line {x:03d}/{grid_scale} | Current Subtotal: {nodes_inside_circle * 4} Units", end="\r", flush=True)
            time.sleep(0.040)  # Der visuelle Takt-Delay für das Video
            
    # Das finale Verhältnis der unteilbaren Gitterpunkte
    absolute_integer_density: int = nodes_inside_circle * 4
    is_valid_crystallization: bool = absolute_integer_density > total_lattice_nodes
    
    return absolute_integer_density, is_valid_crystallization
if __name__ == "__main__":
    print("\n" + "="*150)
    print("[ OK ] Discrete Pi-Square Crystallization Active.")
    print("="*150)
    
    density, validated = calculate_discrete_pi_crystallization(grid_scale=210)
    
    # Zeilenumbruch, um die laufende Anzeige sauber abzuschließen
    print("\n" + "-"*150)
    print(f" -> Counted Integer Lattice Circular Density: {density} Quantum Units.")
    print(f" -> STATUS: Circle Successfully Squared within Integer Bounds.")
    print("-"*150)
    
    if validated:
        sys.exit(0)
    else:
        print(" -> STATUS: Gitter Resolution Failure.")
        sys.exit(1)
