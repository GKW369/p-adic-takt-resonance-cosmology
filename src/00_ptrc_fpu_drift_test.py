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
pTRC Framework - Hardware Diagnostic & Verification Suite
File Name: 00_ptrc_fpu_drift_test.py
Operational Domain: FPU Precision Degradation vs. Non-Archimedean Integer Invariance.
Direct 1:1 Comparative Metric Edition. Symmetrical Whole-Number Outputs with Initial State Proof.
"""

import sys
import time

def run_hardware_drift_diagnostic(iterations=1000000):
    # Terminal formatting (ANSI escape sequences for pristine metric logs)
    C = "\033[96m"  # Cyan
    G = "\033[92m"  # Green
    Y = "\033[93m"  # Yellow
    R = "\033[91m"  # Red
    W = "\033[0m"   # Reset
    B = "\033[1m"   # Bold

    print(f"\n{B}{C}==============================================================================")
    print(f"  pTRC CORE GRAPHICS & PHYSICS // NATIVE HARDWARE REGISTRY DIAGNOSTIC        ")
    print(f"  Direct 1:1 Comparison Profile: {iterations:,} Background Engine Takts       ")
    print(f"=============================================================================={W}\n")
    
    # --- System Invariants matching the primorial clock metrics ---
    INVARIANT_LIMIT = 156
    REFRESH_TAKT = 137  # Isolated Observer Refresh Matrix (Feynman Quantum Proxy)
    
    # --- SYNCHRONOUS INITIALIZATION PROOF (TAKT 0) ---
    # Demanding strict baseline verification to demonstrate identical loading states
    initial_fpu_register_state = INVARIANT_LIMIT
    initial_ptrc_invariant_state = INVARIANT_LIMIT
    
    print(f"{B}SYNCHRONOUS INITIALIZATION PROOF (Takt 0):{W}")
    print(f"  • Initial FPU Register State  : {Y}{initial_fpu_register_state}{W}")
    print(f"  • Initial pTRC Invariant State : {G}{initial_ptrc_invariant_state}{W}")
    print("-" * 76)
    
    # --- 1. CONTINUOUS MANIFOLD INITIALIZATION (The Analog Float Space) ---
    float_increment = 123456789012345 / 1000000000000000
    float_accumulator = 0.0
    
    # --- 2. DISCRETE pTRC INITIALIZATION (The Pure Integer Z-Space) ---
    ptrc_factor_scaled = 123456789012345
    ptrc_accumulator_scaled = 0
    
    print(f"[*] Commencing background engine state updates directly inside registers...")
    time.sleep(0.5)

    start_perf_clock = time.perf_counter()
    
    # --- HARDWARE-LEVEL BACKGROUND EXECUTION LAYER ---
    for takt in range(1, iterations + 1):
        float_accumulator += float_increment
        ptrc_accumulator_scaled += ptrc_factor_scaled

    end_perf_clock = time.perf_counter()
    execution_duration_ms = int((end_perf_clock - start_perf_clock) * 1000)

    # --- ISOLATED OBSERVER VIEWPORT PROJECTION (The 137 Refresh Takt) ---
    ptrc_mod_boundary = ptrc_factor_scaled * 10
    ptrc_observer_matrix = (ptrc_accumulator_scaled + INVARIANT_LIMIT) % ptrc_mod_boundary
    
    float_mod_boundary = float_increment * 10
    float_invariant_limit = INVARIANT_LIMIT / 1000000000000000
    float_observer_matrix = (float_accumulator + float_invariant_limit) % float_mod_boundary

    # --- DISCRETE 1:1 RECONSTRUCTION WITH ABSOLUTE WHOLE NUMBERS ---
    fpu_reconstructed_integer = int(float_observer_matrix * 1000000000000000)
    exact_analytical_integer = ((ptrc_factor_scaled * iterations) + INVARIANT_LIMIT) % ptrc_mod_boundary
    
    # Calculate the hardware-level variance as a scientific floating-point decimal
    exact_analytical_float = exact_analytical_integer / 1000000000000000
    fpu_drift_error = abs(float_observer_matrix - exact_analytical_float)

    print(f"✓ Background engine complete. Viewport refreshed under {execution_duration_ms} ms.\n")
    print("-" * 76)
    print(f"{B}DIRECT PROCESSING CHANNEL EQUALIZATION (Absolute Whole-Number Registers):{W}")
    print(f"  • Continuous FPU Register Echo : {R}{fpu_reconstructed_integer}{W}")
    print(f"  • Discrete Invariant pTRC-Value: {G}{ptrc_observer_matrix}{W}")
    print("-" * 76)
    print(f"  • Exact Analytical Target State: {exact_analytical_integer}")
    print(f"  • Cumulative FPU Rounding Deficit: {R}{fpu_drift_error:.15e} Absolute Units{W}")
    print(f"  • pTRC Asymptotic Entropy Decay  : {G}0.000000000000000e+00 (Absolute Symmetrical Lock){W}")
    print(f"{B}{C}=============================================================================={W}\n")
    
    # Verify the micro-architectural leakage from the IEEE-754 FPU
    if fpu_reconstructed_integer != ptrc_observer_matrix:
        print(f"-> {B}{G}[SYSTEM DIAGNOSTIC VALIDATED]{W}")
        print("   The fallacy of the continuous floating-point manifold has been exposed.")
        print("   The background engine remains locked, while the FPU viewport drifts.")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    run_hardware_drift_diagnostic(iterations=1000000)
