==============================================================================
pTRC Framework - Core Module: Fluid Resonance Waveguide Render Engine
Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
==============================================================================

# -*- coding: utf-8 -*-
r"""
pTRC Framework - Core Graphics: Fluid-Resonance to 144-Facet Waveguide Pipeline
Operational Domain: Symmetrical Integer Translation Matrices (\mathbb{Z}^3).
Directly couples the 1-bit Lattice-Gas Automaton from fluid_resonance.py
with the Mid-Side Stereo Fanning matrix to visualize lossless fluid dynamics.
"""

import os
import sys
import subprocess
import numpy as np

class PTRCFluidLattice:
    """ Simuliert das dichte Modulo-Uhr-Fluid ohne eine einzige Fließkommazahl. """
    def __init__(self, size=32):
        self.size = size
        self.primorial_base = 210
        # Startzustand: Ein hochsymmetrischer, zentraler Energieimpuls (Wirminghaus Invariant 156)
        self.grid = np.zeros((size, size, size), dtype=np.uint8)
        cx, cy, cz = size // 2, size // 2, size // 2
        self.grid[cx-2:cx+3, cy-2:cy+3, cz-2:cz+3] = 156

    def step_fluid_resonance(self, frame_idx):
        """ Taktet das Fluid via ganzzahligem Index-Shift (np.roll Ersatz im Ganzzahlraum). """
        # Symmetrische Oszillation simuliert die hydrodynamische Wellenausbreitung (c=1)
        shift = (frame_idx % 3) - 1
        if shift != 0:
            self.grid = np.roll(self.grid, shift=shift, axis=(0, 1, 2))
        return self.grid

class PTRCTrueCrystalSieve:
    def __init__(self, v_scale=9):
        self.v_scale = int(v_scale)
        self.crystal_axes = self._build_144_facet_vectors()

    def _build_144_facet_vectors(self):
        flat_nodes = [
            2, 1, 0,  2, -1, 0, -2,  1, 0, -2, -1, 0,
            0, 2, 1,  0,  2, -1,  0, -2, 1,  0, -2, -1,
            1, 0, 2, -1,  0,  2,  1,  0, -2, -1,  0, -2
        ]
        base_tensors = np.array(flat_nodes, dtype=np.int32).reshape(12, 3)
        axes = []
        for node in base_tensors:
            for factor in range(1, 13):
                axes.append(node * factor)
        return np.array(axes, dtype=np.int32)

