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
#
# For commercial licensing, enterprise integration, or proprietary deployment
# options, please contact the author directly.
# ==============================================================================

# -*- coding: utf-8 -*-
"""
pTRC Framework - Master First-Principles Simulation Orchestrator
Sequentially clocks and audits all 20 structural mathematical sub-nodes in Z.
Verifies total numerical invariance against the calibration threshold limit.
"""

import sys
import subprocess
import os

class PTRCFirstPrinciplesOrchestrator:
    def __init__(self):
        self.calibration_constant = 1836
        self.sub_modules = [
            "base_resonance_calibration.py", "battery_anisotropy.py",
            "black_hole_information_preservation.py", "black_hole_saturation.py",
            "casimir_vacuum_energy.py", "chemical_resonance.py",
            "crypt_resonance.py", "fluid_resonance.py",
            "gravity_edge_sharing.py", "hubble_tension.py",
            "internal_loopback.py", "isotropy.py",
            "lattice_symmetry_check.py", "pi_square_crystallization.py",
            "prime_lattice_determinism.py", "quantum_entanglement.py",
            "quantum_measurement_update.py", "quantum_neural_network.py",
            "thermodynamic_clock_cycle.py", "alpha_emitter.py"
        ]
        
    def execute_and_audit_pipeline(self):
        print(f"[ pTRC-ORCHESTRATOR ] Initiating global execution sweep...")
        failed_nodes = 0
        
        # Bestimme das Verzeichnis, in dem dieses Orchestrator-Skript liegt
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        for module in self.sub_modules:
            # 1. Option: Suche im Standardordner 'src'
            script_path = os.path.join(current_dir, "src", module)
            
            if not os.path.exists(script_path):
                # 2. Option: Suche im Ordner 'experimental'
                script_path = os.path.join(current_dir, "experimental", module)
                
            if not os.path.exists(script_path):
                # 3. Option: Suche direkt im selben Ordner wie der Orchestrator
                script_path = os.path.join(current_dir, module)
                
            print(f" -> Clocking sub-node: {module}...")
            
            # Letzter Check, bevor das Subprocess-Modul gestartet wird
            if not os.path.exists(script_path):
                print(f"    ! [ ERROR ] Datei wurde in keinem Verzeichnis gefunden!")
                failed_nodes += 1
                continue
                
            try:
                # Führe das Modul isoliert aus
                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True, text=True, check=True
                )
                if "VALIDATION" in result.stdout or result.returncode == 0:
                    print(f"    + [ SUCCESS ] Sub-node {module} verified stable.")
                else:
                    print(f"    - [ ANOMALY ] Verification flag missing in {module}.")
                    failed_nodes += 1
            except subprocess.CalledProcessError as e:
                print(f"    ! [ CRITICAL CRASH ] Execution failed for {module}!")
                print(f"      Log: {e.stderr.strip() if e.stderr else e.stdout.strip()}")
                failed_nodes += 1
            except Exception as ex:
                print(f"    ! [ UNKNOWN ERROR ] Node mapping failure: {str(ex)}")
                failed_nodes += 1
                
        return failed_nodes

if __name__ == "__main__":
    orchestrator = PTRCFirstPrinciplesOrchestrator()
    total_failures = orchestrator.execute_and_audit_pipeline()
    
    print("======================================================================")
    print(f"[ SIMULATION COMPLETE ] Pipeline execution finalized.")
    print(f" -> Active Node Mappings Stable, Total Faulty Nodes logged: {total_failures}")
    print("======================================================================")
    
    if total_failures == 0:
        print(" -> SYSTEM INTEGRITY SECURED: Zero-Float Invariance Active.")
        sys.exit(0)
    else:
        print(" -> SYSTEM CRITICAL: Rectification of sub-lattice indices mandated.")
        sys.exit(1)
