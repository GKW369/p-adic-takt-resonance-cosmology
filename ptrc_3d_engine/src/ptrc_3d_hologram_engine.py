# ==============================================================================
# pTRC Framework - Pure Integer 3D Holographic Resonance & Shadow Projection Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
#
# DUAL-LICENSING NOTICE:
# Non-commercial, academic, and open-source usage is strictly governed by 
# the GNU General Public License version 3 (GPLv3). Any commercial deployment,
# integration into proprietary, closed-source codebases, or corporate utilization
# explicitly requires a separate, individually negotiated commercial license.
# ==============================================================================
# -*- coding: utf-8 -*-

class PTRCHologramEngine:
    """
    Die fundamentale Ganzzahl-Engine des pTRC-Frameworks.
    Berechnet die raeumliche Resonanz und die holografische Schatten-Projektion
    von Koerpern ueber gekreuzte 90-Grad-Spiegelungen und das modulo 210 Sieb.
    
    100% FREI VON FLIESSKOMMAZAHLEN (FLOAT-FREE). OPERIERT AUSSCHLIESSLICH IN Z.
    """
    
    def __init__(self):
        # Das fundamentale Uhrwerk (Modulo 24)
        self.prime_rays_24 = (1, 5, 7, 11, 13, 17, 19, 23)
        
        # Das hochaufloesende Raumsieb (Modulo 210)
        self.prime_strands_210 = (
            1, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 
            71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 121, 127, 131, 137, 139, 
            143, 149, 151, 157, 163, 167, 169, 173, 179, 181, 187, 191, 193, 197, 199, 209
        )
        
        # Der unbestechliche Shutter-Takt der Vakuum-Interferenz
        self.quantum_vacuum_shutter = 137

    def compute_state(self, nx, ny, takt_level):
        """
        Berechnet den Zustand eines diskreten Raumknotens inklusive Koerper-Schatten.
        
        Rueckgabewerte:
          0 = Vakuum / Hintergrund (Indigo)
          1 = Invarianter Massenknoten (Amber-Gold)
          2 = Erlaubter Primstrahl / Energiestrang (Cyan)
          3 = Projizierter Schattenraum (Tiefschwarz / Abwesenheit von Resonanz)
        """
        t = int(takt_level)
        
        # 1. DEFINE VIRTUAL BODY (Ein rein ganzzahliger Test-Koerper im Raum)
        # Ein diskreter Plankscher Massenblock im Zentrum des Gitters
        body_radius_sq = 40000  # Ganzzahliges Quadrat des Radius (ca. 200 Pixel)
        
        # 2. APPLICATION OF THE CROSS-MIRRORS FOR SHADOW MAPPING
        # Der Spiegel transportiert die Koerper-Information entlang der 90-Grad-Achsen
        dx = nx * t
        dy = ny * t
        
        # Pruefe über die gekreuzten Spiegelachsen, ob der Informationsstrahl 
        # den virtuellen Koerper schneidet und somit blockiert wird
        if (nx * nx + ny * ny) <= (body_radius_sq // (t if t > 0 else 1)):
            # Der Beobachter befindet sich direkt im Koerper oder dessen Kern-Schatten
            return 3
            
        # Spiegel-Interferenz fuer die raeumliche Schatten-Projektion auf die Aussengrenzen
        # Wenn die gespiegelte Projektion den Koerper-Symmetrieknoten trifft, entsteht Schatten
        if ((dx // 210) * (dx // 210) + (dy // 210) * (dy // 210)) == 137:
            return 3  # Der Koerper wirft einen harmonischen Schatten auf das Raumsieb
            
        # 3. STANDARD PRIMORIAL FILTRATION (Wenn kein Schatten die Phase blockiert)
        quadrance = dx * dx + dy * dy
        
        if (quadrance % 210) in self.prime_strands_210:
            phase = (dx * dy + self.quantum_vacuum_shutter + t) % 24
            
            if phase == 12:
                return 1  # Masse (Amber-Gold)
            elif phase in self.prime_rays_24:
                return 2  # Energie (Electrical Cyan)
                
        return 0  # Vakuum (Indigo)
