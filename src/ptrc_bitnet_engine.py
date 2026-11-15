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
File: src/ptrc_bitnet_engine.py

Strictly pure integer (-1 adjacent to +1, no zero point), zero-trigonometry,
prime-ring resonance weighted, and bit-identical to embedded/ai/ptrc_bitnet_engine.c.
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
PTRC_AI_PRIME_RING_CNT = 16
PTRC_AI_DEFAULT_THRESH = -1
PTRC_AI_OK = 1
PTRC_AI_ERR = -1

# 16 Coprime Non-Mersenne Prime Rings (gcd(p, 210) == 1, Mersenne primes 3, 7, 31, 127 excluded)
PTRC_AI_PRIME_RINGS: Tuple[int, ...] = (
    11, 13, 17, 19, 23, 29, 37, 41,
    43, 47, 53, 59, 61, 67, 71, 73,
)

# Pure 24-Clock Discrete Quadrance Basis (u^2 + v^2 = 1000^2 in Z \ {0}, no zero)
PTRC_AI_QUAD_24: Tuple[Tuple[int, int], ...] = (
    (1000, 1), (966, 259), (866, 500), (707, 707),
    (500, 866), (259, 966), (-1, 1000), (-259, 966),
    (-500, 866), (-707, 707), (-866, 500), (-966, 259),
    (-1000, -1), (-966, -259), (-866, -500), (-707, -707),
    (-500, -866), (-259, -966), (1, -1000), (259, -966),
    (500, -866), (707, -707), (866, -500), (966, -259),
)


def ptrc_z_no_zero(v: int) -> int:
    """Maps any integer into Z \\ {0}: 0 resolves directly to -1 (no zero state)."""
    return -1 if v == 0 else int(v)


def ptrc_sign_z_no_zero(v: int) -> int:
    """Direct jump activation in Z \\ {0}: >= +1 -> +1, <= -1 -> -1 (no zero crossing)."""
    return 1 if ptrc_z_no_zero(v) >= 1 else -1


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
        self.sponge: List[int] = list((1,)) * PTRC_AI_FACETS
        energy = 1
        for f in range(PTRC_AI_FACETS):
            state = (state ^ (state << 13)) & 0xFFFFFFFFFFFFFFFF
            state = (state ^ (state >> 7)) & 0xFFFFFFFFFFFFFFFF
            state = (state ^ (state << 17)) & 0xFFFFFFFFFFFFFFFF
            val = int(state % PTRC_AI_PRIMORIAL_210) - 105
            val = ptrc_z_no_zero(val)
            self.sponge[f] = val
            energy += val if val >= 1 else -val
        self.takt_counter: int = 1
        self.clock_phase_24: int = 1
        self.resonance_energy: int = ptrc_z_no_zero(energy)
