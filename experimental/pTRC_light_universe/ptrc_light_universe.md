<!-- ==============================================================================
 # pTRC Framework - Discrete 1-Bit Integer Physics Engine
 # Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 # Licensed under the GNU Affero General Public License v3 (AGPLv3).
 # ============================================================================== -->

# 🌌 pTRC Light Universe Engine (`ptrc_light_universe.md`)
**A Dual-Meaning Architecture: "Light" as in Speed of Light ($c = 1$) & "Light" as in Lightweight Silicon Execution**

> *"If a skeptic calls 'Light Universe' presumptuous, it strictly refers to a lightweight, zero-float integer runtime. If an observer looks closer at $c = 1$ quantized wave propagation, it models light itself."*

---

## 🧠 Core Architectural Paradigm

The **pTRC Light Universe Engine** (`ptrc_light_universe_video.c`) unifies spatial memory, discrete physics, and real-time 1080p visualization inside a decentralized **1+12 Closest-Packed Space Crystal Lattice** (Cuboctahedral / FCC packing of 144-facet cells):

1. **Zero RGB Storage in Space (Quantized Wave Physics):**
   * Spatial crystals do not store red, green, or blue pixel values. Instead, each cell holds a discrete **Wave Frequency (`wave_freq`, $0\dots255$)** and **Wave Amplitude (`wave_amp`, $0\dots255$)** alongside its 1-byte core state (`1..81` stable elements, `82..145` DNA/observer clusters) and 120 decentralized memory facets (`outer_facets[120]`).
   * **Observer-Only Retina Transduction:** Color (`RGB`) exists solely at the moment of observation—transduced on the fly when quantized frequency and amplitude intersect the observer's viewport.
2. **Speed-of-Light Propagation ($c = 1\text{ Cell / Takt}$):**
   * Every discrete takt advances wave packets by exactly one lattice unit across the 12 neighbor vectors of the 1+12 Ur-cell.
   * An $O(1)$ **3D Spatial Hash Grid** (`hash_3d_cell`) resolves true neighbor-to-neighbor wave superposition and lateral **Love/Cohesion Resonance (`love_cohesion`)** without $8\times16$ modulo tiling artifacts.
3. **Selective 137-Takt Observer Plane & 120 FPS Transposition Governor:**
   * **Continuous Background Physics:** All 1-takt interactions run continuously across the entire lattice in L1 cache.
   * **Dynamic 120 FPS Transposition:** Measured via monotonic nanosecond telemetry (`clock_gettime`), the observer render plane targets **120 FPS (`8,333,333 ns` frame budget)**. On constrained hardware (such as mobile ARM SoCs), the engine dynamically transposes its facet rasterization stride (`1..4`) and sampling divisor (`137 -> 68 -> 34 -> 17`) using pure integer bit-shifts (`>> 1`) to sustain smooth 120 FPS playback without interrupting the underlying $c = 1$ physics clock.

---

## 🚀 Compilation & Execution (Mobile ARM / Linux Workstation)

```bash
# Compile with native architecture optimizations (tested on Samsung Galaxy S21 FE / ARM Cortex-A77)
gcc -O3 -march=native -Wall -Wextra ptrc_light_universe_video.c -o ptrc_light_vid

# Run simulation & pipe 1080p raw frames directly to FFmpeg
./ptrc_light_vid
```

### Live Telemetry HUD (Top-Left Overlay)
* **Row 1 (6 digits):** Monotonic Universe Takt Counter ($c = 1$ step/takt)
* **Row 2 (Left, 3 digits):** Real-time Observer Render Frame Rate (FPS, targeting 120+)
* **Row 2 (Right, 1 digit):** Active Transposition Stride (`1` = full 144-facet resolution, `2..4` = transposed macro-facets)
