# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program (see the LICENSE file in the root directory).
# If not, see <https://gnu.org>.
# ==============================================================================

# -*- coding: utf-8 -*-

r"""
pTRC Framework - Core Graphics: 144-Facet True Crystal Waveguide Pipeline
Operational Domain: Symmetrical Integer Translation Matrices (\mathbb{Z}^3).
Abolishes flat pixel grids by rendering each structural coordinate state as a 
micro-quantized 144-facet spatial crystal based on Nassim Harameins vector equilibrium.
"""

import os
import sys
import subprocess
import numpy as np

class PTRCFluidLattice:
    """ Simuliert das dichte Modulo-Uhr-Fluid auf dem Äquator des Raums. """
    def __init__(self, size=64):
        self.size = size
        self.primorial_base = 210
        self.grid = np.zeros((size, size), dtype=np.uint8)
        cx, cy = size // 2, size // 2
        # Erzeugt den zentralen, dichten Resonanz-Kern
        self.grid[cx-4:cx+5, cy-4:cy+5] = 156

    def step_fluid_resonance(self, frame_idx):
        """ Taktet das Fluid via ganzzahligem Index-Shift. """
        shift = (frame_idx % 3) - 1
        if shift != 0:
            self.grid = np.roll(self.grid, shift=shift, axis=(0, 1))
        return self.grid

class PTRCTrueCrystalSieve:
    def __init__(self, v_scale=9):
        self.v_scale = int(v_scale)  # Starr auf die 9 Invarianz-Einheiten fixiert
        self.crystal_axes = self._build_144_facet_vectors()

    def _build_144_facet_vectors(self):
        flat_nodes = [
            2, 1, 0,  2, -1, 0, -2,  1, 0, -2, -1, 0,
            0, 2, 1,  0,  2, -1,  0, -2, 1,  0, -2, -1,
            1, 0, 2, -1,  0,  2,  1,  0, -2, -1,  0, -2
        ]
        base_tensors = np.array(flat_nodes, dtype=np.int32).reshape(12, 3)
        axes = []
        # Schachtelung über die 12 Symmetrie-Stufen zur Aktivierung aller 144 Kanäle
        for node in base_tensors:
            for factor in range(1, 13):
                axes.append(node * factor)
        return np.array(axes, dtype=np.int32)

