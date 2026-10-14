# ==============================================================================
# pTRC Framework - 1080p Flight Path Generator (Test Orbit)
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
# GPLv3 Open Source / Commercial License Required
# ==============================================================================
import os
import sys
import numpy as np
from ptrc_clock_core import PTRCModularClockEngine

def render_1080p_frame(engine, cam_x, cam_y, cam_z, frame_idx):
    # Erzeugt ein Full-HD Frame (1920 x 1080)
    width, height = 1920, 1080
    framebuffer = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Dynamische Projektionsachse basierend auf dem Takt
    axis_idx = (engine.global_master_clock + frame_idx) % 144
    axis = engine.crystal_axes[axis_idx]
    
    # Hier wird die mathematische Raummatrix durch das Sieb gezogen
    for y in range(0, height, 4): # Schrittweite 4 für extrem schnelles Test-Rendering
        for x in range(0, width, 4):
            # Transformation der Pixelkoordinaten mit der bewegten Kamera
            dx = (x - width // 2) + int(cam_x)
            dy = (y - height // 2) + int(cam_y)
            quadrance = dx*dx + dy*dy
            
            if (quadrance % 210) <= 156:
                phase = (dx * dy + 137 + int(cam_z)) % 24
                if phase == 12:
                    framebuffer[y:y+4, x:x+4] = [255, 191, 0]  # Amber-Gold (Masse)
                elif phase in:
                    framebuffer[y:y+4, x:x+4] = [0, 230, 240]  # Cyan (Energie)
    return framebuffer

if __name__ == "__main__":
    engine = PTRCModularClockEngine()
    output_dir = "ptrc_test_frames"
    os.makedirs(output_dir, exist_ok=True)
    
    total_frames = 180 # 3 Sekunden bei 60 FPS
    print(f"[ START ] Generating {total_frames} Frames in Full-HD...")
    
    for f in range(total_frames):
        # DYNAMISCHE KAMERABEWEGUNG: Die Kamera fliegt im Kreis und sinkt ab
        angle = (f * 2 * np.pi) / 60  # Eine volle Drehung pro Sekunde
        radius = 300 - (f * 0.5)      # Kamera fliegt langsam nach innen
        
        cam_x = radius * np.cos(angle)
        cam_y = radius * np.sin(angle)
        cam_z = f * 2                 # Verschiebung auf der Z-Zustandsachse
        
        frame = render_1080p_frame(engine, cam_x, cam_y, cam_z, f)
        
        # Als unkomprimiertes, schnelles BMP oder PNG speichern
        import cv2
        cv2.imwrite(f"{output_dir}/frame_{f:04d}.png", frame)
        
        if f % 10 == 0:
            print(f"Bake Progress: {f}/{total_frames} frames done.")
            
    print("[ SUCCESS ] Test-Frames ready for ffmpeg.")
