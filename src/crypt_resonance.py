r"""
pTRC - p-Adic Takt-Resonance Cosmology (Part 5 - Cryptographic Demonstrator)
Symmetrical Data Encryption via the Abelian Modulo-24 Ray Space 
and Geometric Interference Node Inversion.
"""

import numpy as np

# Erlaubter Strahlenraum S nach Formel 1 des mathematischen Axioms
S_RAYS = {1, 5, 7, 11, 13, 17, 19, 23}

def encrypt_character(char, private_key_ray):
    r"""
    Verschlüsselt ein einzelnes Zeichen basierend auf der Gruppeninteraktion.
    Nutzt die Selbstinversion der abelschen Gruppe: (s * s) ≡ 1 (mod 24).
    """
    if private_key_ray not in S_RAYS:
        raise ValueError(f"Key-Strahl muss Element aus S_RAYS {S_RAYS} sein!")
        
    ascii_val = ord(char)
    
    # Zerlegung in Schicht m und Rest s nach Formel 1: N = 24 * m + s
    m = ascii_val // 24
    s = ascii_val % 24
    
    if s == 0:
        s = 24
        m -= 1
        
    # Symmetrische Frequenz-Kreuzung modulo 24 (Formel 2)
    s_ziel = (s * private_key_ray) % 24
    if s_ziel == 0:
        s_ziel = 24
        
    # Emergent encrypted integer token (Interferenzknoten)
    encrypted_token = 24 * m + s_ziel
    return encrypted_token

def decrypt_token(token, private_key_ray):
    r"""
    Entschlüsselt das Token. Da alle Strahlen selbstinvers unter modulo 24 sind,
    ist der Entschlüsselungs-Algorithmus identisch zur Verschlüsselung!
    """
    # Rekonstruktion über dieselbe Modulo-Symmetrie
    m = token // 24
    s_ziel = token % 24
    if s_ziel == 0:
        s_ziel = 24
        m -= 1
        
    # Rückberechnung des ursprünglichen Strahls über die Selbstinversion
    s_orig = (s_ziel * private_key_ray) % 24
    if s_orig == 0:
        s_orig = 24
        
    return chr(24 * m + s_orig)

def run_crypt_demonstrator():
    print("[pTRC-CRYPT] Starte kommerziellen Krypto-Resonanz-Demonstrator...")
    
    secret_message = "Microsoft Quantum Validation Protocol 2026 - Secure"
    key_ray = 17  # Strahl 17 aus der abelschen Gruppe G wählen
    
    print(f" -> Geheime Nachricht: '{secret_message}'")
    print(f" -> Gewählter Key-Strahl (Symmetrieachse): {key_ray}")
    
    # 1. Verschlüsselungsschleife
    tokens = [encrypt_character(c, key_ray) for c in secret_message]
    print(f" -> Generierte Interferenz-Knoten (Tokens):\n    {tokens[:8]} ...")
    
    # 2. Entschlüsselungsschleife
    decrypted_message = "".join([decrypt_token(t, key_ray) for t in tokens])
    print(f" -> Rekonstruierte Nachricht: '{decrypted_message}'")
    
    print("\n================================================================================")
    if secret_message == decrypted_message:
        print(" -> SUCCESS: Datenverlustfreie Gruppeninversion ohne Rundungsfehler verifiziert.")
        print(" -> STATUS: Bereit zur kommerziellen Verwertung (Dual-Licensing GPLv3).")
    else:
        print(" -> WARNING: Destruktive Interferenz im Modulo-Raster detektiert.")
    print("================================================================================")

if __name__ == "__main__":
    run_crypt_demonstrator()
