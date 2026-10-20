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
Filename: ptrc_3d_animation_generator.py
Operational Domain: Pure Discrete Memory Chains (\mathbb{Z}^3) representing 144-facet crystals.
Optimized: 137-Takt Handshake-Belichtung mit dezentralem Routing-Kollaps.
"""

import os
import sys
import subprocess
import time
import platform
import numpy as np
import cv2

# ==============================================================================
# !!! TARGET ZONE: EXPLIZITE UND TAB-FREIE MODUL-KOPPLUNG !!!
# MARKER: PTRC_HARDCODED_NAMESPACE_RESOLVER_2026
# ==============================================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

parent_1 = os.path.dirname(script_dir)
parent_2 = os.path.dirname(parent_1)

for p in [parent_1, parent_2]:
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

print(" -> [ PATH ] Synchronisation für 'ptrc_3d_animation_generator.py' erfolgreich etabliert.")
# ==============================================================================

class PTRC3DAnimationPipeline:
    """
    Rendert die dichte Packung der Raumkristalle exakt getaktet auf das Feynman-Limit.
    Simuliert den dezentralen Handshake der Pixel vor dem Beobachter-Kollaps.
    """
    def __init__(self, total_frames=144):
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        
        # Lokale Geometrie-Auflösung
        self.width = 320
        self.height = 180
        self.depth = 128
        self.invariant_limit = 156
        self.FEYNMAN_LIMIT = 137  # Die fundamentale Belichtungszeit (Handshake-Dauer)
        self.SCALE = 1000
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def _get_cpu_name(self):
        try:
            if platform.system() == "Linux":
                command = "cat /proc/cpuinfo | grep 'model name' | uniq"
                cpu_info = subprocess.check_output(command, shell=True).decode().strip()
                if cpu_info:
                    return cpu_info.split(":")[-1].strip()
        except Exception:
            pass
        return "Intel(R) Core(TM) i3-3217U CPU @ 1.80GHz"

    def generate_deterministic_video_sequence(self):
        """
        Generiert die lückenlose Kristall-Matrix. Schaltet im Hintergrund dezentrale 
        Handshakes, bevor das Bild alle 137 Takte für den Beobachter manifestiert wird.
        """
        cpu_name = self._get_cpu_name()
        print(f"[ PIPELINE ] Verwende Hardware-Profil: {cpu_name}")
        print(f" -> Initieere dezentrale Handshakes über {self.FEYNMAN_LIMIT} Schwingungs-Takte...")
        
        self.total_generation_start = time.perf_counter()
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        
        # Dichteste Packung: Schrittweite 14 schließt bei R^2 = 196 jede Gitterlücke
        kristall_zentren = [
            (0, 0, 0),
            (2, 2, 0), (-2, 2, 0), (2, -2, 0), (-2, -2, 0),
            (2, 0, 2), (2, 0, -2), (-2, 0, 2), (-2, 0, -2),
            (0, 2, 2), (0, 2, -2), (0, -2, 2), (0, -2, -2)
        ]

        v_scale = 14
        target_quadrance = 196
        sieve_tolerance = 12

        global_takt_counter = 0

        for frame_idx in range(self.frames_limit):
            frame_start_time = time.perf_counter()
            frame_buffer = np.zeros((self.stereo_engine.height, self.stereo_engine.width, 3), dtype=np.uint8)
            
            # --- DEZENTRALE HANDSHAKE-PHASE ---
            # Wir simulieren den Informationsfluss durch die Kanäle des Gitters für 137 Takte.
            # Falls die Datenmenge lokal kippt, simuliert der Code die Verlangsamung.
            local_data_density = (frame_idx * 7) % 256
            exceeded_load_bias = 0
            if local_data_density > 200:
                # Lokaler Überlastungs-Dilemma: Das Gitter braucht länger für das Routing
                exceeded_load_bias = (local_data_density - 200) // 10
            
            # Schalte die Hintergrunduhr starr durch die Belichtungszeit
            for internal_takt in range(self.FEYNMAN_LIMIT + exceeded_load_bias):
                self.clock_engine.evolve_clock_one_takt()
                global_takt_counter += 1
            
            # --- DER BEOBACHTER-KOLLAPS (RENDERING) ---
            # Erst jetzt, nach dem vollendeten Handshake, manifestiert sich die Position
            z_flight_offset = (global_takt_counter // 24) % self.depth
            
            for k_x, k_y, k_z in kristall_zentren:
                kx_obj = cx + (k_x * v_scale)
                ky_obj = cy + (k_y * v_scale)
                kz_obj = cz + (k_z * v_scale)
                
                adjusted_z = (kz_obj - z_flight_offset) % self.depth
                if adjusted_z <= 0:
                    adjusted_z = 1
                
                for dx in range(-16, 17):
                    for dy in range(-16, 17):
                        q_dist = (dx * dx) + (dy * dy)
                        
                        # Pi-Sieve Außenkontur-Filter
                        if abs(q_dist - target_quadrance) <= sieve_tolerance:
                            denom = ((adjusted_z * self.SCALE) // 1414) + self.invariant_limit
                            
                            p_x = ((int(kx_obj - cx + dx) * 8) * self.SCALE) // denom
                            p_y = ((int(ky_obj - cy + dy) * 8) * self.SCALE) // denom
                            
                            out_x = (p_x + self.stereo_engine.width // 2) % self.stereo_engine.width
                            out_y = (p_y + self.stereo_engine.height // 2) % self.stereo_engine.height
                            
                            # Die 1-Byte Linsenkanal-Variable steuert die Farbe des Quantenflusses
                            # Simuliert die Lichtablenkung jenseits großer Informationscluster
                            lens_channel = (128 + adjusted_z + exceeded_load_bias) % 256
                            
                            frame_buffer[out_y, out_x] = [255, lens_channel, 0]
            
            cv2.imwrite(os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png"), frame_buffer)
            
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                duration_ms = (time.perf_counter() - frame_start_time) * 1000
                load_msg = f" (+{exceeded_load_bias} Takt Load)" if exceeded_load_bias > 0 else ""
                print(f"    + Frame {frame_idx:03d}/{self.frames_limit} | Takt: {global_takt_counter} | Zeit: {duration_ms:.2f} ms{load_msg}")

        self.total_generation_end = time.perf_counter()

    def compile_lossless_output_video(self):
        """Kompiliert die Einzelbilder mittels FFMPEG zu einem stabilen Videostream."""
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.png")
        target_video = os.path.join(script_dir, "ptrc_hologram_output.mp4")
        
        print(" -> Starte ffmpeg-Kompilierung für das 137-Takt-Belichtungsmodell...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "1", "-preset", "slow", "-pix_fmt", "yuv420p", target_video
        ]
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            print(f"    + [ SUCCESS ] Video mit dezentralem Routing exportiert: '{os.path.basename(target_video)}'")
            
            # Cache bereinigen
            for frame_idx in range(self.frames_limit):
                p = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
                if os.path.exists(p): os.remove(p)
            os.rmdir(self.output_directory)
            return 1
        except Exception:
            print("    ! [ SYSTEM NOTICE ] Fehler bei der FFMPEG-Kompilierung.")
            return 0

if __name__ == "__main__":
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    pipeline.generate_deterministic_video_sequence()
    status = pipeline.compile_lossless_output_video()
    print(f" -> [ VALIDATION ] Video-Pipeline beendet. Status-Code: {status}")
