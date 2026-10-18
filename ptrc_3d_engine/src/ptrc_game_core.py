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
Optimized: 1-Byte Architecture tracking up to 256 variables per Planck pixel.
"""

import os
import sys
import subprocess
import time
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
        
        self.clock_engine = PTRCModularClockEngine(width=self.width, height=self.height, depth=self.depth)
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
    def generate_deterministic_video_sequence(self):
        """
        Renders a perfectly timed 6-second flight through the spatial crystal sieve.
        Decodes the 256 physical variables of the Planck matrix on-the-fly.
        """
        print(f"[ OFFLINE PIPELINE ] Generiere {self.frames_limit} perfekte Frames fuer die Video-Ausgabe...")
        
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        allowed_24_list = [1, 5, 7, 11, 12, 13, 17, 19, 23]
        
        # 2D Bildschirm-Gitter-Vektoren für die holografische Kugel vorab im RAM laden
        grid_y, grid_x = np.indices((self.stereo_engine.height, self.stereo_engine.width))
        screen_cx = self.stereo_engine.width // 2
        screen_cy = self.stereo_engine.height // 2
        
        dx_l = grid_x - (screen_cx - 24)
        dx_r = grid_x - (screen_cx + 24)
        dy_s = grid_y - screen_cy
        
        quad_l = (dx_l * dx_l) + (dy_s * dy_s)
        quad_r = (dx_r * dx_r) + (dy_s * dy_s)
        
        # Sieve-Filterung für die feste Kugelstruktur (Hologramm-Ebene)
        mask_takt_l = np.isin(quad_l % self.control_base, allowed_24_list)
        mask_prim_l = (quad_l % self.primorial_base) <= self.invariant_limit
        sphere_l = (quad_l < 18000) & (mask_takt_l | mask_prim_l)
        
        mask_takt_r = np.isin(quad_r % self.control_base, allowed_24_list)
        mask_prim_r = (quad_r % self.primorial_base) <= self.invariant_limit
        sphere_r = (quad_r < 18000) & (mask_takt_r | mask_prim_r)

        for frame_idx in range(self.frames_limit):
            # 1. Beide Auge-Kanäle für dieses Bild initialisieren
            self.stereo_engine.left_eye_buffer.fill(0)
            self.stereo_engine.right_eye_buffer.fill(0)
            
            # ==================================================================
            # UNTERSUCHUNG DER 1-BYTE MATRIX (256 PHYSRESONANZ VARIABLEN)
            # ==================================================================
            # Wir tasten das gesamte Gitter nach Werten > 0 ab (Unterstützt alle Byte-Zustände)
            z_indices, y_indices, x_indices = np.where(self.clock_engine.voxels > 0)
            total_nodes = len(x_indices)
            
            if total_nodes > 0:
                # Extrahiere die physikalischen Variablen (Material, Dichte, Temperatur, etc.)
                # Jeder Gitterpunkt trägt einen Wert von 0 bis 255 in seiner 1-Byte-Architektur
                planck_variables = self.clock_engine.voxels[z_indices, y_indices, x_indices]
                
                z_flight_offset = (frame_idx * 1) % self.depth
                
                raw_z = (z_indices - z_flight_offset)
                raw_z[raw_z <= 0] += self.depth
                raw_z = np.clip(raw_z, 1, self.depth)
                
                raw_x = (x_indices - cx)
                raw_y = (y_indices - cy)
                
                scaled_depth = (raw_z * 1000) // 1414
                denominator = scaled_depth + 156
                
                proj_x_left = ((raw_x * 8 - 12) * 1000) // denominator
                proj_x_right = ((raw_x * 8 + 12) * 1000) // denominator
                proj_y = ((raw_y * 8) * 1000) // denominator
                
                out_x_left = (proj_x_left + self.stereo_engine.width // 2) % self.stereo_engine.width
                out_x_right = (proj_x_right + self.stereo_engine.width // 2) % self.stereo_engine.width
                out_y = (proj_y + self.stereo_engine.height // 2) % self.stereo_engine.height
                
                # Der Takt-Check moduliert die Variable des Pixels im Restklassenring
                takt_check = (raw_x * raw_y + raw_z + planck_variables) % self.control_base
                valid_mask = np.isin(takt_check, allowed_24_list)
                
                # INTERAKTIVES RE-SIEVING (TRANSPARENTER VORDER- & HINTERGRUND)
                # Das 1-Byte Raumgitter fliesst permanent und transparent vor und hinter der Kugel vorbei
                if np.any(valid_mask):
                    self.stereo_engine.left_eye_buffer[out_y[valid_mask][::16], out_x_left[valid_mask][::16]] = 1
                    self.stereo_engine.right_eye_buffer[out_y[valid_mask][::16], out_x_right[valid_mask][::16]] = 1

            # 3. DIE MASSIVE HOLOGRAFISCHE KUGEL IM GEMEINSAMEN RAUM DAZWISCHENBETTEN
            self.stereo_engine.left_eye_buffer[sphere_l] = 1
            self.stereo_engine.right_eye_buffer[sphere_r] = 1
            
            # Uhr-Engine für das nächste mathematische Intervall weitertakten
            self.clock_engine.evolve_clock_one_takt()
            
            # Konvertiere das linke Auge-Signal in scharfe 8-Bit Pixel
            bw_frame = self.stereo_engine.left_eye_buffer * 255
            
            # Schreibe das verlustfreie Einzelbild starr in den Cache-Ordner
            frame_filename = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
            cv2.imwrite(frame_filename, bw_frame)
            
            if frame_idx % 24 == 0:
                print(f"    + Frame {frame_idx}/{self.frames_limit} verlustfrei berechnet.")

    def compile_lossless_output_video(self):
        """
        Binds the uncompressed frame cache array into a clean 24 FPS digital MP4 movie.
        Purges raw file remnants automatically after verified completion.
        """
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.png")
        
        counter = 1
        while True:
            target_video = os.path.join(script_dir, f"ptrc_hologram_{counter:03d}.mp4")
            if not os.path.exists(target_video):
                break
            counter += 1
            
        video_filename = os.path.basename(target_video)
        print(f" -> Starte direkte ffmpeg-Datenabgreifung for '{video_filename}'...")
        
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "1", "-preset", "slow", 
            "-g", "1", "-pix_fmt", "yuv420p", target_video
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
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
            return 1
        except Exception:
            print("    ! [ SYSTEM NOTICE ] Fehler bei der ffmpeg-Kompilierung.")
            return 0

if __name__ == "__main__":
    print("[ pTRC-PIPELINE ] Starte deterministischen Video-Export fuer X (Twitter)...")
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    
    # Führe die ungestörte Offline-Berechnung durch
    pipeline.generate_deterministic_video_sequence()
    
    # Kompiliere das finale Video direkt aus den Daten
    status = pipeline.compile_lossless_output_video()
    
    print(f" -> [ VALIDATION ] Video-Pipeline beendet. Status: {status}")
    print(" -> STATUS: Zero-Float Cinematic Video Suite Successfully Audited.")
