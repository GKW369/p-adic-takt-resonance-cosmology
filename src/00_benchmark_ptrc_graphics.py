# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Observer Windtunnel v4.6.0
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
# ==============================================================================

"""
Statistischer Benchmark fuer die pTRC 3D-Windkanal- & Grafik-Engine v4.5.0.
Misst ueber eine definierte Laufzeit (Standard: 30 Sekunden) Physik-Takte,
Full-HD-Renderzeiten (1920x1080), Kollisionsraten, Standardabweichung,
Median sowie P95/P99-Latenzen und erzeugt eine zitierfaehige Statistik.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import platform
import statistics
import sys
import tempfile
import time
from importlib import import_module
from pathlib import Path
from typing import Dict, List

from ptrc_light_universe import PTRC_GFX_OK, PTRC_MAX_ENGINES, PTRC_WIND_AGENTS

parity_mod = import_module("00_test_ptrc_graphics_parity")


def calc_stats(samples_ms: List[float]) -> Dict[str, float]:
    ordered = sorted(samples_ms)
    n = len(ordered)
    if n == 0:
        return {"mean": 0.0, "std": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "p95": 0.0, "p99": 0.0}

    mean_v = statistics.fmean(ordered)
    std_v = statistics.stdev(ordered) if n > 1 else 0.0
    med_v = statistics.median(ordered)
    p95_idx = min(n - 1, int(math.ceil(0.95 * n)) - 1)
    p99_idx = min(n - 1, int(math.ceil(0.99 * n)) - 1)

    return {
        "mean": round(mean_v, 3),
        "std": round(std_v, 3),
        "median": round(med_v, 3),
        "min": round(ordered[0], 3),
        "max": round(ordered[-1], 3),
        "p95": round(ordered[p95_idx], 3),
        "p99": round(ordered[p99_idx], 3),
    }


def run_benchmark(duration_sec: float, width: int, height: int, steps_per_frame: int) -> int:
    seed = 137210144
    rgb_buf = (ctypes.c_uint8 * (width * height * 3))()

    step_times_ms: List[float] = []
    render_times_ms: List[float] = []
    frame_times_ms: List[float] = []
    load_samples: List[int] = []
    zero_byte_violations = 0

    with tempfile.TemporaryDirectory() as tmp:
        lib = parity_mod.build_shared_lib(Path(tmp))
        ctx = parity_mod.CPtrcGfxCtx()
        assert lib.ptrc_gfx_init(ctypes.byref(ctx), seed) == PTRC_GFX_OK

        # Warmup (10 Frames)
        for _ in range(10):
            lib.ptrc_gfx_step_takt_adaptive(ctypes.byref(ctx))
            lib.ptrc_gfx_render_observer_rgb24(ctypes.byref(ctx), width, height, rgb_buf)

        # Zaehler nach Warmup sauber starten
        lib.ptrc_gfx_init(ctypes.byref(ctx), seed)
        t_start = time.perf_counter()

        while (time.perf_counter() - t_start) < duration_sec:
            tf0 = time.perf_counter()

            ts0 = time.perf_counter()
            for _ in range(steps_per_frame):
                lib.ptrc_gfx_step_takt_adaptive(ctypes.byref(ctx))
            ts1 = time.perf_counter()
            step_times_ms.append(((ts1 - ts0) * 1000.0) / steps_per_frame)

            tr0 = time.perf_counter()
            rc = lib.ptrc_gfx_render_observer_rgb24(ctypes.byref(ctx), width, height, rgb_buf)
            tr1 = time.perf_counter()
            if rc == PTRC_GFX_OK:
                render_times_ms.append((tr1 - tr0) * 1000.0)

            tf1 = time.perf_counter()
            frame_times_ms.append((tf1 - tf0) * 1000.0)
            load_samples.append(int(ctx.active_load))

            if b"\x00" in bytes(rgb_buf):
                zero_byte_violations += 1

        elapsed = time.perf_counter() - t_start
        total_takts = int(ctx.takt_counter - 1)
        total_collisions = int(ctx.deflection_count - 1)
        total_frames = len(frame_times_ms)
        lib.ptrc_gfx_wipe(ctypes.byref(ctx))

    step_stats = calc_stats(step_times_ms)
    render_stats = calc_stats(render_times_ms)
    frame_stats = calc_stats(frame_times_ms)

    avg_fps = total_frames / elapsed if elapsed > 0.0 else 0.0
    takts_per_sec = total_takts / elapsed if elapsed > 0.0 else 0.0
    collisions_per_sec = total_collisions / elapsed if elapsed > 0.0 else 0.0
    crystal_updates_per_sec = takts_per_sec * PTRC_WIND_AGENTS * 13

    print("=" * 78)
    print("pTRC 3D-WINDKANAL & GRAFIK-ENGINE v4.5.0 — STATISTISCHER BENCHMARK")
    print("=" * 78)
    print(f"System / CPU       : {platform.system()} {platform.machine()} ({os.cpu_count()} Logische Kerne)")
    print(f"Aufloesung         : {width} x {height} (Full-HD RGB24, 100% Integer, 0x00-frei)")
    print(f"Geometrie          : 32cm x 18cm x 8cm | {PTRC_WIND_AGENTS:,} Cluster (1+12 = {PTRC_WIND_AGENTS * 13:,} Kristalle)")
    print(f"Parallel-Engines   : {PTRC_MAX_ENGINES}x pTRC-Sektor-Engines | Takte/Frame: {steps_per_frame}")
    print(f"Messdauer          : {elapsed:.2f} s | Frames: {total_frames:,} | Takte: {total_takts:,}")
    print("-" * 78)
    print(f"Durchsatz Takte/s  : {takts_per_sec:,.2f} Takte/s")
    print(f"Durchsatz FPS      : {avg_fps:,.2f} FPS (Full-HD Software-Z-Buffer)")
    print(f"Kollisionen gesamt : {total_collisions:,} ({collisions_per_sec:,.0f} Interaktionen/s)")
    print(f"Kristall-Updates/s : {crystal_updates_per_sec:,.0f} Raumkristall-Berechnungen/s")
    print(f"Null-Byte-Fehler   : {zero_byte_violations} (in Z^3 \\ {{0}})")
    print("-" * 78)
    print("LATENZ-STATISTIK (in ms):")
    print(f"  1 Physik-Takt (60k Cluster) : Mean={step_stats['mean']} ms | Std={step_stats['std']} ms | Median={step_stats['median']} ms | P95={step_stats['p95']} ms | P99={step_stats['p99']} ms")
    print(f"  Full-HD Render (1+12 ZBuf)  : Mean={render_stats['mean']} ms | Std={render_stats['std']} ms | Median={render_stats['median']} ms | P95={render_stats['p95']} ms | P99={render_stats['p99']} ms")
    print(f"  Gesamt-Frame ({steps_per_frame}T + Render) : Mean={frame_stats['mean']} ms | Std={frame_stats['std']} ms | Median={frame_stats['median']} ms | P95={frame_stats['p95']} ms | P99={frame_stats['p99']} ms")
    print("=" * 78)

    report = {
        "version": "4.5.0",
        "cpu_cores": os.cpu_count(),
        "resolution": f"{width}x{height}",
        "agents_1_plus_12": PTRC_WIND_AGENTS,
        "total_crystals": PTRC_WIND_AGENTS * 13,
        "parallel_engines": PTRC_MAX_ENGINES,
        "elapsed_seconds": round(elapsed, 3),
        "total_frames": total_frames,
        "total_takts": total_takts,
        "total_collisions": total_collisions,
        "takts_per_sec": round(takts_per_sec, 2),
        "avg_fps": round(avg_fps, 2),
        "collisions_per_sec": round(collisions_per_sec, 0),
        "crystal_updates_per_sec": round(crystal_updates_per_sec, 0),
        "zero_byte_violations": zero_byte_violations,
        "latency_ms": {
            "physics_takt": step_stats,
            "full_hd_render": render_stats,
            "total_frame": frame_stats,
        },
    }

    out_path = Path(__file__).resolve().parent.parent / "ptrc_graphics_benchmark_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[OK] JSON-Report gespeichert unter: {out_path}")
    return 0 if zero_byte_violations == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="pTRC 3D-Windkanal & Grafik-Engine Benchmark")
    parser.add_argument("--seconds", type=float, default=30.0, help="Messdauer in Sekunden (Standard: 30)")
    parser.add_argument("--width", type=int, default=1920, help="Bildbreite (Standard: 1920)")
    parser.add_argument("--height", type=int, default=1080, help="Bildhoehe (Standard: 1080)")
    parser.add_argument("--steps", type=int, default=2, help="Physik-Takte pro Frame (Standard: 2)")
    args = parser.parse_args()
    return run_benchmark(args.seconds, args.width, args.height, args.steps)


if __name__ == "__main__":
    sys.exit(main())
