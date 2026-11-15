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
pTRC Resonant BitNet AI Engine v2.0 (Pure Z \\ {0} Integer Reference & C11 ctypes Bridge).

Strictly pure integer, zero-trigonometry, and bit-identical to embedded/ai/ptrc_bitnet_engine.c.
"""

from __future__ import annotations

import ctypes
import pathlib
from typing import List, Optional, Sequence, Tuple

PTRC_AI_FACETS = 144
PTRC_AI_JUNCTIONS = 24
PTRC_AI_MODULO_24 = 24
PTRC_AI_PRIMORIAL_210 = 210
PTRC_AI_TAKT_137 = 137
PTRC_AI_INVARIANT_156 = 156
PTRC_AI_MAX_DIM = 144
PTRC_AI_WORDS_PER_ROW = 3

# Pure 24-Clock Discrete Quadrance Basis (u^2 + v^2 = 1000^2 in Z \ {0}, zero sin/cos)
PTRC_AI_QUAD_24: Tuple[Tuple[int, int], ...] = (
    (1000, 1), (966, 259), (866, 500), (707, 707),
    (500, 866), (259, 966), (-1, 1000), (-259, 966),
    (-500, 866), (-707, 707), (-866, 500), (-966, 259),
    (-1000, -1), (-966, -259), (-866, -500), (-707, -707),
    (-500, -866), (-259, -966), (1, -1000), (259, -966),
    (500, -866), (707, -707), (866, -500), (966, -259),
)


def ptrc_z_no_zero(v: int) -> int:
    """Maps any integer into Z \\ {0} (0 resolves strictly to -1)."""
    return -1 if v == 0 else int(v)


def ptrc_sign_z_no_zero(v: int) -> int:
    """Sign activation in Z \\ {0}: >= 0 -> +1, < 0 -> -1."""
    return 1 if v >= 0 else -1


def _trunc_div(num: int, den: int) -> int:
    """C99/C11 truncating integer division toward zero."""
    q = abs(num) // abs(den)
    return -q if ((num < 0) ^ (den < 0)) else q


def _c_not32(v: int) -> int:
    """32-bit signed bitwise complement (~x in C11)."""
    u = (~v) & 0xFFFFFFFF
    return u - 0x100000000 if (u & 0x80000000) else u


class PtrcBitNetContext:
    """Pure Python reference matching ptrc_bitnet_ctx_t in embedded/ai/ptrc_bitnet_engine.c."""

    def __init__(self, seed: int = 137210144) -> None:
        state = 0x9E3779B97F4A7C15 if seed == 0 else (seed & 0xFFFFFFFFFFFFFFFF)
        self.sponge: List[int] = [1] * PTRC_AI_FACETS
        energy = 0
        for f in range(PTRC_AI_FACETS):
            state = (state ^ (state << 13)) & 0xFFFFFFFFFFFFFFFF
            state = (state ^ (state >> 7)) & 0xFFFFFFFFFFFFFFFF
            state = (state ^ (state << 17)) & 0xFFFFFFFFFFFFFFFF
            val = int(state % PTRC_AI_PRIMORIAL_210) - 105
            val = ptrc_z_no_zero(val)
            self.sponge[f] = val
            energy += abs(val)
        self.takt_counter: int = 1
        self.clock_phase_24: int = 0
        self.resonance_energy: int = ptrc_z_no_zero(energy)


class PtrcBitNetLayer:
    """1-bit {-1, +1} crystalline layer with integer Hebbian plasticity accumulators."""

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        weights_z_no_zero: Sequence[int],
        takt_threshold: int = 0,
    ) -> None:
        if not (1 <= in_dim <= PTRC_AI_MAX_DIM and 1 <= out_dim <= PTRC_AI_MAX_DIM):
            raise ValueError("Dimensions must be within 1..144")
        if len(weights_z_no_zero) != in_dim * out_dim:
            raise ValueError("Weight count mismatch")

        self.in_dim = in_dim
        self.out_dim = out_dim
        self.takt_threshold = int(takt_threshold)
        self.plasticity_acc: List[List[int]] = [
            [16 if weights_z_no_zero[r * in_dim + c] >= 0 else -16 for c in range(in_dim)]
            for r in range(out_dim)
        ]
        self.pos_mask: List[List[int]] = [[0] * PTRC_AI_WORDS_PER_ROW for _ in range(out_dim)]
        self.neg_mask: List[List[int]] = [[0] * PTRC_AI_WORDS_PER_ROW for _ in range(out_dim)]
        self.sync_bitplanes()

    def sync_bitplanes(self) -> None:
        for r in range(self.out_dim):
            for w in range(PTRC_AI_WORDS_PER_ROW):
                self.pos_mask[r][w] = 0
                self.neg_mask[r][w] = 0
            for c in range(self.in_dim):
                word = c >> 6
                bit = 1 << (c & 63)
                if self.plasticity_acc[r][c] >= 0:
                    self.pos_mask[r][word] |= bit
                else:
                    self.neg_mask[r][word] |= bit

    def forward(
        self, ctx: PtrcBitNetContext, input_z_no_zero: Sequence[int]
    ) -> Tuple[List[int], List[int]]:
        in_pos = [0] * PTRC_AI_WORDS_PER_ROW
        in_neg = [0] * PTRC_AI_WORDS_PER_ROW
        for c in range(self.in_dim):
            word = c >> 6
            bit = 1 << (c & 63)
            if input_z_no_zero[c] >= 0:
                in_pos[word] |= bit
            else:
                in_neg[word] |= bit

        phase = ctx.clock_phase_24 % PTRC_AI_MODULO_24
        quad_u, quad_v = PTRC_AI_QUAD_24[phase]
        is_137_sync = (ctx.takt_counter % PTRC_AI_TAKT_137) == 0

        outputs: List[int] = []
        raw_scores: List[int] = []
        step_energy = 0

        for r in range(self.out_dim):
            agree_bits = 0
            disagree_bits = 0
            for w in range(PTRC_AI_WORDS_PER_ROW):
                agree = (self.pos_mask[r][w] & in_pos[w]) | (self.neg_mask[r][w] & in_neg[w])
                disagree = (self.pos_mask[r][w] & in_neg[w]) | (self.neg_mask[r][w] & in_pos[w])
                agree_bits += agree.bit_count()
                disagree_bits += disagree.bit_count()

            dot = agree_bits - disagree_bits
            facet_idx = (r + phase) % PTRC_AI_FACETS
            facet_bias = _trunc_div(ctx.sponge[facet_idx] * quad_u + quad_v, 1000 * 64)
            score = dot + facet_bias - self.takt_threshold

            if is_137_sync:
                ctx.sponge[facet_idx] = ptrc_z_no_zero(_c_not32(ctx.sponge[facet_idx]))
            else:
                ctx.sponge[facet_idx] = ptrc_z_no_zero(
                    ctx.sponge[facet_idx] + ptrc_sign_z_no_zero(score)
                )

            raw_scores.append(score)
            outputs.append(ptrc_sign_z_no_zero(score))
            step_energy += abs(score)

        ctx.takt_counter += 1
        ctx.clock_phase_24 = (ctx.clock_phase_24 + 1) % PTRC_AI_MODULO_24
        ctx.resonance_energy = ptrc_z_no_zero(step_energy)
        return outputs, raw_scores

    def hebbian_step(
        self,
        ctx: PtrcBitNetContext,
        input_z_no_zero: Sequence[int],
        target_z_no_zero: Sequence[int],
        plasticity_gain: int = 4,
    ) -> int:
        pred, _ = self.forward(ctx, input_z_no_zero)
        gain = 1 if plasticity_gain <= 0 else int(plasticity_gain)
        errors = 0

        for r in range(self.out_dim):
            tgt = 1 if target_z_no_zero[r] >= 0 else -1
            if pred[r] != tgt:
                errors += 1
                for c in range(self.in_dim):
                    in_bit = 1 if input_z_no_zero[c] >= 0 else -1
                    delta = tgt * in_bit * gain
                    acc = self.plasticity_acc[r][c] + delta
                    if acc > PTRC_AI_INVARIANT_156:
                        acc = PTRC_AI_INVARIANT_156
                    elif acc < -PTRC_AI_INVARIANT_156:
                        acc = -PTRC_AI_INVARIANT_156
                    self.plasticity_acc[r][c] = ptrc_z_no_zero(acc)

        if errors > 0:
            self.sync_bitplanes()
        return errors


class _CSpongeCtx(ctypes.Structure):
    _fields_ = [
        ("sponge", ctypes.c_int32 * PTRC_AI_FACETS),
        ("takt_counter", ctypes.c_uint64),
        ("clock_phase_24", ctypes.c_uint32),
        ("resonance_energy", ctypes.c_int32),
    ]


class _CLayer(ctypes.Structure):
    _fields_ = [
        ("pos_mask", (ctypes.c_uint64 * PTRC_AI_WORDS_PER_ROW) * PTRC_AI_MAX_DIM),
        ("neg_mask", (ctypes.c_uint64 * PTRC_AI_WORDS_PER_ROW) * PTRC_AI_MAX_DIM),
        ("plasticity_acc", (ctypes.c_int32 * PTRC_AI_MAX_DIM) * PTRC_AI_MAX_DIM),
        ("in_dim", ctypes.c_uint32),
        ("out_dim", ctypes.c_uint32),
        ("takt_threshold", ctypes.c_int32),
    ]


def load_c_bitnet_library(search_root: Optional[pathlib.Path] = None) -> Optional[ctypes.CDLL]:
    """Loads build/libptrc_bitnet.so (or .dll/.dylib) if compiled via CMake."""
    root = search_root or pathlib.Path(__file__).resolve().parent.parent
    candidates = [
        root / "build" / "libptrc_bitnet.so",
        root / "build" / "libptrc_bitnet.dylib",
        root / "build" / "ptrc_bitnet.dll",
        root / "build" / "Release" / "ptrc_bitnet.dll",
    ]
    for cand in candidates:
        if cand.exists():
            lib = ctypes.CDLL(str(cand))
            lib.ptrc_bitnet_ctx_init.argtypes = [ctypes.POINTER(_CSpongeCtx), ctypes.c_uint64]
            lib.ptrc_bitnet_ctx_init.restype = None

            lib.ptrc_bitnet_layer_init.argtypes = [
                ctypes.POINTER(_CLayer),
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.POINTER(ctypes.c_int8),
                ctypes.c_int32,
            ]
            lib.ptrc_bitnet_layer_init.restype = ctypes.c_int

            lib.ptrc_bitnet_forward.argtypes = [
                ctypes.POINTER(_CSpongeCtx),
                ctypes.POINTER(_CLayer),
                ctypes.POINTER(ctypes.c_int8),
                ctypes.POINTER(ctypes.c_int8),
                ctypes.POINTER(ctypes.c_int32),
            ]
            lib.ptrc_bitnet_forward.restype = ctypes.c_int

            lib.ptrc_bitnet_hebbian_step.argtypes = [
                ctypes.POINTER(_CSpongeCtx),
                ctypes.POINTER(_CLayer),
                ctypes.POINTER(ctypes.c_int8),
                ctypes.POINTER(ctypes.c_int8),
                ctypes.c_int32,
            ]
            lib.ptrc_bitnet_hebbian_step.restype = ctypes.c_int

            lib.ptrc_bitnet_wipe.argtypes = [ctypes.POINTER(_CSpongeCtx)]
            lib.ptrc_bitnet_wipe.restype = None
            return lib
    return None
