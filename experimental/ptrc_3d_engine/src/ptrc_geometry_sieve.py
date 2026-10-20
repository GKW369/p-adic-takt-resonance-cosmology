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
"""
pTRC Framework - Static Crystal Geometry Sieve
Operational Domain: Pure Discrete Memory Chains (\mathbb{Z}^3) for zero-space formclosure.
"""

class PTRCGeometrySieve:
    """
    Berechnet die statischen Raumpixel-Zentren für das 13-Sphären-Gitter
    und die raumzentrierte Pyramide im unmanifestierten Ganzzahlfeld.
    """
    def __init__(self, cx, cy, cz, v_scale=14):
        self.cx = int(cx)
        self.cy = int(cy)
        self.cz = int(cz)
        self.v_scale = int(v_scale)

    def generate_monolith_nodes(self, frame_idx):
        """Gibt ortsfeste, ruhig im Raum stehende Kristallstrukturen zurück."""
        kristall_zentren = []
        
        # Frames 0 bis 71: Die vollkommen ruhige Wirminghaus-Kugel-Ur-Zelle
        if frame_idx < 72:
            fcc_sphere = [
                (0, 0, 0),
                (2, 2, 0), (-2, 2, 0), (2, -2, 0), (-2, -2, 0),
                (2, 0, 2), (2, 0, -2), (-2, 0, 2), (-2, 0, -2),
                (0, 2, 2), (0, 2, -2), (0, -2, 2), (0, -2, -2)
            ]
            for k_x, k_y, k_z in fcc_sphere:
                kx = self.cx + (k_x * self.v_scale)
                ky = self.cy + (k_y * self.v_scale)
                kz = self.cz + (k_z * self.v_scale)
                kristall_zentren.append((kx, ky, kz))
                
        # Frames 72 bis 143: Die unbewegliche, massive Pyramide aus Raumkristallen
        else:
            pyramid_nodes = [
                (-2, 2, -2), (2, 2, -2), (2, -2, -2), (-2, -2, -2), # Fundament
                (-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0),     # Mittelstufe
                (0, 0, 2)                                           # Kristallspitze
            ]
            for k_x, k_y, k_z in pyramid_nodes:
                kx = self.cx + (k_x * self.v_scale)
                ky = self.cy + (k_y * self.v_scale) + 12            # Zentrierungskompensation
                kz = self.cz + (k_z * self.v_scale)
                kristall_zentren.append((kx, ky, kz))
                
        return kristall_zentren
