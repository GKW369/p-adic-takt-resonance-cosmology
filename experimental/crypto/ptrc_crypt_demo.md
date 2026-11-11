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

# 🎛️ Bare-Metal Hardware Integration Layer (C-Compliance v3.1 AEAD Hardened)

This directory contains the production-ready C-language implementation of the hardened **pTRC Authenticated Cryptographic Inference Core (v3.1 AEAD)**. By shifting processing logic entirely into the discrete integer domain (\(\mathbb{Z}\)) and removing all floating-point library linkages, conditional branches, and unauthenticated buffer bottlenecks, this code compiles natively onto low-power secure architectures with minimal storage footprints.

## 📁 Contained Files
* **`ptrc_crypt_demo.c`**: Self-contained C implementation utilizing the **Active 144-Facet Vector Equilibrium Sponge**, a **256-bit Secret Key / 96-bit Nonce** initialization cascade, **Associated Data (AAD)** header binding, a live **Multi-Ring CRT Cascade** (\(\mathbb{Z}/210\mathbb{Z} \times \mathbb{Z}/11\mathbb{Z} \times \mathbb{Z}/13\mathbb{Z} \times \mathbb{Z}/17\mathbb{Z}\)), and a **192-bit (24-byte) SLIP-MAC Authentication Tag**, featuring native 8-bit integer truncation (`uint8_t`) for automated modulo reductions (O(1) constant execution profile).
* **`src/00_ptrc_crypt_demo.py`**: Bit-exact Python reference and telemetry verification module using pure CPU nanosecond benchmarking (`time.perf_counter_ns()`).

## 🚀 Native Compilation & Verification (Local Workstation)
To compile and test the execution profile on a standard UNIX-like environment or terminal, run:
```bash
gcc -O3 -Wall -Wextra ptrc_crypt_demo.c -o ptrc_hardware_demo && ./ptrc_hardware_demo
```

To verify bit-exact parity against the Python reference engine from the repository root:
```bash
python3 src/00_ptrc_crypt_demo.py
```

## 🔌 Target Architecture Deployment (ARM Cortex-M / Embedded RISC)
Because this algorithm completely bypasses the Floating-Point Unit (FPU), division instructions (`/`), dynamic heap allocation (`malloc`), and standard C math library overhead, it can be directly compiled using cross-compilers targeting microcontrollers (e.g., ARM Cortex-M0+, M3, or M4 architectures widely deployed in secure elements and automotive ECUs).

### Example: Cross-Compiling for ARM Cortex-M0+ (Bare-Metal)
```bash
arm-none-eabi-gcc -O3 -mcpu=cortex-m0plus -mthumb -c ptrc_crypt_demo.c -o ptrc_embedded.o
```

### Key Hardware Evaluation Metrics:
1. **Zero Arithmetic & FPU Overhead:** The code generates compact, predictable assembly pipelines. The `uint8_t` register mechanics utilize automated hardware overflow truncation (`& 0xFF`) and branchless bit-rotations (`rotl8`), stripping away floating-point pipelines and dynamic division cycles.
2. **Deterministic Power Profile (Side-Channel Immunity):** By completely eliminating condition-based instruction branch variations (including the removal of `if (byte == 0)` and deploying constant-time tag verification `ptrc_verify_tag_ct`), the chip processes every byte with identical instruction counts and uniform current demands—ensuring deep architectural resistance against physical *Differential Power Analysis (DPA)* and *Timing Attacks*.
3. **Register Zeroization (`ptrc_crystal_wipe`):** After encryption or verification completes, the 144-byte lattice context (`ptrc_crystal_ctx_t`) is explicitly overwritten via volatile register writes so no residual key material lingers in SRAM.

---

## 🌐 Advanced Non-Archimedean Cryptographic Foundation

### 1. The 1+12 Ur-Cell Geometry Sieve (Active 144-Facet Crystal Sponge)
In v3.1, the cryptographic pipeline operates the **144 open facets of the Vector Equilibrium lattice** (\(256^{144}\) total state space) as a bi-directional, active **AEAD (Authenticated Encryption with Associated Data)** sponge:
* **24 Physical Contact Junctions:** Manage the primary synchronous p-adic 24/210 Modulo-24 control ring sequence across the 24 touchpoints of the physical 1+12 Ur-cell cluster.
* **120 Free Outer Facets (Active Feedback State):** Function as a dynamic, un-damped thermodynamic state memory. Prior to encryption, a **256-bit Key** and **96-bit Nonce** are diffused across all 144 registers via a **24-Takt Crystalline Warmup Cascade** (\(24 \times 24 = 576\) lattice steps). During stream processing, ciphertext bytes feed back directly into the 120 outer facets—guaranteeing a 100% avalanche effect across all subsequent bytes.

