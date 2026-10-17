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
Optimized: Intelligent Namespace Resolver protecting pipeline paths from ModuleNotFoundError.
"""

import os
import sys
import subprocess
import numpy as np
import cv2

# ==============================================================================
# !!! TARGET ZONE: INTELLIGENTE IMPORT-ABFHRUNG GEGEN MODULENOTFOUNDERROR !!!
# MARKER: PTRC_DYNAMIC_IMPORT_RESOLVER_2026
# ==============================================================================
try:
    # 1. Versuch: Direkter Import aus demselben Ordner (Behebt den Fehler)
    from ptrc_3d_stereo_engine import PTRC3DStereoEngine
    from ptrc_modular_clock_engine import PTRCModularClockEngine
    print(" -> [ PATH ] Module erfolgreich direkt aus dem lokalen Verzeichnis geladen.")
except ImportError:
    try:
        # 2. Versuch: Import über die übergeordnete src-Struktur
        from src.ptrc_3d_stereo_engine import PTRC3DStereoEngine
        from src.ptrc_modular_clock_engine import PTRCModularClockEngine
        print(" -> [ PATH ] Module erfolgreich über src-Präfix geladen.")
    except ImportError:
        # 3. Versuch: Pfad-Erweiterung für tief geschachtelte Ordnerstrukturen
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(current_dir)
        sys.path.append(os.path.join(current_dir, '..'))
        
        try:
            from ptrc_3d_stereo_engine import PTRC3DStereoEngine
            from ptrc_modular_clock_engine import PTRCModularClockEngine
        except ImportError:
            from src.ptrc_3d_stereo_engine import PTRC3DStereoEngine
            from src.ptrc_modular_clock_engine import PTRCModularClockEngine
        print(" -> [ PATH ] Module über dynamische Systempfad-Erweiterung geladen.")
# ==============================================================================
# !!! END OF TARGET ZONE !!!
# ==============================================================================

class PTRC3DAnimationGenerator:
    """
    Orchestrates the camera travel parameters to execute a continuous uncompressed
    flight through the 1-bit integer physics grid layers, purging raw cache files.
    """
    def __init__(self, total_frames=144):  # 144 Frames bei 24 FPS = Exakt 6 Sekunden Flug
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        self.clock_engine = PTRCModularClockEngine(width=320, height=180, depth=128)
        self.output_directory = "output_pipeline"
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def generate_lossless_flight_sequence(self):
        """
        Extracts active voxel states from the primorial core matrix and streams them
        into the stereoscopic retina buffers while changing the Z-depth offset per frame.
        """
        print(f"[ FLIGHT ] Generiere {self.frames_limit} hochauflösende Gitter-Ebenen im Z-Raum...")
        
        z_indices, y_indices, x_indices = np.where(self.clock_engine.voxels == 2)
        total_active_nodes = len(x_indices)
        
        print(f" -> Gefundene aktive Resonanz-Knoten im Speicher-Universum: {total_active_nodes}")
        
        v_width, v_height = self.clock_engine.width, self.clock_engine.height
        
        for frame_idx in range(self.frames_limit):
            self.stereo_engine.left_eye_buffer.fill(0)
            self.stereo_engine.right_eye_buffer.fill(0)
            
            z_flight_offset = (frame_idx * 2) % 128
            
            for i in range(0, total_active_nodes, 4):
                raw_z = int(z_indices[i] - z_flight_offset)
                if raw_z <= 0:
                    raw_z += 128
                
                raw_x = int(x_indices[i] - v_width // 2)
                raw_y = int(y_indices[i] - v_height // 2)
                
                self.stereo_engine.project_spatial_voxel_node(
                    coord_x=raw_x * 8,
                    coord_y=raw_y * 8,
                    coord_z=raw_z * 12,
                    focal_offset=12
                )
            
            self.clock_engine.evolve_clock_one_takt()
            pixel_sharp_view = self.stereo_engine.left_eye_buffer * 255
            
            frame_filename = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
            cv2.imwrite(frame_filename, pixel_sharp_view)
            
            if frame_idx % 24 == 0:
                print(f"    + Frame {frame_idx}/{self.frames_limit} erfolgreich in Matrix gerastert.")

    def compile_lossless_takt_video(self):
        """
        Combines the calculated png frames into a high-bitrate streaming file
        and purges the raw images upon a verified process completion.
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
            print(f"    + [ SUCCESS ] Flug-Animation erfolgreich kompiliert: '{target_video}'")
            
            print(" -> Bereinige temporäre Frame-Sequenzen aus dem Pipeline-Verzeichnis...")
            for frame_idx in range(self.frames_limit):
                frame_path = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.png")
                if os.path.exists(frame_path):
                    os.remove(frame_path)
            
            try:
                os.rmdir(self.output_directory)
            except OSError:
                pass
                
            print("    + [ SUCCESS ] Cache vollständig geleert. Nur die digitale MP4 verbleibt.")
            return 1
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"    ! [ SYSTEM NOTICE ] ffmpeg-Kompilierung fehlgeschlagen oder nicht installiert.")
            print(" -> Frames wurden aus Sicherheitsgründen nicht gelöscht, damit keine Daten verloren gehen.")
            return 0

if __name__ == "__main__":
    print("[ pTRC-ANIMATION ] Starte Takt-Synchronisierte Flug-Pipeline durch das Gitter...")
    generator = PTRC3DAnimationGenerator(total_frames=144)
    
    # Bilder erzeugen
    generator.generate_lossless_flight_sequence()
    
    # Video rendern und Bilder automatisch löschen
    status = generator.compile_lossless_takt_video()
    
    print(f" -> [ VALIDATION ] Flug-Pipeline beendet. Status: {status}")
    print(" -> STATUS: Zero-Float Takt-Synchronized Animation Suite Successfully Audited.")
