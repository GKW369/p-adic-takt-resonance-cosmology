<!--
==============================================================================
pTRC Framework - Discrete 1-Bit Integer Physics Engine
Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.

LICENSE & LIABILITY NOTICE:
Academic, non-commercial research and evaluation is permitted strictly under 
the terms of the GNU Affero General Public License version 3 (AGPLv3).
For the complete, unedited license text see: https://gnu.org

ANY COMMERCIAL DEPLOYMENT, production utilization, or proprietary enterprise 
integration requires a separate, individually negotiated commercial infrastructure 
waiver issued directly by the author.

WARRANTY DISCLAIMER: THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE SYSTEMATICALLY DISCLAIMED.
==============================================================================
-->
# Security Policy & Architectural Symmetrical Boundaries

## 1. Definition of Architectural Vulnerabilities
Within the pTRC framework, security is defined as the maintenance of absolute integer bit-invariance. This system operates strictly within the boundaries of discrete arithmetic (\(\mathbb{Z}\)). 

The intentional or accidental introduction of continuous floating-point fields (\(\mathbb{R}\)), decimal variables (`floats`), or transcendental approximations (π, e) is classified as **Phase Dissipation and Analog Leakage**. 

Any modification or pull request that breaks the modulo-24/210 invariant lattice rules will be discarded immediately at the compiler pipeline layer.

## ⚖️ 2. Commercial Compliance & Warranty Void
While the open-source evaluation branch (AGPLv3) allows academic modifications, notice is hereby given to all corporate entities:
*   Any introduction of floating-point arithmetic or continuous physics models into the core engine components instantly violates the structural integrity of the pTRC framework.
*   Modifications causing **Analog Leakage** will immediately void all commercial support agreements, architectural consulting certificates, and corporate licensing claims.

## 📧 3. Reporting Process
If you identify an calculation boundary bypass or a potential division-by-zero vulnerability that evades the rigid integer safety floors (such as the minimum 1-pixel constraint), do **NOT** open a public GitHub Issue. 

# 🛡️ Security Policy & Architectural Integrity (v3.3)

## 1. Supported Versions & Cryptographic Baseline
Security updates, Zero-Float hygiene audits, and cross-language bit-parity verifications apply strictly to the current **v3.3** architecture:

| Module / Component | Version | Status | Verification Gate |
| :--- | :--- | :--- | :--- |
| **144-Facet Crystalline AEAD & KDF** (`ptrc_crystal.c/.h`, `ptrc_crystal_aead.py`) | `v3.3.x` | **Active** | `src/test_ptrc_crypt_parity.py` & `src/test_ptrc_crypt_metrics.py` |
| **Prime-Lattice Interference Sieve AI** (`ptrc_interference_nn.c/.py`) | `v3.3.x` | **Active** | `src/test_ptrc_ai_parity.py` |
| **Core Simulation Modules** (`src/*.py`) | `v2.x / v3.x` | **Active** | `src/00_ptrc_first_principles_engine.py` |
| Legacy Unauthenticated Stream Prototypes | `< v3.0` | **Deprecated** | Superseded by 192-bit SLIP-MAC AEAD |

---

## 2. Core Security Invariants (Mandatory Compliance)
Any vulnerability or pull request violating the following systemic invariants is classified as a critical architectural defect:

1. **Zero Analog Leakage (Strict $\mathbb{Z} \setminus \{0\}$ Domain):**
   * Floating-point data types (`float`, `double`) and standard floating-point division (`/`) are strictly prohibited across all cryptographic, AI, and physics execution paths.
   * All transformations must execute via deterministic integer arithmetic, fixed-point scaling (`SCALE = 1000` with floor division `//`), or native 1-byte register truncation (`uint8_t` / `& 0xFF`).
2. **Side-Channel & Timing Immunity ($O(1)$ Constant Execution):**
   * Cryptographic data paths must remain strictly **branchless**—no secret-dependent `if`/`else` conditions or table lookups indexed by unmasked secrets.
   * Authentication tags (**192-bit SLIP-MAC**) must be verified exclusively via constant-time bitwise accumulation (`diff |= a[i] ^ b[i]`), failing closed with immediate output buffer zeroization on mismatch.
   * Sensitive 144-facet lattice states must be scrubbed post-execution via `volatile` register writes (`ptrc_crystal_wipe`).
3. **Nonce Uniqueness & Key Derivation Discipline (`pTRC-KDF`):**
   * Never reuse an identical `(256-bit key, 96-bit nonce)` pair across two distinct messages.
   * Always derive fresh session keys and nonces via `ptrc_kdf_derive` / `derive_key_and_nonce` using unique domain context strings or monotonic counters.
4. **Experimental Research Classification:**
   * The v3.3 Crystalline AEAD engine is an independent non-Archimedean cryptographic architecture intended for research, telemetry, and resource-constrained embedded prototyping. Production deployments in regulated sectors require independent external cryptanalytic review.

---

## 3. Reporting a Vulnerability
If you identify a side-channel leak, bit-parity discrepancy between C and Python, or an integer overflow vector:

* **Do not** disclose exploit payloads in public GitHub issues prior to coordination.
* **Contact the Author directly:** `g.wirminghaus@gmx.de` (Kurt Guido Wirminghaus).
* Please include reproduction steps, target architecture details (e.g., x86_64, ARM Cortex-M0+), and output from `src/test_ptrc_crypt_parity.py`.

Please report the mathematical anomaly privately to protect current commercial deployments:
📩 **g.wirminghaus@gmx.de**

---

*Document Classification: Academic Defense Protocol / Security & Compliance Matrix.*  
*Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.*
