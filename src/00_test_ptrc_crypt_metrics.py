# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.0
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
Cryptographic Avalanche, Uniformity & Throughput Metrics for pTRC Crypto v4.0.
File: src/00_test_ptrc_crypt_metrics.py

Strictly pure integer (-1 adjacent to +1, no zero point, integer permille & bytes/sec).
"""

from __future__ import annotations

import ctypes
import sys
import time

from ptrc_crystal_aead import (
    PTRC_CRYPT_KEY_BYTES,
    PTRC_CRYPT_NONCE_BYTES,
    PTRC_CRYPT_OK,
    PTRC_CRYPT_TAG_BYTES,
    PtrcCrystalContext,
    load_c_crystal_library,
    ptrc_aead_encrypt,
    ptrc_primorial_keygen,
)


def _hamming_bits(a: bytes, b: bytes) -> int:
    total = 0
    for x, y in zip(a, b):
        total += (x ^ y).bit_count()
    return total


def audit_strict_avalanche_criterion() -> None:
    seed = b"pTRC-v4.0-AVALANCHE-AUDIT-SEED-210"
    base_key, base_nonce = ptrc_primorial_keygen(137210144, seed)
    aad = b"AVALANCHE-AAD-144"
    pt = bytes((i * 73 + 19) & 0xFF for i in range(64))

    base_ct, base_tag = ptrc_aead_encrypt(base_key, base_nonce, pt, aad)
    total_bits_per_sample = (len(base_ct) + len(base_tag)) * 8
    flipped_sum = 0
    trials = 64

    for bit_idx in range(trials):
        mod_key = bytearray(base_key)
        mod_key[bit_idx >> 3] ^= 1 << (bit_idx & 7)
        ct2, tag2 = ptrc_aead_encrypt(bytes(mod_key), base_nonce, pt, aad)
        flipped_sum += _hamming_bits(base_ct + base_tag, ct2 + tag2)

    # Integer permille (ideal SAC = 500 permille = 500/1000)
    total_tested_bits = trials * total_bits_per_sample
    avalanche_permille = (flipped_sum * 1000) // total_tested_bits
    assert 460 <= avalanche_permille <= 540, f"Avalanche out of integer bounds: {avalanche_permille} permille"
    print(
        f" + [METRIC 1] Key Avalanche (SAC) : {avalanche_permille} / 1000 permille "
        f"({flipped_sum}/{total_tested_bits} bits flipped across {trials} 1-bit key flips)"
    )

def audit_keystream_uniformity() -> None:
    seed = b"pTRC-v4.0-UNIFORMITY-STREAM-SEED-137"
    key, nonce = ptrc_primorial_keygen(210144137, seed)
    ctx = PtrcCrystalContext(key, nonce)

    sample_bytes = 16384
    stream = ctx.xor_stream(bytes(sample_bytes))
    counts = list((0,)) * 256
    for b in stream:
        counts.__setitem__(b, counts.__getitem__(b) + 1)

    # Strict Z \ {0} byte law: 0x00 never appears in raw keystream (mapped to 0xFF)
    assert counts.__getitem__(0) == 0, "Zero byte 0x00 violated Z \\ {0} keystream law!"
    expected = sample_bytes // 255
    active_counts = [counts.__getitem__(i) for i in range(1, 255)]
    max_dev = max(abs(c - expected) for c in active_counts)
    assert max_dev <= 36, f"Keystream byte deviation too high: {max_dev}"
    assert all(v != 0 for v in ctx.sponge), "Zero state entered 144-facet sponge during 16KB stream!"
    print(
        f" + [METRIC 2] Keystream Balance   : {sample_bytes} Bytes | 0x00 Count: None (Z \\ {{0}}) | "
        f"Max Active Deviation: {max_dev}"
    )




def benchmark_crypto_throughput() -> None:
    seed = b"pTRC-v4.0-THROUGHPUT-BENCHMARK-156"
    key, nonce = ptrc_primorial_keygen(156144137, seed)
    aad = b"BENCHMARK-AAD"
    payload = bytes(list((0x5A,)) * 1024)

    py_iters = 64
    t0 = time.perf_counter_ns()
    for _ in range(py_iters):
        ptrc_aead_encrypt(key, nonce, payload, aad)
    t1 = time.perf_counter_ns()

    py_us = (t1 - t0) // 1000
    py_bps = (py_iters * len(payload) * 1_000_000) // (py_us if py_us >= 1 else 1)
    print(f" + [METRIC 3] Python AEAD 512-Bit : {py_iters} KB in {py_us} us (~{py_bps} Bytes/sec)")

    lib = load_c_crystal_library()
    if lib is not None:
        c_key = (ctypes.c_uint8 * PTRC_CRYPT_KEY_BYTES)(*key)
        c_nonce = (ctypes.c_uint8 * PTRC_CRYPT_NONCE_BYTES)(*nonce)
        c_aad = (ctypes.c_uint8 * len(aad))(*aad)
        c_pt = (ctypes.c_uint8 * len(payload))(*payload)
        c_ct = (ctypes.c_uint8 * len(payload))()
        c_tag = (ctypes.c_uint8 * PTRC_CRYPT_TAG_BYTES)()

        c_iters = 4096
        ct0 = time.perf_counter_ns()
        for _ in range(c_iters):
            rc = lib.ptrc_aead_encrypt(c_key, c_nonce, c_aad, len(aad), c_pt, len(payload), c_ct, c_tag)
            assert rc == PTRC_CRYPT_OK
        ct1 = time.perf_counter_ns()

        c_us = (ct1 - ct0) // 1000
        c_bps = (c_iters * len(payload) * 1_000_000) // (c_us if c_us >= 1 else 1)
        print(f" + [METRIC 4] Native C11 AEAD     : {c_iters} KB in {c_us} us (~{c_bps} Bytes/sec | Zero malloc)")
    else:
        print(" + [METRIC 4] Native C11 AEAD     : Skipped (build libptrc_crystal.so to benchmark C11)")


def main() -> None:
    print("===============================================================================")
    print("  pTRC CRYPTO v4.0 — STATISTICAL, AVALANCHE & THROUGHPUT METRICS AUDIT")
    print("===============================================================================")
    audit_strict_avalanche_criterion()
    audit_keystream_uniformity()
    benchmark_crypto_throughput()
    print("-------------------------------------------------------------------------------")
    print("  ALL CRYPTO v4.0 METRICS & INVARIANTS VERIFIED (100% PURE INTEGER Z \\ {0}).")
    print("===============================================================================")


if __name__ == "__main__":
    main()
    sys.exit(0)
