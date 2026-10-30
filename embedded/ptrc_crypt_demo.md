<!-- ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics Engine
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program (see the LICENSE file in the root directory).
 * If not, see <https://gnu.org>.
 * ============================================================================== -->

# 🎛 Bare-Metal Hardware Integration Layer (C-Compliance)

This directory contains the production-ready C-language implementation of the pTRC cryptographic inference core. By shifting processing logic entirely into the discrete integer domain ($\mathbb{Z}$) and removing all floating-point library linkages, this code compiles natively onto low-power secure architectures with minimal storage footprints.

## 📄 Contained Files
* **`ptrc_crypt_demo.c`**: Self-contained C implementation utilizing the **Coprime Residue Symmetry (Modulo 210/24)**, featuring native 8-bit integer truncation for automated modulo reductions ($O(1)$ constant execution profile).

## 🚀 Native Compilation & Verification (Local Workstation)
To compile and test the execution profile on a standard UNIX-like environment or terminal, run:
```bash
gcc ptrc_crypt_demo.c -o ptrc_hardware_demo && ./ptrc_hardware_demo
```

## 🛠 Target Architecture Deployment (ARM Cortex-M / Embedded RISC)
Because this algorithm completely bypasses the Floating-Point Unit (FPU) and standard C library overhead, it can be directly compiled using cross-compilers targeting microcontrollers (e.g., ARM Cortex-M0+, M3, or M4 architectures widely deployed in secure elements and automotive ECUs).

### Example: Cross-Compiling for ARM Cortex-M0+ (Bare-Metal)
```bash
arm-none-eabi-gcc -O3 -mcpu=cortex-m0plus -mthumb -c ptrc_crypt_demo.c -o ptrc_embedded.o
```

### Key Hardware Evaluation Metrics:
1. **Zero Arithmetic Overhead:** The code generates compact, predictable assembly pipelines. The `uint8_t` register mechanics utilize automated hardware overflow truncation, completely stripping away dynamic division or modulo instruction cycles.
2. **Deterministic Power Profile:** By completely eliminating condition-based instruction branch variations, the chip processes data streams with uniform, non-fluctuating current demands—ensuring deep architectural resistance against physical Differential Power Analysis (DPA).
