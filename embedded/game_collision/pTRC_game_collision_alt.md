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

# pTRC 3D Crystal Collision & Particle Engine (Zero-Float C-Core)

## Overview
This module implements a high-speed, deterministic 3D collision detection, fluid-cascade, and rendering engine written in pure C (`C99`). By replacing traditional Cartesian 3D voxel grids (`[x][y][z]`) with a flat **144-facet vector equilibrium register** (`24 contact junctions + 120 free outer facets`), the engine eliminates anisotropic diagonal distortion and CPU memory cache misses.

## Key Architectural Features
* **Zero-Free Bipolar State Space (`-1`, `+1`, `+3`):** Eliminates the arithmetic zero singularity (`0`) completely. Free channels are encoded as `-1`, primary laminar flows as `+1`, and deflected cascade vortices as `+3`.
* **Constant-Time Lookup ($O(1)$):** Collision checks and directional deflections execute directly inside the CPU L1 cache without nested spatial loops or floating-point instructions (`FPU bypass`).
* **Integer 3D Retina Projection & Depth Fog:** Projects up to 25,000 active 3D particles onto a 1080p viewport using fixed-point integer scaling (`SCALE = 1000`, `INVARIANT_LIMIT = 156`), full 360-degree Modulo-24 axis rotation, additive 5×5 crystal shading, and integer Z-depth brightness attenuation (`depth_shade`).
* **Direct FFmpeg Raw-RGB Pipe:** Streams uncompressed 1080p RGB frames directly from memory into FFmpeg without intermediate disk I/O overhead.

## Contained Files
1. **`ptrc_fluid_crystal_3d.c`**: Headless 10,000-particle physics and 3D cascade collision benchmark.
2. **`ptrc_crystal_live_3d.c`**: Real-time ASCII/Terminal 3D visualizer with automatic viewport scaling (`ioctl`).
3. **`ptrc_crystal_video_1080p.c`**: Full-HD (`1920x1080` @ 60 FPS) zero-float 3D video synthesis engine with additive glow shader and Z-depth attenuation via FFmpeg pipe.

## Verified Hardware Benchmarks
Tested on ARM Cortex-A77 (Samsung Galaxy S21 FE / Termux, single-thread `-O3`):
* **10,000 Particles (Bipolar Collision Only):** `62 µs` per takt (~`15,946 FPS`)
* **10,000 Particles (Full 3D Cascade & Deflection):** `98 µs` per takt (~`10,178 FPS`)
* **10,000 Particles (3D Cascade + Live Terminal Retina Projection):** `933 µs` per frame (~`1,071 FPS`)
* **25,000 Particles (Full 1080p 3D Rotation + Additive Shader + Depth Fog):** `2,085 µs` per frame (~`479 FPS`)

---

## Compilation & Execution Guide

### Prerequisites
* **Linux / Ubuntu (Desktop & Laptop):** `sudo apt update && sudo apt install build-essential ffmpeg`
* **Android (Termux):** `pkg update && pkg install clang ffmpeg`

### 1. Linux / Ubuntu (Standard Workstation)
Navigate to `embedded/game_collision` and compile/run any of the three modules:

```bash
# 1. Headless 10,000-Particle Benchmark
gcc -O3 ptrc_fluid_crystal_3d.c -o ptrc_fluid3d && ./ptrc_fluid3d

# 2. Live 3D Terminal Visualizer (Auto-scales to terminal/TV size)
gcc -O3 ptrc_crystal_live_3d.c -o ptrc_live3d && ./ptrc_live3d

# 3. Full-HD 1080p @ 60 FPS Video Synthesis (Outputs 'ptrc_crystal_3d_1080p.mp4')
gcc -O3 ptrc_crystal_video_1080p.c -o ptrc_vid && ./ptrc_vid
```

### 2. Android / Termux (Mobile Execution)
Because Android blocks binary execution inside `/storage/emulated/0/Download` (`noexec` mount flag), compile the binaries into your Termux home directory (`~`):

```bash
# 1. Headless Benchmark
gcc -O3 ptrc_fluid_crystal_3d.c -o ~/ptrc_fluid3d && ~/ptrc_fluid3d

# 2. Live 3D Terminal Visualizer
gcc -O3 ptrc_crystal_live_3d.c -o ~/ptrc_live3d && ~/ptrc_live3d

# 3. Full-HD 1080p Video Export directly into Android Downloads
gcc -O3 ptrc_crystal_video_1080p.c -o ~/ptrc_vid && cd /storage/emulated/0/Download && ~/ptrc_vid
```
