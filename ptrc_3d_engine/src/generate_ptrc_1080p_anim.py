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

# Falls deine ptrc_clock_core.py im Hauptverzeichnis liegt, fügen wir den Pfad hinzu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ptrc_clock_core import PTRCModularClockEngine

def render_1080p_frame(engine, cam_x, cam_y, cam_z, frame_idx):
    """Erzeugt ein Full-HD Frame (1920 x 1080) mit dynamischer Transformation"""
    width, height = 1920, 1080
    
    # Tiefer kosmischer Indigo-Hintergrund (OpenCV nutzt BGR-Reihenfolge: B=35, G=15, R=20)
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    framebuffer[:, :] = [35, 15, 20]
    
    # Dynamische Projektionsachse basierend auf dem Takt und Frame-Index
    axis_idx = (engine.global_master_clock + frame_idx) % 144
    axis = engine.crystal_axes[axis_idx]
    
    # Schrittweite 4 für schnelles, ressourcenschonendes Rendern auf dem Acer-Laptop
    for y in range(0, height, 4): 
        for x in range(0, width, 4):
            # Koordinatenverschiebung durch die Kamerabewegung
            dx = (x - width // 2) + int(cam_x)
            dy = (y - height // 2) + int(cam_y)
            quadrance = dx*dx + dy*dy
            
            # Primoriales Raumsieb modulo 210
            if (quadrance % 210) <= 156:
                phase = (dx * dy + 137 + int(cam_z)) % 24
                
                if phase == 12:
                    # Invariante Massenknoten: Amber-Gold (BGR: B=0, G=190, R=255)
                    framebuffer[y:y+4, x:x+4] = [0, 190, 255]
                elif phase in:
                    # 8 Erlaubte Primstrahlen: Electrical Cyan (BGR: B=255, G=255, R=0)
                    framebuffer[y:y+4, x:x+4] = [255, 255, 0]
    return framebuffer

if __name__ == "__main__":
    engine = PTRCModularClockEngine()
    
    # Pfade definieren
    temp_dir = "ptrc_temp_frames"
    final_video = "ptrc_3s_test_flight.mp4"
    
    # Sauberes Erstellen des temporären Ordners
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180  # 3 Sekunden bei 60 FPS
    print(f"[ 1/3 ] Starte Frame-Baking ({total_frames} Frames, 1080p Full-HD)...")
    
    for f in range(total_frames):
        # DYNAMISCHE FLUGBAHN: Die Kamera fliegt in einer Spirale ins Zentrum
        angle = (f * 2 * np.pi) / 90
        radius = 400 - (f * 1.5)
        
        cam_x = radius * np.cos(angle)
        cam_y = radius * np.sin(angle)
        cam_z = f * 3  # Kontinuierlicher p-adischer Taktvorschub pro Frame
        
        # Frame rendern
        frame = render_1080p_frame(engine, cam_x, cam_y, cam_z, f)
        
        # Speichern des Bildes im temporären Ordner
        file_path = f"{temp_dir}/frame_{f:04d}.png"
        cv2.imwrite(file_path, frame)
        
        if f % 30 == 0:
            print(f"        Fortschritt: {f}/{total_frames} Frames erfolgreich berechnet.")

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
        print(f"        Erfolg: '{final_video}' wurde stabil erzeugt!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen:\n{e.stderr.decode()}")
        sys.exit(1)
        
    print("\n[ 3/3 ] Starte Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print("        Bereinigung abgeschlossen: Temporäre Bilder restlos entfernt.")
        
    print(f"\n[ PIEPERFEKT ] Dein 3-Sekunden-Flug liegt bereit: {final_video}")
