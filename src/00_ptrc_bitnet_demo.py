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
File: src/00_ptrc_bitnet_demo.py
"""

from __future__ import annotations

import ctypes
import time

from ptrc_bitnet_engine import (
    PTRC_AI_DEFAULT_THRESH,
    PTRC_AI_FACETS,
    PTRC_AI_INVARIANT_156,
    PTRC_AI_OK,
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
    print("  pTRC RESONANT BITNET AI v2.0 — PRIME-RING RESONANCE & 1-BIT INFERENCE")
    print(f"  Axioms   : Z \\ {{0}} (No Zero) | {PTRC_AI_FACETS} Facets | Base {PTRC_AI_PRIMORIAL_210} | {PTRC_AI_TAKT_137}-Takt | {PTRC_AI_INVARIANT_156}-Limit")
    print("  Topology : (4+1) -> 4 -> 2 | Prime-Ring Resonance | XNOR + POPCOUNT")
    print("===============================================================================")

    ctx = PtrcBitNetContext(seed=137210144)
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

    hidden_layer = PtrcBitNetLayer(in_dim=5, out_dim=4, weights_z_no_zero=hidden_weights, takt_threshold=3)
    out_layer = PtrcBitNetLayer(
        in_dim=4, out_dim=2, weights_z_no_zero=out_weights, takt_threshold=PTRC_AI_DEFAULT_THRESH
    )

    t0 = time.perf_counter_ns()
    for epoch in range(1, 17):
        locked_patterns: list[int] = list()
        for pat, tgt in zip(patterns, targets):
            hidden_act, _ = hidden_layer.forward(ctx, pat)
            if out_layer.hebbian_step(ctx, hidden_act, tgt, plasticity_gain=16) == PTRC_AI_OK:
                locked_patterns.append(PTRC_AI_OK)
        locked_count = len(locked_patterns)
        print(f" + Training Takt-Epoch {epoch:02d} | Locked: {locked_count}/4 | Resonance Energy: {ctx.resonance_energy}")
        if locked_count == 4:
            break
    t1 = time.perf_counter_ns()

    print("-------------------------------------------------------------------------------")
    for pat, tgt in zip(patterns, targets):
        hidden_act, _ = hidden_layer.forward(ctx, pat)
        out, scores = out_layer.forward(ctx, hidden_act)
        status = "MATCH" if out == tgt else "DIFF"
        print(f" + Input {pat[:4]} -> Output {out} (Scores {scores}) | Target {tgt} [{status}]")

    lib = load_c_bitnet_library()
    if lib is not None:
        c_ctx = _CSpongeCtx()
        lib.ptrc_bitnet_ctx_init(ctypes.byref(c_ctx), 137210144)
        c_layer = _CLayer()
        c_w = (ctypes.c_int8 * len(out_weights))(*out_weights)
        lib.ptrc_bitnet_layer_init(ctypes.byref(c_layer), 4, 2, c_w, PTRC_AI_DEFAULT_THRESH)
        print(f" + C11 Native Kernel   : ACTIVE (sizeof(ctx)={ctypes.sizeof(c_ctx)} bytes, Zero malloc)")
        lib.ptrc_bitnet_wipe(ctypes.byref(c_ctx))
    else:
        print(" + C11 Native Kernel   : Build via 'cmake -B build -S . && cmake --build build'")

    elapsed_us = (t1 - t0) // 1000
    print(f" + Convergence Time    : {elapsed_us} us (Pure Integer Z \\ {{0}} Prime-Ring Resonance)")
    print("===============================================================================")


if __name__ == "__main__":
    main()
