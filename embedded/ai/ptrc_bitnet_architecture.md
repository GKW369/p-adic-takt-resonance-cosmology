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

# pTRC Resonant BitNet AI Engine v2.0 — Architecture & Bare-Metal Guide

## 1. Overview
The **pTRC Resonant BitNet AI Engine v2.0** replaces floating-point matrix multiplications (`GEMM`) and backpropagation with **1-bit bipolar (`{-1, +1}`) XNOR + POPCOUNT inference** and **discrete integer Hebbian plasticity** operating strictly on the $\mathbb{Z} \setminus \{0\}$ 1+12 space-crystal lattice.

- **Zero Floating-Point & Zero Trigonometry:** No `float`, `double`, `sin`, `cos`, or FPU instructions anywhere in the inference or training pipeline.
- **144-Facet Crystalline Sponge & 137-Takt Pulse:** Each forward step couples 64-bit packed bitplanes with a 144-facet resonance state modulated by the **24-Clock Discrete Quadrance Ring** ($u^2 + v^2 = 1000^2$) and synchronized every **137 takts** via bitwise reflection across `-1` (`~x`).
- **Online Integer Hebbian Plasticity:** Weights adapt on-chip using integer accumulators bounded by the **156 Wirminghaus Invariant Limit** (`PTRC_AI_INVARIANT_156 = 156`), eliminating gradient tape memory overhead.
- **Bare-Metal Silicon Ready:** Static stack context (`sizeof(ptrc_bitnet_ctx_t)` = **592 bytes**), zero `malloc`, deterministic `O(1)` execution, and volatile SRAM scrubbing (`ptrc_bitnet_wipe`).

---

## 2. Quick Start (CMake + Python/C11 Parity)

### 1. Build C11 Shared Library & Standalone `00_` Demo
```bash
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

### 2. Run Standalone C11 Demo (`00_ptrc_bitnet_demo`)
```bash
./build/00_ptrc_bitnet_demo
```

### 3. Run Interactive Python/C11 Terminal Demo (`00_ptrc_bitnet_demo.py`)
```bash
PYTHONPATH=src python3 src/00_ptrc_bitnet_demo.py
```

### 4. Run Bit-Parity & Zero-Float Audit Suite
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
