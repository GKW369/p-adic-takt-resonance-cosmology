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

def render_1080p_frame(engine, frame_idx):
    """Rendert ein Full-HD Frame durch rein ganzzahliges Transponieren der Raum-Matrix"""
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Tiefer kosmischer Indigo-Hintergrund (BGR für OpenCV)
    framebuffer[:, :] = [35, 15, 20]
    
    # Fixierte Kristallachse 96 (Symmetrie-Anker)
    axis_idx = 96
    axis = engine.crystal_axes[axis_idx]
    prime_rays = [1, 5, 7, 11, 13, 17, 19, 23]
    
    # Diskreter Transpositions-Takt basierend auf dem Frame
    takt = frame_idx
    
    # Schrittweite 4 für schnelles, flüssiges Test-Rendering auf dem Acer
    for y in range(0, height, 4): 
        for x in range(0, width, 4):
            # Zentrieren der Ur-Koordinaten
            nx = x - width // 2
            ny = y - height // 2
            
            # REIN GANZZAHLIGES TRANSPONIEREN & ROTIEREN IN Z
            # Wir nutzen diskrete Vorzeichenwechsel und Vertauschungen (Symmetriegruppe)
            if takt % 4 == 0:
                dx = nx + takt
                dy = ny
            elif takt % 4 == 1:
                dx = -ny
                dy = nx + takt
            elif takt % 4 == 2:
                dx = -nx - takt
                dy = -ny
            else:
                dx = ny
                dy = -nx - takt
                
            # Interaktive Rückkopplung mit den Außengrenzen des Gitters
            quadrance = dx*dx + dy*dy
            
            # Primoriales Raumsieb modulo 210
            if (quadrance % 210) <= 156:
                phase = (dx * dy + 137 + takt) % 24
                
                if phase == 12:
                    # Amber-Gold (B-G-R für OpenCV)
                    framebuffer[y:y+4, x:x+4] = [0, 190, 255]
                elif phase in prime_rays:
                    # Electrical Cyan (B-G-R für OpenCV)
                    framebuffer[y:y+4, x:x+4] = [255, 255, 0]
    return framebuffer

if __name__ == "__main__":
    engine = PTRCModularClockEngine()
    
    temp_dir = "ptrc_temp_frames"
    final_video = "ptrc_3s_transposed_flight.mp4"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180  # 3 Sekunden bei 60 FPS
    print(f"[ 1/3 ] Starte ganzzahliges Transponieren ({total_frames} Frames, 1080p)...")
    
    for f in range(total_frames):
        frame = render_1080p_frame(engine, f)
        
        file_path = f"{temp_dir}/frame_{f:04d}.png"
        cv2.imwrite(file_path, frame)
        
        if f % 30 == 0:
            print(f"        Matrix-Transposition: Frame {f}/{total_frames} vollzogen.")

    print("\n[ 2/3 ] Bündele den rein ganzzahligen Datenstrom via ffmpeg...")
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
        print(f"\n[ FEHLER ] ffmpeg fehlgeschlagen:\n{e.stderr.decode()}")
        sys.exit(1)
        
    print("\n[ 3/3 ] Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"\n[ PIEPERFEKT ] Das transponierte Gitter liegt bereit: {final_video}")
