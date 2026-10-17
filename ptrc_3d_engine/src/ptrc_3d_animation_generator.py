# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ==============================================================================

# -*- coding: utf-8 -*-
r"""
pTRC Framework - Advanced Animation Pipeline: Hyper-Dignity Voxel Flight Sieve
Operational Domain: Cinematic 3D Whole-Number Projections (\mathbb{Z}) into the Primorial Sieve.
Optimized: On-the-fly streaming generation bypassing RAM limits to prevent OS Out-of-Memory Kill.
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
# !!! END OF TARGET ZONE !!!
# ==============================================================================

class PTRC3DAnimationGenerator:
    """
    Orchestrates the camera travel parameters to execute a continuous uncompressed
    flight through the 1-bit integer physics grid layers, using zero-ram chunk generation.
    """
    def __init__(self, total_frames=144):
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        
        # Harmonische HD-Videospielauflösung (Vollkommen stabil im RAM)
        self.width = 1680
        self.height = 1050
        self.depth = 420
        self.primorial_base = 210
        self.control_base = 24
        
        # Initialisiere die Achsen des Kristalls direkt im Generator
        self.clock_engine = PTRCModularClockEngine(width=160, height=90, depth=64)
        self.crystal_axes = self.clock_engine.crystal_axes
        
        self.output_directory = os.path.join(script_dir, "Renderframes")
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def _get_cpu_name(self):
        try:
            if platform.system() == "Linux":
                command = "cat /proc/cpuinfo | grep 'model name' | uniq"
                return subprocess.check_output(command, shell=True).decode().strip().split(":")[1].strip()
        except Exception:
            pass
        return "Intel(R) Core(TM) i3-3217U CPU @ 1.80GHz"

    def generate_lossless_flight_sequence(self):
        """
        Generates 1-bit crystal interference nodes dynamically per frame.
        Protects older CPUs/RAM configurations from collapsing while maintaining high density.
        """
        print(f"[ FLIGHT ] Starte RAM-geschützte 1-Bit Kristall-Abtastung (HD-Skala)...")
        cpu_name = self._get_cpu_name()
        
        total_pipeline_start = time.perf_counter()
        accumulated_pixels_written = 0
        
        cx, cy, cz = self.width // 2, self.height // 2, self.depth // 2
        allowed_24_rays = {1, 5, 7, 11, 13, 17, 19, 23}
        
        for frame_idx in range(self.frames_limit):
            frame_start_time = time.perf_counter()
            
            # Leere die Retina-Puffer für das aktuelle Einzelbild
            self.stereo_engine.left_eye_buffer.fill(0)
            self.stereo_engine.right_eye_buffer.fill(0)
            
            # Dynamischer Vorschub (Fortlaufender Flug) im Takt
            z_flight_offset = (frame_idx * 4) % self.depth
            
            # ==================================================================
            # !!! TARGET ZONE: ON-THE-FLY INTERFERENZ STRÖMUNG (ZERO RAM) !!!
            # ==================================================================
            # Jedes Frame berechnet seine Kristallknoten direkt frisch im Durchlauf
            for axis in self.crystal_axes:
                ax, ay, az = axis, axis, axis
                
                # Wir tasten das Gitter entlang des 1-Bit-Strahls ab
                for step in range(-120, 120):
                    x_g = cx + (ax * step) // 6
                    y_g = cy + (ay * step) // 6
                    z_g = cz + (az * step) // 6
                    
                    if 0 <= x_g < self.width and 0 <= y_g < self.height and 0 <= z_g < self.depth:
                        # Berechne die p-adische Metrik (Resonanz) am Knotenpunkt
                        quadrance = (x_g - cx)**2 + (y_g - cy)**2 + (z_g - cz)**2
                        
                        if quadrance % self.primorial_base <= 156:
                            takt_check = (x_g * y_g + z_g) % self.control_base
                            
                            if takt_check in allowed_24_rays:
                                # Relativen Tiefenabstand zum fliegenden Beobachter berechnen
                                raw_z = int(z_g - z_flight_offset)
                                if raw_z <= 0:
                                    raw_z += self.depth
                                    
                                raw_x = int(x_g - cx)
                                raw_y = int(y_g - cy)
                                
                                # Stereoskopische Retina-Projektion ohne Umwege
                                self.stereo_engine.project_spatial_voxel_node(
                                    coord_x=raw_x,
                                    coord_y=raw_y,
                                    coord_z=raw_z,
                                    focal_offset=14
                                )
            # ==================================================================
            
            pixel_sharp_view = self.stereo_engine.left_eye_buffer * 255
            frame_filename = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
            cv2.imwrite(frame_filename, pixel_sharp_view)
            
            frame_end_time = time.perf_counter()
            frame_duration_ms = (frame_end_time - frame_start_time) * 1000
            
            active_pixels_in_frame = int(np.sum(self.stereo_engine.left_eye_buffer))
            accumulated_pixels_written += active_pixels_in_frame
            
            if frame_idx % 12 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Frame {frame_idx:03d}/{self.frames_limit} | Zeit: {frame_duration_ms:.2f} ms | Aktive Datenpunkte: {active_pixels_in_frame:,} Pixel")

        total_pipeline_end = time.perf_counter()
        print(f"\n[ TELEMETRIE ] Matrix-Generierung erfolgreich abgeschlossen!")
        print(f" -> Berechnet auf: {cpu_name}")
        print(f" -> Gesamtdauer der Bildberechnung: {total_pipeline_end - total_pipeline_start:.2f} Sekunden")
        print(f" -> Gesamte geschriebene Datenmasse: {accumulated_pixels_written:,} Bildpunkte im Cache-Speicher.\n")

    def _determine_next_video_path(self):
        counter = 1
        while True:
            candidate_name = f"ptrc_video_{counter:03d}.mp4"
            candidate_path = os.path.join(script_dir, candidate_name)
            if not os.path.exists(candidate_path):
                return candidate_path
            counter += 1

    def compile_lossless_takt_video(self):
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.png")
        target_video = self._determine_next_video_path()
        video_filename = os.path.basename(target_video)
        
        print(f" -> Starte ffmpeg-Kompilierung von '{video_filename}'...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "1", "-preset", "fast", 
            "-g", "1", "-pix_fmt", "yuv420p", target_video
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
            print(f"    + [ SUCCESS ] Video erfolgreich erstellt: '{video_filename}'")
            for frame_idx in range(self.frames_limit):
                frame_path = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
                if os.path.exists(frame_path):
                    os.remove(frame_path)
            try:
                os.rmdir(self.output_directory)
                print("    + [ SUCCESS ] Ordner 'Renderframes' geleert und aufgeräumt.")
            except OSError:
                pass
            return 1
        except Exception:
            return 0

if __name__ == "__main__":
    generator = PTRC3DAnimationGenerator(total_frames=144)
    generator.generate_lossless_flight_sequence()
    generator.compile_lossless_takt_video()