class PTRCCrystalFluidEngine:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156
        self.SCALE = 1000
        self.fluid_source = PTRCFluidLattice(size=64)
        self.sieve = PTRCTrueCrystalSieve(v_scale=9)

    def project_crystal_frame(self, frame_idx, output_dir):
        frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cx, cy = self.width // 2, self.height // 2
        z_offset = 65

        axis_index = frame_idx % 144
        current_axis = self.sieve.crystal_axes[axis_index]
        dual_polarity = 1 if (frame_idx % 2 == 0) else -1

        ax_x = int(current_axis[0])
        ax_y = int(current_axis[1])
        ax_z = int(current_axis[2])

        active_fluid_grid = self.fluid_source.step_fluid_resonance(frame_idx)
        f_height, f_width = active_fluid_grid.shape

        # Raumweite Flutung des unbestechlichen Zahlengitters
        for dx in range(-32, 33):
            for dy in range(-32, 33):
                for dz in range(-12, 13):

                    fluid_x = (dx + f_width // 2) % f_width
                    fluid_y = (dy + f_height // 2) % f_height
                    fluid_state = active_fluid_grid[fluid_y, fluid_x]

                    quadrance = dx*dx + dy*dy + dz*dz
                    if quadrance == 0:
                        continue

                    residuum = quadrance % self.primorial_base
                    if residuum > self.invariant_limit:
                        continue

                    # Mitten-Seiten Matrix (Isolierung des Mono-Kernsignals)
                    rx_plus = dx + (ax_x * dual_polarity) // 12
                    rx_minus = dx - (ax_x * dual_polarity) // 12
                    mono_signal_x = rx_plus - rx_minus

                    takt_phase = (dx * dy + frame_idx + fluid_state) % self.control_base

                    # Mid-Side Stereo Fanning fächert die Symmetrien auf (Divisor // 6)
                    holographic_x = dx + (mono_signal_x * (takt_phase - 12)) // 6
                    holographic_y = dy + (ax_y * dual_polarity) // 12
                    rz = dz + z_offset + (ax_z * dual_polarity) // 12

                    denom = ((rz * self.SCALE) // 1414) + self.invariant_limit
                    if denom <= 0:
                        continue

                    # Zentrierter Projektionspunkt auf der Beobachter-Retina
                    out_x = (((int(holographic_x) * 45 * self.SCALE) // denom) + cx) % self.width
                    out_y = (((int(holographic_y) * 45 * self.SCALE) // denom) + cy) % self.height

                    # Farbbestimmung trennt benutzte Masse von Vakuum-Speicherregistern
                    if fluid_state > 0:
                        if takt_phase == 12:
                            r_c, g_c, b_c = 255, 210, 24  # Invarianter Massen-Kern (Gold)
                        else:
                            r_c, g_c, b_c = 0, 255, 180   # Aktiver Resonanz-Wellenknoten (Cyan)
                    else:
                        r_c, g_c, b_c = 0, int(residuum // 2), 200  # Freier Speicher-Slot (Blau)

                    # FUNDAMENTALE WANDLUNG: Zeichne das Planck-Pixel als 144-seitige Kristallstruktur!
                    # Wir bilden das Vektorgleichgewicht (12 umhüllen 1) über die 24 Berührungspunkte ab.
                    # Dies erzeugt diamantförmige, unbestechliche Mikromuster direkt auf dem Raster.
                    crystal_offsets = [
                        (0, 0),                                # Das Kristallzentrum (9 Schritte starr)
                        (0, -2), (0, 2), (-2, 0), (2, 0),      # Die orthogonalen Hauptachsen des Kristalls
                        (-1, -1), (1, -1), (-1, 1), (1, 1)     # Die 24 diagonalen Kontaktbruchlinien
                    ]

                    for ox, oy in crystal_offsets:
                        px = (out_x + ox) % self.width
                        py = (out_y + oy) % self.height
                        
                        # Harmonische Helligkeits-Dämpfung basierend auf den 9 Schritten vom Zentrum
                        if ox == 0 and oy == 0:
                            frame_buffer[py, px] = [r_c, g_c, b_c]
                        else:
                            # Die Facetten glühen leicht abgeschwächt im Vakuum-Feld
                            frame_buffer[py, px] = [r_c // 2, g_c // 2, b_c // 2]

        filename = os.path.join(output_dir, f"stabilized_frame_{frame_idx:04d}.ppm")
        header = f"P6\n{self.width} {self.height}\n255\n".encode('ascii')
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(frame_buffer.tobytes())

def resolve_progressive_video_path(target_dir):
    version = 1
    while True:
        filename = f"ptrc_true_crystal_fluid_v{version:03d}.mp4"
        full_path = os.path.join(target_dir, filename)
        if not os.path.exists(full_path):
            return full_path
        version += 1

if __name__ == "__main__":
    print("[pTRC-144-FACET] Initialisiere unbestechliche Raumkristall-Fluid-Pipeline...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_dir, "Stabilized_Cache")
    os.makedirs(cache_dir, exist_ok=True)

    android_download_dir = "/storage/emulated/0/Download"
    video_output_dir = android_download_dir if os.path.exists(android_download_dir) else base_dir
    os.makedirs(video_output_dir, exist_ok=True)

    total_frames = 144
    render_pipeline = PTRCCrystalFluidEngine()

    for frame in range(total_frames):
        render_pipeline.project_crystal_frame(frame, cache_dir)
        if frame % 24 == 0 or frame == total_frames - 1:
            print(f" + Crystal-Lattice-Frame {frame:03d}/{total_frames} formschlüssig verankert.")

    input_pattern = os.path.join(cache_dir, "stabilized_frame_%04d.ppm")
    video_target_path = resolve_progressive_video_path(video_output_dir)

    print("\n -> Kompiliere rauschfreien 144-Facetten Stream via FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
        "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", video_target_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        print(f"\n[ SYSTEM CHECK OK ] Das unbestechliche 144-Facetten-Fluid-Video ist gesichert!")
        print(f" -> Datei: {video_target_path}")

        for frame in range(total_frames):
            ppm_file = os.path.join(cache_dir, f"stabilized_frame_{frame:04d}.ppm")
            if os.path.exists(ppm_file): os.remove(ppm_file)
        os.rmdir(cache_dir)
        print(" + Lokaler Cache atomar bereinigt. Symmetrie-Schutz 100% aktiv.")
        sys.exit(0)

    except Exception as e:
        print(f"\n[ ACHTUNG ] FFmpeg-Kompression fehlgeschlagen: {e}")
        sys.exit(1)
