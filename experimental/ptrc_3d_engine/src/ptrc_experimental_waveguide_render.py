==============================================================================
pTRC Framework - Experimental Module: Massive Voxel Monolith Projector
Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
==============================================================================

# -*- coding: utf-8 -*-
r"""
pTRC Framework - Experimental Core: Massive Monolith Volumensynthese
Operational Domain: Symmetrical Integer Translation Matrices (\mathbb{Z}^3).
Denses the 144-facet crystal intersections to make the stationary pyramid 
monolith visually solid and distinct from the vacuum matrix layout.
"""

import os
import sys
import subprocess
import numpy as np

class PTRCTrueCrystalSieve:
    """
    Berechnet die dichten, ganzzahligen Raumknoten des 144-seitigen Kristalls.
    Erzeugt ab Frame 72 eine massive, raumfüllende Voxel-Pyramide.
    """
    def __init__(self, v_scale=14):
        self.v_scale = int(v_scale)
        self.crystal_axes = self._build_144_facet_vectors()

    def _build_144_facet_vectors(self):
        flat_nodes = [
            2, 1, 0,  2, -1, 0, -2, 1, 0, -2, -1, 0,
            0, 2, 1,  0, 2, -1,  0, -2, 1,  0, -2, -1,
            1, 0, 2, -1, 0,  2,  1, 0, -2, -1, 0, -2
        ]
        base_tensors = np.array(flat_nodes, dtype=np.int32).reshape(12, 3)
        axes = []
        for node in base_tensors:
            for factor in range(1, 13):
                axes.append(node * factor)
        return np.array(axes, dtype=np.int32)

    def generate_dense_monolith_nodes(self, frame_idx):
        kristall_zentren = []

        # FRAMES 0 BIS 71: Die vollkommen symmetrische 144er-Ur-Zelle
        if frame_idx < 72:
            for axis in self.crystal_axes:
                kx = (axis[0] * self.v_scale) // 2
                ky = (axis[1] * self.v_scale) // 2
                kz = (axis[2] * self.v_scale) // 2
                kristall_zentren.append((kx, ky, kz, 0)) # Type 0: Ur-Zelle

        # FRAMES 72 BIS 143: Die massive, raumzentrierte Pyramide
        else:
            # Wir bauen die Pyramide stufenweise massiv aus, um Hohlräume zu füllen
            # Stufe 3 (Basis, y=-24): Breites Fundament
            for px in range(-2, 3):
                for pz in range(-2, 3):
                    kristall_zentren.append((px * 28, -24, pz * 28, 1))
            
            # Stufe 2 (Mitte, y=0): Mittlere Ebene
            for px in range(-1, 2):
                for pz in range(-1, 2):
                    kristall_zentren.append((px * 28, 0, pz * 28, 1))
            
            # Stufe 1 (Spitze, y=24): Kristallspitze im Zentrum
            kristall_zentren.append((0, 24, 0, 1))

        return kristall_zentren

