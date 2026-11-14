<!-- ==============================================================================
 # pTRC Framework - Discrete 1-Bit Integer Physics Engine
 # Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 #
 # This program is free software: you can redistribute it and/or modify
 # it under the terms of the GNU Affero General Public License as published by
 # the Free Software Foundation, either version 3 of the License, or
 # (at your option) any later version.
 #
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 # GNU Affero General Public License for more details.
 #
 # You should have received a copy of the GNU Affero General Public License
 # along with this program (see the LICENSE file in the root directory).
 # If not, see <https://gnu.org>.
 # ============================================================================== -->

# 🎛️ Bare-Metal Hardware Integration Layer (C-Compliance v4.0 512-Bit Primorial AEAD)

This directory contains the modular, production-ready C-language implementation of the **pTRC Cryptographic Inference Core (v4.0)**. Operating strictly inside the discrete non-zero integer domain ($\mathbb{Z} \setminus \{0\}$) without floating-point linkages, lookup-table RAM overhead, or Mersenne primes, this module delivers **512-bit key strength** inside a ~180-byte stack footprint.

## 📁 Contained Files
* **`ptrc_crystal.h` & `ptrc_crystal.c`**: Modular C core implementing:
  1. **Zero-Table pTRC Primorial Macro-Cascade (`P15 = 614,889,782,588,491,410`)**: Decodes four 64-bit coprime Primorial-anchored ring moduli directly from the first 256 bits of the 512-bit key via Euclidean GCD locking (`ptrc_gcd64`), requiring zero lookup tables in Flash/RAM.
  2. **512-Bit `pTRC-KDF` (`ptrc_kdf_derive`)**: Derives 512-bit session keys and 128-bit nonces via a 576-step crystalline sponge cascade.
  3. **Holographic 4-Quadrant Crossed Plichta-Mirror & 137-Takt Pulse**: Bijective reflection across `-1` inside $\{-128 \dots -1, +1 \dots +128\}$ coupled with a global 137-takt synchronization pulse.
  4. **192-Bit SLIP-MAC AEAD**: Constant-time verification ($O(1)$) and `volatile` SRAM zeroization (`ptrc_crystal_wipe`).
* **`ptrc_crypt_demo.c` & `CMakeLists.txt`**: Standalone verification binary and CMake build configuration.
* **`src/ptrc_crystal_aead.py`, `src/test_ptrc_crypt_parity.py`, `src/test_ptrc_crypt_metrics.py`**: Bit-exact Python reference, cross-language parity audit, and Strict Avalanche Criterion (SAC) benchmark.

## 🚀 Compilation & Verification
```bash
cmake -B build && cmake --build build && ./build/ptrc_hardware_demo
python3 ../../src/test_ptrc_crypt_parity.py
python3 ../../src/test_ptrc_crypt_metrics.py
```

## 🔌 Target Architecture Deployment (ARM Cortex-M0+ Bare-Metal)
```bash
arm-none-eabi-gcc -O3 -mcpu=cortex-m0plus -mthumb -mfloat-abi=soft -c ptrc_crystal.c -o ptrc_crystal.o
```

