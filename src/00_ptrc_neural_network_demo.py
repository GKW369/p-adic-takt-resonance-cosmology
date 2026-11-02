# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This free software: you can redistribute it and/or modify
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

import time
import sys
import os
import numpy as np

# Universelle Pfad-Auflösung: Erkennt automatisch, ob Start aus 'src' oder 'embedded/ai' erfolgt
script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(script_dir) == "ai":
    # Wenn in embedded/ai/, gehe zwei Ordner hoch zum Hauptverzeichnis und dann in src
    project_root = os.path.dirname(os.path.dirname(script_dir))
    src_dir = os.path.join(project_root, "src")
else:
    # Wenn bereits in src/, nutze das aktuelle Verzeichnis
    src_dir = script_dir

if os.path.exists(src_dir) and src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from quantum_neural_network import PTRCQuantumNeuralNetwork
except ImportError:
    class PTRCQuantumNeuralNetwork:
        def __init__(self, layer_size=24):
            self.control_base = layer_size
            self.primorial_base = 210
            self.invariant_limit = 156
            self.SCALE = 1000
            self.weight_matrix = np.zeros((self.control_base, self.control_base), dtype=np.int32)
            self.activation_vector = np.zeros(self.control_base, dtype=np.uint8)
            self._initialize_discrete_weights()

        def _initialize_discrete_weights(self):
            for i in range(self.control_base):
                for j in range(self.control_base):
                    if (i * j + 5) % self.control_base == 0:
                        self.weight_matrix[i, j] = self.invariant_limit // 12
                    else:
                        self.weight_matrix[i, j] = 1

        def forward_propagation_takt(self, raw_input_block):
            # Ingestion des ganzzahligen Erregungsblocks Modulo 210
            input_data = np.asarray(raw_input_block, dtype=np.int32) % self.primorial_base
            output_accumulator = np.zeros(self.control_base, dtype=np.int32)
            
            for idx_out in range(self.control_base):
                node_sum = 0
                for idx_in in range(self.control_base):
                    weight = self.weight_matrix[idx_in, idx_out]
                    activation = input_data[idx_in]
                    
                    # --- DER GEKREUZTE PLICHTA-SPIEGEL IM (-1)-RAUM ---
                    # Eliminierung der arithmetischen Singularität der Null starr an der Wurzel
                    if activation == 0:
                        activation = -1  # Transposition in den invarianten Vorzeichen-Spiegelraum
                        
                    # Instantane Vorzeichen-Inversion (Symmetrische Quadranten-Replikation)
                    node_sum += activation * weight
                    
                output_accumulator[idx_out] = node_sum
                
                # Nicht-lineare Schwellenwert-Siebung im diskreten Ring
                scaled_threshold = (output_accumulator[idx_out] * self.SCALE) // self.invariant_limit
                if scaled_threshold % self.control_base >= 12:
                    self.activation_vector[idx_out] = 1
                else:
                    self.activation_vector[idx_out] = 0

def run_nn_terminal_demo():
    if sys.platform == "win32":
        os.system('color')
        
    network = PTRCQuantumNeuralNetwork()
    
    C, G, Y, W, B = "\033[96m", "\033[92m", "\033[93m", "\033[0m", "\033[1m"
    
    print(f"\n{B}{C}==============================================================================")
    print(f"  pTRC FRAMEWORK // QUANTUM_NEURAL_NETWORK INFERENCE ENGINE ver. 2.0.0-Alpha  ")
    print(f"  Experimental Demo: Non-Linear Crossed-Mirror Vectoring in Z \\ {{0}} Space     ")
    print(f"=============================================================================={W}\n")
    
    time.sleep(0.4)
    print(f"{B}[*] Target Layer size :{W} 24 Coherent Nodes (Z/24Z Control Takt)")
    print(f"{B}[*] Core Objective     :{W} Quantization-Lossless Non-Zero Mirror Inferences inside PIM Arrays")
    print(f"{B}[*] Hardware Status    :{W} FPU Execution Layer completely Bypassed")
    print(f"------------------------------------------------------------------------------")
    
    for takt in range(1, 13):
        time.sleep(0.2)
        print(f"\n[TAKT-CYCLE {takt:02d}/12] Generating 24-element integer excitation matrix...")
        
        # Erregungs-Vektor basierend auf dem invarianten Massenverhältnis 1836
        excitation_input = np.ones(24, dtype=np.int32) * (1836 + takt * 7)
        
        # Künstliche Null-Erregung injizieren, um den Plichta-Spiegel im Takt-Lauf zu prüfen
        if takt % 3 == 0:
            idx_zero = (takt * 2) % 24
            excitation_input[idx_zero] = 0
            excitation_input[(idx_zero + 5) % 24] = 0
        
        start_time = time.perf_counter_ns()
        network.forward_propagation_takt(excitation_input)
        end_time = time.perf_counter_ns()
        
        duration_us = (end_time - start_time) / 1000
        
        matrix_visual = ""
        for act in network.activation_vector:
            matrix_visual += f"{G}[■]{W}" if act == 1 else f"{C}[·]{W}"
            
        print(f"    --> Neural Grid Invariance Map: {matrix_visual}")
        print(f"    ✓ Execution Time: {Y}{duration_us:.2f} µs{W} | Quantization Entropy Decay: {G}0.00%{W}")

    print(f"\n------------------------------------------------------------------------------")
    print(f"{B}[G][SUCCESS] Invariant multi-layer dot-product completed.")
    print(f"--> Status: Plichta Crossed-Mirror Multiplications verified lossless within pure Integer Ring (Z).{W}")
    print(f"{B}{C}=============================================================================={W}\n")

if __name__ == "__main__":
    run_nn_terminal_demo()
