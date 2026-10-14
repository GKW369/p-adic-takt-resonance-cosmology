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

def render_1080p_frame(engine, depth_shift, frame_idx):
    """Rendert ein Full-HD Frame, indem sich der Beobachter DURCH die p-adischen Schichten bewegt"""
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Tiefer kosmischer Indigo-Hintergrund (BGR für OpenCV)
    framebuffer[:, :] = [35, 15, 20]
    
    # FIXIERTE KRISTALLACHSE 96: Perfekte Symmetrie für den rauschfreien Tiefenflug
    axis_idx = 96
    axis = engine.crystal_axes[axis_idx]
    
    # Die 8 erlaubten Primzahlen-Strahlen des Z/24Z-Uhrsystems
    prime_rays = [1, 5, 7, 11, 13, 17, 19, 23]
    
    for y in range(0, height, 1): # Pixelgenau (Schrittweite 1) für maximale Schärfe auf dem Fernseher!
        for x in range(0, width, 1):
            dx = x - width // 2
            dy = y - height // 2
            
            # depth_shift verschiebt uns entlang der Achse durch die Quadranz-Schichten
            quadrance = dx*dx + dy*dy + int(depth_shift)*10
            
            if (quadrance % 210) <= 156:
                phase = (dx * dy + 137 + int(depth_shift)) % 24
                
                if phase == 12:
                    # Amber-Gold (B-G-R für OpenCV)
                    framebuffer[y, x] = [0, 190, 255]
                elif phase in prime_rays:
                    # Electrical Cyan (B-G-R für OpenCV)
                    framebuffer[y, x] = [255, 255, 0]
    return framebuffer

if __name__ == "__main__":
    engine = PTRCModularClockEngine()
    
    temp_dir = "ptrc_temp_frames"
    final_video = "ptrc_3s_test_flight.mp4"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180  # 3 Sekunden bei 60 FPS
    print(f"[ 1/3 ] Starte echten 3D-Tiefenflug auf Achse 96 ({total_frames} Frames, pixelgenau)...")
    
    for f in range(total_frames):
        # Der Tiefen-Vorschub: Wir reisen pro Frame tiefer in die Gitterstruktur
        depth_shift = f * 2
        
        frame = render_1080p_frame(engine, depth_shift, f)
        
        file_path = f"{temp_dir}/frame_{f:04d}.png"
        cv2.imwrite(file_path, frame)
        
        if f % 30 == 0:
            print(f"        Fortschritt: {f}/{total_frames} Frames tiefer eingetaucht.")

    print("\n[ 2/3 ] Bündele stabiles 3D-Video via ffmpeg...")
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
        
    print(f"\n[ PIEPERFEKT ] Schau dir den echten Tiefenflug an: {final_video}")
