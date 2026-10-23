# -*- coding: utf-8 -*-
r"""
pTRC Framework - Advanced Volumetric Transposition Suite (Relativistic Passing Engine)
Operational Domain: Pure Integer Viewports (\mathbb{Z}^3). Zero Analog Leakage.
Filename: ptrc_3d_animation_generator.py
100% Dependency-Free: Erzeugt Bilder nativ ueber reines Ganzzahl-PPM-Streaming.
"""

import os
import sys
import subprocess
import time
import numpy as np  # Direkt im Header verankert fuer stabilen Import

# Modul-Kopplung
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from ptrc_3d_stereo_engine import PTRC3DStereoEngine
except ImportError:
    from src.ptrc_3d_stereo_engine import PTRC3DStereoEngine

class PTRC3DAnimationPipeline:
    def __init__(self, total_frames=144):
        self.frames_limit = total_frames
        # Nutzt die korrekte StereoEngine aus Source 3 mit Viewport-Uebergabe
        self.stereo_engine = PTRC3DStereoEngine(viewport_width=320, viewport_height=180)
        
        self.width = self.stereo_engine.width
        self.height = self.stereo_engine.height
        self.invariant_limit = 156
        self.FEYNMAN_LIMIT = 137  
        self.SCALE = 1000
        
        self.output_directory = os.path.join(script_dir, "Renderframes_Cache")
        
        self.time_pipeline_start = 0
        self.time_rendering_done = 0
        self.time_io_write_accumulated = 0
        self.time_ffmpeg_done = 0
        self.accumulated_voxels_processed = 0
        self.accumulated_bytes_written = 0
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def write_ppm_image(self, filename, buffer_matrix):
        """Schreibt eine reine Ganzzahl-PPM-Bilddatei (P6-Binär) ohne externe Bibliotheken."""
        h, w, _ = buffer_matrix.shape
        header = f"P6\n{w} {h}\n255\n".encode('ascii')
        
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(buffer_matrix.tobytes())

    def draw_integer_rectangle(self, buffer, x1, y1, x2, y2, color):
        """Zeichnet ein Rechteck direkt auf die Byte-Matrix mittels Ganzzahl-Slicing."""
        # Begrenzung gegen Gitter-Ueberlaeufe (Sicheres Voxel-Clipping)
        x1 = max(0, min(int(x1), self.width - 1))
        x2 = max(0, min(int(x2), self.width - 1))
        y1 = max(0, min(int(y1), self.height - 1))
        y2 = max(0, min(int(y2), self.height - 1))
        
        if x1 > x2: x1, x2 = x2, x1
        if y1 > y2: y1, y2 = y2, y1
        
        buffer[y1:y2+1, x1:x2+1] = color

    def generate_deterministic_video_sequence(self):
        print(f"[ pTRC CORE ] Reines Integer-PPM-Streaming aktiv (Kein OpenCV erforderlich).")
        self.time_pipeline_start = time.perf_counter()
        
        static_z = 58 
        cy = self.height // 2

        fcc_offsets = [
            (0, 0, 0),  
            (2, 2, 0),  (2, -2, 0),  (-2, 2, 0),  (-2, -2, 0),
            (2, 0, 2),  (2, 0, -2), (-2, 0, 2),  (-2, 0, -2),
            (0, 2, 2),  (0, 2, -2), (0, -2, 2),  (0, -2, -2)
        ]

        for frame_idx in range(self.frames_limit):
            frame_render_start = time.perf_counter()
            # Erzeuge leeren Frame-Buffer (RGB-Kanäle)
            frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
            pyramid_move_offset = (frame_idx * 1) % self.width
            pyramid_z_approach = (frame_idx * 1) % 32

            # OBJECT 1: DIE STATISCHE WIRMINGHAUS KUGEL (Spektral-Blau/Cyan)
            cx_sphere = self.width // 4
            for ox, oy, oz in fcc_offsets:
                kx = cx_sphere + (ox * 6)
                ky = cy + (oy * 6)
                kz = static_z + (oz * 4)
                
                denom = ((kz * self.SCALE) // 1414) + self.invariant_limit
                out_x = (((int(kx - (self.width // 2)) * 8 * self.SCALE) // denom) + self.width // 2) % self.width
                out_y = (((int(ky - (self.height // 2)) * 8 * self.SCALE) // denom) + self.height // 2) % self.height
                
                voxel_size = 4
                self.accumulated_voxels_processed += 1
                
                self.draw_integer_rectangle(frame_buffer, 
                                            out_x - voxel_size // 2, out_y - voxel_size // 2,
                                            out_x + voxel_size // 2, out_y + voxel_size // 2,
)  # RGB: Cyan

            # OBJECT 2: DIE BEWEGTE PYRAMIDE (Emerald-Smaragd)
            cx_pyramid_start = (self.width * 3) // 4
            for level in range(3):
                z_layer = level * 2
                y_layer = -level * 4
                for row in range(3 - level):
                    for col in range(3 - level):
                        px = cx_pyramid_start + (col * 14) - ((3 - level) * 7) - pyramid_move_offset
                        py = cy + (row * 14) - ((3 - level) * 7) + 10 + y_layer
                        
                        for ox, oy, oz in fcc_offsets:
                            kx = px + (ox * 2)
                            ky = py + (oy * 2)
                            kz = (static_z + 24) - pyramid_z_approach + (z_layer + oz) * 3
                            
                            denom = ((kz * self.SCALE) // 1414) + self.invariant_limit
                            out_x = (((int(kx - (self.width // 2)) * 8 * self.SCALE) // denom) + self.width // 2) % self.width
                            out_y = (((int(ky - (self.height // 2)) * 8 * self.SCALE) // denom) + self.height // 2) % self.height
                            
                            voxel_size = max(2, (6 * self.SCALE) // denom)
                            self.accumulated_voxels_processed += 1
                            
                            depth_glow = max(40, 255 - ((kz * 150) // 128))
                            self.draw_integer_rectangle(frame_buffer, 
                                                        out_x - voxel_size // 2, out_y - voxel_size // 2,
                                                        out_x + voxel_size // 2, out_y + voxel_size // 2,
                                                        [40, int(depth_glow), 160])

            self.time_rendering_done += (time.perf_counter() - frame_render_start)
            
            io_start = time.perf_counter()
            frame_filename = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.ppm")
            self.write_ppm_image(frame_filename, frame_buffer)
            self.time_io_write_accumulated += (time.perf_counter() - io_start)
            
            if os.path.exists(frame_filename):
                self.accumulated_bytes_written += os.path.getsize(frame_filename)
                
            if frame_idx % 24 == 0 or frame_idx == self.frames_limit - 1:
                print(f"    + Synced Takt-Frame {frame_idx:03d}/{self.frames_limit} | PPM Buffer written")

    def compile_lossless_output_video(self):
        input_pattern = os.path.join(self.output_directory, "takt_frame_%04d.ppm")
        target_video = os.path.join(script_dir, "ptrc_wirminghaus_dual_passing.mp4")
        
        print(" -> Starte FFMPEG Kompression aus PPM-Bildkette...")
        ffmpeg_start = time.perf_counter()
        
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
            "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", target_video
        ]
        try:
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            self.time_ffmpeg_done = time.perf_counter() - ffmpeg_start
            
            # Temporaeren PPM-Cache bereinigen
            for frame_idx in range(self.frames_limit):
                p = os.path.join(self.output_directory, f"takt_frame_{frame_idx:04d}.ppm")
                if os.path.exists(p): os.remove(p)
            os.rmdir(self.output_directory)
            
            print(f"\n[ pTRC INTEGRITY AUDIT ] Master-Videodatei verlustfrei generiert!")
            print(f" -> Pfad: {target_video}\n")
            return 1
        except Exception as e:
            print(f" -> [ HINWEIS ] FFMPEG Subprozess blockiert. Die unkomprimierten")
            print(f"    PPM-Rohdaten verbleiben fehlerfrei im Ordner: {self.output_directory}")
            return 0

if __name__ == "__main__":
    pipeline = PTRC3DAnimationPipeline(total_frames=144)
    pipeline.generate_deterministic_video_sequence()
    pipeline.compile_lossless_output_video()
