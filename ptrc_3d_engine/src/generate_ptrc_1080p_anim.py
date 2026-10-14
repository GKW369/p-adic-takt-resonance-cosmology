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

def render_1080p_frame(engine, cam_x, cam_y, cam_z, frame_idx):
    """Erzeugt ein Full-HD Frame (1920 x 1080) mit dynamischer Transformation"""
    width, height = 1920, 1080
    
    # Tiefer kosmischer Indigo-Hintergrund (BGR für OpenCV)
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    framebuffer[:, :] = [40, 0, 20]
    
    # Dynamische Projektionsachse basierend auf dem Takt
    axis_idx = (engine.global_master_clock + frame_idx) % 144
    axis = engine.crystal_axes[axis_idx]
    
    # Die erlaubten Primzahlen-Strahlen des Z/24Z-Uhrsystems
    prime_rays = [1, 5, 7, 11, 13, 17, 19, 23]
    
    # Schrittweite 4 für schnelles, flüssiges Test-Rendering
    for y in range(0, height, 4): 
        for x in range(0, width, 4):
            dx = (x - width // 2) + int(cam_x)
            dy = (y - height // 2) + int(cam_y)
            quadrance = dx*dx + dy*dy
            
            if (quadrance % 210) <= 156:
                phase = (dx * dy + 137 + int(cam_z)) % 24
                
                if phase == 12:
                    # Amber-Gold (B-G-R für OpenCV)
                    framebuffer[y:y+4, x:x+4] = [0, 190, 255]
                elif phase in prime_rays:
                    # Electrical Cyan (B-G-R für OpenCV)
                    framebuffer[y:y+4, x:x+4] = [255, 255, 0]
    return framebuffer

if __name__ == "__main__":
    engine = PTRCModularClockEngine()
    
    # Temporärer Ordner und finales Video
    temp_dir = "ptrc_temp_frames"
    final_video = "ptrc_3s_test_flight.mp4"
    
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180  # 3 Sekunden bei 60 FPS
    print(f"[ 1/3 ] Starte Frame-Baking ({total_frames} Frames, 1080p)...")
    
    for f in range(total_frames):
        # Dynamische Flugbahn: Spirale ins Zentrum
        angle = (f * 2 * np.pi) / 90
        radius = 400 - (f * 1.5)
        
        cam_x = radius * np.cos(angle)
        cam_y = radius * np.sin(angle)
        cam_z = f * 3
        
        frame = render_1080p_frame(engine, cam_x, cam_y, cam_z, f)
        
        file_path = f"{temp_dir}/frame_{f:04d}.png"
        cv2.imwrite(file_path, frame)
        
        if f % 30 == 0:
            print(f"        Fortschritt: {f}/{total_frames} Frames fertig.")

    print("\n[ 2/3 ] Starte automatische ffmpeg-Videobündelung...")
    
    # Der ffmpeg-Befehl als systemunabhängiges Array
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "60",
        "-i", f"{temp_dir}/frame_%04d.png",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        final_video
    ]
    
    # Führt ffmpeg direkt im Hintergrund aus
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"        Erfolg: '{final_video}' wurde fehlerfrei generiert!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen:\n{e.stderr.decode()}")
        sys.exit(1)
        
    print("\n[ 3/3 ] Starte Systembereinigung (Lösche temporäre Bilder)...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print("        Bereinigung abgeschlossen: 25-GB-Speicherrisiko eliminiert.")
        
    print(f"\n[ PIEPERFEKT ] Dein 3-Sekunden-Flug liegt bereit: {final_video}")
