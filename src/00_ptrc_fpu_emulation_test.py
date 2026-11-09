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
r"""
pTRC Framework - FPU Repurposing & Verification Suite
File Name: 00_ptrc_fpu_emulation_test.py
Operational Domain: Forcing IEEE-754 Float64 Mantissa to act as Bit-Invariant Integer Space.
"""

import sys

def run_fpu_emulation_proof(iterations=1000000):
    # ANSI-Farben für pristine Logs auf dem Ubuntu-Terminal
    C = "\033[96m"  # Cyan
    G = "\033[92m"  # Green
    R = "\033[91m"  # Red
    W = "\033[0m"   # Reset
    B = "\033[1m"   # Bold

    print(f"\n{B}{C}==============================================================================")
    print(f"  pTRC EXPERIMENTAL // HARDWARE FPU GANZZAHL-EMULATIONS-PROOF                ")
    print(f"  Testing {iterations:,} Steps directly inside the Float64 Mantissa Registers ")
    print(f"=============================================================================={W}\n")

    # --- Unser pTRC Takt-System ---
    PRIMORIAL_BASE = 210
    CONTROL_TAKT = 24
    INVARIANT_LIMIT = 156
    
    # 1. PURE INTEGER Z-SPACE
    ptrc_factor_integer = 123456789
    ptrc_accumulator_integer = 0

    # 2. EMULATED FPU Z-SPACE (Wir nutzen float, aber füttern es mit pTRC-Ganzzahlen!)
    fpu_factor_emulated = float(123456789)
    fpu_accumulator_emulated = float(0)

    print("[*] Feeding the 53-bit FPU Float64 mantissa with whole pTRC integers...")
    
    # Der unbestechliche Schleifenlauf
    for takt in range(1, iterations + 1):
        ptrc_accumulator_integer += ptrc_factor_integer
        fpu_accumulator_emulated += fpu_factor_emulated  # Hardware-FPU führt Float-Addition aus

    # Multi-Modulares Uhrsieb auf beiden Registern anwenden
    # Wichtig: Bei der FPU nutzen wir die Ganzzahl-Boden-Division (//), um FPUs Divisionsrauschen zu blockieren
    ptrc_final_sieve = (ptrc_accumulator_integer + INVARIANT_LIMIT) % PRIMORIAL_BASE
    fpu_final_sieve = int((fpu_accumulator_emulated + float(INVARIANT_LIMIT)) % float(PRIMORIAL_BASE))

    print(f"✓ Loop complete. Maximum Float64 capacity limit: 9,007,199,254,740,992")
    print(f"  Current FPU Register value achieved:           {int(fpu_accumulator_emulated):,}\n")
    print("-" * 76)
    print(f"{B}DIRECT REGISTER EQUALIZATION DATA:{W}")
    print(f"  • Pure Integer Z-Register : {G}{ptrc_accumulator_integer}{W}")
    print(f"  • Emulated Float64-Register: {G}{int(fpu_accumulator_emulated)}{W}")
    print("-" * 76)
    print(f"{B}Final Uhrsieb Core Status Match (Modulo-210 Verification):{W}")
    print(f"  • pTRC Integer Sieve State:  {G}{ptrc_final_sieve}{W}")
    print(f"  • FPU Emulated Sieve State:  {G}{fpu_final_sieve}{W}")
    print("-" * 76)

    # Der unbestechliche Beweis
    emulation_drift = abs(fpu_accumulator_emulated - float(ptrc_accumulator_integer))
    print(f"  • Cumulative FPU Emulation Drift: {G}{emulation_drift:.15e} Invariant Units{W}")
    
    if ptrc_accumulator_integer == int(fpu_accumulator_emulated) and ptrc_final_sieve == fpu_final_sieve:
        print(f"\n-> {B}{G}[EMULATION PROOF SUCCESSFUL]{W}")
        print("   The FPU has been successfully hijacked by the pTRC framework.")
        print("   As long as states remain inside the 53-bit mantissa, FPU drift drops to absolute ZERO.")
        print(f"{B}{C}=============================================================================={W}\n")
        sys.exit(0)
    else:
        print(f"\n-> {B}{R}[PROOF FAILED]{W} Numerical divergence detected.")
        sys.exit(1)

if __name__ == "__main__":
    run_hardware_drift_diagnostic = run_fpu_emulation_proof
    run_hardware_drift_diagnostic(iterations=1000000)
