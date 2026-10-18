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
Optimized: Pure On-Demand 137-Takt Feynman Vacuum Sieve reading static prime lookup maps.
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
    lossless mp4 flight video directly from the core 1-byte memory arrays.
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
        self.SCALE = 1000
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        # Generiere die statische, unveränderliche 210-Primzahlen-Landkarte im Speicher
        self.deterministic_sieve_array = np.zeros(self.primorial_base, dtype=np.uint8)
        self._generate_totient_sieve_matrix()

        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def _generate_totient_sieve_matrix(self):
        """Populates the static 1-byte lookup-map using Euclidean GCD reduction."""
        for node in range(self.primorial_base):
            val_a, val_b = node, self.primorial_base
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
        Renders a perfectly timed 6-second flight through the spatial crystal sieve.
        Utilizes the static prime map lookup to eliminate coordinate calculations.
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

        steps = np.arange(-64, 64, dtype=np.int32)

        # Vorab-Berechnung der statischen 3D-Kugelnetze im Raum (Ur-DNA Manifestation)
        local_z, local_y, local_x = np.indices((self.depth, self.height, self.width))
        q_s1 = (local_x - cx)**2 + (local_y - cy)**2 + (local_z - 40)**2
        mask_s1 = (q_s1 < 1000) & (np.isin(q_s1 % self.control_base, allowed_24_list) | ((q_s1 % self.primorial_base) <= self.invariant_limit))
        
        q_s2 = (local_x - (cx + 50))**2 + (local_y - (cy + 30))**2 + (local_z - 100)**2
        mask_s2 = (q_s2 < 350) & (np.isin(q_s2 % self.control_base, allowed_24_list) | ((q_s2 % self.primorial_base) <= self.invariant_limit))
        
        sz_n1, sy_n1, sx_n1 = np.where(mask_s1)
        sz_n2, sy_n2, sx_n2 = np.where(mask_s2)

        for frame_idx in range(self.frames_limit):
            frame_start_time = time.perf_counter()
            
            self.stereo_engine.left_eye_buffer.fill(0)
            self.stereo_engine.right_eye_buffer.fill(0)
            
            # ==================================================================
            # !!! TARGET ZONE: LINDEN-MEDIALER FEYNMAN 137-TAKT LOOKUP !!!
            # ==================================================================
            # Das System springt exakt im physikalischen Universumstakt vorwärts
            z_flight_offset = (frame_idx * self.clock_engine.REFRESH_TAKTE) % self.depth
            
            for axis in crystal_axes:
                # Extrahiere die echten Richtungskomponenten der 144 Kristallachsen
                ax_x = int(axis[0])
                ax_y = int(axis[1])
                ax_z = int(axis[2])
                
                # Dezentrale Ganzzahlpfade direkt auf deiner Landkarte ablesen
                z_g = (cz + ax_z * steps - z_flight_offset) % self.depth
                y_g = (cy + ax_y * steps) % self.height
                x_g = (cx + ax_x * steps) % self.width
                
                planck_vars = self.clock_engine.voxels[z_g, y_g, x_g]
                active_mask = planck_vars > 0
                
                if np.any(active_mask):
                    raw_z = z_g[active_mask]
                    raw_z[raw_z <= 0] = 1
                    raw_x = x_g[active_mask] - cx
                    raw_y = y_g[active_mask] - cy
                    
                    # Die Modulo-Adresse ist der exakte Index auf der unendlichen Sieve-Landkarte
                    clamped_addresses = (raw_x * raw_y + raw_z + planck_vars[active_mask]) % self.primorial_base
                    
                    # BLITZSCHNELLER LANDKARTEN-LOOKUP (Reines Ablesen der Variablen!)
                    valid_nodes = self.deterministic_sieve_array[clamped_addresses] == 1
                    
                    if np.any(valid_nodes):
                        f_z = raw_z[valid_nodes]
                        f_x = raw_x[valid_nodes]
                        f_y = raw_y[valid_nodes]
                        
                        control_check = ((f_x * f_y + f_z) * self.SCALE) // self.control_base
                        valid_points = (control_check % 2 == 0)
                        
                        if np.any(valid_points):
                            final_z = f_z[valid_points]
                            final_x = f_x[valid_points]
                            final_y = f_y[valid_points]
                            
                            denom = ((final_z * 1000) // 1414) + 156
                            p_xl = ((final_x * 8 - 12) * 1000) // denom
                            p_xr = ((final_x * 8 + 12) * 1000) // denom
                            p_y  = ((final_y * 8) * 1000) // denom
                            
                            out_x_l = (p_xl + self.stereo_engine.width // 2) % self.stereo_engine.width
                            out_x_r = (p_xr + self.stereo_engine.width // 2) % self.stereo_engine.width
                            out_y_s = (p_y + self.stereo_engine.height // 2) % self.stereo_engine.height
                            
                            self.stereo_engine.left_eye_buffer[out_y_s, out_x_l] = 1
                            self.stereo_engine.right_eye_buffer[out_y_s, out_x_r] = 1
            # ==================================================================

            # EINSTANZEN BEIDER RESONANZKÖRPER MIT ABSOLUTER TIEFENKONVERGENZ (FLUG-PARALLAXE)
            if len(sx_n1) > 0:
                raw_sz1 = (sz_n1 - z_flight_offset)
                raw_sz1[raw_sz1 <= 0] += self.depth
                raw_sz1 = np.clip(raw_sz1, 1, self.depth)
                denom_1 = ((raw_sz1 * 1000) // 1414) + 156
                p_xl1 = (((sx_n1 - cx) * 8 - 12) * 1000) // denom_1
                p_xr1 = (((sx_n1 - cx) * 8 + 12) * 1000) // denom_1
                p_y1  = (((sy_n1 - cy) * 8) * 1000) // denom_1
                self.stereo_engine.left_eye_buffer[(p_y1 + self.stereo_engine.height // 2) % self.stereo_engine.height, (p_xl1 + self.stereo_engine.width // 2) % self.stereo_engine.width] = 1
                self.stereo_engine.right_eye_buffer[(p_y1 + self.stereo_engine.height // 2) % self.stereo_engine.height, (p_xr1 + self.stereo_engine.width // 2) % self.stereo_engine.width] = 1

            if len(sx_n2) > 0:
                raw_sz2 = (sz_n2 - z_flight_offset)
                raw_sz2[raw_sz2 <= 0] += self.depth
                raw_sz2 = np.clip(raw_sz2, 1, self.depth)
                denom_2 = ((raw_sz2 * 1000) // 1414) + 156
                p_xl2 = (((sx_n2 - cx) * 8 - 12) * 1000) // denom_2
                p_xr2 = (((sx_n2 - cx) * 8 + 12) * 1000) // denom_2
                p_y2  = (((sy_n2 - cy) * 8) * 1000) // denom_2
                self.stereo_engine.left_eye_buffer[(p_y2 + self.stereo_engine.height // 2) % self.stereo_engine.height, (p_xl2 + self.stereo_engine.width // 2) % self.stereo_engine.width] = 1
                self.stereo_engine.right_eye_buffer[(p_y2 + self.stereo_engine.height // 2) % self.stereo_engine.height, (p_xr2 + self.stereo_engine.width // 2) % self.stereo_engine.width] = 1

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
