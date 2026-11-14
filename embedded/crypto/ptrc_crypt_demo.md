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


# 🎛️ Bare-Metal Hardware Integration Layer (C-Compliance v3.2 Holographic AEAD)

This directory contains the modular, production-ready C-language implementation of the hardened **pTRC Authenticated Cryptographic Inference Core (v3.2)**. By shifting processing logic entirely into the discrete non-zero integer domain ($\mathbb{Z} \setminus \{0\}$) and removing all floating-point linkages, conditional branches, and unauthenticated buffer bottlenecks, this engine compiles natively onto low-power secure architectures.

## 📁 Contained Files
* **`ptrc_crystal.h` & `ptrc_crystal.c`**: Modular C core implementing the **Active 144-Facet Vector Equilibrium Sponge**, **4-Quadrant Crossed Plichta-Mirror reflection over `-1`**, the **137-Takt Fine-Structure Render Pulse**, a live **Multi-Ring CRT Cascade** ($\mathbb{Z}/210\mathbb{Z} \times \mathbb{Z}/11\mathbb{Z} \times \mathbb{Z}/13\mathbb{Z} \times \mathbb{Z}/17\mathbb{Z}$), and a **192-bit (24-byte) SLIP-MAC Authentication Tag**.
* **`ptrc_crypt_demo.c`**: Standalone verification binary demonstrating AEAD encryption, AAD header binding, and 1-bit tamper rejection.
* **`src/ptrc_crystal_aead.py` & `src/test_ptrc_crypt_parity.py`**: Bit-exact Python reference and automated cross-language parity audit.

## 🚀 Compilation & Verification
```bash
gcc -O3 -Wall -Wextra ptrc_crystal.c ptrc_crypt_demo.c -o ptrc_hardware_demo && ./ptrc_hardware_demo
python3 src/test_ptrc_crypt_parity.py
```

## 🔌 Target Architecture Deployment (ARM Cortex-M0+ Bare-Metal)
```bash
arm-none-eabi-gcc -O3 -mcpu=cortex-m0plus -mthumb -c ptrc_crystal.c -o ptrc_crystal.o
```

---

## 🌐 Non-Archimedean Cryptographic Architecture (v3.2)

### 1. Holographic 4-Quadrant Crossed Plichta-Mirror ($\mathbb{Z} \setminus \{0\}$)
Every incoming byte (`0..255`) is lifted into the signed, zero-free domain $\{-128 \dots -1, +1 \dots +128\}$, reflected directly across `-1` without passing through a zero-singularity, and rotated across the four quadrants of the Prime Cross (`q_rot = (quadrant_phase & 3) * 2`). This preserves 100% bijective reversibility while embedding holographic quadrant phase into every byte.

### 2. Macroscopic 137-Takt Fine-Structure Render Pulse
At every $137\text{th}$ takt (`takt_counter % 137 == 0`), the engine folds all 24 contact junctions into a global parity snapshot and reflects it holographically across all 120 outer facets. Because `137` is coprime to all internal rings (`210`, `24`, `11`, `13`, `17`), the minimum non-repeating period expands to **69,939,870 takts** inside single-byte registers while maintaining deterministic constant-time execution ($O(1)$).

### 3. Active 144-Facet Sponge & 192-Bit SLIP-MAC Integrity
* **Warmup & Finalization:** A 256-bit key and 96-bit nonce diffuse across all 144 facets over 576 steps ($24 \times 24$).
* **Fail-Closed Authentication:** Associated Data (AAD) and 32-bit lengths bind into the 24-byte SLIP-MAC tag. Constant-time tag verification (`ptrc_verify_tag_ct`) wipes the output buffer immediately upon any 1-bit discrepancy, followed by `volatile` register zeroization (`ptrc_crystal_wipe`).

 
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

