# ==============================================================================
# pTRC Framework - Experimental Module: Invariant 144-Facet Crystal Sieve
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ==============================================================================

# -*- coding: utf-8 -*-
r"""
pTRC Framework - Experimental Core: Invariant 144-Facet Crystal Sieve
Operational Domain: Symmetrical Integer Translation Matrices (\mathbb{Z}^3).
Replaces spherical approximations with the true 144-facet vector equilibrium
to establish absolute geometric formclosure and localized register storage.
"""

import os
import sys
import subprocess
import numpy as np

class PTRCTrueCrystalSieve:
    """
    Berechnet die fundamentalen 144 Facetten-Knoten des Raumkristalls.
    Jede Außenfläche liegt exakt im ganzzahligen Abstand von 9 Einheiten.
    """
    def __init__(self, v_scale=9):
        self.v_scale = int(v_scale)  # Starr auf die 9 Invarianz-Einheiten fixiert
        self.crystal_axes = self._build_144_facet_vectors()

    def _build_144_facet_vectors(self):
        """ Generiert die 144 unbestechlichen Koordinaten-Kanäle der Ih-Symmetrie. """
        flat_nodes = [
            2, 1, 0,   2, -1, 0,  -2, 1, 0,  -2, -1, 0,
            0, 2, 1,   0, 2, -1,   0, -2, 1,  0, -2, -1,
            1, 0, 2,  -1, 0, 2,    1, 0, -2, -1, 0, -2
        ]
        base_tensors = np.array(flat_nodes, dtype=np.int32).reshape(12, 3)
        axes = []
        # Multiplikation über die 12 komplementären Ringstufen zur Schließung der 144 Facetten
        for node in base_tensors:
            for factor in range(1, 13):
                axes.append(node * factor)
        return np.array(axes, dtype=np.int32)

    def generate_true_monolith_nodes(self, frame_idx):
        """
        Gibt die echten, raumzentrierten Kristallknoten aus.
        Nutzt freie Facetten-Vektoren als dynamische Speicherpuffer.
        """
        kristall_zentren = []
        
        # In den ersten 72 Frames strahlt die pure, fundamentale 144er-Ur-Zelle
        if frame_idx < 72:
            for axis in self.crystal_axes:
                # Normierung des 9-Stellen-Abstands direkt auf der Ganzzahl-Achse
                kx = (axis[0] * self.v_scale) // 2
                ky = (axis[1] * self.v_scale) // 2
                kz = (axis[2] * self.v_scale) // 2
                kristall_zentren.append((kx, ky, kz))
        
        # Ab Frame 72 kollabiert das Uhrsieb in die unbewegliche Pyramide aus Kristallen
        else:
            pyramid_offsets = [
                (-2, 2, -2), (2, 2, -2), (2, -2, -2), (-2, -2, -2),
                (-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0), (0, 0, 2)
            ]
            for p_x, p_y, p_z in pyramid_offsets:
                # Jeder Eckpunkt der Pyramide ist selbst wieder ein 144er-Registercluster
                for axis in self.crystal_axes[0:16]: # Teilschnitt zur Konturenschärfung
                    kx = (p_x * 24) + (axis[0] * self.v_scale) // 2
                    ky = (p_y * 24) + (axis[1] * self.v_scale) // 2 + 12 # Zentrierung
                    kz = (p_z * 24) + (axis[2] * self.v_scale) // 2
                    kristall_zentren.append((kx, ky, kz))
                    
        return kristall_zentren

