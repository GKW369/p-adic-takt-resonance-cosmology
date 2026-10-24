# ==============================================================================
# pTRC Framework - Experimental Module: Resonant Band Interference Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ==============================================================================

# -*- coding: utf-8 -*-
r"""
pTRC Framework - Experimental Core: Resonant Band Interference Engine
Operational Domain: Symmetrical Integer Translation Matrices (\mathbb{Z}^3).
Stabilizes the asymmetric Modulo-210/24 interference bands visible in landscape 
mode by coupling the 156 residue offset with progressive crystal axis routing.
"""

import os
import sys
import subprocess
import numpy as np

class PTRCGeometrySieve:
    def __init__(self, cx, cy, cz, v_scale=14):
        self.cx = int(cx)
        self.cy = int(cy)
        self.cz = int(cz)
        self.v_scale = int(v_scale)

    def generate_monolith_nodes(self, frame_idx):
        kristall_zentren = []
        if frame_idx < 72:
            # Die 13 Sphären der Ur-Zelle
            fcc_sphere = [
                (0, 0, 0), (2, 2, 0), (-2, 2, 0), (2, -2, 0), (-2, -2, 0),
                (2, 0, 2), (2, 0, -2), (-2, 0, 2), (-2, 0, -2),
                (0, 2, 2), (0, 2, -2), (0, -2, 2), (0, -2, -2)
            ]
            for k_x, k_y, k_z in fcc_sphere:
                kristall_zentren.append((k_x * self.v_scale, k_y * self.v_scale, k_z * self.v_scale))
        else:
            # Die massive Pyramide
            pyramid_nodes = [
                (-2, 2, -2), (2, 2, -2), (2, -2, -2), (-2, -2, -2),
                (-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0), (0, 0, 2)
            ]
            for k_x, k_y, k_z in pyramid_nodes:
                kristall_zentren.append((k_x * self.v_scale, k_y * self.v_scale + 12, k_z * self.v_scale))
        return kristall_zentren

class PTRCResonantBandEngine:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156
        self.SCALE = 1000
        self.crystal_axes = self._build_invariant_axes()
        self.sieve = PTRCGeometrySieve(cx=width//2, cy=height//2, cz=65, v_scale=14)

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

    def project_resonant_frame(self, frame_idx, output_dir):
        frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cx, cy = self.width // 2, self.height // 2
        z_offset = 65
        
        axis_index = frame_idx % 144
        current_axis = self.crystal_axes[axis_index]
        dual_polarity = 1 if (frame_idx % 2 == 0) else -1
        
        ax_x = int(current_axis[0])
        ax_y = int(current_axis[1])
        ax_z = int(current_axis[2])
        
        active_monoliths = self.sieve.generate_monolith_nodes(frame_idx)
        
        for mx, my, mz in active_monoliths:
            for dx in range(-8, 9):
                for dy in range(-8, 9):
                    for dz in range(-8, 9):
                        
                        pk_x = mx + dx
                        pk_y = my + dy
                        pk_z = mz + dz
                        
                        quadrance = pk_x*pk_x + pk_y*pk_y + pk_z*pk_z
                        if quadrance == 0:
                            continue
                            
                        # 1. ERWEITERTES MODULO-210 RAUMSIEB
                        residuum = quadrance % self.primorial_base
                        if residuum > self.invariant_limit:
                            continue
                            
                        # Mitten-Seiten Matrix zur Abgreifung des Mono-Kerns
                        rx_plus = pk_x + (ax_x * dual_polarity) // 12
                        rx_minus = pk_x - (ax_x * dual_polarity) // 12
                        mono_signal_x = rx_plus - rx_minus
                        
                        takt_phase = (pk_x * pk_y + frame_idx) % self.control_base
                        
                        # STABILISIERTE INTERFERENZ-FÄCHERUNG (Mitten-Seiten Verschränkung)
                        # Verhindert den totalen Linienkollaps und bringt die Querformat-Bänder in Fluss
                        holographic_x = pk_x + (mono_signal_x * (takt_phase - 12)) // 6
                        holographic_y = pk_y + (ax_y * dual_polarity) // 12
                        rz = pk_z + z_offset + (ax_z * dual_polarity) // 12
                        
                        denom = ((rz * self.SCALE) // 1414) + self.invariant_limit
                        if denom <= 0:
                            continue
                            
                        out_x = (((int(holographic_x) * 45 * self.SCALE) // denom) + cx) % self.width
                        out_y = (((int(holographic_y) * 45 * self.SCALE) // denom) + cy) % self.height
                        
                        # Farbzuordnung nach deinen Spektralgesetzen (Eichwert 156 & 1836)
                        if frame_idx < 72:
                            # Kugel-Resonanzphase: Cyan-Gitter mit energetischen Goldknoten
                            if residuum % 24 == 12:
                                r_c, g_c, b_c = 255, 210, 24
                            else:
                                r_c, g_c, b_c = 0, 255, 210
                            voxel_size = 3
                        else:
                            # Pyramiden-Massephase: Gold-Kern mit feinen Resonanzbändern
                            if takt_phase in {1, 5, 7, 11, 13, 17, 19, 23}:
                                r_c, g_c, b_c = 0, 180, 255
                            else:
                                r_c, g_c, b_c = 255, 210, 24
                            voxel_size = 4
                            
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
        filename = f"ptrc_resonant_bands_v{version:03d}.mp4"
        full_path = os.path.join(target_dir, filename)
        if not os.path.exists(full_path):
            return full_path
        version += 1

if __name__ == "__main__":
    print("[pTRC-BANDS] Berechne das raumübergreifende Mitten-Seiten Interferenzsieb...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_dir, "Stabilized_Cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    android_download_dir = "/storage/emulated/0/Download"
    video_output_dir = android_download_dir if os.path.exists(android_download_dir) else base_dir
    os.makedirs(video_output_dir, exist_ok=True)
    
    total_frames = 144
    rotator = PTRCResonantBandEngine()
    
    print(f" -> Taktung läuft auf dem S21FE Snapdragons/Exynos-Integer-Layer...")
    for frame in range(total_frames):
        rotator.project_resonant_frame(frame, cache_dir)
        if frame % 24 == 0 or frame == total_frames - 1:
            print(f"    + Band-Lattice-Frame {frame:03d}/{total_frames} harmonisch gefiltert.")
            
    input_pattern = os.path.join(cache_dir, "stabilized_frame_%04d.ppm")
    video_target_path = resolve_progressive_video_path(video_output_dir)
    
    print("\n -> Kompiliere verschränkten 2D-Flächen-Stream via FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
        "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", video_target_path
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        print(f"\n[ SYSTEM CHECK OK ] Das verfeinerte pTRC-Hologramm wurde ausgegeben!")
        print(f" -> Datei: {video_target_path}")
        
        for frame in range(total_frames):
            ppm_file = os.path.join(cache_dir, f"stabilized_frame_{frame:04d}.ppm")
            if os.path.exists(ppm_file): os.remove(ppm_file)
        os.rmdir(cache_dir)
        print("    + Cache-Register geleert. Invarianz auf Hardware-Ebene gesichert.")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n[ ACHTUNG ] FFmpeg-Fehler: {e}")
        sys.exit(1)
