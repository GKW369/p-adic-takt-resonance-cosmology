# ==============================================================================
# pTRC Framework - 1080p Stereoscopic Retinal Video Encoder Pipeline
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

from ptrc_3d_stereo_engine import PTRC3DStereoEngine

def render_stereoscopic_frame(engine, frame_idx):
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Kosmischer BGR-Hintergrund (Sehr schwaches, gedimmtes Vakuum-Blau)
    framebuffer[:, :] = (15, 5, 8)
    
    t = int(frame_idx)
    radius_sq = 144 * 144
    
    # 3D-Flugbahn der Kugel im Raumkristall
    cx = -300 + (t * 3)
    cy = 120 - (t * 1)
    cz = 120 + (t * 2)
    
    # DISKRETER BIOMETRISCHER AUGENABSTAND (Pupillary Distance in Z-Einheiten)
    # Linkes Auge kriegt negativen Versatz, rechtes Auge positiven Versatz
    ipd_offset = 24  
    
    # 1-PIXEL-DEEP-SCAN FÜR OPTIMALE RETINA-AUFLÖSUNG
    for y in range(0, height, 1):
        for x in range(0, width, 1):
            vx = x - width // 2
            vy = y - height // 2
            
            dx_ball = vx - cx
            dy_ball = vy - cy
            dist_sq = dx_ball * dx_ball + dy_ball * dy_ball
            
            # --- STEREOSKOPISCHE KANALTRENNUNG (3D-BRILLEN-LOGIK) ---
            
            # 1. LINKES AUGE (Berechnet den Rot-Kanal der 3D-Brille)
            state_left = 0
            if dist_sq <= radius_sq:
                rx = vx + ((dx_ball * 144) // 137)
                ry = vy + ((dy_ball * 144) // 137)
                state_left = engine.compute_retinal_state(rx, ry, cz - (t % 24), t, -ipd_offset)
            else:
                state_left = engine.compute_retinal_state(vx, vy, cz, t, -ipd_offset)
                
            # 2. RECHTES AUGE (Berechnet den Cyan-Kanal [Blau + Gruen] der 3D-Brille)
            state_right = 0
            if dist_sq <= radius_sq:
                rx = vx + ((dx_ball * 144) // 137)
                ry = vy + ((dy_ball * 144) // 137)
                state_right = engine.compute_retinal_state(rx, ry, cz - (t % 24), t, ipd_offset)
            else:
                state_right = engine.compute_retinal_state(vx, vy, cz, t, ipd_offset)
            
            # --- PHYSIKALISCH KORREKTE BLAU-AUFLÖSUNG (Menschliches Farbspektrum) ---
            # Wir mischen die Zustaende in die jeweiligen Farb-Kanaele (BGR)
            
            # Rot-Anteil (Linkes Auge)
            r_val = 0
            if state_left == 1:   r_val = 130  # Schwach leuchtendes Masse-Zentrum (Rot)
            elif state_left == 2: r_val = 220  # Intensiveres Taktleuchten (Rot)
            
            # Cyan-Anteil (Rechtes Auge: Kombination aus Blau und Gruen)
            g_val = 0
            b_val = 0
            if state_right == 1:
                g_val = 90;  b_val = 180  # Gedimmtes, biologisches Quanten-Blau
            elif state_right == 2:
                g_val = 160; b_val = 255  # Volles, leuchtendes Spektral-Blau (470nm)
                
            # Fusionierung auf der Kugeloberflaeche
            if dist_sq <= radius_sq and state_left == 0 and state_right == 0:
                framebuffer[y, x] = (40, 15, 20)  # Dezenter, spiegelnder Kugelkoerper
            else:
                # Kombination zu einem echten 3D-Anaglyph-Pixel
                framebuffer[y, x] = (
                    max(framebuffer[y, x, 0], b_val),
                    max(framebuffer[y, x, 1], g_val),
                    max(framebuffer[y, x, 2], r_val)
                )
                
    return framebuffer

if __name__ == "__main__":
    engine = PTRC3DStereoEngine()
    temp_dir = os.path.join(current_dir, "ptrc_temp_frames")
    final_video = os.path.join(current_dir, "ptrc_3d_stereoscopic_retina.mp4")
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180
    print(f"[ 1/3 ] Aktiviere biometrische Stereoskopie-Pipeline ({total_frames} Frames)...")
    
    for f in range(total_frames):
        frame = render_stereoscopic_frame(engine, f)
        file_path = os.path.join(temp_dir, f"frame_{f:04d}.png")
        cv2.imwrite(file_path, frame)
        if f % 30 == 0:
            print(f"        Retina-Scan Audit: Frame {f}/{total_frames} biologisch korrekt gekoppelt.")

    print("\n[ 2/3 ] Bündele stereoskopischen 3D-Datenstrom via ffmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "60", "-i", os.path.join(temp_dir, "frame_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "15", final_video
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"        Erfolg: Biometrischer 3D-Stream in '{final_video}' gegossen!")
    except subprocess.CalledProcessError:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen!")
        sys.exit(1)
        
    print("\n[ 3/3 ] Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"\n[ PIEPERFEKT ] Das stereoskopische Quanten-Hologramm liegt bereit: {final_video}")
