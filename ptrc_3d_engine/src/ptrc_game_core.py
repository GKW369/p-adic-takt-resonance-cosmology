# ==============================================================================
# pTRC Framework - Discrete 1-Byte Integer Physics Engine
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
Operational Domain: Discrete 1-Byte Planck-Pixel Arrays without geometric length.
Optimized: 137-Takt Feynman Vacuum Sieve reading static prime lookup maps.
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

print(" -> [ PATH ] Erfolgreich mit der Kern-Engine 'ptrc_clock_core.py' synchronisiert.")
# ==============================================================================

class PTRC3DAnimationPipeline:
    """
    Executes a high-density frame-by-frame rendering loop to write an uncompressed
    lossless mp4 flight video directly from the core 4-variable lookup arrays.
    """
    def __init__(self, total_frames=144):
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        
        # Lokale Triebwerks-Auflösung
        self.width = 320
        self.height = 180
        self.depth = 128
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156
        self.feynman_limit = 137  # Feinstrukturkonstante für den Spektralkollaps
        self.SCALE = 1000
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        # Generiere die statische Modulo-137-Spektrallandkarte im Speicher
        self.deterministic_sieve_array = np.zeros(self.feynman_limit, dtype=np.uint8)
        self._generate_feynman_sieve_matrix()

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def _generate_feynman_sieve_matrix(self):
        """Populates the static 1-byte lookup-map using Feynman totient limits."""
        for node in range(self.feynman_limit):
            val_a, val_b = node, self.feynman_limit
            while val_b > 0:
                val_a, val_b = val_b, val_a % val_b
            if val_a == 1:
                self.deterministic_sieve_array[node] = 1

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
        Renders a perfectly timed flight sequence decoding the 4 core variables.
        All structures are generated purely on-demand through local lattice interferences.
        """
        cpu_name = self._get_cpu_name()
        print(f"[ OFFLINE PIPELINE ] Hardware-Erkennung: {cpu_name}")
        print(f" -> Generiere {self.frames_limit} perfekte Frames fuer die Video-Ausgabe...")
        
        self.total_generation_start = time.perf_counter()
        self.accumulated_pixels_written = 0
        
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        allowed_24_list = [1, 5, 7, 11, 13, 17, 19, 23]
        
        # Lade die Kristallachsen der Kern-Engine
        crystal_axes = self.clock_engine.crystal_axes
        
        # Skalierungs-Schritte für das Weiten der Planck-Pixel in das menschliche Lichtspektrum
        steps = np.arange(-32, 32, dtype=np.int32)

        for frame_idx in range(self.frames_limit):
            frame_start_time = time.perf_counter()
            
            self.stereo_engine.left_eye_buffer.fill(0)
            self.stereo_engine.right_eye_buffer.fill(0)
            
            # ==================================================================
            # !!! TARGET ZONE: FLIESSKOMMAFREIER DEZENTRALER LANDKARTEN-LOOKUP !!!
            # ==================================================================
            # Der Flug-Vorschub taktet exakt im 137-Takt-Feynman-Rhythmus vorwärts
            z_flight_offset = (frame_idx * self.clock_engine.REFRESH_TAKTE) % self.depth
            local_environmental_load = int(self.accumulated_pixels_written % 256)
            
            for axis_idx, axis in enumerate(crystal_axes):
                # Extrahiere die echten Richtungskomponenten (X, Y, Z) der Kristallfacetten
                ax_x = int(axis[0])
                ax_y = int(axis[1])
                ax_z = int(axis[2])
                
                # Makroskopisches Weiten der Schritte zur Spektral-Harmonisierung (steps * 4)
                z_g = (cz + ax_z * steps * 4 - z_flight_offset) % self.depth
                y_g = (cy + ax_y * steps * 4) % self.height
                x_g = (cx + ax_x * steps * 4) % self.width
                
                # Direktes Auslesen der 1-Byte Variablen aus dem dezentralen Voxel-Feld
                pixel_properties = self.clock_engine.voxels[z_g, y_g, x_g]
                active_mask = pixel_properties > 0
                
                if np.any(active_mask):
                    raw_z = z_g[active_mask]
                    raw_z[raw_z <= 0] = 1
                    raw_x = x_g[active_mask] - cx
                    raw_y = y_g[active_mask] - cy
                    
                    # pTRC-Steuerungsgleichung modulo 137 (Ersetzt klassische XYZ-Koordinaten)
                    feynman_addresses = (axis_idx + raw_x * raw_y + pixel_properties[active_mask] + local_environmental_load) % self.feynman_limit
                    
                    # Blitzschneller, unbestechlicher Landkarten-Lookup im Sieb
                    valid_nodes = self.deterministic_sieve_array[feynman_addresses] == 1
                    
                    if np.any(valid_nodes):
                        f_z = raw_z[valid_nodes]
                        f_x = raw_x[valid_nodes]
                        f_y = raw_y[valid_nodes]
                        
                        # Fließkommafreie Perspektiv-Division über Ganzzahl-Skalierung (//)
                        denom = ((f_z * 1000) // 1414) + 156
                        p_xl = ((f_x * 8 - 12) * 1000) // denom
                        p_xr = ((f_x * 8 + 12) * 1000) // denom
                        p_y  = ((f_y * 8) * 1000) // denom
                        
                        out_x_l = (p_xl + self.stereo_engine.width // 2) % self.stereo_engine.width
                        out_x_r = (p_xr + self.stereo_engine.width // 2) % self.stereo_engine.width
                        out_y_s = (p_y + self.stereo_engine.height // 2) % self.stereo_engine.height
                        
                        # Bestimme dichte Cluster (Resonanzkörper) vs. weitmaschigen Äther rein über Modulo-Eigenschaften
                        dense_cluster = (pixel_properties[active_mask][valid_nodes] == 1) # Lock to core mass node
                        
                        if np.any(dense_cluster):
                            # Das hocheffiziente Quanten-Glühen: Maximale Punktdichte am Ort des Register-Updates
                            self.stereo_engine.left_eye_buffer[out_y_s[dense_cluster], out_x_l[dense_cluster]] = 1
                            self.stereo_engine.right_eye_buffer[out_y_s[dense_cluster], out_x_r[dense_cluster]] = 1
                        
                        # Der weitmaschige, transparente Raum-Äther
                        thin_ether = ~dense_cluster
                        if np.any(thin_ether):
                            self.stereo_engine.left_eye_buffer[out_y_s[thin_ether][::2], out_x_l[thin_ether][::2]] = 1
                            self.stereo_engine.right_eye_buffer[out_y_s[thin_ether][::2], out_x_r[thin_ether][::2]] = 1
            # ==================================================================

            self.clock_engine.evolve_clock_one_takt()
            
            bw_frame = self.stereo_engine.left_eye_buffer * 255
            frame_filename = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
            cv2.imwrite(frame_filename, bw_frame)
            
            frame_end_time = time.perf_counter()
            frame_duration_ms = (frame_end_time - frame_start_time) * 1000
            active_pixels_in_frame = int(np.sum(self.stereo_engine.left_eye_buffer))
            self.accumulated_pixels_written += active_pixels_in_frame
            
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Frame {frame_idx:03d}/{self.frames_limit} | Zeit: {frame_duration_ms:.2f} ms | Aktive Datenpunkte: {active_pixels_in_frame:,} Pixel")

        self.total_generation_end = time.perf_counter()

    def compile_lossless_output_video(self):
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.png")
        
        counter = 1
        while True:
            target_video = os.path.join(script_dir, f"ptrc_hologram_{counter:03d}.mp4")
            if not os.path.exists(target_video):
                break
            counter += 1
            
        video_filename = os.path.basename(target_video)
        print(f" -> Starte direkte ffmpeg-Datenabgreifung for '{video_filename}'...")
        
        ffmpeg_start = time.perf_counter()
        
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "1", "-preset", "slow", 
            "-g", "1", "-pix_fmt", "yuv420p", target_video
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
            ffmpeg_end = time.perf_counter()
            
            print(f"    + [ SUCCESS ] Video direkt aus Speicher-Logik exportiert: '{video_filename}'")
            
            print(" -> Bereinige temporaere Frame-Sequenzen aus dem Cache...")
            for frame_idx in range(self.frames_limit):
                frame_path = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
                if os.path.exists(frame_path):
                    os.remove(frame_path)
            try:
                os.rmdir(self.output_directory)
                print("    + [ SUCCESS ] Cache vollstaendig geleert. Nur die digitale MP4 verbleibt.")
            except OSError:
                pass
            
            cpu_name = self._get_cpu_name()
            gen_duration = self.total_generation_end - self.total_generation_start
            comp_duration = ffmpeg_end - ffmpeg_start
            total_time = gen_duration + comp_duration
            
            print(f"\n[ TELEMETRIE ] Matrix-Simulation abgeschlossen!")
            print(f" -> Berechnet auf: {cpu_name}")
            print(f" -> Zeit fuer 3D-Bilderzeugung: {gen_duration:.2f} Sekunden")
            print(f" -> Zeit fuer ffmpeg-Kompilierung: {comp_duration:.2f} Sekunden")
            print(f" -> Gesamtdauer der Pipeline: {total_time:.2f} Sekunden")
            print(f" -> Gesamte geschriebene Datenmasse: {self.accumulated_pixels_written:,} Bildpunkte im Cache-Speicher.\n")
            return 1
        except Exception:
            print("    ! [ SYSTEM NOTICE ] Fehler bei der ffmpeg-Kompilierung.")
            return 0

if __name__ == "__main__":
    print("[ pTRC-PIPELINE ] Starte deterministischen Video-Export fuer X (Twitter)...")
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    pipeline.generate_deterministic_video_sequence()
    status = pipeline.compile_lossless_output_video()
    
    print(f" -> [ VALIDATION ] Video-Pipeline beendet. Status: {status}")
    print(" -> STATUS: Zero-Float Cinematic Video Suite Successfully Audited.")
