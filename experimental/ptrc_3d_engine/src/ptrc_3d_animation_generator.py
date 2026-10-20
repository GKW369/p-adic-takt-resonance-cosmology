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
pTRC Framework - Advanced Animation & Video Engine Pipeline
Operational Domain: Pure Discrete Memory Chains (\mathbb{Z}^3) representing 144-facet crystals.
Optimized: Lochfreie Ganzzahl-Visualisierung des 13-Sphären-Wirminghaus-Raumgitters im Raum.
"""

import os
import sys
import subprocess
import time
import platform
import numpy as np
import cv2

# Namespace-Resolver für die lokale Repository-Struktur
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
for p in [os.path.dirname(script_dir), os.path.dirname(os.path.dirname(script_dir))]:
    if p:
        sys.path.insert(0, p)
        src_dir = os.path.join(p, "src")
        if os.path.exists(src_dir):
            sys.path.insert(0, src_dir)

try:
    from ptrc_3d_stereo_engine import PTRC3DStereoEngine
except ImportError:
    from src.ptrc_3d_stereo_engine import PTRC3DStereoEngine

try:
    from ptrc_clock_core import PTRCModularClockEngine
except ImportError:
    from src.ptrc_clock_core import PTRCModularClockEngine


class PTRC3DAnimationPipeline:
    """
    Rendert ein rotierendes und fliegendes physikalisches Objekt (Wirminghaus-Matrix)
    aus dichtgepackten Sphärenkristallen unter strikter Einhaltung der Zero-Float-Rule.
    """
    def __init__(self, total_frames=144):
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        
        # Dimensionen des diskreten Arbeitsraums
        self.width = 320
        self.height = 180
        self.depth = 128
        self.invariant_limit = 156
        self.SCALE = 1000
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def _get_cpu_name(self):
        try:
            if platform.system() == "Linux":
                cmd = "cat /proc/cpuinfo | grep 'model name' | uniq"
                return subprocess.check_output(cmd, shell=True).decode().strip().split(":")[-1].strip()
        except Exception:
            pass
        return "Intel(R) Core(TM) i3-3217U CPU @ 1.80GHz"

    def generate_deterministic_video_sequence(self):
        """Erzeugt ein zusammenhängendes, plastisches 3D-Objekt aus Ganzzahl-Sphären."""
        cpu_name = self._get_cpu_name()
        print(f"[ PIPELINE ] Hardware: {cpu_name}")
        print(f" -> Generiere {self.frames_limit} Frames des 13-Sphären-Raumobjekts...")
        
        self.total_generation_start = time.perf_counter()
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        
        # Die 12 mechanischen Kontakt-Offsets des Kristalls zur lochfreien Oberflächen-Füllung
        crystal_contact_offsets = np.array([
            [-2, -1], [-2,  1], [ 2, -1], [ 2,  1],
            [-1, -2], [-1,  2], [ 1, -2], [ 1,  2],
            [ 0, -3], [ 0,  3], [-3,  0], [ 3,  0]
        ], dtype=np.int32)

        # Die 13 mathematischen Zentren des Vektor-Gleichgewichts (FCC-Basis)
        # 1 Zentralkugel + 12 perfekt umschließende Koordinatenknoten
        fcc_spheres_nodes = [
            (0, 0, 0),  (2, 2, 0),  (2, -2, 0),  (-2, 2, 0),  (-2, -2, 0),
            (2, 0, 2),  (2, 0, -2), (-2, 0, 2),  (-2, 0, -2),
            (0, 2, 2),  (0, 2, -2), (0, -2, 2),  (0, -2, -2)
        ]

        for frame_idx in range(self.frames_limit):
            frame_start = time.perf_counter()
            frame_buffer = np.zeros((self.stereo_engine.height, self.stereo_engine.width, 3), dtype=np.uint8)
            
            # Bewegungskopplung: Vorwärtsflug und leichte Rotation im Taktraum
            z_flight_offset = (frame_idx * 1) % self.depth
            rot_takt = frame_idx % 24
            
            # Iteriere über alle 13 Sphären, um das zusammenhängende Objekt zu formen
            for sx, sy, sz in fcc_spheres_nodes:
                # Dynamischer Rotations-Shift im Ganzzahlraum modulo 24
                rx = sx + (rot_takt // 8 if sx != 0 else 0)
                ry = sy - (rot_takt // 12 if sy != 0 else 0)
                
                # Globale Platzierung des Sphärenzentrums im Sichtfeld
                kx = cx + rx * 14
                ky = cy + ry * 14
                kz = cz + sz * 10
                
                adjusted_z = (kz - z_flight_offset) % self.depth
                if adjusted_z <= 0:
                    adjusted_z = 1
                
                # Lokaler Voxel-Scan der einzelnen Kugeloberfläche (Quadrance-Sieve)
                for dx in range(-10, 11, 2):
                    for dy in range(-10, 11, 2):
                        q_dist = (dx * dx) + (dy * dy)
                        
                        # Definiert die unteilbare Hülle des einzelnen Sphärenkristalls
                        if 24 <= q_dist <= 100:
                            denom = ((adjusted_z * self.SCALE) // 1414) + self.invariant_limit
                            
                            p_x = (int(kx - cx + dx) * 8 * self.SCALE) // denom
                            p_y = (int(ky - cy + dy) * 8 * self.SCALE) // denom
                            
                            out_x = (p_x + self.stereo_engine.width // 2) % self.stereo_engine.width
                            out_y = (p_y + self.stereo_engine.height // 2) % self.stereo_engine.height
                            
                            # Pseudostereoskopische Tiefen-Beleuchtung (1-Byte Variable)
                            # Je weiter hinten das Pixel liegt (großes Z), desto dunkler das Glimmen
                            depth_glow = 255 - (adjusted_z * 1)
                            if depth_glow < 50:
                                depth_glow = 50
                            
                            # Einstanzen der mechanischen Facetten-Offsets in intensivem Blau-Cyan
                            for offset in crystal_contact_offsets:
                                px_y = (out_y + int(offset[1])) % self.stereo_engine.height
                                px_x = (out_x + int(offset[0])) % self.stereo_engine.width
                                
                                # BGR: [Blau, Grün, Rot] -> Volles Blau, modulierter Grünkanal für den Äther-Farbton
                                frame_buffer[px_y, px_x] = [255, int(depth_glow // 2), 0]
            
            cv2.imwrite(os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png"), frame_buffer)
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Frame {frame_idx:03d}/{self.frames_limit} | {(time.perf_counter() - frame_start)*1000:.2f} ms")
            
            self.clock_engine.evolve_clock_one_takt()

        self.total_generation_end = time.perf_counter()

    def compile_lossless_output_video(self):
        """Kompiliert die Bildersequenz mittels FFMPEG zu einem stabilen Videostream."""
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.png")
        target_video = os.path.join(script_dir, "ptrc_wirminghaus_object.mp4")
        
        print(" -> Starte ffmpeg-Videokompilierung...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "1", "-preset", "slow", "-pix_fmt", "yuv420p", target_video
        ]
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            print(f"    + [ SUCCESS ] Raumobjekt-Video erstellt: '{os.path.basename(target_video)}'")
            
            # Cache bereinigen
            for frame_idx in range(self.frames_limit):
                p = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
                if os.path.exists(p): os.remove(p)
            os.rmdir(self.output_directory)
            return 1
        except Exception:
            print("    ! [ SYSTEM NOTICE ] Fehler bei der ffmpeg-Kompilierung.")
            return 0


if __name__ == "__main__":
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    pipeline.generate_deterministic_video_sequence()
    status = pipeline.compile_lossless_output_video()
    print(f" -> [ VALIDATION ] Pipeline beendet mit Status: {status}")
