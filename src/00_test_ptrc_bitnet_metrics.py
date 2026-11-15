# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & AI Inference Engine
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
Cryptographic-Grade Statistical, Invariant & Throughput Metrics for pTRC BitNet AI v2.0.
File: src/00_test_ptrc_bitnet_metrics.py

Strictly pure integer (integer microseconds & takts/sec), verifying:
1. (4+1) -> 4 -> 2 Hebbian convergence speed & 1,000-takt online resonance stability
2. Strict Z \\ {0} domain integrity & 156 Wirminghaus invariant saturation bounds
3. 144-facet sponge resonance dispersion across multiple 137-takt mirror pulses
4. Native C11 vs. Python integer inference throughput (takts/sec & us/inference)
"""

from __future__ import annotations

import ctypes
import sys
import time

from ptrc_bitnet_engine import (
    PTRC_AI_FACETS,
    PTRC_AI_INVARIANT_156,
    PTRC_AI_TAKT_137,
    PtrcBitNetContext,
    PtrcBitNetLayer,
    _CLayer,
    _CSpongeCtx,
    load_c_bitnet_library,
)


def _get_crystal_xor_dataset() -> tuple[list[list[int]], list[list[int]], list[int], list[int]]:
    patterns = [
        list((-1, -1, -1, -1, 1)),
        list((-1, 1, -1, 1, 1)),
        list((1, -1, 1, -1, 1)),
        list((1, 1, 1, 1, 1)),
    ]
    targets = [
        list((-1, 1)),
        list((1, -1)),
        list((1, -1)),
        list((-1, 1)),
    ]
    hidden_weights = [val for row in patterns for val in row]
    out_weights = list((1, -1, 1, -1, -1, 1, -1, 1))
    return patterns, targets, hidden_weights, out_weights


def audit_convergence_and_stability() -> int:
    ctx = PtrcBitNetContext(seed=137210144)
    patterns, targets, hidden_weights, out_weights = _get_crystal_xor_dataset()
    hidden_layer = PtrcBitNetLayer(in_dim=5, out_dim=4, weights_z_no_zero=hidden_weights, takt_threshold=3)
    out_layer = PtrcBitNetLayer(in_dim=4, out_dim=2, weights_z_no_zero=out_weights, takt_threshold=0)

    converged_epoch = 0
    for epoch in range(1, 25):
        err = 0
        for pat, tgt in zip(patterns, targets):
            hidden_act, _ = hidden_layer.forward(ctx, pat)
            err += out_layer.hebbian_step(ctx, hidden_act, tgt, plasticity_gain=16)
        if err == 0:
            converged_epoch = epoch
            break

    assert converged_epoch > 0, "Hebbian plasticity failed to converge within 24 epochs!"

    # Verify 1,000 continuous takts across seven 137-takt mirror sync pulses with zero drift
    mismatches = 0
    for takt in range(1000):
        idx = takt & 3
        hidden_act, _ = hidden_layer.forward(ctx, patterns[idx])
        out, _ = out_layer.forward(ctx, hidden_act)
        if out != targets[idx]:
            mismatches += 1
        assert all(v != 0 for v in ctx.sponge), f"Zero state detected in sponge at takt {takt}!"

    assert mismatches == 0, f"Post-convergence drift detected ({mismatches} mismatches over 1,000 takts)!"
    print(f" + [METRIC 1] Hebbian Convergence : Epoch {converged_epoch} | 1,000-Takt Drift: 0 errors")
    return converged_epoch



def audit_invariant_156_and_resonance() -> None:
    ctx = PtrcBitNetContext(seed=210144137)
    weights = [1 if ((i * 7 + 3) % 3) != 0 else -1 for i in range(16 * 8)]
    layer = PtrcBitNetLayer(in_dim=16, out_dim=8, weights_z_no_zero=weights, takt_threshold=0)

    inp_a = [1 if (i & 1) == 0 else -1 for i in range(16)]
    inp_b = [-1 if (i & 1) == 0 else 1 for i in range(16)]
    tgt_a = list((1, -1, 1, -1, 1, -1, 1, -1))
    tgt_b = list((-1, 1, -1, 1, -1, 1, -1, 1))

    max_acc_seen = 0
    min_acc_seen = 0
    sync_pulses = 0

    for step in range(PTRC_AI_TAKT_137 * 4):
        if (ctx.takt_counter % PTRC_AI_TAKT_137) == 0:
            sync_pulses += 1
        if (step & 1) == 0:
            layer.hebbian_step(ctx, inp_a, tgt_a, plasticity_gain=8)
        else:
            layer.hebbian_step(ctx, inp_b, tgt_b, plasticity_gain=8)

        for row in layer.plasticity_acc:
            for acc in row:
                assert acc != 0, "Zero value violated Z \\ {0} in plasticity_acc!"
                if acc > max_acc_seen:
                    max_acc_seen = acc
                if acc < min_acc_seen:
                    min_acc_seen = acc

    assert max_acc_seen <= PTRC_AI_INVARIANT_156, f"Exceeded +156 invariant limit: {max_acc_seen}"
    assert min_acc_seen >= -PTRC_AI_INVARIANT_156, f"Exceeded -156 invariant limit: {min_acc_seen}"

    unique_facet_states = len(set(ctx.sponge))
    assert unique_facet_states >= 16, f"Low sponge resonance diversity: {unique_facet_states}"
    print(
        f" + [METRIC 2] 156-Limit Bounds    : [{min_acc_seen}, +{max_acc_seen}] | "
        f"137-Pulses: {sync_pulses} | Active Sponge States: {unique_facet_states}/{PTRC_AI_FACETS}"
    )


def benchmark_throughput() -> None:
    in_dim = 64
    out_dim = 32
    weights = [1 if ((i * 13 + 5) & 1) == 0 else -1 for i in range(in_dim * out_dim)]
    inp = [1 if ((i * 3 + 1) & 1) == 0 else -1 for i in range(in_dim)]
    iters = 5000

    py_ctx = PtrcBitNetContext(seed=137210144)
    py_layer = PtrcBitNetLayer(in_dim=in_dim, out_dim=out_dim, weights_z_no_zero=weights, takt_threshold=0)

    t0 = time.perf_counter_ns()
    for _ in range(iters):
        py_layer.forward(py_ctx, inp)
    t1 = time.perf_counter_ns()

    py_us = (t1 - t0) // 1000
    py_tps = (iters * 1_000_000) // (py_us if py_us > 0 else 1)
    print(f" + [METRIC 3] Python 1-Bit Engine : {iters} takts (64x32) in {py_us} us (~{py_tps} takts/sec)")

    lib = load_c_bitnet_library()
    if lib is not None:
        c_ctx = _CSpongeCtx()
        lib.ptrc_bitnet_ctx_init(ctypes.byref(c_ctx), 137210144)
        c_layer = _CLayer()
        c_w = (ctypes.c_int8 * len(weights))(*weights)
        lib.ptrc_bitnet_layer_init(ctypes.byref(c_layer), in_dim, out_dim, c_w, 0)
        c_in = (ctypes.c_int8 * in_dim)(*inp)
        c_out = (ctypes.c_int8 * out_dim)()
        c_scores = (ctypes.c_int32 * out_dim)()

        c_iters = 50000
        ct0 = time.perf_counter_ns()
        for _ in range(c_iters):
            lib.ptrc_bitnet_forward(ctypes.byref(c_ctx), ctypes.byref(c_layer), c_in, c_out, c_scores)
        ct1 = time.perf_counter_ns()

        c_us = (ct1 - ct0) // 1000
        c_tps = (c_iters * 1_000_000) // (c_us if c_us > 0 else 1)
        print(
            f" + [METRIC 4] Native C11 Engine   : {c_iters} takts (64x32) in {c_us} us "
            f"(~{c_tps} takts/sec | Context: {ctypes.sizeof(c_ctx)}B SRAM)"
        )
        lib.ptrc_bitnet_wipe(ctypes.byref(c_ctx))
    else:
        print(" + [METRIC 4] Native C11 Engine   : Skipped (build via CMake/gcc to benchmark libptrc_bitnet.so)")


def main() -> None:
    print("===============================================================================")
    print("  pTRC BITNET AI v2.0 — STATISTICAL, INVARIANT & THROUGHPUT METRICS AUDIT")
    print("===============================================================================")
    audit_convergence_and_stability()
    audit_invariant_156_and_resonance()
    benchmark_throughput()
    print("-------------------------------------------------------------------------------")
    print("  ALL AI BITNET v2.0 METRICS & INVARIANTS VERIFIED (100% PURE INTEGER).")
    print("===============================================================================")


if __name__ == "__main__":
    main()
    sys.exit(0)
