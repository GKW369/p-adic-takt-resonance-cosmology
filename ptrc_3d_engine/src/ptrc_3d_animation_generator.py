# ==============================================================================
# pTRC Framework - 1080p Kaleidoscope Takt-Synchronized Retina Video Encoder
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
#
# DUAL-LICENSING NOTICE:
# Non-commercial, academic, and open-source usage is strictly governed by 
# the GNU General Public License version 3 (GPLv3). Any commercial deployment,
# integration into proprietary, closed-source codebases, or corporate 
# utilization explicitly requires a separate, individually negotiated license.
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
    framebuffer[:, :] = (15, 5, 8)  # Spektrales Ruhe-Blau (Hintergrund)
    
    t = int(frame_idx)
    radius_sq = 144 * 144  # Der 144-seitige Raumkristall-Radius
    
    # Ganzzahlige 3D-Flugbahn der Kugel
    cx = -300 + (t * 3)
    cy = 120 - (t * 1)
    cz = 120 + (t * 2)
    
    ipd_offset = 24  # Diskreter Augenabstand (Modulo-24 gekoppelt)
    
    # RADIKALER 1-PIXEL-DEEP-SCAN IM HOLOGRAPHISCHEN KREUZRAUM
    for y in range(0, height, 1):
        for x in range(0, width, 1):
            vx = x - width // 2
            vy = y - height // 2
            
            dx_ball = vx - cx
            dy_ball = vy - cy
            dist_sq = dx_ball * dx_ball + dy_ball * dy_ball
            
            # --- DOPPELSPALT-DUALITÄT (KANALTRENNUNG IN Z VIA KALEIDOSKOP) ---
            
            # 1. LINKES AUGE (Rot-Kanal)
            if dist_sq <= radius_sq:
                rx = vx + ((dx_ball * 144) // 137)
                ry = vy + ((dy_ball * 144) // 137)
                state_left = engine.compute_retinal_state(rx, ry, cz - (t % 24), t, -ipd_offset)
            else:
                state_left = engine.compute_retinal_state(vx, vy, cz, t, -ipd_offset)
                
            # 2. RECHTES AUGE (Cyan-Kanal)
            if dist_sq <= radius_sq:
                rx = vx + ((dx_ball * 144) // 137)
                ry = vy + ((dy_ball * 144) // 137)
                state_right = engine.compute_retinal_state(rx, ry, cz - (t % 24), t, ipd_offset)
            else:
                state_right = engine.compute_retinal_state(vx, vy, cz, t, ipd_offset)
            
            # Absolute, ungerundete Zuweisung im biologischen BGR-Spektrum
            r_val = 130 if state_left == 1 else (220 if state_left == 2 else 0)
            g_val = 90 if state_right == 1 else (160 if state_right == 2 else 0)
            b_val = 180 if state_right == 1 else (255 if state_right == 2 else 0)
                
            if dist_sq <= radius_sq and state_left == 0 and state_right == 0:
                framebuffer[y, x] = (40, 15, 20)  # Gekreuzter 90-Grad-Spiegelkörper
            else:
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
    print(f"[ 1/3 ] Starte 100% fließkommafreie Matrix-Pipeline ({total_frames} Frames)...")
    
    for f in range(total_frames):
        frame = render_stereoscopic_frame(engine, f)
        cv2.imwrite(os.path.join(temp_dir, f"frame_{f:04d}.png"), frame)
        if f % 24 == 0:
            print(f"        Takt-Synchronisation: Frame {f}/{total_frames} im 4-Quadranten-Kreuz verankert.")

    print("\n[ 2/3 ] Bündele Datenstrom SYNCHRONISIERT AUF DEN MODULO-24 TIMING-TAKT...")
    # CRF 0 und -g 1 erzwingen unbestechliche, pixelscharfe Keyframes bei genau 24 FPS
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "24", "-i", os.path.join(temp_dir, "frame_%04d.png"),
        "A", "-c:v", "libx264", "-crf", "0", "-preset", "veryslow", "-g", "1", "-pix_fmt", "yuv420p", final_video
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"        Erfolg: Verlustfreies 4-Hologramm-Video in '{final_video}' erstarrt!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen: {e.stderr.decode()}")
        sys.exit(1)
        
    print("\n[ 3/3 ] Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"\n[ SYSTEMTAKT AKTIV ] Das raster-abgestimmte Video steht bereit: {final_video}")
