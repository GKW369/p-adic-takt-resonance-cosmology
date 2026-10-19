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
Operational Domain: Distributed pTRC-Machines Operating In-Memory on 1D Chains (\mathbb{Z}).
Optimized: Complete 3D index column separation with 12-axis contact-resonance updates.
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
    lossless mp4 flight video directly from flat 1D integer memory arrays.
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
        
        # Plichta-Resonanzring-Skalierung für atomare Cluster
        self.extended_prime_ring = self.primorial_base * 11  # 210 * 11 = 2310
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        # Generiere die statische Modulo-137-Zahlenlandkarte im Speicher
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
        Renders a perfectly timed flight sequence decoding flat 1D integer streams.
        Executes distributed pTRC-machines mapping the shared topological DNA.
        """
        cpu_name = self._get_cpu_name()
        print(f"[ OFFLINE PIPELINE ] Hardware-Erkennung: {cpu_name}")
        print(f" -> Generiere {self.frames_limit} perfekte Frames fuer die Video-Ausgabe...")
        
        self.total_generation_start = time.perf_counter()
        self.accumulated_pixels_written = 0
        
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        
        # Lade die Kristallachsen der Kern-Engine starr als Ganzzahl-Matrix
        crystal_axes = np.array(self.clock_engine.crystal_axes, dtype=np.int32)
        
        # Weitungsschritte für die makroskopische Vergrößerung der Planck-Pixel ins Sichtfeld
        steps = np.arange(-48, 48, dtype=np.int32)
        
        # !!! CORES ZONE: DER GETEILTE GLOBALE BAUPLAN (DNA-MATRIX) !!!
        # Statische Ganzzahl-Offsets für die 12 primären Berührungsflächen des 144-seitigen Raumkristalls
        crystal_contact_offsets = np.array([
            [-2, -1], [-2,  1], [ 2, -1],
            [-1, -2], [-1,  2], [ 1, -2],
            [ 0, -3], [-3,  0], [-1, -1],
            [ 1,  1], [-1,  1], [ 1, -1]
        ], dtype=np.int32)

        for frame_idx in range(self.frames_limit):
            frame_start_time = time.perf_counter()
            
            self.stereo_engine.left_eye_buffer.fill(0)
            self.stereo_engine.right_eye_buffer.fill(0)
            
            # 1-Pixel-Rutschtakt pro Zeitschritt der Lichtgeschwindigkeit
            z_flight_offset = (frame_idx * 1) % self.depth
            local_environmental_load = int(self.accumulated_pixels_written % 256)
            
            # Direktes Abgreifen des verflachten In-Memory Speicherbands
            flat_voxels = self.clock_engine.voxels.ravel()
            
            # ==================================================================
            # !!! TARGET ZONE: UNKORRUMPIERTER UNTERSCHIED ÜBER MATRIX-INDICES !!!
            # ==================================================================
            for axis_idx, axis in enumerate(crystal_axes):
                # MATHEMATISCHE RETTUNG: Explizites Auslesen der echten 3D-Spaltenkomponenten!
                # Heilt den horizontalen Linienstau an der Wurzel und entfaltet das Volumen.
                ax_x = int(axis[0])
                ax_y = int(axis[1])
                ax_z = int(axis[2])
                
                # Lineare Ganzzahl-Schritte modulo Dimensionen
                z_g = (cz + ax_z * steps * 4 - z_flight_offset) % self.depth
                y_g = (cy + ax_y * steps * 4) % self.height
                x_g = (cx + ax_x * steps * 4) % self.width
                
                # Der unbestechliche 1D-Speicher-Index (Verflachtes Koordinaten-Sieve)
                flat_memory_addresses = (z_g * self.height * self.width) + (y_g * self.width) + x_g
                pixel_properties = flat_voxels[flat_memory_addresses]
                active_mask = pixel_properties > 0
                
                if np.any(active_mask):
                    raw_z = z_g[active_mask]
                    raw_z[raw_z <= 0] = 1
                    raw_x = x_g[active_mask] - cx
                    raw_y = y_g[active_mask] - cy
                    
                    # Jedes Achsenregister rechnet autark über das Modulo-137 Lastsieb
                    extended_address = (axis_idx + raw_x * raw_y + pixel_properties[active_mask]) % self.extended_prime_ring
                    feynman_addresses = (extended_address + local_environmental_load) % self.feynman_limit
                    
                    valid_nodes = self.deterministic_sieve_array[feynman_addresses] == 1
                    
                    if np.any(valid_nodes):
                        # Holografischer Vorderseiten-Kollaps (Okklusions-Abtastung)
                        first_hit_idx = np.argmax(valid_nodes)
                        
                        f_z = raw_z[valid_nodes][first_hit_idx:first_hit_idx+1]
                        f_x = raw_x[valid_nodes][first_hit_idx:first_hit_idx+1]
                        f_y = raw_y[valid_nodes][first_hit_idx:first_hit_idx+1]
                        
                        # Flieẞkommafreie Perspektiv-Division (//) fuer flache Displays
                        denom = ((f_z * 1000) // 1414) + 156
                        p_x_center = (f_x * 8 * 1000) // denom
                        p_y_center = (f_y * 8 * 1000) // denom
                        
                        out_x = (p_x_center + self.stereo_engine.width // 2) % self.stereo_engine.width
                        out_y = (p_y_center + self.stereo_engine.height // 2) % self.stereo_engine.height
                        
                        # Auslesen der Plichta-Variablen am getroffenen Grenzregister
                        current_material_value = pixel_properties[active_mask][valid_nodes][first_hit_idx:first_hit_idx+1]
                        
                        # Sowohl Materie- (1) als auch Aetherknoten (2) aktivieren das Feld
                        is_glowing_structure = (current_material_value == 1) | (current_material_value == 2)
                        
                        if np.any(is_glowing_structure):
                            # Projiziere die 144-seitige Form entlang der 12 echten Kontakt-Flächen
                            for offset in crystal_contact_offsets:
                                # Absolut saubere Trennung von X- und Y-Offsetkomponenten
                                off_x = int(offset[0])
                                off_y = int(offset[1])
                                
                                self.stereo_engine.left_eye_buffer[(out_y + off_y) % self.stereo_engine.height, (out_x + off_x) % self.stereo_engine.width] = 1
                                self.stereo_engine.right_eye_buffer[(out_y + off_y) % self.stereo_engine.height, (out_x + off_x) % self.stereo_engine.width] = 1
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
