# ==============================================================================
# pTRC Framework - Pure Integer Biometric Retinal Stereo Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
#
# DUAL-LICENSING NOTICE:
# Non-commercial, academic, and open-source usage is strictly governed by 
# the GNU Affero General Public License version 3 (AGPLv3). Any commercial deployment,
# integration into proprietary, closed-source codebases, or corporate utilization
# explicitly requires a separate, individually negotiated commercial license.
# ==============================================================================
# -*- coding: utf-8 -*-

class PTRC3DStereoEngine:
    def __init__(self):
        # Die 8 erlaubten Hauptstrahlen der abelschen Symmetriegruppe
        self.allowed_24_rays = {1, 5, 7, 11, 13, 17, 19, 23}
        self.PRIMORIAL_RING = 210  
        self.INVARIANT_LIMIT = 156  # Dein unbestechlicher Grenzknoten
        self.SCALE = 1000

    def compute_retinal_state(self, vx, vy, cz, takt_level, eye_offset):
        """Berechnet das Feld ueber die perfekte duale Plus/Minus-Spiegelung"""
        t = int(takt_level)
        
        # DAS PRINZIP DER DUALITÄT (Plus/Minus Zeit-Oszillation)
        # Die Matrix schaltet im Takt zwischen komplementaeren Raeumen um
        dual_polarity = 1 if (t % 2 == 0) else -1
        
        # Biometrische Netzhautkrümmung (Der Augen-Sensor)
        retinal_depth_sq = (vx * vx + vy * vy) // 144
        
        # Rechtwinkliger Stereo-Versatz gekoppelt an die Polarität
        x_eye = (vx + eye_offset) * dual_polarity
        y_eye = vy * dual_polarity
        z_eye = (cz - retinal_depth_sq)
        
        # Der 1414-Overhead auf den diagonalen Pfaden
        dx_diag = (x_eye * 1414) // self.SCALE
        dy_diag = (y_eye * 1414) // self.SCALE
        
        # RECHTWINKLIGE SPIEGELSYMMETRIE (90-Grad-Kreuzintercept)
        # Hier verschmelzen Plus und Minus im unendlichen Raum jenseits von -1
        if (t % 2) == 1:
            mx, my, mz = -dx_diag, -dy_diag, -z_eye
        else:
            mx, my, mz = dx_diag, dy_diag, z_eye
            
        dx = mx + mz + t
        dy = my - mz
        quadrance = dx*dx + dy*dy + mz*mz
        
        # 1. DAS PLANETARE MODULO-UHRSIEB
        residuum_primorial = quadrance % self.PRIMORIAL_RING
        
        if residuum_primorial <= self.INVARIANT_LIMIT:
            
            # 2. DER Z/24Z KONTROLLTAKT (144-seitige Feldkoordination)
            takt_check = (dx * dy + t) % 24
            
            if takt_check in self.allowed_24_rays:
                return 2  # Aktiver Resonanz-Knoten (Spektral-Blau)
            elif takt_check == 12:
                return 1  # Invarianter Massen-Knoten (Spektral-Gold)
                
        return 0  # Quanten-Vakuum
