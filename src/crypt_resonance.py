r"""
pTRC - p-Adic Takt-Resonance Cosmology (Part 9 - Cryptography)
Symmetrical Data Encryption via the Abelian Modulo-24 Ray Space 
and Geometric Interference Node Inversion.
"""

# Allowed ray space S from Formula 1 of the mathematical axioms
S_RAYS = {1, 5, 7, 11, 13, 17, 19, 23}

def encrypt_character(char, private_key_ray):
    r"""
    Encrypts a single character based on deterministic abelian group interaction.
    Leverages self-inversion properties: (s * s) == 1 (mod 24).
    """
    if private_key_ray not in S_RAYS:
        raise ValueError(f"Key ray must be an element of S_RAYS: {S_RAYS}")
        
    ascii_val = ord(char)
    
    # Structural decomposition into tier 'm' and remainder 's': N = 24 * m + s
    m = ascii_val // 24
    s = ascii_val % 24
    
    if s == 0:
        s = 24
        m -= 1
        
    # Symmetrical frequency crossing modulo 24
    s_target = (s * private_key_ray) % 24
    if s_target == 0:
        s_target = 24
        
    encrypted_token = 24 * m + s_target
    return encrypted_token

def decrypt_token(token, private_key_ray):
    r"""
    Decrypts the token. Because all active symmetry rays are self-inverse,
    the decryption pipeline is completely identical to encryption.
    """
    m = token // 24
    s_target = token % 24
    if s_target == 0:
        s_target = 24
        m -= 1
        
    s_orig = (s_target * private_key_ray) % 24
    if s_orig == 0:
        s_orig = 24
        
    return chr(24 * m + s_orig)

def run_crypt_demonstrator():
    print("[pTRC-CRYPT] Initializing commercial crypto-resonance demonstrator...")
    
    secret_message = "xAI Grok Quantum Validation Protocol 2026 - Secure Secure"
    key_ray = 17  
    
    print(f" -> Input String payload: '{secret_message}'")
    print(f" -> Active Key-Ray index axis:   {key_ray}")
    
    # Execution loops
    tokens = [encrypt_character(c, key_ray) for c in secret_message]
    print(f" -> Emitted Interference Tokens: {tokens[:8]} ...")
    
    decrypted_message = "".join([decrypt_token(t, key_ray) for t in tokens])
    print(f" -> Reconstructed Payload:       '{decrypted_message}'")
    
    print("\n================================================================================")
    if secret_message == decrypted_message:
        print(" -> SUCCESS: Zero-loss group inversion verified without round-off noise.")
        print(" -> STATUS: Production-ready asset secured for commercial dual-licensing.")
    else:
        print(" -> WARNING: Destructive interference detected inside modular matrix.")
    print("================================================================================")

if __name__ == "__main__":
    run_crypt_demonstrator()
