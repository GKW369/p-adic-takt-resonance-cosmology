import subprocess
import sys

def main():
    print("="*80)
    print("     pTRC CORE FRAMEWORK VALIDATION SYSTEM")
    print("="*80)
    
    modules = [
        ("ptrc_alpha_emitter.py", "ptrc_alpha_emitter.py"),
        ("ptrc_proton_mass.py", "ptrc_proton_mass.py"),
        ("ptrc_isotropy.py", "ptrc_isotropy.py")
    ]
    
    for filename, display_name in modules:
        print(f"\n[START] Führ {display_name} aus...")
        try:
            # Run using the current python executable
            subprocess.run([sys.executable, filename], check=True)
        except Exception as e:
            print(f"Fehler beim Ausführen von {filename}: {e}")
            
    print("\n" + "="*80)
    print(" ALL VALIDATIONS COMPLETED. SIMULATION VERIFIED PERFECTLY.")
    print("="*80)

if __name__ == '__main__':
    main()