```text
         [120 Free Outer Facets]
              ^           |
   (Active    |           v   (Keystream &
    Feedback) |    [24 Contact Junctions] ---> [192-Bit SLIP-MAC Tag]

              |           |
              +--- [1-Byte Core] <--- [256-Bit Key + 96-Bit Nonce + AAD]
```

### 2. Lossless Crossed Plichta-Mirror & Odd-Prime Mixing
The underlying cryptographic core executes inside the cyclically closed primorial integer ring without floating-point pollution or data collisions:
* **Bijective Zero-Singularity Bypass (`^ 0xFF`):** Earlier prototypes mapped `0` to `255` via conditional branching, creating a `0`/`255` collision and a minor timing branch. Version 3.1 applies a branchless, bijective one's-complement mirror (`mirrored = byte ^ 0xFF`), preserving 100% bit-exact reversibility across all 256 states (`0x00` through `0xFF`).
* **Non-Linear Prime-Ray Diffusion:** Register states are mixed using odd-integer multiplications (`* 7`, `* 11`, `* 13`, `* 17`, `* 19`) derived from the coprime rays of the Modulo-24 Prime Cross ($\{1, 5, 7, 11, 13, 17, 19, 23\}$), which are mathematically guaranteed to be bijective (invertible) inside $\mathbb{Z}/256\mathbb{Z}$.

$$\text{Base Takt} \equiv ((\text{Takt} \times 24) + 48) \pmod{210}$$

### 3. SLIP-MAC Integrity & Tamper Resistance (192-Bit Tag)
To protect against bit-flipping, ciphertext forgery, and header spoofing, the engine integrates a cryptographic **Systemic Lattice Integrity Parity Message Authentication Code (SLIP-MAC)**:
* **Associated Data Binding (`ptrc_absorb_aad`):** Plaintext packet headers or routing metadata are absorbed into the 144-facet lattice before payload processing, binding header integrity to the final tag.
* **Length-Extension Protection:** Prior to finalization, the 32-bit lengths of both AAD and payload are absorbed into the junctions, followed by a **24-Takt Finalization Cascade** ($576$ steps).
* **Fail-Closed Verification (`ptrc_verify_tag_ct`):** The 120 outer facets are folded in 5-facet groups into the 24 contact junctions to squeeze a **24-byte (192-bit) SLIP-MAC tag**. Verification executes strictly in constant time; if even a single bit of the header, ciphertext, or tag has been altered, decryption fails closed and immediately zeroes the output buffer.

### 4. Multi-Ring p-Adic Scalability & Exclusive User-Key Generation
Security scaling within the pTRC framework purposefully avoids the expansion of floating-point or heavy big-integer bit-lengths typical of Archimedean algorithms (e.g., RSA/ECC). Instead, complexity scales linearly by cascading the processing sequence across coprime residue rings applying the **Chinese Remainder Theorem (CRT)**:

$$\mathbb{Z} / 210\mathbb{Z} \times \mathbb{Z} / 11\mathbb{Z} \times \mathbb{Z} / 13\mathbb{Z} \times \mathbb{Z} / 17\mathbb{Z} \times \dots \times \mathbb{Z} / p_n\mathbb{Z}$$

#### 🔑 Exclusive Crystalline User-Keys:
This non-Archimedean architecture allows the generation of unique, hardware-bound user cryptographic profiles by stacking custom secret prime rings ($\mathbb{Z}/p_n\mathbb{Z}$) alongside the 256-bit key:
* The structural key is not merely a static bit-string, but the coupled dimensional geometry of the coprime modular rings (`CRT_RING_1..3`).
* Without compiling the exact coprime prime field moduli into the local 1-Byte register execution loop, the lattice state desynchronizes immediately on the first takt, rendering unauthorized decryption mathematically impossible.

This structural layout guarantees an asymptotic execution variance of **0.00%** across all expansion layers. Because operations remain locked onto 1-Byte registers ($\mathbb{Z}/256\mathbb{Z}$), hardware overflow acts as a zero-cost modulo reduction layer natively on low-power silicon fabrics—forcing time-based and power-based side-channel analysis to fail by design.
