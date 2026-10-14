# ==============================================================================
# pTRC Framework - 1080p High-Resolution 1-Pixel Spatial Sieve Renderer
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
#
# DUAL-LICENSING NOTICE:
# Non-commercial, academic, and open-source usage is strictly governed by 
# the GNU General Public License version 3 (GPLv3). Any commercial deployment,
# integration into proprietary, closed-source codebases, or corporate 
# utilization explicitly requires a separate, individually negotiated 
# Proprietary Commercial License from the copyright holder.
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
    
    # Tiefer kosmischer Indigo-Hintergrund (BGR)
    framebuffer[:, :] = (35, 15, 20)
    
    # 144er Kristall-Radius im Quadrat
    radius = 180
    radius_sq = radius * radius
    
    # Sanfter, kontinuierlicher 3D-Flug des Kugelzentrums
    cx = -300 + (frame_idx * 3)
    cy = 150 - (frame_idx * 1)
    cz = 100 + (frame_idx * 2)
    
    # Takt-Dynamik gekoppelt an das 137er-Planck-Limit
    t = int(frame_idx)
    
    # RADIKALER 1-PIXEL-DEEP-SCAN: Berechnet jeden Bildpunkt einzeln für maximale Schärfe!
    for y in range(0, height, 1): 
        for x in range(0, width, 1):
            vx = x - width // 2
            vy = y - height // 2
            
            # Distanz zum Kugel-Resonanzzentrum
            dx_ball = vx - cx
            dy_ball = vy - cy
            dist_sq = dx_ball * dx_ball + dy_ball * dy_ball
            
            if dist_sq <= radius_sq:
                # REINE HOLOGRAFISCHE KREUZSPIEGELUNG AUF DER OBERFLÄCHE
                # Der 1414-Overhead beugt das Feld direkt auf der Kugelkrümmung
                rx = vx + ((dx_ball * 1414) // 1000)
                ry = vy + ((dy_ball * 1414) // 1000)
                rz = cz - (t % 24)
                
                state = engine.compute_state(rx, ry, rz, t)
                if state == 1:
                    framebuffer[y, x] = (100, 220, 255)  # Aufglühendes Bernstein-Gold
                elif state == 2:
                    framebuffer[y, x] = (255, 255, 180)  # Hochauflösendes Neon-Cyan
                else:
                    framebuffer[y, x] = (55, 25, 30)     # Strukturierter Kugel-Körper
            else:
                # UNGESTÖRTES HINTERGRUND-GITTER
                state = engine.compute_state(vx, vy, cz, t)
                if state == 1:
                    framebuffer[y, x] = (0, 190, 255)    # Messerscharfe Gold-Streben
                elif state == 2:
                    framebuffer[y, x] = (255, 255, 0)    # Messerscharfe Neon-Cyan Röhren
                    
    return framebuffer

if __name__ == "__main__":
    engine = PTRC3DHologramEngine()
    temp_dir = os.path.join(current_dir, "ptrc_temp_frames")
    final_video = os.path.join(current_dir, "ptrc_3d_sphere_flight.mp4")
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180  # 3 Sekunden echtes 60-FPS-Kino-Profil
    print(f"[ 1/3 ] Aktiviere 1-Pixel-Deep-Scan Pipeline ({total_frames} Frames)...")
    
    for f in range(total_frames):
        frame = render_animation_frame(engine, f)
        file_path = os.path.join(temp_dir, f"frame_{f:04d}.png")
        cv2.imwrite(file_path, frame)
        if f % 30 == 0:
            print(f"        Auflösungs-Audit: Frame {f}/{total_frames} ultra-scharf auf die Platte gehämmert.")

    print("\n[ 2/3 ] Bündele unkomprimierten 1080p-Datenstrom via ffmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "60", "-i", os.path.join(temp_dir, "frame_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15", final_video  # CRF 15 für absolute Studio-Qualität
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"        Erfolg: Ultra-HD Matrix-Stream stabil in '{final_video}' gegossen!")
    except subprocess.CalledProcessError:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen!")
        sys.exit(1)
        
    print("\n[ 3/3 ] Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"\n[ PIEPERFEKT ] Das hochauflösende 3D-Hologramm steht bereit: {final_video}")
