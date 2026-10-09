# pTRC Core Framework: Discrete Integer Computational Physics

An informational, discrete alternative for physical space simulations. This framework refactors physical mechanics from continuous real-number fields (\(\mathbb{R}^4\)) into highly efficient, integer-based coordinate matrices (\(\mathbb{Z}\)) using modular layout spaces.

By enforcing a strict sub-clocking limit (c = 1 pixel/clock) and deploying modular integer cycles (\(\mathbb{Z}/210\mathbb{Z}\) and \(\mathbb{Z}/24\mathbb{Z}\)), this engine significantly reduces computational overhead for complex structural, collision, and aerodynamic boundary calculations.

---

## 🔬 Computational Philosophy & Architecture

### 1. Finite Lattice Discretization
To eliminate the infinite division bottlenecks (\(\frac{1}{0}\)) inherent to continuous geometric environments, this framework restricts spatial representations to hard discrete lattice steps. Below the designated hardware scale, positions are processed via native integer boundaries, optimizing compiler-level pipeline execution. Transcendental constants like π or e do not exist on the fundamental hardware layer; they are treated as macroscale geometric illusions caused by pixel-aliasing over large coordinate distances.

### 2. Angular Approximation via Icosahedral Mapping
Discrete grids inherently suffer from directional rendering artifacts (anisotropy). The pTRC framework counters this by mapping spatial vectors to the 120 elements of the icosahedral symmetry group (\(I_h\)). This layout forces higher-order coordinate alignment variations to cancel out identically to zero, relegating lattice artifacts to an unmeasurable 6th-order magnitude (\(\mathcal{O}(\ell_P^4)\)), thus providing a balanced macroscopic approximation of isotropic fields.

### 3. High-Efficiency Phenomenological Modules
This framework contains 18 separate evaluation modules designed to simulate macroscale and quantum-scale interactions through simplified, discrete cellular automata logic. 

*   **`base_resonance_calibration.py`** – Establishes the core invariant calibration constant (1836 whole-number base states) to synchronize the primary modulo lattice cycles.
*   **`fluid_resonance.py`** – Executes a fully operational 2D Lattice-Gas Cellular Automaton (LGCA) fluid flow profile using pure integer bit-shifting, eliminating Navier-Stokes floating-point divergence.
*   **`quantum_entanglement.py`** – Models instantaneous non-local state synchronization via shared-memory array indexing in the processor kernel without signal transmission.
*   **`prime_lattice_determinism.py`** – Identifies vacant address gaps along the cyclic reflection axes of the active modulo system clock.
---

## 🚀 Execution & Performance Benchmarks

To run the visualization matrix and check the internal module sync paths, execute the master engine script within an Ubuntu terminal environment:

```bash
python3 00_ptrc_first_principles_engine.py
```

### Purpose of the Project
This framework serves as an experimental, high-efficiency algorithmic engine showing how complex multi-scale physics, multi-body collisions, and fluid dynamics can be simulated inside a deterministic, finite state machine with zero floating-point lag and zero accumulation errors.

---

## 🔬 Advanced Research & Experimental Node

For forward-looking developers and researchers interested in open-system thermodynamics, non-linear parametric resonance, and Tesla’s bifilar vector potential structures:

*   **`experimental/experimental_parametric_overunity.py`** – An isolated, theoretical simulation module modeling transient current cuts (dI/dt → ∞) and orthogonal field geometry.
*   **Theoretical Extension:** For the full advanced algebraic expansion of this coupling mechanic, see the secondary research paper included in this repository: `paper_experimental_resonance.txt`.

*Note: Experimental modules are strictly isolated from the 18 production-ready core simulation modules to guarantee system-wide operational stability during industrial code validation.*

---

## ⚖️ License & Commercial Exploitation (Dual-Licensing)

### 1. Open Source Evaluation (GPLv3)
This software is licensed under the **GNU General Public License v3 (GPLv3)**. Under the terms of the GPLv3, any third-party software, commercial game engine, or physics middleware that incorporates, forks, or links to this repository **must also be fully disclosed as open-source software**. 

### 🎯 2. Commercial & Corporate Licensing (EA, Nintendo, Aerospace, AI)
For commercial entities (e.g., video game publishers, sports simulations, aerospace developers, hardware-level AI compiler designers) requiring the integration of the pTRC integer-and-modulo physics architecture into **proprietary closed-source codebases**, a separate commercial license is mandatory. 

## 🛡️ Security Policy
Please review our [SECURITY.md](SECURITY.md) before integrating this framework into corporate pipelines. All lattice anomalies or potential buffer vulnerabilities must be reported privately to avoid exploiting closed proprietary systems.

Commercial licensing bypasses the GPLv3 open-source requirements and grants the right to adapt the core algorithms for high-performance proprietary systems. 

*   **For commercial licensing inquiries, architectural consulting, or corporate integration requests, contact the author privately:** 
    📧 **g.wirminghaus@gmx.de** 

## 🛡️ Security Policy
Please review our [SECURITY.md](SECURITY.md) before integrating this framework into corporate pipelines. All lattice anomalies or potential buffer vulnerabilities must be reported privately to avoid exploiting closed proprietary systems.

---

*Copyright (c) 2026 Kurt Guido Wirminghaus. Dedicated to the foundational insights of Max Planck, Nikola Tesla, and Peter Plichta.*
