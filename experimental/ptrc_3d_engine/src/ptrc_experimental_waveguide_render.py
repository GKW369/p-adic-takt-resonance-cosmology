# ==============================================================================
# pTRC Framework - Experimental Module: Mono-Sieve Phase Cancellation Render
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ==============================================================================

# -*- coding: utf-8 -*-
r"""
pTRC Framework - Experimental Core: Mono/Stereo Phase Cancellation Matrix
Operational Domain: Symmetrical Integer Translation Matrices (\mathbb{Z}^3).
Applies Plichta/Michta cross-mirror inversion to extract pure mono-state invariants
and cancel out continuous noise via clock-phase subtraction layers.
"""

import os
import sys
import subprocess
import numpy as np

class PTRCMonoSieveRotator:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156
        self.SCALE = 1000
        self.crystal_axes = self._build_invariant_axes()

    def _build_invariant_axes(self):
        flat_nodes = [
            2, 1, 0,   2, -1, 0,  -2, 1, 0,  -2, -1, 0,
            0, 2, 1,   0, 2, -1,   0, -2, 1,  0, -2, -1,
            1, 0, 2,  -1, 0, 2,    1, 0, -2, -1, 0, -2
        ]
        base = np.array(flat_nodes, dtype=np.int32).reshape(12, 3)
        axes = []
        for node in base:
            for factor in range(1, 13):
                axes.append(node * factor)
        return np.array(axes, dtype=np.int32)

    def project_mono_cancelled_frame(self, frame_idx, output_dir):
        """
        Nutzt das Prinzip der Audio-Phasenschau: Zieht komplementäre Spiegelachsen
        voneinander ab, um den invarianten Mono-Kern rauschfrei freizulegen.
        """
        frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cx, cy = self.width // 2, self.height // 2
        z_offset = 65
        
        axis_index = frame_idx % 144
        current_axis = self.crystal_axes[axis_index]
        
        # Duale Polarität: Oszilliert über -1 hinaus (Plus/Minus Welten)
        dual_polarity = 1 if (frame_idx % 2 == 0) else -1
        
        ax_x = int(current_axis[0])
        ax_y = int(current_axis[1])
        ax_z = int(current_axis[2])
        
        for dx in range(-15, 16):
            for dy in range(-15, 16):
                for dz in range(-15, 16):
                    
                    quadrance = dx*dx + dy*dy + dz*dz
                    if quadrance == 0:
                        continue
                        
                    if (quadrance % self.primorial_base) > self.invariant_limit:
                        continue
                        
                    # DIE ERLEUCHTUNG: Mono/Stereo-Auslöschung im Ganzzahlraum
                    # Plus-Kanal und Minus-Kanal spiegeln sich über den inversen Takt
                    rx_plus = dx + (ax_x * dual_polarity) // 12
                    rx_minus = dx - (ax_x * dual_polarity) // 12
                    
                    # Subtraktion der Kanäle isoliert das reine, rauschfreie "Mono-Signal"
                    # Versatz bestimmt die Einzigartigkeit des lokalen Informationsclusters
                    rx_mono = rx_plus - rx_minus
                    ry_mono = (dy + (ax_y * dual_polarity) // 12) * 2
                    rz = dz + z_offset + (ax_z * dual_polarity) // 12
                    
                    denom = ((rz * self.SCALE) // 1414) + self.invariant_limit
                    if denom <= 0:
                        continue
                        
                    # Das isolierte Monosignal steuert die unbestechliche Pixelkoordinate
                    out_x = (((int(rx_mono) * 45 * self.SCALE) // denom) + cx) % self.width
                    out_y = (((int(ry_mono) * 45 * self.SCALE) // denom) + cy) % self.height
                    
                    takt_check = (dx * dy + frame_idx) % self.control_base
                    
                    if takt_check == 12:
                        r_c, g_c, b_c = 255, 210, 24  # Invarianter Kern (Gold)
                        voxel_size = 4
                    elif takt_check in {1, 5, 7, 11, 13, 17, 19, 23}:
                        r_c, g_c, b_c = 0, 255, 210  # Resonanz-Knoten (Cyan)
                        voxel_size = 3
                    else:
                        glow = max(30, 180 - ((rz * 100) // 128))
                        r_c, g_c, b_c = 0, int(glow) // 2, int(glow)
                        voxel_size = 2
                        
                    y1, y2 = max(0, out_y - voxel_size // 2), min(self.height - 1, out_y + voxel_size // 2)
                    x1, x2 = max(0, out_x - voxel_size // 2), min(self.width - 1, out_x + voxel_size // 2)
                    frame_buffer[y1:y2+1, x1:x2+1] = [r_c, g_c, b_c]
                    
        filename = os.path.join(output_dir, f"stabilized_frame_{frame_idx:04d}.ppm")
        header = f"P6\n{self.width} {self.height}\n255\n".encode('ascii')
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(frame_buffer.tobytes())

def resolve_progressive_video_path(target_dir):
    version = 1
    while True:
        filename = f"ptrc_mono_matrix_v{version:03d}.mp4"
        full_path = os.path.join(target_dir, filename)
        if not os.path.exists(full_path):
            return full_path
        version += 1

if __name__ == "__main__":
    print("[pTRC-MONO-SIEVE] Starte Inferenz-Projektion basierend auf Phasenauslöschung...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_dir, "Stabilized_Cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    android_download_dir = "/storage/emulated/0/Download"
    video_output_dir = android_download_dir if os.path.exists(android_download_dir) else base_dir
    os.makedirs(video_output_dir, exist_ok=True)
    
    total_frames = 144
    rotator = PTRCMonoSieveRotator()
    
    print(f" -> Berechne {total_frames} Takt-Symmetrien über gekreuzte Interzepte...")
    for frame in range(total_frames):
        rotator.project_mono_cancelled_frame(frame, cache_dir)
        if frame % 24 == 0 or frame == total_frames - 1:
            print(f"    + Mono-Lattice-Frame {frame:03d}/{total_frames} im Register verankert.")
            
    input_pattern = os.path.join(cache_dir, "stabilized_frame_%04d.ppm")
    video_target_path = resolve_progressive_video_path(video_output_dir)
    
    print("\n -> Kompiliere rauschfreien Video-Stream via FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
        "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", video_target_path
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        print(f"\n[ SYSTEM CHECK OK ] Invarianter Mono-Matrix-Stream gesichert!")
        print(f" -> Datei: {video_target_path}")
        
        for frame in range(total_frames):
            ppm_file = os.path.join(cache_dir, f"stabilized_frame_{frame:04d}.ppm")
            if os.path.exists(ppm_file): os.remove(ppm_file)
        os.rmdir(cache_dir)
        print("    + Lokaler Cache atomar bereinigt. Zero Floats erhalten.")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n[ ACHTUNG ] FFmpeg-Fehler: {e}")
        sys.exit(1)
