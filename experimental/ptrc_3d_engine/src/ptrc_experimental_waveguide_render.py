# ==============================================================================
# pTRC Framework - Experimental Module: Invariant Kaleidoscope Rotator & Compiler
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program free software: you can redistribute it and/or modify
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
pTRC Framework - Experimental Core: Holographic Voxel Projection Stabilizer
Operational Domain: Symmetrical Integer Translation Matrices (\mathbb{Z}^3).
Fixes coordinate jittering during clock-cycled multi-axis crystal transitions.
Automated with progressive MP4 sequence execution and localized cache purge.
"""

import os
import sys
import subprocess
import time
import numpy as np

class PTRCStabilizedRotator:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156
        self.SCALE = 1000
        
        # Vorab generierte, unbestechliche 144 Kristallachsen für den Richtungs-Lookup
        self.crystal_axes = self._build_invariant_axes()

    def _build_invariant_axes(self):
        """ Generiert 144 exakte, ganzzahlige Richtungs-Vektoren. """
        flat_nodes = [
            2, 1, 0,   2, -1, 0,  -2, 1, 0,  -2, -1, 0,
            0, 2, 1,   0, 2, -1,   0, -2, 1,  0, -2, -1,
            1, 0, 2,  -1, 0, 2,    1, 0, -2, -1, 0, -2
        ]
        base = np.array(flat_nodes, dtype=np.int32).reshape(12, 3)
        axes = []
        for node in base:
            for factor in range(1, 13):
                axes.append(node * factor)
        return np.array(axes, dtype=np.int32)

    def project_stabilized_frame(self, frame_idx, output_dir):
        """
        Rendert ein rauschfreies und ungezacktes FullHD-Frame.
        Sichert die Array-Werte sauber ab, um Mehrdeutigkeiten zu verhindern.
        """
        frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cx, cy = self.width // 2, self.height // 2
        z_offset = 65
        
        # Bestimme die aktuelle Projektionsachse über das Modulo-System
        axis_index = frame_idx % 144
        current_axis = self.crystal_axes[axis_index]
        
        # Duale Polaritäts-Oszillation (Plus/Minus Takt aus Modul 41)
        dual_polarity = 1 if (frame_idx % 2 == 0) else -1
        
        # FIX: Aufteilung der Achsen-Vektoren in explizite Skalare, um ValueError-Arrays zu verhindern
        ax_x = int(current_axis[0])
        ax_y = int(current_axis[1])
        ax_z = int(current_axis[2])
        
        # Iteration durch den lokalen Planck-Raumblock
        for dx in range(-15, 16):
            for dy in range(-15, 16):
                for dz in range(-15, 16):
                    
                    quadrance = dx*dx + dy*dy + dz*dz
                    if quadrance == 0:
                        continue
                        
                    # 1. DAS MODULO-210 PHYSIK-SIEB
                    if (quadrance % self.primorial_base) > self.invariant_limit:
                        continue
                        
                    # Algebraische Achsen-Rotation ohne ungenaue Trigonometrie
                    # Fixiert über die skalarischt isolierten Achsen-Komponenten
                    rx = dx + (ax_x * dual_polarity) // 12
                    ry = dy + (ax_y * dual_polarity) // 12
                    rz = dz + z_offset + (ax_z * dual_polarity) // 12
                    
                    # Perspektivischer Teiler im reinen Ganzzahlraum
                    denom = ((rz * self.SCALE) // 1414) + self.invariant_limit
                    if denom <= 0:
                        continue
                        
                    out_x = (((int(rx) * 45 * self.SCALE) // denom) + cx) % self.width
                    out_y = (((int(ry) * 45 * self.SCALE) // denom) + cy) % self.height
                    
                    # Farb-Klassifizierung basierend auf der Modulo-24 Resonanz
                    takt_check = (dx * dy + frame_idx) % self.control_base
                    
                    if takt_check == 12:
                        r_c, g_c, b_c = 255, 210, 24  # Invarianter Massen-Knoten (Gold)
                        voxel_size = 4
                    elif takt_check in {1, 5, 7, 11, 13, 17, 19, 23}:
                        r_c, g_c, b_c = 0, 255, 210  # Aktiver Resonanz-Knoten (Cyan)
                        voxel_size = 3
                    else:
                        # Hintergrund-Vakuumgitter mit Tiefenglühen
                        glow = max(30, 180 - ((rz * 100) // 128))
                        r_c, g_c, b_c = 0, int(glow) // 2, int(glow)
                        voxel_size = 2
                        
                    # Sicheres Einzeichnen ins Pixel-Array
                    y1, y2 = max(0, out_y - voxel_size // 2), min(self.height - 1, out_y + voxel_size // 2)
                    x1, x2 = max(0, out_x - voxel_size // 2), min(self.width - 1, out_x + voxel_size // 2)
                    frame_buffer[y1:y2+1, x1:x2+1] = [r_c, g_c, b_c]
                    
        # Binärer P6-PPM-Export zur absoluten Vermeidung von Kompressions-Rauschen
        filename = os.path.join(output_dir, f"stabilized_frame_{frame_idx:04d}.ppm")
        header = f"P6\n{self.width} {self.height}\n255\n".encode('ascii')
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(frame_buffer.tobytes())

def resolve_progressive_video_path(target_dir):
    """ Ermittelt einen fortlaufenden, nummerierten Dateinamen. """
    version = 1
    while True:
        filename = f"ptrc_interference_v{version:03d}.mp4"
        full_path = os.path.join(target_dir, filename)
        if not os.path.exists(full_path):
            return full_path
        version += 1

if __name__ == "__main__":
    print("[pTRC-ROTATOR] Initialisiere unbestechliche 3D-Rotations-Inferenz...")
    
    # Basispfäde deklarieren
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_dir, "Stabilized_Cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Zielverzeichnis für Videos ermitteln (Nutzt Standard-Download-Pfad für Termux)
    android_download_dir = "/storage/emulated/0/Download"
    if os.path.exists(android_download_dir):
        video_output_dir = android_download_dir
    else:
        video_output_dir = base_dir
        
    os.makedirs(video_output_dir, exist_ok=True)
    
    # 144 Frames decken das volle Spektrum deines Raumkristall-Uhrsystems ab
    total_frames = 144
    rotator = PTRCStabilizedRotator()
    
    # 1. SCHRITT: BERECHNUNG DER DETEKTIONS-MATRIZEN
    print(f" -> Starte dichte FullHD-Volumensynthese ({total_frames} Frames)...")
    for frame in range(total_frames):
        rotator.project_stabilized_frame(frame, cache_dir)
        if frame % 24 == 0 or frame == total_frames - 1:
            print(f"    + Invarianter Takt-Frame {frame:03d}/{total_frames} im Cache verankert.")
            
    # 2. SCHRITT: DETERMINISTISCHE FFMPEG-KOMPRESSION
    input_pattern = os.path.join(cache_dir, "stabilized_frame_%04d.ppm")
    video_target_path = resolve_progressive_video_path(video_output_dir)
    
    print("\n -> Starte unbeschädigte MP4-Videokompilierung via FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
        "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", video_target_path
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        print(f"\n[ SYSTEM CHECK OK ] Kristall-Video erfolgreich generiert und gesichert!")
        print(f" -> Ausgabedatei: {video_target_path}")
        
        # 3. SCHRITT: STRIKTE REGISTERBEREINIGUNG (Löschen der PPM-Massen)
        print("\n -> Starte atomare Bereinigung des lokalen Festplatten-Caches...")
        for frame in range(total_frames):
            ppm_file = os.path.join(cache_dir, f"stabilized_frame_{frame:04d}.ppm")
            if os.path.exists(ppm_file):
                os.remove(ppm_file)
        os.rmdir(cache_dir)
        print("    + Cache-Ordner rückstandslos entfernt. Speicherplatz freigegeben.")
        print("=" * 90)
        print(" -> STATUS: Zero-Float Pipeline-Lauf erfolgreich abgeschlossen. Synchronisation sauber.")
        print("=" * 90)
        sys.exit(0)
        
    except Exception as e:
        print(f"\n[ ACHTUNG ] FFmpeg-Kompression fehlgeschlagen: {e}")
        print(f" -> Die PPM-Bilder verbleiben im Sicherheits-Puffer: {cache_dir}")
        sys.exit(1)
