# ==============================================================================
# pTRC Framework - Pure Integer 3D Holographic Resonance Core Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
# GPLv3 Open Source / Commercial License Required
# ==============================================================================
# -*- coding: utf-8 -*-

class PTRC3DHologramEngine:
    def __init__(self):
        # Das fundamentale Modulo-24 Uhrwerk (8 Primstrahlen nach Plichta)
        self.prime_rays_24 = (1, 5, 7, 11, 13, 17, 19, 23)
        
        # Das 48-Strang Raumsieb modulo 210 (Skalierbare Primzahlenringerweiterung)
        self.prime_strands_210 = (
            1, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 
            71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 121, 127, 131, 137, 139, 
            143, 149, 151, 157, 163, 167, 169, 173, 179, 181, 187, 191, 193, 197, 199, 209
        )
        self.quantum_vacuum_shutter = 137

    def compute_state(self, x, y, z, takt_level):
        """
        Berechnet den Zustand eines Knotens. Operiert beidseitig im positiven und 
        negativen Ganzzahlbereich über die 90-Grad-Kreuzspiegelung.
        """
        t = int(takt_level)
        
        # DIE 90-GRAD-KREUZSPIEGELUNG FÜR DIE TIEFEN-INFORMATION (Z)
        # Spiegel 1: Inversion (1 ist -1 bei ungeradem Takt)
        if (t % 2) == 1:
            mx = -x
            my = -y
            mz = -z
        else:
            mx = x
            my = y
            mz = z
            
        # Spiegel 2: Orthogonale Achsen-Transposition mit integrierter Tiefe mz
        if ((t // 2) % 2) == 1:
            dx = my + mz + t
            dy = mx - mz
        else:
            dx = mx + mz + t
            dy = my - mz
            
        # Diskrete 3D-Quadranz (Interferenz mit den Außengrenzen des Gitters)
        quadrance = dx*dx + dy*dy + mz*mz
        
        # 1. FILTRATION: Modulo 210 Raumsieb (48 primoriale Stränge)
        if (quadrance % 210) in self.prime_strands_210:
            
            # 2. FILTRATION & REIN GANZZAHLIGE VERDICKUNG (Modulo 24 Phase)
            # Die Phase bestimmt die mathematische Resonanz-Ausdehnung
            phase = (dx * dy * (mz if mz != 0 else 1) + self.quantum_vacuum_shutter + t) % 24
            
            # Kern-Resonanz (Zentrum des Gitterstrangs)
            if phase == 12:
                return 1  # Invarianter Massenknoten (Amber-Gold)
                
            # Erweiterte Phasen-Nachbarschaft (Ganzzahlige Verdickung des Leuchtens)
            # Wenn die Phase nahe an den Primstrahlen liegt, leuchtet die Umgebung mit
            elif phase in self.prime_rays_24:
                return 2  # Leuchtender Energiestrang (Neon-Cyan)
                
        return 0  # Kosmisches Indigo-Vakuumsieb
