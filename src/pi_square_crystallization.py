# -*- coding: utf-8 -*-
"""
pTRC Framework - Core Module 20: Discrete Pi Square Crystallization
Strict Integer Ontology (Z) - Zero Fractional Approximations.
Renders a perfectly locked integer circle matrix live in the terminal.
Cinema Profile: Symmetrical 150-Character Grid Layout.
"""
import sys
import time

def render_discrete_circle_matrix():
    """
    Renders the whole-number geometry line by line to the terminal.
    Uses strict integer rules without a single float or pi calculation.
    """
    WIDTH = 150
    HEIGHT = 40
    cx = WIDTH // 2
    cy = HEIGHT // 2
    
    nodes_inside_circle = 0
    
    # Terminal komplett leeren und Cursor nach ganz oben links setzen
    print("\033[2J\033[H", end="", flush=True) 
    print("="*150)
    print(f"[ pTRC SPACE CRYSTAL ] GEOMETRIC CIRCLE CRYSTALLIZATION | HARDWARE RADIAL SWEEP | ZERO FLOATS".center(150))
    print("="*150)
    
    # Zeile für Zeile durch das gerasterte Planck-Universum gehen
    for y in range(HEIGHT):
        row_chars = []
        dy_squared = (y - cy) * (y - cy)
        
        for x in range(WIDTH):
            dx = x - cx
            
            # Ganzzahlige Korrektur des X/Y-Seitenverhältnisses im Terminal (1:3)
            dx_corrected = (dx * dx) // 9
            
            # Reine ganzzahlige Pythagoras-Koordinaetenprüfung (Radius im Quadrat = 210)
            if dx_corrected + dy_squared <= 210:
                nodes_inside_circle += 1
                
                # Kristallisation der Außenkante als stolzes "O"
                if 180 <= dx_corrected + dy_squared <= 210:
                    row_chars.append("O")
                else:
                    row_chars.append(".") # Das Innere des informationellen Kreises
            else:
                row_chars.append("-") # Der leere Raum außerhalb
                
        # Drucke die Zeile und flushe sofort für die fließende Animation
        print("".join(row_chars), flush=True)
        time.sleep(0.040) # Visueller Takt-Delay für den Videoaufbau
        
    return nodes_inside_circle * 4
if __name__ == "__main__":
    # Startet die grafische Raster-Engine im Terminal
    total_units = render_discrete_circle_matrix()
    
    # Absolute Eliminierung des Dezimalpunkts. Ausgabe erfolgt rein ganzzahlig!
    print("="*150)
    print(f" -> Counted Integer Lattice Circular Density: {total_units} Quantum Units.")
    print(f" -> STATUS: Circle Successfully Squared within Integer Bounds. Pi is a Pixel-Density Artifact.")
    print("="*150)
    
    # Überprüfung zur Absicherung der automatisierten Actions-Pipeline
    if total_units > 1000:
        sys.exit(0)
    else:
        print(" -> STATUS: Gitter Resolution Failure.")
        sys.exit(1)
