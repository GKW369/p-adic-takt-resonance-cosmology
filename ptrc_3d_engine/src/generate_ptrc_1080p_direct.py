# ==============================================================================
# pTRC Framework - 1080p Mirror-Sphere Video Animation Pipeline
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

# Pfad-Korrektur: Fügt den aktuellen Ordner des Skripts zu Pythons Suchpfad hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# HIER ABGEGLICHEN: Der exakte Name der mathematischen Klasse ohne "3D"
from ptrc_3d_hologram_engine import PTRCHologramEngine

def render_animation_frame(engine, takt_level):
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Tiefer kosmischer Indigo-Hintergrund
    framebuffer[:, :] = (35, 15, 20)
    
    # Schrittweite 4 für ultra-schnelles i3-Laptop-Baking
    for y in range(0, height, 4):
        for x in range(0, width, 4):
            nx = x - (width // 2)
            ny = y - (height // 2)
            
            state = engine.compute_state(nx, ny, takt_level)
            
            if state == 1:
                # Gitter leuchtet intensiv: Amber-Gold
                framebuffer[y:y+4, x:x+4] = (0, 190, 255)
            elif state == 2:
                # Gitter leuchtet intensiv: Electrical Cyan
                framebuffer[y:y+4, x:x+4] = (255, 255, 0)
            elif state == 3:
                # Kugel-Spiegelung / Schatten: Etwas matteres Gold für metallischen Look
                framebuffer[y:y+4, x:x+4] = (0, 130, 190)
            elif state == 4:
                # Kugel-Spiegelung: Etwas matteres Cyan für metallischen Look
                framebuffer[y:y+4, x:x+4] = (180, 180, 0)
                
    return framebuffer

if __name__ == "__main__":
    engine = PTRCHologramEngine()
    
    temp_dir = os.path.join(current_dir, "ptrc_temp_frames")
    final_video = os.path.join(current_dir, "ptrc_3d_sphere_flight.mp4")
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180  # 3 Sekunden bei 60 FPS
    print(f"[ 1/3 ] Bake Kugel-Flug durch das 144-Facetten-Gitter ({total_frames} Frames)...")
    
    for f in range(total_frames):
        takt_level = 1 + f
        frame = render_animation_frame(engine, takt_level)
        
        file_path = os.path.join(temp_dir, f"frame_{f:04d}.png")
        cv2.imwrite(file_path, frame)
        
        if f % 30 == 0:
            print(f"        Taktstufe: {takt_level}/{total_frames} - Kugel im Koordinatenfluss.")

    print("\n[ 2/3 ] Bündele 3D-Spiegel-Datenstrom via ffmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "60",
        "-i", os.path.join(temp_dir, "frame_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        final_video
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"        Erfolg: '{final_video}' wurde fehlerfrei generiert!")
    except subprocess.CalledProcessError:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen!")
        sys.exit(1)
        
    print("\n[ 3/3 ] Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"\n[ PIEPERFEKT ] Die vollendete 3D-Kugel-Animation steht bereit: {final_video}")
