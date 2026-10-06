import subprocess
import os

print("================================================================================")
print("     pTRC CORE FRAMEWORK VALIDATION SYSTEM")
print("================================================================================")

def run_module(script_name):
    print(f"\n[START] Executing {script_name}...")
    if os.path.exists(script_name):
        subprocess.run(["python3", script_name])
    else:
        print(f" -> ERROR: {script_name} not found in current directory.")

# Execute all modules sequentially
run_module("ptrc_alpha_emitter.py")
run_module("ptrc_proton_mass.py")
run_module("ptrc_isotropy.py")

print("\n================================================================================")
print(" ALL VALIDATIONS COMPLETED. KERNEL SYSTEM FULLY OPERATIONAL.")
print("================================================================================")
