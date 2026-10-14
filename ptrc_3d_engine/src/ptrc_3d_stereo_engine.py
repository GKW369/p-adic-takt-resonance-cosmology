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
        # Die 8 erlaubten Hauptstrahlen der abelschen Symmetriegruppe aus deiner Urdatei
        self.allowed_24_rays = {1, 5, 7, 11, 13, 17, 19, 23}
        
        # SKALIERBARKEIT: Basis-Primorial 210 (Erweiterbar auf 2310 oder 30030)
        self.PRIMORIAL_RING = 210  
        
        # Dein unbestechlicher Grenzknoten aus der Urdatei
        self.INVARIANT_LIMIT = 156  
        
        self.fine_structure_inverse = 137
        self.SCALE = 1000

    def compute_retinal_state(self, vx, vy, cz, takt_level, eye_offset):
        """Berechnet den Netzhaut-Zustand exakt nach dem 156-Grenzknoten-Gesetz"""
        t = int(takt_level)
        
        # SYSTEM-TAKT-SPIEGELUNG (np.roll-Äquivalent im unendlichen Raum)
        # Berechnet die Verschiebung im positiven und negativen Bereich jenseits von -1
        current_hour = t % 24
        axis_to_roll = current_hour % 3
        shift_amount = (t // 24) if (current_hour < 12) else -(t // 24)
        
        # Biometrische Netzhautkrümmung
        retinal_depth_sq = (vx * vx + vy * vy) // 144
        
        # Einkoppeln des Stereo-Versatzes und der Takt-Verschiebung
        x_eye = vx + eye_offset + (shift_amount if axis_to_roll == 0 else 0)
        y_eye = vy + (shift_amount if axis_to_roll == 1 else 0)
        z_eye = cz - retinal_depth_sq + (shift_amount if axis_to_roll == 2 else 0)
        
        # Diogonaler CMB-Overhead
        dx_diag = (x_eye * 1414) // self.SCALE
        dy_diag = (y_eye * 1414) // self.SCALE
        
        # 90-Grad-Kreuzspiegelung für die Richtungsumkehr
        if (t % 2) == 1:
            mx, my, mz = -dx_diag, -dy_diag, -z_eye
        else:
            mx, my, mz = dx_diag, dy_diag, z_eye
            
        dx = mx + mz + t
        dy = my - mz
        quadrance = dx*dx + dy*dy + mz*mz
        
        # 1. DAS MODULO-UHRSIEB (Exakt das Gesetz aus deiner Urdatei!)
        residuum_primorial = quadrance % self.PRIMORIAL_RING
        
        if residuum_primorial <= self.INVARIANT_LIMIT:
            
            # 2. DER Z/24Z KONTROLLTAKT-CHECK
            takt_check = (dx * dy + self.fine_structure_inverse + t) % 24
            
            if takt_check in self.allowed_24_rays:
                return 2  # Aktiver Resonanz-Knoten (Lichtleitend / Blau)
            elif takt_check == 12:
                return 1  # Invarianter Massen-Knoten (Materie / Gold)
                
        return 0  # Biologisches Ruhe-Vakuum
