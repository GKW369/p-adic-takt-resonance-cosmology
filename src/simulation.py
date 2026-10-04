"""
pTRC - p-Adic Takt-Resonance Cosmology
Numerical Verification of 4th-Order Isotropy on Icosahedral Quasicrystal Lattices
"""

import numpy as np

def get_icosahedral_axes():
    """
    Generates the 6 independent directional vectors projected from the 6D hypercubic lattice
    pointing to the vertices of a regular icosahedron.
    """
    phi = (1.0 + np.sqrt(5.0)) / 2.0  # Golden Ratio
    norm = np.sqrt(1.0 + phi**2)
    
    # 12 vertices of an icosahedron
    vertices = np.array([
        [phi, 1.0, 0.0], [phi, -1.0, 0.0], [-phi, 1.0, 0.0], [-phi, -1.0, 0.0],
        [0.0, phi, 1.0], [0.0, phi, -1.0], [0.0, -phi, 1.0], [0.0, -phi, -1.0],
        [1.0, 0.0, phi], [-1.0, 0.0, phi], [1.0, 0.0, -phi], [-1.0, 0.0, -phi]
    ]) / norm
    
    # Filter out antipodal duplicates to get 6 unique axes
    unique_axes = []
    for vec in vertices:
        if not any(np.allclose(vec, -u) or np.allclose(vec, u) for u in unique_axes):
            unique_axes.append(vec)
            
    return np.array(unique_axes)[:6]

def calculate_dispersion(k_vector, ell_P=1.0):
    r"""
    Calculates the exact energy dispersion relation:
    omega^2 = 2 * \sum_{i=1}^6 (1 - \cos(\vec{k} \cdot \vec{v}_i \ell_P))
    """
    axes = get_icosahedral_axes()
    terms = 0.0
    for vi in axes:
        dot_product = np.dot(k_vector, vi)
        terms += 1.0 - np.cos(dot_product * ell_P)
    
    return 2.0 * terms
    
def verify_isotropy(k_magnitude=0.1, samples=100):
    """
    Tests directional dispersion to numerically prove the absence of angular anisotropy
    up to the O(ell_P^4) limit.
    """
    print(f"[pTRC] Scanning isotropic boundaries at |k| = {k_magnitude}...")
    axes = get_icosahedral_axes()
    
    dispersions = []
    # Generate random angular directions on a 3D sphere
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
    print(f" -> Dispersion Variance across {samples} orientations: {variance:.2e}")
    if variance < 1e-12:
        print(" -> SUCCESS: Angular anisotropy identically zero up to O(ell_P^4).")
    else:
        print(" -> WARNING: Residual lattice effects detected.")

if __name__ == "__main__":
    verify_isotropy(k_magnitude=0.05, samples=500)

