# Contributing to the pTRC Framework (CONTRIBUTING.md)

Welcome to the pTRC (p-Adic Takt-Resonance Cosmology) project. To maintain the architectural and physical integrity of this repository, all contributors must strictly adhere to the fundamental structural and physical rules established in this framework.

This project rejects the continuous real-number space continuum (\(\mathbb{R}^4\)) entirely and operates exclusively within the ring of discrete integers (\(\mathbb{Z}\)).

---

## 🚫 Immutable Code-Hygiene & Validation Rules

Every Pull Request (PR) is automatically audited by our GitHub Actions pipeline (`test_matrix.yml`) and a static code analyzer. Any violation of the rules below will result in an immediate, automated rejection of the PR.

### 1. Absolute Ban on Floating-Point Arithmetic (Zero-Float-Rule)
The core engine operates strictly on a whole-number hardware layer.
* **Banned:** Any use of the `float` data type, decimal point declarations (e.g., `137.0` or `0.5`), and continuous or transcendental constants (such as `math.pi` or `math.e`).
* **Required:** Explicit integer values and types (`int`, `np.int32`, `np.uint8`). Fractional relationships must be mapped via Fixed-Point Scaling.

### 2. Division Protection (Analog Leakage Prevention)
Standard analog division using the single slash operator (`/`) is strictly classified as an "Analog Leakage Exploit" and is banned from the active codebase because it forces Python to instantiate continuous fields in RAM.
* **Banned:** `X / Y`
* **Required:** Use the predefined Fixed-Point Scaling metric (`SCALE = 1000`). Always upscale the value in the numerator first, then apply strict integer floor division (`//`).
* **Example:** `result = (value * SCALE) // divisor`

### 3. Pure Integer Output Layer (No Decimal Formatting)
All terminal logs, outputs, and visualization steps must reflect the discrete ontology of the system.
* **Banned:** Printing log strings containing decimal dots, commas, or artificially split substrings designed to mimic continuous decimals.
* **Required:** Map display variables natively to discrete, unsharable sub-units (e.g., `"Milli-Units"`, `"Milli-Hubble-Units"`, `"Nanoseconds"`), and print the scaled integers directly.

### 4. Strict Deterministic Reversibility
* **Banned:** Continuous random sampling methods like `np.random.rand()` or time benchmarks tracking standard float seconds.
* **Required:** Deploy strict, integer-bounded pseudorandom generation via `np.random.randint()`. Time-tracking benchmarks must run exclusively via undivisible CPU nanoseconds using `time.time_ns()`.

---

## 📂 Repository Structure & Submission Boundaries

When submitting changes, ensure your modifications strictly respect our decoupled directory map without mixing methodologies:
* **`src/`:** Reserved exclusively for production-ready, 100% integer-compliant core simulation modules.
* **`experimental/`:** Advanced informational space research, non-linear parametric resonance, or open-system energy surplus calculations must remain isolated here. Never merge experimental open-system code into the stable `src/` core.

By opening a Pull Request, you certify that you have successfully validated your code locally using the master engine script (`python src/00_ptrc_first_principles_engine.py`) and agree to publish your contributions under the project's GPLv3 license.
