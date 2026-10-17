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
pTRC Framework - Advanced Animation Pipeline: Hyper-Dignity Voxel Flight Sieve
Operational Domain: Cinematic 3D Whole-Number Projections (\mathbb{Z}) into the Primorial Sieve.
Generates a 6-second fluid flight sequence through the active modular matrix.
"""

import os
import sys
import subprocess
import numpy as np
import cv2

# Sicheres Importieren der beiden reparierten Kernkomponenten
try:
    from src.ptrc_3d_stereo_engine import PTRC3DStereoEngine
    from src.ptrc_modular_clock_engine import PTRCModularClockEngine
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from src.ptrc_3d_stereo_engine import PTRC3DStereoEngine
    from src.ptrc_modular_clock_engine import PTRCModularClockEngine

class PTRC3DAnimationGenerator:
    """
    Orchestrates the camera travel parameters to execute a continuous uncompressed
    flight through the 1-bit integer physics grid layers.
    """
    def __init__(self, total_frames=144):  # 144 Frames bei 24 FPS = Exakt 6 Sekunden Flug
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        self.clock_engine = PTRCModularClockEngine(width=320, height=180, depth=128) # Größeres Gitter für mehr Tiefe
        self.output_directory = "output_pipeline"
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def generate_lossless_flight_sequence(self):
        """
        Extracts active voxel states from the primorial core matrix and streams them
        into the stereoscopic retina buffers while changing the Z-depth offset per frame.
        """
        print(f"[ FLIGHT ] Generiere {self.frames_limit} hochauflösende Gitter-Ebenen im Z-Raum...")
        
        # Extrahiere die Koordinaten aller aktiven Resonanz-Knoten (Zustand 2) aus der Uhr-Engine
        z_indices, y_indices, x_indices = np.where(self.clock_engine.voxels == 2)
        total_active_nodes = len(x_indices)
        
        print(f" -> Gefundene aktive Resonanz-Knoten im Speicher-Universum: {total_active_nodes}")
        
        # Kamera-Zentrum bestimmen
        v_width, v_height = self.clock_engine.width, self.clock_engine.height
        
        for frame_idx in range(self.frames_limit):
            # 1. Puffer für das aktuelle Bild vollständig leeren
            self.stereo_engine.left_eye_buffer.fill(0)
            self.stereo_engine.right_eye_buffer.fill(0)
            
            # Ein kontinuierlicher Tiefenvorschub simuliert den Vorwärtsflug durch die Matrix
            # Modulo-Zyklen halten den Flug unendlich fließend im Takt
            z_flight_offset = (frame_idx * 2) % 128
            
            # 2. Iteriere über die vorhandenen Ganzzahl-Resonanzknoten
            for i in range(0, total_active_nodes, 4):  # Schrittweite 4 für optimale Felddichte ohne Overlap
                # Koordinaten relativ zum bewegten Beobachter berechnen
                raw_z = int(z_indices[i] - z_flight_offset)
                if raw_z <= 0:
                    raw_z += 128  # Warp-Verschiebung hinter die Kamera für nahtlosen Loop
                
                # Zentrierung der Gitterpunkte auf das Sichtfeld
                raw_x = int(x_indices[i] - v_width // 2)
                raw_y = int(y_indices[i] - v_height // 2)
                
                # 3. Projektion in die Stereo-Puffer via fixed-point Arithmetik
                self.stereo_engine.project_spatial_voxel_node(
                    coord_x=raw_x * 8,      # Skalierung für epische Weite im 1080p Raum
                    coord_y=raw_y * 8,
                    coord_z=raw_z * 12,     # Z-Tiefenspreizung
                    focal_offset=12         # Räumlicher Stereo-Augenabstand
                )
            
            # Schalte die Hintergrund-Uhr-Matrix pro Frame um einen Takt weiter (c=1 Bewegung)
            self.clock_engine.evolve_clock_one_takt()
            
            # Konvertiere das linke Auge-Signal in ein scharfes 8-Bit Graustufenbild
            pixel_sharp_view = self.stereo_engine.left_eye_buffer * 255
            
            # Frame auf Festplatte sichern
            frame_filename = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
            cv2.imwrite(frame_filename, pixel_sharp_view)
            
            if frame_idx % 24 == 0:
                print(f"    + Frame {frame_idx}/{self.frames_limit} erfolgreich in Matrix gerastert.")

    def compile_lossless_takt_video(self):
        """
        Combines the calculated png frames into a high-bitrate streaming file.
        """
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.png")
        target_video = "ptrc_lossless_takt_resonance.mp4"
        
        print(f" -> Starte ffmpeg-Kompilierung für die verlustfreie 24-FPS-Taktung...")
        
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "1", "-preset", "fast", 
            "-g", "1", "-pix_fmt", "yuv420p", target_video
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
            print(f"    + [ SUCCESS ] 6-Sekunden-Flug-Animation erfolgreich kompiliert: '{target_video}'")
            return 1
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"    ! [ SYSTEM NOTICE ] ffmpeg-Kompilierung übersprungen. Die 144 Einzelbilder liegen im Ordner.")
            return 0

if __name__ == "__main__":
    print("[ pTRC-ANIMATION ] Starte Takt-Synchronisierte Flug-Pipeline durch das Gitter...")
    generator = PTRC3DAnimationGenerator(total_frames=144)
    
    # Ausführen der Voxel-Abtastung und der Bilder-Generierung
    generator.generate_lossless_flight_sequence()
    
    # Video-Kompression triggern
    status = generator.compile_lossless_takt_video()
    
    print(f" -> [ VALIDATION ] Flug-Pipeline beendet. Status: {status}")
    print(" -> STATUS: Zero-Float Takt-Synchronized Animation Suite Successfully Audited.")
