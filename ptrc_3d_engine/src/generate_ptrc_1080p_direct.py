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
    """Rendert die holografische Matrix ueber gekreuzte 90-Grad-Ganzzahlspiegelungen"""
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Tiefer kosmischer Indigo-Hintergrund (BGR fuer OpenCV)
    framebuffer[:, :] = [35, 15, 20] 
    
    # Fixierte Kristallachse 96 (Symmetrie-Anker)
    axis_idx = 96
    axis = engine.crystal_axes
    prime_rays = 
    
    # Der aktuelle diskrete Taktzustand ab Ebene 1
    t = int(takt_level)
    
    # Schrittweite 2 fuer messerscharfe Tiefenwirkung auf dem 4K-Fernseher
    for y in range(0, height, 2): 
        for x in range(0, width, 2):
            # Zentrieren auf den mathematischen Ursprung (Ebene 1)
            nx = x - (width // 2)
            ny = y - (height // 2)
            
            # DIE 90-GRAD-KREUZSPIEGELUNG (HOLOGRAFISCHE SPEICHEREBENE)
            # Spiegel 1 (Horizontal/Vertikal): Inversion über den Takt (1 ist -1)
            if (t % 2) == 1:
                mx = -nx
                my = -ny
            else:
                mx = nx
                my = ny
                
            # Spiegel 2 (90 Grad gekreuzt): Transposition der Achsen im Taktverlauf
            # Faltet die inneren Schichten rein ganzzahlig nach aussen!
            if ((t // 2) % 2) == 1:
                dx = my + t
                dy = mx
            else:
                dx = mx + t
                dy = my
                
            # Orthogonale Interferenz mit den Aussengrenzen des Gitters
            quadrance = dx*dx + dy*dy
            
            # Primoriales Raumsieb modulo 210
            if (quadrance % 210) <= 156:
                phase = (dx * dy + 137 + t) % 24
                
                if phase == 12:
                    framebuffer[y:y+2, x:x+2] =     # Amber-Gold (Masse)
                elif phase in prime_rays:
                    framebuffer[y:y+2, x:x+2] =     # Electrical Cyan (Energie)
    return framebuffer

if __name__ == "__main__":
    engine = PTRCModularClockEngine()
    
    temp_dir = "ptrc_temp_frames"
    final_video = "ptrc_3s_hologram_mirror.mp4"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180  # 3 Sekunden bei 60 FPS
    print(f"[ 1/3 ] Starte holografische Kreuzspiegelung ab EBENE 1 ({total_frames} Frames)...")
    
    for f in range(total_frames):
        # Wir starten exakt auf Ebene 1 und schalten die Spiegelungen pro Takt weiter
        takt_level = 1 + f
        
        frame = render_1080p_frame(engine, takt_level)
        
        file_path = f"{temp_dir}/frame_{f:04d}.png"
        cv2.imwrite(file_path, frame)
        
        if f % 30 == 0:
            print(f"        Spiegel-Takt: {takt_level}/{total_frames} interference computed.")

    print("\n[ 2/3 ] Bündele perfekten Ganzzahl-Datenstrom via ffmpeg...")
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
        print(f"        Erfolg: '{final_video}' wurde fehlerfrei generiert!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen!")
        sys.exit(1)
        
    print("\n[ 3/3 ] Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"\n[ PIEPERFEKT ] Das gekreuzte Hologramm steht bereit: {final_video}")