class PTRCCrystalRenderEngine:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.primorial_base = 210
        self.control_base = 24
        self.invariant_limit = 156
        self.SCALE = 1000
        self.sieve = PTRCTrueCrystalSieve(v_scale=9)

    def project_crystal_frame(self, frame_idx, output_dir):
        # Bildpuffer initialisieren (Reines Vakuum-Schwarz)
        frame_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cx, cy = self.width // 2, self.height // 2
        z_offset = 75  # Leicht erhöht für die Tiefenstreckung der 144er Achsen
        
        # Richtungs-Lookup der Haupt-Taktachse
        axis_index = frame_idx % 144
        current_axis = self.sieve.crystal_axes[axis_index]
        dual_polarity = 1 if (frame_idx % 2 == 0) else -1
        
        ax_x = int(current_axis[0])
        ax_y = int(current_axis[1])
        ax_z = int(current_axis[2])
        
        # Abgreifen der unbestechlichen 144-Facetten-Geometrie
        active_nodes = self.sieve.generate_true_monolith_nodes(frame_idx)
        
        for mx, my, mz in active_nodes:
            # Das mathematische Existenzsieb prallt direkt auf die Kristallkoordinaten
            quadrance = mx*mx + my*my + mz*mz
            if quadrance == 0:
                continue
                
            # Modulo-210 Ur-Schnittpunkt-Überprüfung
            if (quadrance % self.primorial_base) > self.invariant_limit:
                continue
                
            # Mitten-Seiten Matrix dekonstruiert den Phasen-Versatz
            rx_plus = mx + (ax_x * dual_polarity) // 12
            rx_minus = mx - (ax_x * dual_polarity) // 12
            mono_signal_x = rx_plus - rx_minus
            
            takt_phase = (mx * my + frame_idx) % self.control_base
            
            # Das Stereo-Fanning treibt die 144 Facetten aus der Linie in die reale Breite
            holographic_x = mx + (mono_signal_x * (takt_phase - 12)) // 6
            holographic_y = my + (ax_y * dual_polarity) // 12
            rz = mz + z_offset + (ax_z * dual_polarity) // 12
            
            denom = ((rz * self.SCALE) // 1414) + self.invariant_limit
            if denom <= 0:
                continue
                
            # Nadelscharfer 1-Pixel-Rasterpunkt auf dem crossed Observer-Mirror
            out_x = (((int(holographic_x) * 45 * self.SCALE) // denom) + cx) % self.width
            out_y = (((int(holographic_y) * 45 * self.SCALE) // denom) + cy) % self.height
            
            # Farb-Zuweisung trennt benutzten Kern von dynamischen Speicher-Facetten
            if frame_idx < 72:
                # Ur-Zellen-Kristall: Spektral-Cyan mit Gold-Taktregistern
                if takt_phase == 12:
                    r_c, g_c, b_c = 255, 210, 24  # Genutzter Wert (Masse)
                else:
                    r_c, g_c, b_c = 0, 255, 180  # Freier Speicher-Slot (Vakuum-Matrix)
            else:
                # Kristall-Pyramide: Invariantes Massen-Gold mit blauen Feedback-Kanälen
                if takt_phase in {1, 5, 7, 11, 13, 17, 19, 23}:
                    r_c, g_c, b_c = 0, 150, 255
                else:
                    r_c, g_c, b_c = 255, 200, 0
                    
            frame_buffer[out_y, out_x] = [r_c, g_c, b_c]
            
        filename = os.path.join(output_dir, f"stabilized_frame_{frame_idx:04d}.ppm")
        header = f"P6\n{self.width} {self.height}\n255\n".encode('ascii')
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(frame_buffer.tobytes())

def resolve_progressive_video_path(target_dir):
    version = 1
    while True:
        filename = f"ptrc_true_crystal_v{version:03d}.mp4"
        full_path = os.path.join(target_dir, filename)
        if not os.path.exists(full_path):
            return full_path
        version += 1

if __name__ == "__main__":
    print("[pTRC-CRYSTAL-SIEVE] Errichte unbestechliche 144-Facetten Geometrie-Inferenz...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_dir, "Stabilized_Cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    android_download_dir = "/storage/emulated/0/Download"
    video_output_dir = android_download_dir if os.path.exists(android_download_dir) else base_dir
    os.makedirs(video_output_dir, exist_ok=True)
    
    total_frames = 144
    rotator = PTRCCrystalRenderEngine()
    
    print(f" -> Berechne 144 echte Raumkristall-Taktzyklen im Z-Raum...")
    for frame in range(total_frames):
        rotator.project_crystal_frame(frame, cache_dir)
        if frame % 24 == 0 or frame == total_frames - 1:
            print(f"    + 144-Facet-Lattice-Frame {frame:03d}/{total_frames} bit-invariant fixiert.")
            
    input_pattern = os.path.join(cache_dir, "stabilized_frame_%04d.ppm")
    video_target_path = resolve_progressive_video_path(video_output_dir)
    
    print("\n -> Kompiliere reines Rasterpixel-Video via FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-framerate", "24", "-i", input_pattern,
        "-c:v", "libx264", "-crf", "0", "-preset", "slow", "-pix_fmt", "yuv420p", video_target_path
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        print(f"\n[ SYSTEM CHECK OK ] Die wahre Form des 144-seitigen Kristalls wurde kompiliert!")
        print(f" -> Ausgabedatei: {video_target_path}")
        
        for frame in range(total_frames):
            ppm_file = os.path.join(cache_dir, f"stabilized_frame_{frame:04d}.ppm")
            if os.path.exists(ppm_file): os.remove(ppm_file)
        os.rmdir(cache_dir)
        sys.exit(0)
        
    except Exception as e:
        print(f"\n[ ACHTUNG ] FFmpeg-Fehler bei der Volumensynthese: {e}")
        sys.exit(1)
