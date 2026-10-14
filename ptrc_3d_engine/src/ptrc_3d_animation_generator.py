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

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from ptrc_3d_hologram_engine import PTRC3DHologramEngine

def render_animation_frame(engine, frame_idx):
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    framebuffer[:, :] = (35, 15, 20)  # Indigo Hintergrund
    
    # Kugel-Parameter (144er Symmetrie-Radius im Quadrat)
    radius = 144
    radius_sq = radius * radius
    
    # 3D-Flugbahn der Kugel (Ganzzahlige Schritte rauf, runter und durch die Tiefe Z)
    cx = -250 + (frame_idx * 4)
    cy = 120 - (frame_idx * 2)
    cz = 150 + (frame_idx * 3)
    
    for y in range(0, height, 4):
        for x in range(0, width, 4):
            vx = x - width // 2
            vy = y - height // 2
            
            # Distanz des Pixelstrahls zur fliegenden Kugel
            dx_ball = vx - cx
            dy_ball = vy - cy
            dist_sq = dx_ball*dx_ball + dy_ball*dy_ball
            
            if dist_sq <= radius_sq:
                # OBERFLÄCHEN-SPIEGELUNG: Die Kugel wirft die Strahlen über die 
                # gekreuzten Achsen negativ zurück in die pTRC-Engine
                rx = -dx_ball * 2
                ry = -dy_ball * 2
                rz = -cz  # Inversion in die Tiefe
                
                state = engine.compute_state(rx, ry, rz, frame_idx)
                if state == 1:
                    framebuffer[y:y+4, x:x+4] = (150, 230, 255)  # Glänzendes Amber-Gold
                elif state == 2:
                    framebuffer[y:y+4, x:x+4] = (255, 255, 200)  # Glänzendes Neon-Cyan
                else:
                    framebuffer[y:y+4, x:x+4] = (50, 30, 40)     # Spiegelnder Kugel-Körper
            else:
                # DAS ENTKOPPELTE, REIN MATHEMATISCHE LEUCHT-GITTER
                state = engine.compute_state(vx, vy, cz, frame_idx)
                if state == 1:
                    framebuffer[y:y+4, x:x+4] = (0, 190, 255)    # Harmonisch verdicktes Amber-Gold
                elif state == 2:
                    framebuffer[y:y+4, x:x+4] = (255, 255, 0)    # Harmonisch verdicktes Neon-Cyan
                    
    return framebuffer

if __name__ == "__main__":
    engine = PTRC3DHologramEngine()
    temp_dir = os.path.join(current_dir, "ptrc_temp_frames")
    final_video = os.path.join(current_dir, "ptrc_3d_sphere_flight.mp4")
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180
    print(f"[ 1/3 ] Starte rein modulare 3D-Animations-Projektion ({total_frames} Frames)...")
    
    for f in range(total_frames):
        frame = render_animation_frame(engine, f)
        file_path = os.path.join(temp_dir, f"frame_{f:04d}.png")
        cv2.imwrite(file_path, frame)
        if f % 30 == 0:
            print(f"        Taktstufe: {f}/{total_frames} Z-layers and shadows baked.")

    print("\n[ 2/3 ] Bündele den rein ganzzahligen Datenstrom via ffmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "60", "-i", os.path.join(temp_dir, "frame_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", final_video
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
        
    print(f"\n[ PIEPERFEKT ] Die rein ganzzahlige Animation liegt bereit: {final_video}")
