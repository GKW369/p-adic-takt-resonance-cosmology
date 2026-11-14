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

# Security & Cryptographic Disclosure Policy

## Scope & Supported Versions

The **pTRC Framework** (`p-adic-takt-resonance-cosmology`) implements experimental non-Archimedean integer arithmetic ($\mathbb{Z} \setminus \{0\}$) across discrete physics, Edge-AI, and the **v4.0 512-Bit Primorial AEAD & SLIP-MAC** cryptographic inference core (`embedded/crypto/` and `src/ptrc_crystal_aead.py`).

| Component / Version | Status | Support & Audit Level |
| :--- | :--- | :--- |
| **v4.0 (`main` branch)** — 512-Bit Primorial AEAD + `pTRC-KDF` + 192-Bit SLIP-MAC | **Active** | Full constant-time & cross-language parity audit |
| **v3.x (`main` branch)** — Holographic 4-Quadrant AEAD + 137-Takt Pulse | **Superseded** | Replaced by v4.0 Primorial Macro-Cascade |
| **v2.x and earlier** | **Unsupported** | Historical research prototypes only |

---

## Cryptographic Security Guarantees & Boundaries

1. **Zero-Float & Constant-Time Execution ($O(1)$):**
   All cryptographic state transitions execute exclusively in discrete integer registers (`int8_t` to `uint64_t`) without floating-point instructions, lookup tables in Flash/RAM, or secret-dependent memory indexing.
2. **Fail-Closed Authentication (`192-bit SLIP-MAC`):**
   `ptrc_aead_decrypt` verifies the 24-byte authentication tag in constant time (`ptrc_verify_tag_ct`) and immediately wipes output buffers upon any 1-bit modification to ciphertext, nonce, or Associated Data (AAD).
3. **Volatile Register Zeroization (`ptrc_crystal_wipe`):**
   Internal 144-facet sponge states and Primorial ring accumulators are erased via `volatile` pointer writes to prevent compiler dead-store elimination.
4. **Research Evaluation Notice:**
   This software is provided under **GNU AGPLv3** as independent scientific research. Before deploying any cryptographic primitive into safety-critical or regulated production systems, conduct an independent third-party cryptographic review and side-channel power/EM measurement on your target silicon.

---

## Reporting a Vulnerability or Cryptographic Finding

Please **do not** open public GitHub issues for suspected cryptographic weaknesses, timing leaks, buffer boundary issues, or tag-forgery vectors.

Instead, report findings privately via one of the following channels:

* **Direct Email:** `g.wirminghaus@gmx.de` (Subject: `[SECURITY / pTRC-Crypto] <Short Summary>`)
* **GitHub Private Vulnerability Reporting:** Use the **Security → Advisories → Report a vulnerability** tab in this repository.

### What to Include in Your Report
* Affected file(s) and line numbers (e.g., `embedded/crypto/ptrc_crystal.c` or `src/ptrc_crystal_aead.py`).
* Exact test vectors (hex-encoded 512-bit key, 128-bit nonce, AAD, plaintext/ciphertext, and 192-bit tag) reproducing the issue.
* Target compiler, optimization flags, and CPU architecture (e.g., `arm-none-eabi-gcc -O3 -mcpu=cortex-m0plus`).

### Response Timeline
* **Acknowledgment:** Within **72 hours** of receipt.
* **Initial Triage & Reproducibility Assessment:** Within **7 days**.
* **Patch & Coordinated Disclosure:** Upon verification via `src/00_test_ptrc_crypt_parity.py` and `src/00_test_ptrc_crypt_metrics.py`, a fix and credit note will be published on `main`.

---

## Automated Verification Commands

Before submitting a security patch or pull request affecting cryptographic code, verify that all automated gates pass:

```bash
cmake -B build -S . && cmake --build build
./build/ptrc_hardware_demo
python3 src/00_test_ptrc_crypt_parity.py
python3 src/00_test_ptrc_crypt_metrics.py
python3 src/00_ptrc_crypt_demo.py
```
