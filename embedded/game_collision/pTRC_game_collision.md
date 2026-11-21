# pTRC Game-Collision Engine (`ptrc_game_collision`) — `v4.6.0`

**Deterministic 1-Bit Integer Physics, Zero-Tunneling Guarantee & Lockstep Multiplayer Verification**  
Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.  
License: GNU Affero General Public License v3.0 (AGPL-3.0).

---

## 1. Motivation: Deterministic Collision Detection for Real-Time Simulation

Conventional game physics engines rely on IEEE-754 floating-point arithmetic (`float`/`double`), continuous time deltas (`dt`), and axis-aligned octrees. In high-density or networked environments, this introduces three fundamental failure modes:
1. **Geometric Tunneling:** High-velocity projectiles or particles pass through thin boundaries between discrete integration steps.
2. **Multiplayer Desynchronization:** Differences in CPU instruction sets, FMA contractions, or compiler optimizations cause floating-point state drift across clients.
3. **Cubic Lattice Artifacts:** Axis-aligned spatial grids introduce directional bias and diagonal aliasing.

**`ptrc_game_collision` resolves these limitations architecturally on top of `ptrc_light_universe` v4.6.0:**
* **Zero-Tunneling Invariant (`tunneling_escapes == 0`):** All `60,000` dynamic bodies (`780,000` space crystals) evolve on a discrete, zero-free `1+12` cuboctahedral lattice (\(\mathbb{Z}^3 \setminus \{0\}\)). No entity can skip a lattice site or penetrate a solid boundary without triggering a deterministic deflection.
* **100% Bit-Identical Lockstep (`lockstep_state_hash`):** After every physics tick, a deterministic 64-bit Primorial-FNV checksum is computed over all `60,000` spatial coordinates and `1-byte` state registers. Independent simulation instances produce bit-identical hashes across arbitrary tick horizons.
* **Real-Time Contact Classification:** Separates every tick's interactions into **rigid-body impacts** (rotating 3D crystal pyramid and centered 3D crystal sphere) and **particle-to-particle collisions** (mediated across `65,536` FCC occupancy slots and `144`-facet anisotropic scattering).

---

## 2. Core C11 API (`ptrc_game_collision.h`)

| Function | Description |
| :--- | :--- |
| `ptrc_gc_init(world, seed)` | Initializes the 3D windtunnel domain, `60,000` `1+12` clusters, and the initial 64-bit lockstep hash. |
| `ptrc_gc_step_tick(world)` | Advances the simulation by one deterministic tick (via adaptive `1..8` sector engines), updates hit counters, and verifies `tunneling_escapes == 0`. |
| `ptrc_gc_compute_lockstep_hash(world)` | Computes the deterministic 64-bit state checksum across all active bodies. |
| `ptrc_gc_render_rgb24(world, w, h, out)` | Renders the observer perspective into `0x00`-free RGB24 (`1920 × 1080`). |

---

## 3. Verification & Live Telemetry Showcase

```bash
# 1. Execute C11 build, lockstep determinism & zero-tunneling audit
chmod +x embedded/game_collision/verify_ptrc_collision.sh
./embedded/game_collision/verify_ptrc_collision.sh

# 2. Launch Full-HD Game-Collision Live Showcase (with real-time hit counters & lockstep hash)
python3 src/00_ptrc_game_collision_live.py
```
