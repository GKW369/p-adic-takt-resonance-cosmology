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

def render_animation_frame(engine, absolute_takt, eye_offset=0):
    """
    Rendert ein Frame. 'eye_offset' ist der ganzzahlige Adress-Versatz 
    für die spätere 3D-Headset-Stereoskopie!
    """
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    framebuffer[:, :] = (35, 15, 20)  # Indigo
    
    t = int(absolute_takt)
    radius_sq = 144 * 144  # Gekoppelt an die 144er-Vektor-Matrix
    
    # 3D-Kugelzentrum wandert rein ganzzahlig
    cx = -300 + (t // 40) + eye_offset
    cy = 150 - (t // 80)
    cz = 200 + (t // 60)
    
    for y in range(0, height, 4):
        for x in range(0, width, 4):
            vx = x - width // 2
            vy = y - height // 2
            
            dx_ball = vx - cx
            dy_ball = vy - cy
            dist_sq = dx_ball * dx_ball + dy_ball * dy_ball
            
            # PRÜFUNG: SCHNITTSTELLE KUGELOBERFLÄCHE
            if dist_sq <= radius_sq:
                # LICHTAUSBREITUNGS-EFFEKT:
                # Wir berechnen die Lichtbrechung auf der Kugel über den 144er-Kanal-Faktor
                rx = vx + ((dx_ball * 144) // 137)
                ry = vy + ((dy_ball * 144) // 137)
                rz = cz - (t % 153)
                
                state = engine.compute_state(rx, ry, rz, t)
                if state == 1:
                    framebuffer[y:y+4, x:x+4] = (100, 210, 255) # Plastisches Gold-Glühen
                elif state == 2:
                    framebuffer[y:y+4, x:x+4] = (255, 255, 180) # Neon-Cyan Licht-Kaskade
                else:
                    framebuffer[y:y+4, x:x+4] = (60, 25, 35)    # Kugel-Körper
            else:
                # STRÖMUNGSMISCHUNG & FLUID-RESORANZ IM HINTERGRUND
                if cx < vx < cx + 400 and abs(dy_ball) < 180:
                    sog_x = vx - (t % 24)
                    sog_y = vy + (1 if vy < cy else -1)
                    state = engine.compute_state(sog_x, sog_y, cz, t)
                else:
                    state = engine.compute_state(vx, vy, cz, t)
                    
                if state == 1:
                    framebuffer[y:y+4, x:x+4] = (0, 190, 255)   # Amber Gitterbalken
                elif state == 2:
                    framebuffer[y:y+4, x:x+4] = (255, 255, 0)   # Leuchtende Neonröhren
                elif cx < vx < cx + 200 and state == 0:
                    framebuffer[y:y+4, x:x+4] = (45, 15, 60)    # Fluid-Wirbel-Schimmer
                    
    return framebuffer

if __name__ == "__main__":
    engine = PTRC3DHologramEngine()
    temp_dir = os.path.join(current_dir, "ptrc_temp_frames")
    final_video = os.path.join(current_dir, "ptrc_3d_sphere_flight.mp4")
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 120
    print(f"[ 1/3 ] Bake 137-Takt-Animation mit 144-Vektor Lichtbrechung...")
    
    for f in range(total_frames):
        # Refresh exakt alle 137 Takte (Alpha-Axiom)
        absolute_takt = f * 137
        
        frame = render_animation_frame(engine, absolute_takt, eye_offset=0)
        file_path = os.path.join(temp_dir, f"frame_{f:04d}.png")
        cv2.imwrite(file_path, frame)
        if f % 20 == 0:
            print(f"        Realität erzeugt bei Takt: {absolute_takt}")

    print("\n[ 2/3 ] Bündele 137-Takt-Datenstrom via ffmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "30", "-i", os.path.join(temp_dir, "frame_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", final_video
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"        Erfolg: '{final_video}' wurde erzeugt!")
    except subprocess.CalledProcessError:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen!")
        sys.exit(1)
        
    print("\n[ 3/3 ] Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"\n[ PIEPERFEKT ] Das quantisierte Licht-Hologramm steht bereit: {final_video}")
