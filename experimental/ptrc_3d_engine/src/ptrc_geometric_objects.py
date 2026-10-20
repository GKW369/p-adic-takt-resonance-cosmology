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
pTRC Framework - Discrete Geometric Objects Storage
Operational Domain: Pure Discrete Matrix Nodes (\mathbb{Z}^3) for Kugel and Pyramide.
"""

class PTRCGeometricObjects:
    """
    Stellt die fixierten Ganzzahl-Zentren für die lückenlosen Raumobjekte bereit.
    """
    @staticmethod
    def get_wirminghaus_sphere_nodes():
        """Liefert die 13 Zentren des Vektor-Gleichgewichts (FCC-Ur-Zelle)."""
        return [
            (0, 0, 0),  (2, 2, 0),  (2, -2, 0),  (-2, 2, 0),  (-2, -2, 0),
            (2, 0, 2),  (2, 0, -2), (-2, 0, 2),  (-2, 0, -2),
            (0, 2, 2),  (0, 2, -2), (0, -2, 2),  (0, -2, -2)
        ]

    @staticmethod
    def get_massive_pyramid_nodes():
        """Stapelt die 144-seitigen Kristallbausteine etagenweise zu einer Pyramide."""
        nodes = []
        for level in range(3):
            z_layer = level * 2
            y_layer = -level * 4
            for row in range(3 - level):
                for col in range(3 - level):
                    x_offset = (col * 16) - ((3 - level) * 8) + 8
                    y_offset = (row * 16) - ((3 - level) * 8) + 8 + y_layer
                    nodes.append((x_offset, y_offset, z_layer))
        return nodes