class PTRCMassiveHologramEngine:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156
        self.SCALE = 1000
        self.sieve = PTRCTrueCrystalSieve(v_scale=14)

    def project_massive_frame(self, frame_idx, output_dir):
        frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cx, cy = self.width // 2, self.height // 2
        z_offset = 75

        axis_index = frame_idx % 144
        current_axis = self.sieve.crystal_axes[axis_index]
        dual_polarity = 1 if (frame_idx % 2 == 0) else -1

        ax_x = int(current_axis[0])
        ax_y = int(current_axis[1])
        ax_z = int(current_axis[2])

        active_nodes = self.sieve.generate_dense_monolith_nodes(frame_idx)

        for mx, my, mz, obj_type in active_nodes:
            # Lokale Volumen-Verdichtung (Verhindert das Skelettieren auf FullHD)
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    for dz in range(-4, 5):

                        pk_x = mx + dx
                        pk_y = my + dy
                        pk_z = mz + dz

                        quadrance = pk_x*pk_x + pk_y*pk_y + pk_z*pk_z
                        if quadrance == 0:
                            continue

                        if (quadrance % self.primorial_base) > self.invariant_limit:
                            continue

                        # Mitten-Seiten Matrix dekonstruiert den Phasen-Versatz
                        rx_plus = pk_x + (ax_x * dual_polarity) // 12
                        rx_minus = pk_x - (ax_x * dual_polarity) // 12
                        mono_signal_x = rx_plus - rx_minus

                        takt_phase = (pk_x * pk_y + frame_idx) % self.control_base

                        # Mid-Side Stereo Fanning: Weitet den massiven Körper in die Breite aus
                        holographic_x = pk_x + (mono_signal_x * (takt_phase - 12)) // 5
                        holographic_y = pk_y + (ax_y * dual_polarity) // 12
                        rz = pk_z + z_offset + (ax_z * dual_polarity) // 12

                        denom = ((rz * self.SCALE) // 1414) + self.invariant_limit
                        if denom <= 0:
                            continue

                        out_x = (((int(holographic_x) * 45 * self.SCALE) // denom) + cx) % self.width
                        out_y = (((int(holographic_y) * 45 * self.SCALE) // denom) + cy) % self.height

                        # Farbunderscheidung: Ur-Zelle (Cyan) vs Massive Pyramide (Gold)
                        if obj_type == 0:
                            r_c, g_c, b_c = 0, 255, 180
                            voxel_size = 2
                        else:
                            # Kontraststarke Gold-Masse für den massiven Monolithen
                            r_c, g_c, b_c = 255, 200, 0
                            voxel_size = 4 # Größere Stempelauflösung für plastische Konturen

                        # Plastisches Einzeichnen über den lokalen Pixelpuffer
                        if voxel_size == 2:
                            frame_buffer[out_y, out_x] = [r_c, g_c, b_c]
                        else:
                            y1, y2 = max(0, out_y - 1), min(self.height - 1, out_y + 1)
                            x1, x2 = max(0, out_x - 1), min(self.width - 1, out_x + 1)
                            frame_buffer[y1:y2+1, x1:x2+1] = [r_c, g_c, b_c]

        filename = os.path.join(output_dir, f"stabilized_frame_{frame_idx:04d}.ppm")
        header = f"P6\n{self.width} {self.height}\n255\n".encode('ascii')
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(frame_buffer.tobytes())

def resolve_progressive_video_path(target_dir):
    version = 1
    while True:
        filename = f"ptrc_massive_monolith_v{version:03d}.mp4"
        full_path = os.path.join(target_dir, filename)
        if not os.path.exists(full_path):
            return full_path
        version += 1

if __name__ == "__main__":
    print("[pTRC-MONOLITH] Starte massive 3D-Volumensynthese...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_dir, "Stabilized_Cache")
    os.makedirs(cache_dir, exist_ok=True)

    android_download_dir = "/storage/emulated/0/Download"
    video_output_dir = android_download_dir if os.path.exists(android_download_dir) else base_dir
    os.makedirs(video_output_dir, exist_ok=True)

    total_frames = 144
    rotator = PTRCMassiveHologramEngine()

    print(" -> Berechne dichte Kristall-Voxel-Strukturen auf dem S21FE...")
    for frame in range(total_frames):
        rotator.project_massive_frame(frame, cache_dir)
        if frame % 24 == 0 or frame == total_frames - 1:
            print(f" + Massive-Frame {frame:03d}/{total_frames} im Raum verankert.")

    input_pattern = os.path.join(cache_dir, "stabilized_frame_%04d.ppm")
    video_target_path = resolve_progressive_video_path(video_output_dir)

    print("\n -> Kompiliere rauschfreies Massiv-Video via FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
        "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", video_target_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        print(f"\n[ SYSTEM CHECK OK ] Die massive Pyramiden-Masse wurde erfolgreich geformt!")
        print(f" -> Ausgabedatei: {video_target_path}")

        for frame in range(total_frames):
            ppm_file = os.path.join(cache_dir, f"stabilized_frame_{frame:04d}.ppm")
            if os.path.exists(ppm_file): os.remove(ppm_file)
        os.rmdir(cache_dir)
        print(" + Lokaler Cache atomar bereinigt. Zero Floats intakt.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ ACHTUNG ] FFmpeg-Fehler: {e}")
        sys.exit(1)
