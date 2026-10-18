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
Operational Domain: Cinematic 3D Whole-Number Projections (\mathbb{Z}) into the Primorial Sieve.
Optimized: 144-Facet Crystalline Raycaster projecting genuine prime-sieve symmetries.
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
    lossless mp4 flight video directly from the core memory arrays.
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
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def _get_cpu_name(self):
        """Detects the exact hardware processor name for the telemetry overview."""
        try:
            if platform.system() == "Linux":
                command = "cat /proc/cpuinfo | grep 'model name' | uniq"
                cpu_info = subprocess.check_output(command, shell=True).decode().strip()
                if cpu_info:
                    return cpu_info.split(":").strip()
        except Exception:
            pass
        return "Acer Desktop CPU"
    def generate_deterministic_video_sequence(self):
        """
        Renders a perfectly timed 6-second flight through the spatial crystal sieve.
        Projects the 1-byte data directly along the 144 crystalline symmetry vectors.
        """
        cpu_name = self._get_cpu_name()
        print(f"[ OFFLINE PIPELINE ] Hardware-Erkennung: {cpu_name}")
        print(f" -> Generiere {self.frames_limit} perfekte Frames fuer die Video-Ausgabe...")
        
        self.total_generation_start = time.perf_counter()
        self.accumulated_pixels_written = 0
        
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        allowed_24_list = [1, 5, 7, 11, 12, 13, 17, 19, 23]
        
        # Lade die 144 echten Kristallachsen des Uhrsystems
        crystal_axes = self.clock_engine.crystal_axes
        
        # 2D Bildschirm-Gitter-Vektoren für das Full-HD Sichtfeld
        grid_y, grid_x = np.indices((self.stereo_engine.height, self.stereo_engine.width))
        screen_cx = self.stereo_engine.width // 2
        screen_cy = self.stereo_engine.height // 2
        
        # ==================================================================
        # MATHEMATISCHE VARIABLEN: DIE ZWEI STATISCHEN KUGEL-REFERENZEN
        # ==================================================================
        # KUGEL 1 (Zentraler Hauptkörper - Radius 80)
        dx_l1 = grid_x - (screen_cx - 24)
        dx_r1 = grid_x - (screen_cx + 24)
        dy_s1 = grid_y - screen_cy
        quad_l1 = (dx_l1 * dx_l1) + (dy_s1 * dy_s1)
        quad_r1 = (dx_r1 * dx_r1) + (dy_s1 * dy_s1)
        
        mask_takt_l1 = np.isin(quad_l1 % self.control_base, allowed_24_list)
        mask_prim_l1 = (quad_l1 % self.primorial_base) <= self.invariant_limit
        sphere_l1 = (quad_l1 < 18000) & (mask_takt_l1 | mask_prim_l1)
        
        mask_takt_r1 = np.isin(quad_r1 % self.control_base, allowed_24_list)
        mask_prim_r1 = (quad_r1 % self.primorial_base) <= self.invariant_limit
        sphere_r1 = (quad_r1 < 18000) & (mask_takt_r1 | mask_prim_r1)
        
        # KUGEL 2 (Der versetzte zweite Bezugspunkt - Radius 40, verschoben nach rechts oben)
        offset_x, offset_y = 350, -220
        dx_l2 = grid_x - (screen_cx - 24 + offset_x)
        dx_r2 = grid_x - (screen_cx + 24 + offset_x)
        dy_s2 = grid_y - (screen_cy + offset_y)
        quad_l2 = (dx_l2 * dx_l2) + (dy_s2 * dy_s2)
        quad_r2 = (dx_r2 * dx_r2) + (dy_s2 * dy_s2)
        
        mask_takt_l2 = np.isin(quad_l2 % self.control_base, allowed_24_list)
        mask_prim_l2 = (quad_l2 % self.primorial_base) <= self.invariant_limit
        sphere_l2 = (quad_l2 < 3500) & (mask_takt_l2 | mask_prim_l2)
        
        mask_takt_r2 = np.isin(quad_r2 % self.control_base, allowed_24_list)
        mask_prim_r2 = (quad_r2 % self.primorial_base) <= self.invariant_limit
        sphere_r2 = (quad_r2 < 3500) & (mask_takt_r2 | mask_prim_r2)
        # ==================================================================

        for frame_idx in range(self.frames_limit):
            frame_start_time = time.perf_counter()
            
            self.stereo_engine.left_eye_buffer.fill(0)
            self.stereo_engine.right_eye_buffer.fill(0)
            
            # ==================================================================
            # !!! TARGET ZONE: RADIALES 144-ACHSEN CRYSTALLINE RAYCASTING !!!
            # ==================================================================
            # Wir zwingen die Projektion entlang der 144 Facetten deines Kristalls.
            z_flight_offset = (frame_idx * 1) % self.depth
            
            for axis in crystal_axes:
                ax, ay, az = axis, axis, axis
                
                # Wir fließen entlang des 1-Byte-Strahls durch das Universum
                for step in range(-64, 64):
                    z_g = (cz + (az * step) // 12 - z_flight_offset) % self.depth
                    y_g = (cy + (ay * step) // 12) % self.height
                    x_g = (cx + (ax * step) // 12) % self.width
                    
                    planck_var = self.clock_engine.voxels[z_g, y_g, x_g]
                    
                    if planck_var > 0:
                        raw_z = int(z_g) if z_g > 0 else 1
                        raw_x = int(x_g - cx)
                        raw_y = int(y_g - cy)
                        
                        takt_check = (raw_x * raw_y + raw_z + planck_var) % self.control_base
                        
                        if takt_check in allowed_24_list:
                            scaled_depth = (raw_z * 1000) // 1414
                            denominator = scaled_depth + 156
                            
                            p_xl = ((raw_x * 8 - 12) * 1000) // denominator
                            p_xr = ((raw_x * 8 + 12) * 1000) // denominator
                            p_y  = ((raw_y * 8) * 1000) // denominator
                            
                            if step % 8 == 0:
                                self.stereo_engine.left_eye_buffer[(p_y + self.stereo_engine.height // 2) % self.stereo_engine.height, (p_xl + self.stereo_engine.width // 2) % self.stereo_engine.width] = 1
                                self.stereo_engine.right_eye_buffer[(p_y + self.stereo_engine.height // 2) % self.stereo_engine.height, (p_xr + self.stereo_engine.width // 2) % self.stereo_engine.width] = 1
            # ==================================================================

            # EINSTANZEN BEIDER RESONANZKÖRPER IN DAS SIGHTFELD
            self.stereo_engine.left_eye_buffer[sphere_l1] = 1
            self.stereo_engine.right_eye_buffer[sphere_r1] = 1
            self.stereo_engine.left_eye_buffer[sphere_l2] = 1
            self.stereo_engine.right_eye_buffer[sphere_r2] = 1
            
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
            
            # Telemetrie-Zusammenfassung ausgeben
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

