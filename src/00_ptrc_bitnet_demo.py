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
Interactive Terminal Demonstration for pTRC Resonant BitNet AI Engine v2.0.
"""

from __future__ import annotations

import ctypes
import time

from ptrc_bitnet_engine import (
    PTRC_AI_FACETS,
    PTRC_AI_INVARIANT_156,
    PTRC_AI_PRIMORIAL_210,
    PTRC_AI_TAKT_137,
    PtrcBitNetContext,
    PtrcBitNetLayer,
    _CLayer,
    _CSpongeCtx,
    load_c_bitnet_library,
)


def main() -> None:
    print("===============================================================================")
    print("  pTRC RESONANT BITNET AI v2.0 — 1-BIT CRYSTALLINE INFERENCE & HEBBIAN LEARNING")
    print(f"  Axioms : Z \\ {{0}} (No Zero) | {PTRC_AI_FACETS} Facets | Base {PTRC_AI_PRIMORIAL_210} | {PTRC_AI_TAKT_137}-Takt | {PTRC_AI_INVARIANT_156}-Limit")
    print("  Kernel : 100% Zero-Float | XNOR + POPCOUNT Bitplanes | Online Integer Hebbian")
    print("===============================================================================")

    ctx = PtrcBitNetContext(seed=137210144)
    init_weights = [1, -1, 1, -1, -1, 1, -1, 1]
    layer = PtrcBitNetLayer(in_dim=4, out_dim=2, weights_z_no_zero=init_weights, takt_threshold=0)

    patterns = [
        [-1, -1, -1, -1],
        [-1, 1, -1, 1],
        [1, -1, 1, -1],
,
    ]
    targets = [
        [-1, 1],
        [1, -1],
        [1, -1],
        [-1, 1],
    ]

    t0 = time.perf_counter_ns()
    for epoch in range(1, 16):
        err = 0
        for pat, tgt in zip(patterns, targets):
            err += layer.hebbian_step(ctx, pat, tgt, plasticity_gain=4)
        print(f" + Training Takt-Epoch {epoch:02d} | Mismatches: {err} | Resonance Energy: {ctx.resonance_energy}")
        if err == 0:
            break
    t1 = time.perf_counter_ns()

    print("-------------------------------------------------------------------------------")
    for pat, tgt in zip(patterns, targets):
        out, scores = layer.forward(ctx, pat)
        status = "MATCH" if out == tgt else "DIFF"
        print(f" + Input {pat} -> Output {out} (Scores {scores}) | Target {tgt} [{status}]")

    lib = load_c_bitnet_library()
    if lib is not None:
        c_ctx = _CSpongeCtx()
        lib.ptrc_bitnet_ctx_init(ctypes.byref(c_ctx), 137210144)
        c_layer = _CLayer()
        c_w = (ctypes.c_int8 * len(init_weights))(*init_weights)
        lib.ptrc_bitnet_layer_init(ctypes.byref(c_layer), 4, 2, c_w, 0)
        print(f" + C11 Native Kernel   : ACTIVE (sizeof(ctx)={ctypes.sizeof(c_ctx)} bytes, Zero malloc)")
        lib.ptrc_bitnet_wipe(ctypes.byref(c_ctx))
    else:
        print(" + C11 Native Kernel   : Build via 'cmake -B build -S . && cmake --build build'")

    elapsed_us = (t1 - t0) // 1000
    print(f" + Convergence Time    : {elapsed_us} us (Pure Integer Z \\ {{0}} Arithmetic)")
    print("===============================================================================")


if __name__ == "__main__":
    main()