class PTRCFluidRenderEngine:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156
        self.SCALE = 1000
        self.fluid_source = PTRCFluidLattice(size=24)
        self.sieve = PTRCTrueCrystalSieve(v_scale=9)

    def project_fluid_frame(self, frame_idx, output_dir):
        frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cx, cy = self.width // 2, self.height // 2
        z_offset = 75

        axis_index = frame_idx % 144
        current_axis = self.sieve.crystal_axes[axis_index]
        dual_polarity = 1 if (frame_idx % 2 == 0) else -1

        ax_x = int(current_axis[0])
        ax_y = int(current_axis[1])
        ax_z = int(current_axis[2])

        # 1. AKTUELLE FLUID-RESONANZ-MATRIX HOLEN
        active_fluid_grid = self.fluid_source.step_fluid_resonance(frame_idx)
        f_depth, f_height, f_width = active_fluid_grid.shape

        # 2. ITERATION DURCH DIE STRÖMUNGSZELLEN
        for z in range(f_depth):
            for y in range(f_height):
                for x in range(f_width):
                    fluid_state = active_fluid_grid[z, y, x]
                    if fluid_state == 0:
                        continue

                    # Transformation der Gitterkoordinaten bezogen auf das Kristall-Sieve
                    mx = (x - f_width // 2) * 16
                    my = (y - f_height // 2) * 16
                    mz = (z - f_depth // 2) * 16

                    quadrance = mx*mx + my*my + mz*mz
                    if quadrance == 0:
                        continue

                    # Modulo-210 Existenzsieb
                    if (quadrance % self.primorial_base) > self.invariant_limit:
                        continue

                    # MITTEN-SEITEN AUSLÖSCHUNG (Isoliert die reine Fluid-Symmetrie)
                    rx_plus = mx + (ax_x * dual_polarity) // 12
                    rx_minus = mx - (ax_x * dual_polarity) // 12
                    mono_signal_x = rx_plus - rx_minus

                    takt_phase = (mx * my + frame_idx) % self.control_base

                    # Stereo-Fanning treibt die Fluid-Wirbel auseinander
                    holographic_x = mx + (mono_signal_x * (takt_phase - 12)) // 6
                    holographic_y = my + (ax_y * dual_polarity) // 12
                    rz = mz + z_offset + (ax_z * dual_polarity) // 12

                    denom = ((rz * self.SCALE) // 1414) + self.invariant_limit
                    if denom <= 0:
                        continue

                    out_x = (((int(holographic_x) * 45 * self.SCALE) // denom) + cx) % self.width
                    out_y = (((int(holographic_y) * 45 * self.SCALE) // denom) + cy) % self.height

                    # Farbspektrum trennt strömende Energie von freien Speicher-Registern
                    if takt_phase == 12:
                        r_c, g_c, b_c = 255, 210, 24  # Manifestierte Fluid-Masse (Gold)
                    elif takt_phase in {1, 5, 7, 11, 13, 17, 19, 23}:
                        r_c, g_c, b_c = 0, 255, 180  # Resonanz-Adern (Cyan)
                    else:
                        r_c, g_c, b_c = 0, 80, 255   # Dynamische Speicher-Facetten (Vakuum-Blau)

                    # Atomares 1-Pixel-Rastermapping
                    frame_buffer[out_y, out_x] = [r_c, g_c, b_c]

        filename = os.path.join(output_dir, f"stabilized_frame_{frame_idx:04d}.ppm")
        header = f"P6\n{self.width} {self.height}\n255\n".encode('ascii')
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(frame_buffer.tobytes())

def resolve_progressive_video_path(target_dir):
    version = 1
    while True:
        filename = f"ptrc_fluid_resonance_v{version:03d}.mp4"
        full_path = os.path.join(target_dir, filename)
        if not os.path.exists(full_path):
            return full_path
        version += 1

if __name__ == "__main__":
    print("[pTRC-FLUID-PIPE] Kopple Fluid-Resonanz mit 144-Facetten-Gitter...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_dir, "Stabilized_Cache")
    os.makedirs(cache_dir, exist_ok=True)

    android_download_dir = "/storage/emulated/0/Download"
    video_output_dir = android_download_dir if os.path.exists(android_download_dir) else base_dir
    os.makedirs(video_output_dir, exist_ok=True)

    total_frames = 144
    render_pipeline = PTRCFluidRenderEngine()

    print(f" -> Berechne hydrodynamische Volumensynthese auf dem S21FE...")
    for frame in range(total_frames):
        render_pipeline.project_crystal_frame(frame, cache_dir)
        if frame % 24 == 0 or frame == total_frames - 1:
            print(f" + Fluid-Lattice-Frame {frame:03d}/{total_frames} bit-invariant gefiltert.")

    input_pattern = os.path.join(cache_dir, "stabilized_frame_%04d.ppm")
    video_target_path = resolve_progressive_video_path(video_output_dir)

    print("\n -> Kompiliere rauschfreien Fluid-Stream via FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
        "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", video_target_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        print(f"\n[ SYSTEM CHECK OK ] Fluid-Resonanz-Video erfolgreich in Downloads gesichert!")
        print(f" -> Datei: {video_target_path}")

        for frame in range(total_frames):
            ppm_file = os.path.join(cache_dir, f"stabilized_frame_{frame:04d}.ppm")
            if os.path.exists(ppm_file): os.remove(ppm_file)
        os.rmdir(cache_dir)
        print(" + Cache-Register atomar geleert. Zero Floats erhalten.")
        sys.exit(0)

    except Exception as e:
        print(f"\n[ ACHTUNG ] FFmpeg-Fehler: {e}")
        sys.exit(1)
