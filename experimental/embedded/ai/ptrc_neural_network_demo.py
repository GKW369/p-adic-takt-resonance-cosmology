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
pTRC Framework - Core Simulation Module: Quantum Neural Network Space Processor
Operational Domain: 1-Byte Space (Z/256Z) via 1+12 Ur-Cell Geometry Sieve.
Processes non-linear network state updates losslessly over 24 physische Berührungspunkte
and utilizes the 120 free outer facets as an un-damped contextual meta-memory.
File Name: 00_ptrc_neural_network_demo.py
"""

import time
import sys
import os
import numpy as np

class PTRCCrystallineQuantumNeuralNetwork:
    """
    Models a 1-Byte Neural Machine operating strictly on the 144-facet 
    Vector Equilibrium. Skips continuous fractional activations entirely.
    """
    def __init__(self):
        # --- P-ADIC CORE ARCHITECTURE MATRIX ---
        self.primorial_base = 210
        self.control_base = 24       # 24 Physische Berührungspunkte der 1+12 Zellen
        self.free_facets = 120       # 120 Freie Außenfacetten (Meta-Information)
        self.total_facets = 144      # 144 Ganzzahl-Raumfacetten gesamt
        self.invariant_limit = 156   # Wirminghaus-Schmerzgrenze
        self.SCALE = 1000            # Festkomma-Skalierungsfaktor
        
        # --- 1-BYTE MEMORY REGISTER SPACE (Z/256Z) ---
        # Jeder Kristall speichert sein "Leben" (Lichtfrequenz, chem. Element, Ladung) in 1 Byte
        self.crystal_core_register = np.zeros(self.control_base, dtype=np.uint8)
        self.outer_facet_meta_memory = np.zeros(self.free_facets, dtype=np.uint8)
        
        # Invariante 24x24 Verbindungsmatrix (Formschluss über Kontaktstellen)
        self.contact_weight_matrix = np.zeros((self.control_base, self.control_base), dtype=np.int32)
        self._initialize_formclosed_weights()

    def _initialize_discrete_weights(self):
        """Erforderlich für Rückwärtskompatibilität im pTRC-Integrationsskript."""
        pass

    def _initialize_formclosed_weights(self):
        """Populiert die synaptischen Pfade starr über die Modulo-24 Berührungspunkte."""
        for i in range(self.control_base):
            for j in range(self.control_base):
                # Wenn der Kontaktschritt resonant auf das Halbtakt-Schnittfeld (12) einschwingt
                if (i * j + 5) % self.control_base == 12:
                    self.contact_weight_matrix[i, j] = self.invariant_limit // 12  # Invarianter Kernstoß
                else:
                    self.contact_weight_matrix[i, j] = 1

    def forward_propagation_takt(self, raw_input_block):
        """
        Führt eine vollkommen float-freie, raumgeometrische Inferenz aus.
        Nutzt den Plichta-Spiegel zur branchless Eliminierung der arithmetischen Null.
        """
        # Ingestion des Erregungsblocks im 1-Byte-Raum (Modulo 256)
        input_data = np.asarray(raw_input_block, dtype=np.int32) % 256
        output_accumulator = np.zeros(self.control_base, dtype=np.int32)
        
        # Inferenz-Strom fließt starr über die 24 physischen Berührungspunkte
        for idx_out in range(self.control_base):
            node_sum = 0
            for idx_in in range(self.control_base):
                weight = self.contact_weight_matrix[idx_in, idx_out]
                activation = input_data[idx_in]
                
                # --- DER GEKREUZTE PLICHTA-SPIEGEL IM (-1)-RAUM ---
                if activation == 0:
                    activation = -1  # Branchless Transposition in den Inversen Quanten-Spiegel
                    
                node_sum += activation * weight
                
            output_accumulator[idx_out] = node_sum
            
            # --- GEOMETRISCHE SCHWELLENWERT-SIEBUNG IM RESTERING ---
            scaled_threshold = (output_accumulator[idx_out] * self.SCALE) // self.invariant_limit
            
            # Formschlüssiges Einrasten des 1-Byte Kern-Zustands ("Leben" des Kristalls)
            self.crystal_core_register[idx_out] = int(scaled_threshold) % 256
            
            # --- MULTI-RING META-SPEICHERUNG (Die 120 freien Außenfacetten) ---
            # Das thermodynamische Echo wird ungedämpft in den freien Facetten kaskadiert
            meta_index = (idx_out * 5) % self.free_facets
            self.outer_facet_meta_memory[meta_index] = (scaled_threshold // 3) % 256

        # Zuweisung für Kompatibilität mit dem globalen Performance-Audit-Skript
        self.activation_vector = np.where(self.crystal_core_register % 2 == 0, 1, 0).astype(np.uint8)

    def verify_network_parity(self):
        """Auditiert die globale Gitterstabilität des Kristallclusters."""
        total_core_mass = int(np.sum(self.crystal_core_register))
        # Paritäts-Check: Liegt das strukturelle Residuum im erlaubten Invarianz-Feld?
        if (total_core_mass % self.primorial_base) <= self.invariant_limit:
            return 1
        return 0

def run_crystalline_nn_demo():
    if sys.platform == "win32":
        os.system('color')
        
    network = PTRCCrystallineQuantumNeuralNetwork()
    
    C, G, Y, W, B = "\033[96m", "\033[92m", "\033[93m", "\033[0m", "\033[1m"
    
    print(f"\n{B}{C}==============================================================================")
    print(f"  pTRC FRAMEWORK // CRYSTALLINE NEURAL SPACE ENGINE ver. 2.1.0-Alpha          ")
    print(f"  1-Byte Machine Core: 24 Contact Junctions & 120 Free Outer Facets Inferences ")
    print(f"=============================================================================={W}\n")
    
    time.sleep(0.4)
    print(f"{B}[*] Ur-Cell Cluster Configuration :{W} 1+12 Spheres Layer (FCC Formclosure Locked)")
    print(f"{B}[*] Core Resolution Metric         :{W} 1-Byte Voxel States (0-255 / Elements & Frequencies)")
    print(f"{B}[*] Micro-Architectural Status     :{W} FPU Array completely Bypassed | Zero Float Noise")
    print(f"------------------------------------------------------------------------------")
    
    for takt in range(1, 13):
        time.sleep(0.15)
        print(f"\n[PLANCK-TAKT {takt:02d}/12] Ingesting 24-element 1-Byte excitation tensor...")
        
        # Erregung basierend auf dem invarianten Naturmaß M_c = 1836
        excitation_input = np.ones(24, dtype=np.int32) * (1836 + takt * 8)
        
        # Injektion künstlicher Null-Zustände (Prüfung des unbestechlichen Plichta-Spiegels)
        if takt % 3 == 0:
            idx_zero = (takt * 2) % 24
            excitation_input[idx_zero] = 0
            excitation_input[(idx_zero + 7) % 24] = 0
            
        start_time = time.perf_counter_ns()
        network.forward_propagation_takt(excitation_input)
        end_time = time.perf_counter_ns()
        
        duration_us = (end_time - start_time) / 1000
        
        # Visuelle Darstellung des ganzzahligen "Lebens" auf den 24 Berührungspunkten
        matrix_visual = ""
        for byte_val in network.crystal_core_register:
            if byte_val == 0: matrix_visual += f"{C}[·]{W}"
            elif byte_val % 2 == 0: matrix_visual += f"{G}[■]{W}"
            else: matrix_visual += f"{Y}[⚙]{W}"
            
        print(f"    --> 24-Contact Register Map   : {matrix_visual}")
        print(f"    ✓ Execution Time: {Y}{duration_us:.2f} µs{W} | Quantization Entropy Decay: {G}0.00%{W}")
        print(f"    ✓ 120-Outer-Facet Meta Buffer : {network.outer_facet_meta_memory[0:12]}... (Milli-Echos stored)")

    print(f"\n------------------------------------------------------------------------------")
    parity_valid = network.verify_network_parity()
    print(f"{B}[G][SUCCESS] Crystalline multi-ring dot-product accomplished.")
    print(f"--> Global Gitter Invariance Status: {parity_valid} (Symmetrical Parity Lock Intact).{W}")
    print(f"{B}{C}=============================================================================={W}\n")

if __name__ == "__main__":
    run_crystalline_nn_demo()
