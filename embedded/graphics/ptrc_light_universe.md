# pTRC Light Universe — Discrete 1-Bit Integer Physics & Observer Graphics (`v4.6.0`)

**144-Facet Crystal Anisotropy, Supercompact 1+12 Space Lattice & Adaptive Multi-Engine Windtunnel**  
Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.  
License: GNU Affero General Public License v3.0 (AGPL-3.0).

---

## 1. Architectural Overview (`v4.6.0`)

`ptrc_light_universe` is a deterministic, pure-integer physics and observer-rendering engine implemented in **ISO C11** alongside a bit-identical **Python reference implementation**. The engine operates entirely without floating-point arithmetic (`float`/`double`), without dynamic heap allocation during runtime execution, and without zero-valued states (`0` / `0x00`).

* **Zero-Free Discrete Space (\(\mathbb{Z}^3 \setminus \{0\}\)):** All spatial coordinates, momentum vectors, and color/state bytes strictly exclude zero. Origin crossings are resolved deterministically via a crossed Plichta reflection (`-1 <-> +1`).
* **144-Facet Crystal Anisotropy:** The internal state memory comprises **144 facets** (`120` memory facets and `24` contact junctions). Every scattering event couples deterministically across the active 24-phase clock (`clock_phase_24`) and the 137-tick mirror pulse (`PTRC_GFX_TAKT_137`).
* **Supercompact 1+12 Space Lattice (Cuboctahedral / FCC Packing):** Lattice sites are constrained to even coordinate parity (`(x + y + z) & 1 == 0`) to eliminate orthogonal stepping and cubic Moiré interference. Each agent represents a cluster of **1 central crystal + 12 surrounding shell crystals** (`13` space crystals).
* **Hardware `int32` GPU Probing & CPU Fallback:** Upon initialization, the engine dynamically probes via `dlopen("libOpenCL.so.1")` for native hardware integer ALUs (`INT32-GPU`) and falls back seamlessly and bit-identically to `CPU-INT` when no OpenCL ICD is present.

---

## 2. 1-Byte State Register (`state_byte`, `1..255`)

| Bit Position | Mask | Function | Domain / Semantics |
| :--- | :--- | :--- | :--- |
| **Bit 7** | `0x80` | **Cohesion & Binding Anchor** (`cohesion_anchor`) | `0` = unbound, `1` = strongly bound cluster (preserves `1+12` neighborhood cohesion) |
| **Bits 6..5** | `0x60` | **Optical & Material Mode** (`optics_mode`) | `0` = Opaque, `1` = Translucent, `2` = Crystalline, `3` = Field-Coupled |
| **Bits 4..0** | `0x1F` | **Digital Wavelength** (`wavelength_id`) | `1..31` (Retinal color and momentum transposition) |

---

## 3. 3D Windtunnel Dimensions (`32 cm × 18 cm × 8 cm`)

| Component | Physical Dimensions | Zero-Free Lattice (\(\mathbb{Z}^3 \setminus \{0\}\)) | Physical Role |
| :--- | :--- | :--- | :--- |
| **Windtunnel Volume** | **32 cm × 18 cm × 8 cm** | `X ∈ [-960..+960]`, `Y ∈ [-540..+540]`, `Z ∈ [-240..+240]` | Laminar inflow at left boundary (`-X`), outflow & recirculation at right (`+X`) |
| **Fluid Molecule Agents** | **30,000 Clusters** | **1+12 = 13 crystals each** (`390,000` active crystals) | Momentum exchange across `65,536` FCC slots + `144`-facet anisotropic scattering |
| **Rotating 3D Pyramid** | **Height 9.0 cm, Base 6.4 cm** | Center `X = -320, Y = 0, Z = +55` (`3,288` sub-angular steps) | Positioned `0.9 cm` toward rear wall (`0.6 cm` front flow clearance), splitting primary inflow |
| **Rotating 3D Sphere** | **Ø 5.8 cm** (`R = 175`) | Center `X = +320, Y = -140, Z = +75` | Suspended `1.25 cm` toward rear wall (`2.3 cm` front flow clearance) with zero wall friction & balanced impact rate |

