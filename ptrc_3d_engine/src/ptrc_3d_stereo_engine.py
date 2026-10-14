# ==============================================================================
# pTRC Framework - Pure Integer Biometric Retinal Stereo Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
# GPLv3 Open Source / Commercial License Required
# ==============================================================================
# -*- coding: utf-8 -*-

class PTRC3DStereoEngine:
    def __init__(self):
        # Das fundamentale Modulo-24 Uhrwerk und das 210er Raumsieb
        self.prime_rays_24 = (1, 5, 7, 11, 13, 17, 19, 23)
        self.prime_strands_210 = (
            1, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 
            71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 121, 127, 131, 137, 139, 
            143, 149, 151, 157, 163, 167, 169, 173, 179, 181, 187, 191, 193, 197, 199, 209
        )
        self.fine_structure_inverse = 137
        self.SCALE = 1000

    def compute_retinal_state(self, vx, vy, cz, takt_level, eye_offset):
        """
        Berechnet den Zustand eines Punktes auf der gekruemmten Netzhaut.
        'eye_offset' simuliert den horizontalen Pupillenabstand (IPD).
        """
        t = int(takt_level)
        
        # 1. BIOMETRISCHE NETZHAUT-KRÜMMUNG (Retinal Curvature Check)
        # Die Netzhaut ist eine sphaerische Schale. Wir berechnen den invarianten 
        # Krümmungsradius (Augen-Ablesesensor) rein ganzzahlig ueber Quadrance-Faltung.
        retinal_depth_sq = (vx * vx + vy * vy) // 144
        
        # Verschiebung des Strahls durch die Linse unter Berücksichtigung des Auges (Parallaxe)
        x_eye = vx + eye_offset
        y_eye = vy
        z_eye = cz - retinal_depth_sq  # Die Krümmung biegt die Z-Ebene nach hinten durch!
        
        # 2. DIAGONALER CMB-PATH OVERHEAD (1414-Pfad-Faktor)
        dx_diag = (x_eye * 1414) // self.SCALE
        dy_diag = (y_eye * 1414) // self.SCALE
        
        # 3. 90-GRAD-KREUZSPIEGELUNG (Achsen-Inversion beidseitig in Z)
        if (t % 2) == 1:
            mx = -dx_diag; my = -dy_diag; mz = -z_eye
        else:
            mx = dx_diag; my = dy_diag; mz = z_eye
            
        dx = mx + mz + t
        dy = my - mz
        quadrance = dx*dx + dy*dy + mz*mz
        
        # 4. MATRIX FILTRATION
        if (quadrance % 210) in self.prime_strands_210:
            phase = (dx * dy * (mz if mz != 0 else 1) + self.fine_structure_inverse + t) % 24
            
            if phase == 12:
                return 1  # Invarianter Massenknoten
            elif phase in self.prime_rays_24:
                return 2  # Leuchtender Energiestrang
                
        return 0  # Biologisches Ruhe-Vakuum
