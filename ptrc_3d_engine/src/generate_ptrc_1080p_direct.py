# ==============================================================================
# pTRC Framework - 1080p Holographic Crystal Flight Pipeline (Ebene 1 Start)
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

def render_1080p_frame(engine, depth_level, frame_idx):
    """Rendert die holografische Projektion startend von Ebene 1"""
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Tiefer kosmischer Indigo-Hintergrund
    framebuffer[:, :] = [35, 15, 20]
    
    # Fixierte Kristallachse 96 (Symmetrie-Anker)
    axis_idx = 96
    axis = engine.crystal_axes[axis_idx]
    prime_rays = [1, 5, 7, 11, 13, 17, 19, 23]
    
    # Der aktuelle Zustand auf der Speicherebene (Z)
    dz = int(depth_level)
    
    # Schrittweite 2 für scharfe Fernseher-Projektion
    for y in range(0, height, 2): 
        for x in range(0, width, 2):
            dx = x - width // 2
            dy = y - height // 2
            
            # HOLOGRAFISCHE WECHSELWIRKUNG:
            # Die Quadranz skaliert mit der Speicherebene dz, da das Gitter
            # mit seinen Außengrenzen interagiert. Das erzeugt die echte Umhüllung!
            quadrance = (dx*dx + dy*dy) * dz
            
            # Raumsieb modulo 210 filtert die unendliche Zahl
            if (quadrance % 210) <= 156:
                # Phasen-Interferenz zwischen Speicher-Ebene und Raum-Hologramm
                phase = (dx * dy * dz + 137) % 24
                
                if phase == 12:
                    framebuffer[y:y+2, x:x+2] = [0, 190, 255]     # Amber-Gold (Masse)
                elif phase in prime_rays:
                    framebuffer[y:y+2, x:x+2] = [255, 255, 0]     # Electrical Cyan (Energie)
    return framebuffer

if __name__ == "__main__":
    engine = PTRCModularClockEngine()
    
    temp_dir = "ptrc_temp_frames"
    final_video = "ptrc_3s_hologram_flight.mp4"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180  # 3 Sekunden bei 60 FPS
    print(f"[ 1/3 ] Starte holografischen Tauchgang ab EBENE 1 ({total_frames} Frames)...")
    
    for f in range(total_frames):
        # Wir starten exakt bei Ebene 1 und rücken pro Frame um 1 p-adische Ebene vor
        depth_level = 1 + f
        
        frame = render_1080p_frame(engine, depth_level, f)
        
        file_path = f"{temp_dir}/frame_{f:04d}.png"
        cv2.imwrite(file_path, frame)
        
        if f % 30 == 0:
            print(f"        Speicherebene: {depth_level}/{total_frames} wird projiziert.")

    print("\n[ 2/3 ] Bündele holografischen Datenstrom via ffmpeg...")
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
        
    print(f"\n[ PIEPERFEKT ] Das Hologramm ist bereit für den Fernseher: {final_video}")
