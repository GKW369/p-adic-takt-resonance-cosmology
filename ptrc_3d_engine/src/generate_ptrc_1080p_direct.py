# ==============================================================================
# pTRC Framework - 1080p Direct MP4 Video Encoder & Auto-Cleanup Pipeline
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
from ptrc_clock_core import PTRCModularClockEngine

def render_1080p_frame(engine, takt_level):
    """Rendert das 3D-Hologramm ueber das 48-Strang-Raumsieb und die Modulo-24-Uhr"""
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Tiefer kosmischer Indigo-Hintergrund (BGR)
    framebuffer[:, :] = [35, 15, 20]
    
    # Fixierte Kristallachse 96 (Symmetrie-Anker)
    axis_idx = 96
    axis = engine.crystal_axes[axis_idx]
    
    # Die 8 invarianten Primstrahlen der Modulo-24-Uhr (Plichta-Basis)
    uhr_rays = [1, 5, 7, 11, 13, 17, 19, 23]
    
    # DIE 48 PRIMORIALEN STRÄNGE MODULO 210 (Euler-Phi φ(210) = 48)
    sieb_strands = [1, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 121, 127, 131, 137, 139, 143, 149, 151, 157, 163, 167, 169, 173, 179, 181, 187, 191, 193, 197, 199, 209]
    
    # HINWEIS ZUR ERWEITERBARKEIT (FRAKTALE SKALIERUNG):
    # - Modulo 2310 (2*3*5*7*11) -> φ(2310) = 480 primoriale Straenge
    # - Modulo 30030 (2*3*5*7*11*13) -> φ(30030) = 5760 primoriale Straenge
    
    t = int(takt_level)
    
    # Schrittweite 4 fuer fluessiges Echtzeit-Baking auf dem Acer-Laptop
    for y in range(0, height, 4): 
        for x in range(0, width, 4):
            nx = x - (width // 2)
            ny = y - (height // 2)
            
            # 90-GRAD-KREUZSPIEGELUNG (1 ist -1 im Takt)
            if (t % 2) == 1:
                mx = -nx
                my = -ny
            else:
                mx = nx
                my = ny
                
            # Zweite Spiegelachse im 90-Grad-Versatz
            if ((t // 2) % 2) == 1:
                dx = my + t
                dy = mx
            else:
                dx = mx + t
                dy = my
                
            quadrance = dx*dx + dy*dy
            
            # Filter 1: Das hochaufgeloeste 48-Strang-Raumsieb
            if (quadrance % 210) in sieb_strands:
                # Filter 2: Die zeitliche Phaseninterferenz der Modulo-24-Uhr
                phase = (dx * dy + 137 + t) % 24
                
                if phase == 12:
                    framebuffer[y:y+4, x:x+4] = [0, 190, 255]      # Amber-Gold (Masse)
                elif phase in uhr_rays:
                    framebuffer[y:y+4, x:x+4] = [255, 255, 0]      # Electrical Cyan (Energie)
    return framebuffer

if __name__ == "__main__":
    engine = PTRCModularClockEngine()
    
    temp_dir = "ptrc_temp_frames"
    final_video = "ptrc_3s_primorial_hologram.mp4"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180
    print(f"[ 1/3 ] Bake 48-Strang-Hologramm mit Modulo-24 Kopplung ({total_frames} Frames)...")
    
    for f in range(total_frames):
        takt_level = 1 + f
        frame = render_1080p_frame(engine, takt_level)
        
        file_path = f"{temp_dir}/frame_{f:04d}.png"
        cv2.imwrite(file_path, frame)
        
        if f % 30 == 0:
            print(f"        Taktstufe: {takt_level}/{total_frames} Z-Achsen-Knoten berechnet.")

    print("\n[ 2/3 ] Buendele rein ganzzahligen 48-Strang-Datenstrom via ffmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "60",
        "-i", f"{temp_dir}/frame_%04d.png",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        final_video
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"        Erfolg: '{final_video}' wurde stabil erzeugt!")
    except subprocess.CalledProcessError:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen!")
        sys.exit(1)
        
    print("\n[ 3/3 ] Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"\n[ PIEPERFEKT ] Das vollendete Primorial-Hologramm liegt bereit: {final_video}")