## 4. Verified Benchmark Statistics (`v4.6.0`, 60 s Continuous Run, Linux x86_64)

Measured using `src/00_benchmark_ptrc_graphics.py --seconds 60` at native **Full-HD resolution (`1920 × 1080`)**, **8 adaptive pTRC sector engines (`1..8` dynamic)**, and `30,000` `1+12` clusters (`390,000` space crystals, including `20,080` bound cohesive clusters):

| Metric | Measured Value (`v4.6.0`) |
| :--- | :--- |
| **Duration / Frames / Ticks** | `60.07 s` \| `511` Full-HD Frames \| `1,022` Physics Ticks |
| **Physics Tick Latency (30,000 Clusters)** | **Mean `2.372 ms`** \| Std `0.263 ms` \| Median `2.291 ms` \| P95 `2.846 ms` \| P99 `3.642 ms` |
| **Full-HD Software Z-Buffer (`1+12` Projection)** | **Mean `113.425 ms`** \| Std `3.565 ms` \| Median `113.283 ms` \| P95 `119.100 ms` \| P99 `126.723 ms` |
| **Total Frame Rate (`2 Ticks + Full-HD Render`)** | **`8.51 FPS`** (Mean `115.851 ms`, Median `117.881 ms`) |
| **Collision & Interaction Throughput** | **`21,522,758` Collisions** (`358,285` interactions/s) |
| **Crystal Node Updates per Second** | **`13,270,161` crystal computations/s** |
| **Zero-Byte Violations (`0x00` in \(\mathbb{Z}^3 \setminus \{0\}\))** | **`0` (100% zero-free & bit-identical C11 \(\leftrightarrow\) Python)** |

---

## 5. Adaptive Engine Scaling (`1..8`) & Event Horizon (`PTRC_RENDER_STALL`)

Each observer cluster is dynamically allocated the required number of parallel pTRC sector engines (`assigned_engines = 1..8`) based on local information density (`active_load`) and bound cohesive clusters (`bound_clusters`):

| Effective Load (`load + bound >> 7`) | Allocated pTRC Engines | Observer Interval | System State |
| :--- | :--- | :--- | :--- |
| `< 950` | `1` Engine | `137` Ticks | **Laminar / Minimal Load** (`PTRC_RENDER_READY`) |
| `950 .. 1349` | `2` Engines | `137` Ticks | **Moderate Compression** |
| `1350 .. 1899` | `4` Engines | `274` Ticks (`2 × 137`) | **Vortex Congestion / Local Time Dilation** |
| `>= 1900` (`load < 2600`) | `8` Engines (Maximum) | `548` Ticks (`4 × 137`) | **High-Density Cohesive Cluster** |
| `active_load >= 2600` | `8` Engines (Saturated) | `0` (Suspended) | **Event Horizon / Singularity** (`PTRC_RENDER_STALL`) |

---

## 6. Files & Quick Start

* `embedded/graphics/ptrc_light_universe.h` — C11 header & data structures (`ptrc_gfx_ctx_t`).
* `embedded/graphics/ptrc_light_universe.c` — C11 implementation (adaptive `1..8` engines, `int32` GPU probe, Z-buffer).
* `src/ptrc_light_universe.py` — Bit-identical Python reference implementation.
* `src/00_test_ptrc_graphics_parity.py` — Bit-parity & `0x00`-freedom audit (`C11 <-> Python`).
* `src/00_ptrc_live_viewer.py` — Interactive Full-HD live observer (`1920 × 1080`).
* `src/00_benchmark_ptrc_graphics.py` — Statistical long-duration benchmark (`ptrc_graphics_benchmark_report.json`).

```bash
./embedded/graphics/verify_ptrc_graphics.sh
python3 src/00_benchmark_ptrc_graphics.py --seconds 60
python3 src/00_ptrc_live_viewer.py
```
