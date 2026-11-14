<!--
==============================================================================
pTRC Framework - Discrete 1-Bit Integer Physics & AI Inference Engine
Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program (see the LICENSE file in the root directory).
If not, see <https://gnu.org>.
==============================================================================
-->

# pTRC Resonant BitNet AI Engine (v1.0 Foundation & v2.0 Bare-Metal C11/Python)

## 1. Overview
The **pTRC Resonant BitNet AI Engine** eliminates floating-point matrix multiplications (`GEMM`) and gradient backpropagation in favor of **1-bit bipolar (`{-1, +1}`) integer inference** operating strictly on the discrete $\mathbb{Z} \setminus \{0\}$ 1+12 space-crystal lattice.

- **v1.0 Foundational Concept (`src/00_ptrc_neural_network_demo.py`):** Demonstrates non-linear classification (such as 2-input XOR via a discrete `2 -> 16 -> 2` bipolar perceptron) using integer threshold activation in $\mathbb{Z} \setminus \{0\}$ without a zero state (`0` maps strictly to `-1`).
- **v2.0 Bare-Metal C11 & Python BitNet Engine (`embedded/ai/ptrc_bitnet_engine.c` & `src/ptrc_bitnet_engine.py`):** Scales the architecture to 64-bit packed XNOR + POPCOUNT bitplanes, a **144-facet crystalline resonance sponge**, **24-Clock Discrete Quadrance** phase coupling ($u^2 + v^2 = 1000^2$), a global **137-takt synchronization pulse** (`~x` reflection across `-1`), and **online integer Hebbian plasticity** bounded by the **156 Wirminghaus Invariant Limit**.
- **Silicon & Microcontroller Ready:** Static stack context (`sizeof(ptrc_bitnet_ctx_t)` = **592 bytes**), zero `malloc`, zero `float`/`double`, zero FPU instructions, deterministic `O(1)` latency, and volatile SRAM scrubbing (`ptrc_bitnet_wipe`).

---

## 2. Quick Start (CMake + Python/C11 Parity)

### 1. Build C11 Shared Libraries & Standalone `00_` Demos
```bash
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

### 2. Run Standalone C11 AI Demo (`00_ptrc_bitnet_demo`)
```bash
./build/00_ptrc_bitnet_demo
```

### 3. Run Interactive Python/C11 BitNet Terminal Demo (`00_ptrc_bitnet_demo.py`)
```bash
PYTHONPATH=src python3 src/00_ptrc_bitnet_demo.py
```

### 4. Run Foundational v1.0 Bipolar XOR Demo (`00_ptrc_neural_network_demo.py`)
```bash
PYTHONPATH=src python3 src/00_ptrc_neural_network_demo.py
```

### 5. Run Bit-Parity, Hebbian Convergence & Zero-Float Audit Suite
```bash
PYTHONPATH=src python3 src/test_ptrc_bitnet.py
```

---

## 3. Standalone C11 & Bare-Metal ARM Cortex-M0+ Compilation

### Standalone C11 Build (Without CMake)
```bash
gcc -O3 -std=c11 -Wall -Wextra -Wpedantic -Iembedded/ai \
    src/00_ptrc_bitnet_demo.c embedded/ai/ptrc_bitnet_engine.c \
    -o 00_ptrc_bitnet_demo
./00_ptrc_bitnet_demo
```

### Bare-Metal ARM Cortex-M0+ Cross-Compile Check
```bash
arm-none-eabi-gcc -c embedded/ai/ptrc_bitnet_engine.c \
    -Iembedded/ai \
    -mcpu=cortex-m0plus -mthumb -mfloat-abi=soft \
    -O2 -std=c11 -ffreestanding -Wall -Wextra -Werror \
    -o ptrc_bitnet_m0plus.o
```
