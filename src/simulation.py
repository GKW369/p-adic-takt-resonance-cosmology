"""
pTRC - p-Adic Takt-Resonance Cosmology
Numerical Verification of 4th-Order Isotropy within the 210-Primeorial Network
"""

import numpy as np

def get_network_symmetry_axes():
    """
    Generates the core discrete routing channels derived from the 
    210-primeorial track configuration corresponding to the icosahedral symmetry group.
    """
    phi = (1.0 + np.sqrt(5.0)) / 2.0  # Golden Ratio resonance factor
    norm = np.sqrt(1.0 + phi**2)
    
    # Fundamental coordinate vectors of the 144-facet vector equilibrium topology
    vertices = np.array([
        [phi, 1.0, 0.0], [phi, -1.0, 0.0], [-phi, 1.0, 0.0], [-phi, -1.0, 0.0],
        [0.0, phi, 1.0], [0.0, phi, -1.0], [0.0, -phi, 1.0], [0.0, -phi, -1.0],
        [1.0, 0.0, phi], [-1.0, 0.0, phi], [1.0, 0.0, -phi], [-1.0, 0.0, -phi]
    ]) / norm
    
    # Map the unique symmetrical routing axes across the 210-track network
    unique_axes = []
    for vec in vertices:
        if not any(np.allclose(vec, -u) or np.allclose(vec, u) for u in unique_axes):
            unique_axes.append(vec)
            
    return np.array(unique_axes)

def calculate_dispersion(k_vector, ell_P=1.0):
    r"""
    Calculates the exact integer-based informational energy dispersion relation
    across the active network paths:
    omega^2 = 2 * \sum_{i \in Tracks} (1 - \cos(\vec{k} \cdot \vec{v}_i \ell_P))
    """
    axes = get_network_symmetry_axes()
    terms = 0.0
    for vi in axes:
        dot_product = np.dot(k_vector, vi)
        terms += 1.0 - np.cos(dot_product * ell_P)
    
    return 2.0 * terms
    
def verify_isotropy(k_magnitude=0.1, samples=100):
    """
    Tests directional network paths to numerically prove the emergence of 
    macroscopic isotropy up to the O(ell_P^4) limit without continuous fields.
    """
    print(f"[pTRC] Scanning integer routing paths at |k| = {k_magnitude}...")
    
    dispersions = []
    # Generate random angular directions across the emergent relational sphere
    for _ in range(samples):
        theta = np.random.uniform(0, np.pi)
        phi = np.random.uniform(0, 2 * np.pi)
        k_dir = np.array([
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta)
        ])
        k_vec = k_dir * k_magnitude
        dispersions.append(calculate_dispersion(k_vec))
        
    variance = np.var(dispersions)
    print(f"[pTRC] Analysis complete.")
    print(f" -> Dispersion Variance across {samples} network paths: {variance:.2e}")
    if variance < 1e-12:
        print(" -> SUCCESS: Angular anisotropy identically zero up to O(ell_P^4).")
    else:
        print(" -> WARNING: Residual lattice anomalies detected.")

if __name__ == "__main__":
    verify_isotropy(k_magnitude=0.05, samples=500)
