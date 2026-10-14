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

def render_1080p_frame(engine, depth_shift):
    """Rendert ein absolut stabiles, rauschfreies 3D-Hologramm ohne Stroboskop-Blitzen"""
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Tiefer kosmischer Indigo-Hintergrund (BGR)
    framebuffer[:, :] = [35, 15, 20]
    
    # Fixierte Kristallachse 96 (Symmetrie-Anker)
    axis_idx = 96
    axis = engine.crystal_axes[axis_idx]
    
    # Die 8 invarianten Primstrahlen der Modulo-24-Uhr (Plichta-Basis)
    uhr_rays = [1, 5, 7, 11, 13, 17, 19, 23]
    
    # DIE 48 PRIMORIALEN STRÄNGE MODULO 210
    sieb_strands = [
        1, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 
        71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 121, 127, 131, 137, 139, 
        143, 149, 151, 157, 163, 167, 169, 173, 179, 181, 187, 191, 193, 197, 199, 209
    ]
    
    # Der Tiefenvorschub in die Speicherebene
    z = int(depth_shift)
    
    # Schrittweite 4 fuer fluessiges, schnelles i3-Baking
    for y in range(0, height, 4): 
        for x in range(0, width, 4):
            nx = x - (width // 2)
            ny = y - (height // 2)
            
            # STABILE SPIEGEL-SITUATION (Kein Wechsel mehr pro Frame!)
            # Die 90-Grad-Kreuzung steht felsenfest im Raum
            mx = -nx
            my = ny
            
            # Die Tiefenkomponente z verschiebt die Raumstruktur ganzzahlig
            dx = mx + z
            dy = my + z
                
            quadrance = dx*dx + dy*dy
            
            # Filter 1: Das 48-Strang-Raumsieb modulo 210
            if (quadrance % 210) in sieb_strands:
                # Filter 2: Die zeitliche Phaseninterferenz der modulo 24 Uhr
                # Das z im Phasenschluss sorgt fuer das harmonische Wandern der Knoten
                phase = (dx * dy + 137 + z) % 24
                
                if phase == 12:
                    framebuffer[y:y+4, x:x+4] = [0, 190, 255]      # Amber-Gold (Masse)
                elif phase in uhr_rays:
                    framebuffer[y:y+4, x:x+4] = [255, 255, 0]      # Electrical Cyan (Energie)
    return framebuffer

if __name__ == "__main__":
    engine = PTRCModularClockEngine()
    
    temp_dir = "ptrc_temp_frames"
    final_video = "ptrc_3s_primorial_hologram.mp4"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    total_frames = 180
    print(f"[ 1/3 ] Bake rauschfreie 48-Strang-Tiefenstruktur ({total_frames} Frames)...")
    
    for f in range(total_frames):
        # Sanfter Ganzzahl-Vorschub: 4 Einheiten pro Frame tief in die Struktur
        depth_shift = f * 4
        
        frame = render_1080p_frame(engine, depth_shift)
        file_path = f"{temp_dir}/frame_{f:04d}.png"
        cv2.imwrite(file_path, frame)
        
        if f % 30 == 0:
            print(f"        Tiefenstufe: {depth_shift} Einheiten vorwaerts gedrungen.")

    print("\n[ 2/3 ] Buendele stabilisierten Ganzzahl-Datenstrom via ffmpeg...")
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
        print(f"        Erfolg: '{final_video}' wurde absolut flackerfrei erzeugt!")
    except subprocess.CalledProcessError:
        print(f"\n[ FEHLER ] ffmpeg-Kompilierung fehlgeschlagen!")
        sys.exit(1)
        
    print("\n[ 3/3 ] Systembereinigung...")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"\n[ PIEPERFEKT ] Das stabile Hologramm liegt bereit: {final_video}")
