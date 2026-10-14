# ==============================================================================
# pTRC Framework - 1080p 3D Sphere Flight Animation & Auto-Cleanup Pipeline
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
#
# DUAL-LICENSING NOTICE:
# Non-commercial, academic, and open-source usage is strictly governed by 
# the GNU General Public License version 3 (GPLv3). Any commercial deployment,
# integration into proprietary, closed-source codebases, or corporate utilization
# explicitly requires a separate, individually negotiated commercial license.
# ==============================================================================
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
import numpy as np
import cv2

# Importiere deine offizielle neue 3D-Engine
from ptrc_3d_hologram_engine import PTRC3DHologramEngine

def render_animation_frame(engine, ball_x, ball_y, ball_z, takt_level):
    """Rendert ein Full-HD Frame mit fliegender, spiegelnder Kugel im 48-Strang-Sieb"""
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Tiefer kosmischer Indigo-Hintergrund (BGR)
    framebuffer[:, :] = (35, 15, 20)
    
    # Konstanter Radius der Kugel im Quadrat (reiner Integer-Raum)
    ball_radius_sq = 144 * 144  # Abgestimmt auf deine 144 Kristallfacetten
    
    # Schrittweite 4 fuer fluessiges Echtzeit-Baking auf dem Acer-Laptop
    for y in range(0, height, 4): 
        for x in range(0, width, 4):
            # Zentrieren der Bildschirmkoordinaten
            nx = x - (width // 2)
            ny = y - (height // 2)
            
            # 1. BERECHNUNG DER KUGEL-GEOMETRIE (Rein ganzzahlig im 3D-Raum)
            # Distanz zum bewegten Kugelzentrum
            dx_ball = nx - int(ball_x)
            dy_ball = ny - int(ball_y)
            dist_to_ball_sq = dx_ball * dx_ball + dy_ball * dy_ball
            
            # Pruefe, ob der Strahl die Kugel trifft
            if dist_to_ball_sq <= ball_radius_sq:
                # REIN GANZZAHLIGE SPIEGELUNG:
                # Die Kugel invertiert die Raumkoordinaten ueber die Achsen der Engine
                # und spiegelt das Gitter auf ihrer eigenen Oberflaeche
                sx = -nx + int(ball_z)
                sy = -ny + int(ball_z)
                
                state = engine.compute_state(sx, sy, takt_level)
                if state == 1:
                    framebuffer[y:y+4, x:x+4] = (100, 220, 255) # Gespiegeltes Amber (heller)
                elif state == 2:
                    framebuffer[y:y+4, x:x+4] = (255, 255, 150) # Gespiegeltes Cyan-Leuchten
                else:
                    framebuffer[y:y+4, x:x+4] = (10, 5, 8)      # Tiefschwarzer Kugel-Kernaustritt
                continue
            
            # 2. BERECHNUNG DES UMGEBENDEN GITTERS VIA ENGINE
            # Wir nutzen ball_z, um das Gitter synchron im Hintergrund fliessen zu lassen
            state = engine.compute_state(nx + int(ball_z), ny + int(ball_z), takt_level)
            
            if state == 1:
                framebuffer[y:y+4, x:x+4] = (0, 190, 255)     # Amber-Gold (Masseknoten)
            elif state == 2:
                # LEUCHTENDE GITTERSTREBEN: Erhoehte Farbintensitaet im Cyan-Bereich
                framebuffer[y:y+4, x:x+4] = (255, 255, 50)    # Pulsierendes Electrical Cyan
            elif state == 3:
                framebuffer[y:y+4, x:x+4] = (0, 0, 0)         # Projizierter Schattenraum
                
    return framebuffer

if __name__ == "__main__":
    # Initialisiere deine 3D-Engine
    engine = PTRC3DHologramEngine()
    
    temp_dir = "ptrc_temp_frames"
    final_video = "ptrc_3d_sphere_cosmology.mp4"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180  # 3 Sekunden bei 60 FPS
    print(f"[ 1/3 ] Starte Schoepfungs-Animation ({total_frames} Frames, 60 FPS, 1080p)...")
    
    for f in range(total_frames):
        # DIE FLUGBAHN DER KUGEL: Rein ganzzahlige Schrittweiten durch das Gitter
        # Die Kugel fliegt eine diskrete Schleife von links unten nach rechts oben
        ball_x = -300 + (f * 3.5)
        ball_y = 200 - (f * 2.2)
        ball_z = f * 2  # Gleichzeitiger raeumlicher Vorschub des Hintergrundgitters
        
        # Der Zeittakt fuer deine 90-Grad-Spiegelkopplung
        takt_level = 1 + f
        
        frame = render_animation_frame(engine, ball_x, ball_y, ball_z, takt_level)
        
        file_path = f"{temp_dir}/frame_{f:04d}.png"
        cv2.imwrite(file_path, frame)
        
        if f % 30 == 0:
            print(f"        Animation-Baking: Frame {f}/{total_frames} prozessiert.")

    print("\n[ 2/3 ] Buendele leuchtenden 3D-Datenstrom via ffmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "60",
        "-i", f"{temp_dir}/frame_%04d.png",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",  # Noch hoehere Qualitaet fuer messerscharfe Punkte auf dem Fernseher
        final_video
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"        Erfolg: '{final_video}' wurde absolut stabil erzeugt!")
    except subprocess.CalledProcessError:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen!")
        sys.exit(1)
        
    print("\n[ 3/3 ] Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"\n[ PIEPERFEKT ] Deine spiegelnde Kugel fliegt durch das Gitter: {final_video}")
