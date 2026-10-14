# ==============================================================================
# pTRC Framework - Pure Integer Biometric Retinal Stereo Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
#
# DUAL-LICENSING NOTICE:
# Non-commercial, academic, and open-source usage is strictly governed by 
# the GNU General Public License version 3 (GPLv3). Any commercial deployment,
# integration into proprietary, closed-source codebases, or corporate utilization
# explicitly requires a separate, individually negotiated commercial license.
# ==============================================================================
# -*- coding: utf-8 -*-

class PTRC3DStereoEngine:
    def __init__(self):
        # Das originale, unbestechliche Modulo-24 Uhrwerk (8 Primstrahlen nach Plichta)
        self.prime_rays_24 = (1, 5, 7, 11, 13, 17, 19, 23)
        
        # Das hochauflösende 48-Strang Raumsieb modulo 210 (Euler-Phi φ(210) = 48)
        self.prime_strands_210 = (
            1, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 
            71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 121, 127, 131, 137, 139, 
            143, 149, 151, 157, 163, 167, 169, 173, 179, 181, 187, 191, 193, 197, 199, 209
        )
        self.fine_structure_inverse = 137
        self.SCALE = 1000

    def compute_retinal_state(self, vx, vy, cz, takt_level, eye_offset):
        """
        Berechnet den Zustand eines Punktes auf der gekrümmten Netzhaut.
        'eye_offset' simuliert den horizontalen Pupillenabstand (IPD).
        """
        t = int(takt_level)
        
        # BIOMETRISCHE NETZHAUT-KRÜMMUNG (Retinal Curvature Check)
        # Die Netzhaut ist eine sphärische Schale. Wir berechnen den invarianten 
        # Krümmungsradius (Augen-Ablesesensor) rein ganzzahlig über Quadrance-Faltung.
        retinal_depth_sq = (vx * vx + vy * vy) // 144
        
        # Verschiebung des Strahls durch die Linse unter Berücksichtigung des Auges (Parallaxe)
        x_eye = vx + eye_offset
        y_eye = vy
        z_eye = cz - retinal_depth_sq  # Die Krümmung biegt die Z-Ebene nach hinten durch!
        
        # DIAGONALER CMB-PATH OVERHEAD (1414-Pfad-Faktor)
        dx_diag = (x_eye * 1414) // self.SCALE
        dy_diag = (y_eye * 1414) // self.SCALE
        
        # 90-GRAD-KREUZSPIEGELUNG (Achsen-Inversion beidseitig in Z)
        if (t % 2) == 1:
            mx = -dx_diag; my = -dy_diag; mz = -z_eye
        else:
            mx = dx_diag; my = dy_diag; mz = z_eye
            
        dx = mx + mz + t
        dy = my - mz
        quadrance = dx*dx + dy*dy + mz*mz
        
        # MATRIX FILTRATION
        if (quadrance % 210) in self.prime_strands_210:
            phase = (dx * dy * (mz if mz != 0 else 1) + self.fine_structure_inverse + t) % 24
            
            if phase == 12:
                return 1  # Invarianter Massenknoten (Amber-Gold)
            elif phase in self.prime_rays_24:
                return 2  # Leuchtender Energiestrang (Neon-Cyan)
                
        return 0  # Biologisches Ruhe-Vakuum
