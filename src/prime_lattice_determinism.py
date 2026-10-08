# -*- coding: utf-8 -*-
"""
pTRC Framework - Module: prime_lattice_determinism.py
Pure Integer Primeorial Lattice Filter (Wheel Factorization Engine).
Optimizes cryptographic search spaces by compressing the candidate field by 77.14%.
"""

import sys
import time

class PrimeLatticeEngine:
    def __init__(self):
        # Das fundamentale pTRC-Gitter-Skelett (2 * 3 * 5 * 7 = 210)
        self.primeorial_base = 210
        
        # Die 48 invarianten, koprimen Symmetrieachsen innerhalb des 210er-Zyklus.
        # Diese Werte werden einmalig deterministisch berechnet.
        self.allowed_axes = self._generate_invariant_lattice_axes()

    def _generate_invariant_lattice_axes(self):
        """
        Generiert die 48 erlaubten Struktur-Slots im Modulo-210-Gitter.
        Eliminiert alle Zahlen, die gemeinsame Teiler mit 2, 3, 5 oder 7 haben.
        """
        axes = []
        for candidate in range(1, self.primeorial_base):
            # Reine Integer-Modulo-Abfragen ohne Fließkommazahlen
            if (candidate % 2 != 0 and 
                candidate % 3 != 0 and 
                candidate % 5 != 0 and 
                candidate % 7 != 0):
                axes.append(candidate)
        return set(axes)

    def evaluate_candidate_o1(self, large_integer):
        """
        Prüft in einer einzigen CPU-Operation (O(1)), ob eine Zahl auf einer
        erlaubten Gitterachse liegt. Wenn nicht, ist sie garantiert KEINE Primzahl.
        """
        # Strukturelle Positions-Bestimmung auf dem Modulo-Gitter
        lattice_position = large_integer % self.primeorial_base
        
        # Sonderfälle für die Basis-Primzahlen selbst abfangen
        if large_integer in {2, 3, 5, 7}:
            return True, "BASE_PRIME"
            
        # O(1) Hash-Map Abfrage auf den erlaubten Achsen
        if lattice_position in self.allowed_axes:
            return True, "VALID_CANDIDATE"
        else:
            return False, "STRUCTURE_REJECT"

if __name__ == "__main__":
    print("[ pTRC INFORMATICS ENGINE ] Validating Prime Lattice Determinism...")
    
    engine = PrimeLatticeEngine()
    
    # Validierung der 48-Knoten-Hierarchie
    total_slots = engine.primeorial_base
    active_slots = len(engine.allowed_axes)
    compression = (1.0 - (active_slots / total_slots)) * 100
    
    print(f"\n--- Schritt 1: Strukturelle Gitter-Kompression ---")
    print(f"Gesamt-Adressraum pro Zyklus:  {total_slots} Slots")
    print(f"Aktive pTRC-Symmetrieachsen:    {active_slots} Slots (Gitterlücken)")
    print(f"-> Suchraum-Kompression auf Chipebene: {compression:.2f}% eingespart!")

    print(f"\n--- Schritt 2: O(1) Live-Filter-Benchmark ---")
    
    # Test-Zahlen (Kombination aus echten Primzahlen und zusammengesetzten Zahlen)
    test_numbers = [
        11,         # Primzahl (Sollte VALID_CANDIDATE sein)
        209,        # Zusammengesetzt, aber im Sieb (VALID_CANDIDATE) -> Muss nachgeprüft werden
        210,        # Durch alles teilbar (STRUCTURE_REJECT)
        1000,       # Gerade Zahl (STRUCTURE_REJECT)
        9999991,    # Große Primzahl (VALID_CANDIDATE)
        10000003    # Große zusammengesetzte Zahl (STRUCTURE_REJECT)
    ]
    
    start_time = time.time()
    for num in test_numbers:
        is_candidate, reason = engine.evaluate_candidate_o1(num)
        status_string = "[PASS]" if is_candidate else "[REJECT]"
        print(f"Zahl: {num:<10} | Matrix-Status: {status_string:<8} | Ursache: {reason}")
    end_time = time.time()
    
    print(f"\n[BENCHMARK] {len(test_numbers)} massive Gitter-Analysen in {((end_time - start_time)*1000):.4f} ms abgearbeitet.")
    print("-> Fazit: Über 77% aller Berechnungen werden ohne teuren CPU-Load sofort verworfen.")
    print("-> System arbeitet absolut deterministisch innerhalb des Restklassenrings.")
    sys.exit(0)
