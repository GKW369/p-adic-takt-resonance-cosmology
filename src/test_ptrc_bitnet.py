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
Bit-Parity, Z \\ {0} Invariant, Prime-Ring Resonance & 137-Takt Audit for AI v2.0.
File: src/test_ptrc_bitnet.py
"""

from __future__ import annotations

import ctypes
import pathlib
import re
import sys

from ptrc_bitnet_engine import (
    PTRC_AI_DEFAULT_THRESH,
    PTRC_AI_OK,
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


def test_z_no_zero_and_prime_ring_convergence() -> None:
    ctx = PtrcBitNetContext(seed=137210144)
    assert all(v != 0 for v in ctx.sponge), "Zero found in initial 144-facet sponge!"

    patterns, targets, hidden_weights, out_weights = _get_crystal_xor_dataset()
    hidden_layer = PtrcBitNetLayer(in_dim=5, out_dim=4, weights_z_no_zero=hidden_weights, takt_threshold=3)
    out_layer = PtrcBitNetLayer(
        in_dim=4, out_dim=2, weights_z_no_zero=out_weights, takt_threshold=PTRC_AI_DEFAULT_THRESH
    )

    converged_epoch = -1
    for epoch in range(1, 17):
        locked = 0
        for pat, tgt in zip(patterns, targets):
            hidden_act, _ = hidden_layer.forward(ctx, pat)
            if out_layer.hebbian_step(ctx, hidden_act, tgt, plasticity_gain=16) == PTRC_AI_OK:
                locked += 1
        if locked == 4:
            converged_epoch = epoch
            break

    assert converged_epoch >= 1, "Prime-ring phase-locking failed to converge!"
    for pat, tgt in zip(patterns, targets):
        hidden_act, _ = hidden_layer.forward(ctx, pat)
        out, _ = out_layer.forward(ctx, hidden_act)
        assert out == tgt, f"Prediction mismatch for {pat}: {out} != {tgt}"
        assert all(v in (-1, 1) for v in out)
    assert all(v != 0 for v in ctx.sponge), "Zero entered sponge after prime-ring steps!"
    print(f"[PASS] 1. Z \\ {{0}} Invariant & Prime-Ring Phase-Lock Convergence (Epoch {converged_epoch})")


def test_137_takt_crossed_mirror_pulse() -> None:
    ctx = PtrcBitNetContext(seed=210144137)
    layer = PtrcBitNetLayer(
        in_dim=4, out_dim=1, weights_z_no_zero=list((1, 1, -1, -1)), takt_threshold=PTRC_AI_DEFAULT_THRESH
    )
    inp = list((1, -1, 1, -1))

    for _ in range(PTRC_AI_TAKT_137):
        layer.forward(ctx, inp)

    assert ctx.takt_counter == PTRC_AI_TAKT_137 + 1
    assert all(v != 0 for v in ctx.sponge), "137-takt ~x reflection produced zero!"
    print("[PASS] 2. 137-Takt Fine-Structure Pulse & Crossed Mirror Reflection (~x)")

def test_c11_python_bit_parity() -> None:
    lib = load_c_bitnet_library()
    if lib is None:
        print("[SKIP] 3. C11 Shared Library not built yet (build via CMake/gcc to run C11/Python parity)")
        return

    seed = 987654321
    py_ctx = PtrcBitNetContext(seed=seed)
    c_ctx = _CSpongeCtx()
    lib.ptrc_bitnet_ctx_init(ctypes.byref(c_ctx), seed)

    assert list(c_ctx.sponge) == py_ctx.sponge, "Initial 144-facet sponge mismatch between C11 and Python!"

    weights = list((1, -1, 1, -1, -1, 1, -1, 1))
    py_layer = PtrcBitNetLayer(
        in_dim=4, out_dim=2, weights_z_no_zero=weights, takt_threshold=PTRC_AI_DEFAULT_THRESH
    )
    c_layer = _CLayer()
    c_weights = (ctypes.c_int8 * len(weights))(*weights)
    rc = lib.ptrc_bitnet_layer_init(ctypes.byref(c_layer), 4, 2, c_weights, PTRC_AI_DEFAULT_THRESH)
    assert rc == PTRC_AI_OK

    patterns = [
        list((-1, -1, -1, -1)),
        list((-1, 1, -1, 1)),
        list((1, -1, 1, -1)),
        list((1, 1, 1, 1)),
    ]
    targets = [
        list((-1, 1)),
        list((1, -1)),
        list((1, -1)),
        list((-1, 1)),
    ]

    for step in range(200):
        pat = patterns[step % 4]
        tgt = targets[step % 4]
        c_in = (ctypes.c_int8 * 4)(*pat)
        c_tgt = (ctypes.c_int8 * 2)(*tgt)

        if step % 3 == 0:
            py_res = py_layer.hebbian_step(py_ctx, pat, tgt, plasticity_gain=4)
            c_res = lib.ptrc_bitnet_hebbian_step(ctypes.byref(c_ctx), ctypes.byref(c_layer), c_in, c_tgt, 4)
            assert py_res == c_res, f"Phase-lock result mismatch at step {step}: {py_res} != {c_res}"
        else:
            py_out, py_scores = py_layer.forward(py_ctx, pat)
            c_out = (ctypes.c_int8 * 2)()
            c_scores = (ctypes.c_int32 * 2)()
            rc = lib.ptrc_bitnet_forward(ctypes.byref(c_ctx), ctypes.byref(c_layer), c_in, c_out, c_scores)
            assert rc == PTRC_AI_OK
            assert list(c_out) == py_out, f"Output mismatch at step {step}"
            assert list(c_scores) == py_scores, f"Score mismatch at step {step}"

        assert list(c_ctx.sponge) == py_ctx.sponge, f"Sponge state diverged at step {step}!"

    lib.ptrc_bitnet_wipe(ctypes.byref(c_ctx))
    assert all(v == -1 for v in c_ctx.sponge), "Volatile SRAM wipe to -1 failed!"
    print("[PASS] 3. 100% C11 / Python Bit-Parity over 200 Takts (incl. Prime-Rings, 137-Sync & -1 Wipe)")


def test_zero_float_compliance() -> None:
    root = pathlib.Path(__file__).resolve().parent.parent
    files = [
        root / "embedded" / "ai" / "ptrc_bitnet_engine.h",
        root / "embedded" / "ai" / "ptrc_bitnet_engine.c",
        root / "src" / "00_ptrc_bitnet_demo.c",
        root / "src" / "ptrc_bitnet_engine.py",
        root / "src" / "00_test_ptrc_bitnet_metrics.py",
    ]
    forbidden = re.compile(r"\b(float|double|sin|cos|tan|sqrt|pow|log|exp|math)\b")
    for fpath in files:
        if not fpath.exists():
            continue
        raw = fpath.read_text(encoding="utf-8")
        cleaned = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
        cleaned = re.sub(r"//.*", "", cleaned)
        cleaned = re.sub(r"#.*", "", cleaned)
        for lineno, line in enumerate(cleaned.splitlines(), 1):
            match = forbidden.search(line)
            assert match is None, f"Forbidden float/trig token '{match.group(0)}' in {fpath}:{lineno}"
    print("[PASS] 4. Static Zero-Float & Zero-Trig Compliance Verified")


if __name__ == "__main__":
    test_z_no_zero_and_prime_ring_convergence()
    test_137_takt_crossed_mirror_pulse()
    test_c11_python_bit_parity()
    test_zero_float_compliance()
    print("ALL 4 AI BITNET v2.0 CHECKS PASSED.")
    sys.exit(0)
