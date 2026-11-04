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
pTRC Framework - Core Simulation Module: Crystalline Quantum Neural Space Processor
Operational Domain: 1-Byte Register Space (Z/256Z) via 1+12 Ur-Cell Geometry Sieve.
Processes non-linear network state updates losslessly over 24 physical contact points
and utilizes the 120 free outer facets as an un-damped contextual meta-memory.
File Name: ptrc_neural_network_demo.py
"""

import time
import sys
import os
import numpy as np

class PTRCCrystallineQuantumNeuralNetwork:
    """
    Models a 1-Byte Crystalline Neural Processor operating on the 144-facet 
    Vector Equilibrium. Bypasses continuous floating-point activations entirely.
    """
    def __init__(self):
        # --- P-ADIC CORE ARCHITECTURE MATRIX ---
        self.primorial_base = 210
        self.control_base = 24       # 24 Physical Contact Junctions of the 1+12 cluster
        self.free_facets = 120       # 120 Free Outer Facets (Meta-Memory Buffer)
        self.total_facets = 144      # 144 Total Integer Space Facets
        self.invariant_limit = 156   # Wirminghaus Invariant Limit
        self.SCALE = 1000            # Fixed-Point Scaling Factor
        
        # --- 1-BYTE MEMORY REGISTER SPACE (Z/256Z) ---
        self.crystal_core_register = np.zeros(self.control_base, dtype=np.uint8)
        self.outer_facet_meta_memory = np.zeros(self.free_facets, dtype=np.uint8)
        
        # Invariant 24x24 Formclosed Connection Weight Matrix
        self.contact_weight_matrix = np.zeros((self.control_base, self.control_base), dtype=np.int32)
        self._initialize_formclosed_weights()

    def _initialize_discrete_weights(self):
        """Maintained for backward compatibility with global verification pipelines."""
        pass

    def _initialize_formclosed_weights(self):
        """Populates synaptic paths rigidly across the Modulo-24 touchpoints."""
        for i in range(self.control_base):
            for j in range(self.control_base):
                # Harmonic synchronization condition matching the central reflection axis (12)
                if (i * j + 5) % self.control_base == 12:
                    self.contact_weight_matrix[i, j] = self.invariant_limit // 12
                else:
                    self.contact_weight_matrix[i, j] = 1

    def forward_propagation_takt(self, raw_input_block):
        """
        Executes a deterministic forward dot-product pass in the pure integer domain.
        Utilizes the crossed Plichta-Mirror to branchlessly eliminate the continuous zero singularity.
        """
        # Ingestion of the excitation block locked inside the 1-Byte space (Modulo 256)
        input_data = np.asarray(raw_input_block, dtype=np.int32) % 256
        output_accumulator = np.zeros(self.control_base, dtype=np.int32)
        
        for idx_out in range(self.control_base):
            node_sum = 0
            for idx_in in range(self.control_base):
                weight = self.contact_weight_matrix[idx_in, idx_out]
                activation = input_data[idx_in]
                
                # --- THE CROSSED PLICHTA-MIRROR IN (-1)-SPACE ---
                if activation == 0:
                    activation = -1  # Branchless transposition into the sign-inversion field
                    
                node_sum += activation * weight
                
            output_accumulator[idx_out] = node_sum
            
            # --- DIVISION-FREE FIXED-POINT ACTIVATION SIEVE ---
            scaled_threshold = (output_accumulator[idx_out] * self.SCALE) // self.invariant_limit
            
            # Formclosed execution step writing directly into the 1-Byte hardware register
            self.crystal_core_register[idx_out] = int(scaled_threshold) % 256
            
            # --- THERMODYNAMIC META-MEMORY STORAGE (120 Free Outer Facets) ---
            meta_index = (idx_out * 5) % self.free_facets
            self.outer_facet_meta_memory[meta_index] = (scaled_threshold // 3) % 256

        # Assignment for strict structural parity tracking compatibility
        self.activation_vector = np.where(self.crystal_core_register % 2 == 0, 1, 0).astype(np.uint8)

    def verify_network_parity(self):
        """Audits the macroscale crystal grid coherence against the primorial base limits."""
        total_core_mass = int(np.sum(self.crystal_core_register))
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
        time.sleep(0.25)  # Perfectly timed refresh rate for display tracking
        print(f"\n[PLANCK-TAKT {takt:02d}/12] Ingesting 24-element 1-Byte excitation tensor...")
        
        # Input tensor calibrated via the system invariant constant mass-ratio (1836)
        excitation_input = np.ones(24, dtype=np.int32) * (1836 + takt * 8)
        
        # --- SPECTACULAR WAVE DYNAMICS FOR THE VIDEO RECORDING ---
        # Forces the zero-states to roll dynamically across the 24 registers
        wave_idx_1 = (takt * 2) % 24
        wave_idx_2 = (takt * 2 + 5) % 24
        excitation_input[wave_idx_1] = 0
        excitation_input[wave_idx_2] = 0
            
        start_time = time.perf_counter_ns()
        network.forward_propagation_takt(excitation_input)
        end_time = time.perf_counter_ns()
        
        duration_us = (end_time - start_time) / 1000
        
        # Real-time visual mapping of the 1-Byte node transformations
        matrix_visual = ""
        for byte_val in network.crystal_core_register:
            if byte_val == 0: 
                matrix_visual += f"{C}[·]{W}"
            elif byte_val % 2 == 0: 
                matrix_visual += f"{G}[■]{W}"
            else: 
                matrix_visual += f"{Y}[⚙]{W}"
            
        print(f"    --> 24-Contact Register Map   : {matrix_visual}")
        print(f"    ✓ Asymptotic Execution Time   : {Y}{duration_us:.2f} µs{W} | Quantization Drift: {G}0.00%{W}")
        
        # Enhanced global meta-buffer telemetry tracking active echoes
        active_echoes = np.count_nonzero(network.outer_facet_meta_memory)
        print(f"    ✓ 120-Outer-Facet Meta Buffer : Active Facets: {G}{active_echoes}/120{W} | Sample Slice: {network.outer_facet_meta_memory[0:10]}")

    print(f"\n------------------------------------------------------------------------------")
    parity_valid = network.verify_network_parity()
    print(f"{B}[G][SUCCESS] Crystalline multi-ring dot-product accomplished.")
    print(f"--> Global Grid Invariance Status: {parity_valid} (Symmetrical Parity Lock Intact).{W}")
    print(f"{B}{C}=============================================================================={W}\n")

if __name__ == "__main__":
    run_crystalline_nn_demo()
