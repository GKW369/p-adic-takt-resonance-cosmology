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
    """Rendert das 3D-Hologramm ueber das 48-strahlige modulo 210 Sieb und das modulo 24 Uhrwerk"""
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Tiefer kosmischer Indigo-Hintergrund (BGR fuer OpenCV)
    framebuffer[:, :] = (35, 15, 20)
    
    # Fixierte Kristallachse 96 (Symmetrie-Anker)
    axis_idx = 96
    axis = engine.crystal_axes[axis_idx]
    
    # 1. DAS FUNDAMENTALE UHRWERK: Die 8 erlaubten Primstrahlen der modulo 24 Uhr (nach Plichta)
    prime_rays_24 = (1, 5, 7, 11, 13, 17, 19, 23)
    
    # 2. DAS HOCHAUFLOESENDE RAUMSIEB: Die 48 invarianten Stränge der modulo 210 Restklassengruppe
    # ERWEITERUNGSHINWEIS: Dieses System ist unendlich skalierbar ueber die Eulersche Phi-Funktion.
    # Naechste hoehre Stufe waere das naechste Primorial: modulo 2310 mit exakt 480 Straengen (48 * (11-1)).
    prime_strands_210 = (
        1, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 
        71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 121, 127, 131, 137, 139, 
        143, 149, 151, 157, 163, 167, 169, 173, 179, 181, 187, 191, 193, 197, 199, 209
    )
    
    t = int(takt_level)
    
    # Schrittweite 2 fuer messerscharfe Tiefenwirkung auf dem 4K-Fernseher
    for y in range(0, height, 2): 
        for x in range(0, width, 2):
            nx = x - (width // 2)
            ny = y - (height // 2)
            
            # Gekreuzte 90-Grad-Spiegelung (1 ist -1 bei ungeradem Takt)
            if (t % 2) == 1:
                mx = -nx
                my = -ny
            else:
                mx = nx
                my = ny
                
            if ((t // 2) % 2) == 1:
                dx = my + t
                dy = mx
            else:
                dx = mx + t
                dy = my
                
            # Interaktive Rueckkopplung mit den Aussengrenzen der Matrix
            quadrance = dx*dx + dy*dy
            
            # FILTRATION EBENE 1: Faellt die Quadranz auf einen der 48 primorialen Straenge?
            if (quadrance % 210) in prime_strands_210:
                
                # FILTRATION EBENE 2: Phasen-Taktung ueber die modulo 24 Uhr
                phase = (dx * dy + 137 + t) % 24
                
                if phase == 12:
                    framebuffer[y:y+2, x:x+2] = (0, 190, 255)     # Amber-Gold (Masse)
                elif phase in prime_rays_24:
                    framebuffer[y:y+2, x:x+2] = (255, 255, 0)     # Electrical Cyan (Energie)
    return framebuffer

if __name__ == "__main__":
    engine = PTRCModularClockEngine()
    
    temp_dir = "ptrc_temp_frames"
    final_video = "ptrc_3s_primorial_hologram.mp4"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180  # 3 Sekunden bei 60 FPS
    print(f"[ 1/3 ] Starte 48-Strang-Baking ab EBENE 1 ({total_frames} Frames)...")
    
    for f in range(total_frames):
        takt_level = 1 + f
        frame = render_1080p_frame(engine, takt_level)
        
        file_path = f"{temp_dir}/frame_{f:04d}.png"
        cv2.imwrite(file_path, frame)
        
        if f % 30 == 0:
            print(f"        Primorial-Takt: {takt_level}/{total_frames} Z-layers projected.")

    print("\n[ 2/3 ] Buendele den 48-Strang-Datenstrom via ffmpeg...")
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
    except subprocess.CalledProcessError as e:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen!")
        sys.exit(1)
        
    print("\n[ 3/3 ] Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"\n[ PIEPERFEKT ] Das 48-Strang-Hologramm steht bereit: {final_video}")
