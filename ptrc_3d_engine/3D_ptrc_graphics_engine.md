<!--
==============================================================================
pTRC Framework - 144-Facet Spatial Crystal Graphics System
Module: 3D Engine Architecture & Specifications Documentation
Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>

DUAL-LICENSING NOTICE:
Non-commercial, academic, and open-source usage is strictly governed by 
the GNU General Public License version 3 (GPLv3). Any commercial deployment,
integration into proprietary, closed-source codebases, or corporate utilization
explicitly requires a separate, individually negotiated commercial license.
==============================================================================
-->

# pTRC Framework: 144-Facet Spatial Crystal 3D Graphics Engine

This document specifies the deterministic, 100% floating-point-free 3D graphics layer of the pTRC framework. Unlike traditional graphics pipelines that rely on hardware FPUs and analog trigonometric approximations, this engine operates entirely within the ring of integers (\(\mathbb{Z}\)) via a modular residue class clock system (Z/210Z and Z/24Z).

## 🔬 Visual Architecture & Axioms

- **Quantum Image Refresh:** Coherent image collapse and state evaluation trigger precisely every **137 clock cycles** (Alpha Shutter Matrix derived from the fine-structure constant).
- **Constant Velocity:** Information and photon propagation operate at a rigid discrete velocity of **c = 1 pixel/clock**.
- **144-Facet Geometry:** Vision rays march strictly along the invariant trajectories derived from the 144-facet vector equilibrium matrix.
- **Infinite Scalability:** The system has no upper bounds. When the spatial grid saturates, the next primorial expansion layer (e.g., Z/2310Z, Z/30030Z) is layered seamlessly without breaking the rendering loop.

## 📁 Repository Assets in this Directory

- `ptrc_clock_core.py`: The core mathematical engine managing the Z/210Z and Z/24Z sieve matrices.
- `main_renderer.py`: The live 3D ray-marching terminal preview running along the 144 spatial facets.
- `ptrc_4k_genesis.py`: The fixed-point 4K Ultra-HD renderer which bakes pure number theory onto the disk.
- `generate_ptrc_4k_anim.py`: A 39-second, 60 FPS presentation generator demonstrating rollercoaster and stable-orbit paths inside the integer matrix.
- `ptrc_4k_genesis.ppm`: The **raw, uncompressed 4K reference master file**. Download this file to your device to inspect the lossless arithmetic micro-structure without timeline compression.
- `ptrc_4k_genesis.png`: High-resolution web preview.

## 🚀 Execution

To run the native 144-facet spatial ray-marching preview directly inside your terminal, execute:
```bash
python3 main_renderer.py
```

To bake the loss-free 4K Ultra-HD fixed-point holofractal image, deploy:
```bash
python3 ptrc_4k_genesis.py
```

To generate the 2340 high-resolution frames for the 39-second presentation ride, run:
```bash
python3 generate_ptrc_4k_anim.py
```

## ⚖️ Intellectual Property & Licensing

All algorithms, architectures, and rendering paradigms documented in this file are the exclusive intellectual property of **Kurt Guido Wirminghaus**. 

- **Academic & Open-Source Copyleft:** Protected under the **GNU General Public License version 3 (GPLv3)**. Any public modification or deployment must remain fully open-source under identical terms.
- **Commercial & Proprietary Deployment:** Any commercial integration into proprietary software, gaming engines, custom silicon architectures, or enterprise environments (specifically by console manufacturers or corporate developers) **explicitly requires a separate, individually negotiated commercial license** from the copyright holder.

---
*The pTRC Graphics Layer is a proprietary subset of the p-adic Takt Resonance Cosmology engine.*
