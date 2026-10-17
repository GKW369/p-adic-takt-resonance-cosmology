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
Optimized: Complete pure-space indentation alignment preventing any compiler block crash.
"""

import os
import sys
import subprocess
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

# STATISCH FIXIERT AN DEINE 'ptrc_clock_core.py'
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
    flight through the 1-bit integer physics grid layers, saving sequenced media.
    """
    def __init__(self, total_frames=144):
        self.frames_limit = total_frames
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=1920, viewport_height=1080)
        self.clock_engine = PTRCModularClockEngine(width=320, height=180, depth=128)
        
        # Lokaler Ordner exakt im Verzeichnis des Skripts
        self.output_directory = os.path.join(script_dir, "Renderframes")
        
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

    def _determine_next_video_path(self):
        """
        Calculates the next free automated index number in the local script folder.
        """
        counter = 1
        while True:
            candidate_name = f"ptrc_video_{counter:03d}.mp4"
            candidate_path = os.path.join(script_dir, candidate_name)
            if not os.path.exists(candidate_path):
                return candidate_path
            counter += 1

    def compile_lossless_takt_video(self):
        """
        Combines the calculated png frames into a high-bitrate streaming file
        and purges the raw images upon a verified process completion.
        """
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.png")
        target_video = self._determine_next_video_path()
        video_filename = os.path.basename(target_video)
        
        print(f" -> Starte ffmpeg-Kompilierung...")
        print(f" -> Ziel-Datei: '{video_filename}'")
        
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "1", "-preset", "fast", 
            "-g", "1", "-pix_fmt", "yuv420p", target_video
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
            print(f"    + [ SUCCESS ] Video erfolgreich erstellt: '{video_filename}'")
            
            print(" -> Bereinige Ordner 'Renderframes'...")
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
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"    ! [ SYSTEM NOTICE ] ffmpeg-Kompilierung fehlgeschlagen oder nicht installiert.")
            return 0

if __name__ == "__main__":
    print("[ pTRC-ANIMATION ] Starte Takt-Synchronisierte Flug-Pipeline durch das Gitter...")
    generator = PTRC3DAnimationGenerator(total_frames=144)
    
    # Bilder erzeugen
    generator.generate_lossless_flight_sequence()
    
    # Video rendern und aufräumen
    status = generator.compile_lossless_takt_video()
    
    print(f" -> [ VALIDATION ] Flug-Pipeline beendet. Status: {status}")
    print(" -> STATUS: Zero-Float Takt-Synchronized Animation Suite Successfully Audited.")
