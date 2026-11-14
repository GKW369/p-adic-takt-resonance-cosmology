<!--
# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# LICENSE & LIABILITY NOTICE:
# Academic, non-commercial research and evaluation is permitted strictly under 
# the terms of the GNU Affero General Public License version 3 (AGPLv3).
# For the complete, unedited license text see: https://gnu.org
#
# ANY COMMERCIAL DEPLOYMENT, production utilization, or proprietary enterprise 
# integration requires a separate, individually negotiated commercial infrastructure 
# waiver issued directly by the author.
#
# WARRANTY DISCLAIMER: THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE SYSTEMATICALLY DISCLAIMED.
# ==============================================================================
-->

# Contributing to the pTRC Framework

Thank you for your interest in contributing to **p-Adic Takt Resonance Cosmology (pTRC)**. Because this repository investigates deterministic, non-Archimedean integer physics ($\mathbb{Z} \setminus \{0\}$) and side-channel-resistant cryptography, every contribution must adhere strictly to our zero-floating-point, deterministic engineering invariants.

---

## Core Architectural Invariants (Mandatory Rules)

1. **Strict Zero-Float Rule ($\mathbb{Z} \setminus \{0\}$):**
   * Production physics, lattice, Edge-AI, and cryptographic code (`src/`, `embedded/`) **must not** use `float`, `double`, `math.sin`, `math.cos`, `math.sqrt`, or IEEE-754 floating-point approximations.
   * All scaling, rotations, and wave lookups must execute via fixed integer scales (`SCALE = 1000`), integer floor division (`//`), or discrete residue rings ($\mathbb{Z}/210\mathbb{Z}$, $\mathbb{Z}/24\mathbb{Z}$, $P_{15}$).
   * Floating-point math is permitted **only** inside dedicated comparison benchmarks (e.g., `src/00_ptrc_fpu_drift_test.py`) or terminal human-readable summary metrics.

2. **Constant-Time Execution ($O(1)$) & Zero Heap Allocation in Embedded C:**
   * All C11 bare-metal code under `embedded/crypto/` must compile cleanly with `-std=c11 -Wall -Wextra -Werror` and cross-compile for `arm-none-eabi-gcc -mcpu=cortex-m0plus -mfloat-abi=soft`.
   * Avoid `malloc`/`free`, secret-dependent branches, and secret-dependent memory lookups.

3. **Bit-Exact C11 $\leftrightarrow$ Python Parity:**
   * Any change to the v4.0 512-bit Primorial AEAD (`embedded/crypto/ptrc_crystal.c`) must maintain 100% bit-exact parity with the Python reference (`src/ptrc_crystal_aead.py`), verified across 512-bit key, 128-bit nonce, and 192-bit SLIP-MAC test vectors.

4. **AGPLv3 License Header Compliance:**
   * Every new `.py`, `.c`, `.h`, `.yml`, or `.md` file must include the standard pTRC AGPLv3 copyright header at the top of the file.

---

## Local Verification Checklist Before Opening a Pull Request

Run the complete local verification suite from the repository root before submitting changes:

```bash
# 1. Core 20-Module Physics, Cosmology & Edge-AI Verification
python3 src/00_ptrc_first_principles_engine.py
python3 embedded/ai/00_ptrc_neural_network_demo.py

# 2. C11 Build & Standalone 512-Bit Hardware Demo
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
./build/ptrc_hardware_demo

# 3. Cross-Language Bit-Parity, Avalanche Metrics & Terminal Demo
python3 src/00_test_ptrc_crypt_parity.py
python3 src/00_test_ptrc_crypt_metrics.py
python3 src/00_ptrc_crypt_demo.py
```

---

## Licensing & Contributor Agreement

By submitting a pull request to this repository, you agree that your contributions are licensed under the **GNU Affero General Public License v3.0 (AGPLv3)** and that the author retains the right to offer separate commercial infrastructure exemptions under the dual-licensing model described in `README.md`.
