# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer 3D Engine Core
# Module: 4K Ultra-HD Lossless 39-Second Animation Generator (3840 x 2160 @ 60FPS)
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

def generate_animation():
    # 4K-Auflösung und Framerate-Struktur
    width, height = 3840, 2160
    fps = 60
    duration_seconds = 39
    total_frames = fps * duration_seconds # Exakt 2340 Frames
    
    output_dir = "ptrc_output_frames"
    os.makedirs(output_dir, exist_ok=True)
    
    # Versuche PIL zu importieren, falls nicht vorhanden wird es installiert
    try:
        from PIL import Image
    except ImportError:
        import subprocess
        print("[pTRC-SETUP] Installing required package 'pillow' via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
        from PIL import Image

    print("================================================================================")
    print(f"[pTRC-ANIMATION] Initiating 39-Second 4K Ultra-HD Ride: {total_frames} Frames")
    print("================================================================================")
    
    # Axiomatische Gitter-Parameter
    CLOCK_210 = 210
    CLOCK_24 = 24
    ALPHA_137 = 137
    allowed_rays = {1, 5, 7, 11, 13, 17, 19, 23}
    
    # Vorbereiten des Koordinatengitters im RAM (Vektorisierte Indizes für Performance)
    y_indices, x_indices = np.indices((height, width), dtype=np.int64)
    
    for frame_idx in range(total_frames):
        # --- REINE GANZZAHL-KAMERASTEUERUNG (Achterbahn vs. Ruhe) ---
        # Wir steuern den dynamischen Pfad ohne Sinus/Float rein über Frame-Modulo
        
        # Phase 1: Ruhiger Zoom (Frames 0 bis 599)
        if frame_idx < 600:
            zoom_factor = 1000 + (frame_idx * 2)
            shift_x = 0
            shift_y = 0
        # Phase 2: Achterbahn-Sturzflug und harte Kurven (Frames 600 bis 1499)
        elif frame_idx < 1500:
            ride_takt = frame_idx - 600
            zoom_factor = 2200 + ((ride_takt * ride_takt) // 200) # Exponentieller Sturz
            shift_x = ((ride_takt * 8) % 800) - 400
            shift_y = ((ride_takt * ride_takt // 30) % 600) - 300
        # Phase 3: Abbremsen und majestätischer Orbit (Frames 1500 bis 2339)
        else:
            slow_takt = frame_idx - 1500
            zoom_factor = 8000 - (slow_takt * 3) # Sanftes Zurückgleiten
            shift_x = int(300 * ((slow_takt % 240) - 120) // 120)
            shift_y = int(200 * (((slow_takt + 60) % 240) - 120) // 120)

        # Frame-Puffer initialisieren
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Kamera-Zentrum im diskreten Raum verschieben
        cx = (width // 2) + shift_x
        cy = (height // 2) + shift_y
        
        dx = x_indices - cx
        dy = y_indices - cy
        
        # Quadrance skaliert berechnen für den unendlichen Zoom
        quadrance = ((dx*dx + dy*dy) * 1000) // zoom_factor
        
        # Sieve und Phase berechnen
        residuum_210 = quadrance % CLOCK_210
        sieve_active = (residuum_210 <= 156)
        ray_phase = (x_indices * y_indices + ALPHA_137 + frame_idx) % CLOCK_24
        
        # A: Hintergrund-Vakuum-Welle (Wechselt im Takt der 137)
        bg_shading = ((quadrance % ALPHA_137) * 45) // ALPHA_137
        img_array[..., 0] = bg_shading // 3
        img_array[..., 1] = bg_shading // 4
        img_array[..., 2] = bg_shading // 2
        
        # B: Quanten-Energie-Flusslinien (Cyan)
        cyan_mask = sieve_active & np.isin(ray_phase, list(allowed_rays))
        img_array[cyan_mask, 0] = 0
        img_array[cyan_mask, 1] = (180 + (quadrance[cyan_mask] % 75)) & 255
        img_array[cyan_mask, 2] = (210 + (quadrance[cyan_mask] % 45)) & 255
        
        # C: Invariante Massen-Knoten (Bernstein-Gold)
        gold_mask = sieve_active & (ray_phase == 12)
        img_array[gold_mask, 0] = (230 + (quadrance[gold_mask] % 25)) & 255
        img_array[gold_mask, 1] = (160 + (quadrance[gold_mask] % 35)) & 255
        img_array[gold_mask, 2] = 24
        
        # Frame abspeichern via Pillow
        img = Image.fromarray(img_array, 'RGB')
        frame_filename = os.path.join(output_dir, f"frame_{frame_idx:04d}.png")
        img.save(frame_filename, format="PNG")
        
        # Live-Telemetrie im Terminal ausgeben
        if frame_idx % 60 == 0:
            progress = (frame_idx * 100) // total_frames
            print(f" -> Progress: {progress}% | Rendered Takt-Frame {frame_idx}/{total_frames} | Zoom: {zoom_factor}")

    print(f"\n[ SUCCESS ] All {total_frames} 4K frames successfully saved in '{output_dir}/'!")
    print("\n=== SO ERSTELLST DU DAS FERTIGE VIDEO FÜR DEINE PRÄSENTATION ===")
    print("Führe einfach diesen Befehl in deinem Terminal aus:")
    print(f"ffmpeg -framerate 60 -i {output_dir}/frame_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 ptrc_39s_presentation_4k.mp4")

if __name__ == "__main__":
    import numpy as np # Absicherung für den globalen Scope
    generate_animation()

