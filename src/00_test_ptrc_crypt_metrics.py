# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.5.0
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

r"""
pTRC v4.5.0 Cryptographic Metrics Audit (SAC Avalanche, Unbiased Uniformity & C11 Speed).
File: src/00_test_ptrc_crypt_metrics.py (Complete)
"""

from __future__ import annotations

import ctypes
import pathlib
import sys
import time
from typing import Tuple

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ptrc_crystal_aead import (  # noqa: E402
    PTRC_CRYPT_KEY_BYTES,
    PTRC_CRYPT_NONCE_BYTES,
    PTRC_CRYPT_OK,
    PTRC_CRYPT_TAG_BYTES,
    PtrcCrystalContext,
    load_c_crystal_library,
    ptrc_aead_decrypt,
    ptrc_aead_encrypt,
    ptrc_primorial_keygen,
)


def _popcount_bytes(a: bytes, b: bytes) -> int:
    total = 0
    for x, y in zip(a, b):
        total += (x ^ y).bit_count()
    return total


def audit_strict_avalanche_criterion() -> Tuple[int, int, int]:
    """Tests single-bit key flips across all 64 key bytes (64 trials x 704 output bits)."""
    base_key, base_nonce = ptrc_primorial_keygen(420210, b"PTRC_SAC_AVALANCHE_SEED_V45")
    aad = b"SAC_AUDIT_AAD_144"
    pt = b"A" * 64

    base_ct, base_tag = ptrc_aead_encrypt(base_key, base_nonce, pt, aad=aad)
    base_out = base_ct + base_tag
    bits_per_trial = len(base_out) * 8

    total_flipped = 0
    total_bits = 0
    for byte_idx in range(PTRC_CRYPT_KEY_BYTES):
        mod_key = bytearray(base_key)
        mod_key[byte_idx] ^= 1 << (byte_idx & 7)
        ct, tag = ptrc_aead_encrypt(bytes(mod_key), base_nonce, pt, aad=aad)
        flipped = _popcount_bytes(base_out, ct + tag)
        total_flipped += flipped
        total_bits += bits_per_trial

    permille = (total_flipped * 1000) // total_bits
    assert 440 <= permille <= 560, f"SAC avalanche out of bounds: {permille}/1000"
    return total_flipped, total_bits, permille


def audit_keystream_uniformity(sample_len: int = 16384) -> Tuple[int, int, int]:
    """Verifies zero-free internal state {1..256} and unbiased 256-bucket XOR distribution."""
    key, nonce = ptrc_primorial_keygen(999137, b"PTRC_UNIFORMITY_AUDIT_V45")
    ctx = PtrcCrystalContext(key, nonce)

    counts = * 256
    zero_internal_states = 0
    for _ in range(sample_len):
        st = ctx.next_keystream_state()
        if st < 1 or st > 256:
            zero_internal_states += 1
        ks_byte = (st - 1) & 0xFF
        counts[ks_byte] += 1

    assert zero_internal_states == 0, f"Found {zero_internal_states} invalid internal states outside {{1..256}}"
    min_c = min(counts)
    max_c = max(counts)
    expected = sample_len // 256  # 64
    max_dev = max(abs(max_c - expected), abs(min_c - expected))
    assert min_c > 0, "Missing byte bucket in unbiased keystream"
    assert max_dev <= 40, f"Excessive bucket deviation: {max_dev} (expected ~{expected})"
    return zero_internal_states, min_c, max_c


def audit_throughput_and_parity() -> None:
    key, nonce = ptrc_primorial_keygen(777210, b"PTRC_THROUGHPUT_SEED_V45")
    aad = b"PERF_HEADER_24"

    # Python 64 KB benchmark
    py_len = 64 * 1024
    py_pt = bytes(((i * 137 + 1) & 0xFF) for i in range(py_len))
    t0 = time.perf_counter_ns()
    py_ct, py_tag = ptrc_aead_encrypt(key, nonce, py_pt, aad=aad)
    rc, py_rec = ptrc_aead_decrypt(key, nonce, py_ct, py_tag, aad=aad)
    t1 = time.perf_counter_ns()
    assert rc == PTRC_CRYPT_OK and py_rec == py_pt
    py_us = max(1, (t1 - t0) // 1000)
    py_bps = (py_len * 1_000_000) // py_us

    lib = load_c_crystal_library(ROOT)
    if lib is not None:
        c_len = 4096 * 1024
        c_pt = (ctypes.c_uint8 * c_len).from_buffer_copy(
            bytes(((i * 73 + 11) & 0xFF) for i in range(c_len))
        )
        c_ct = (ctypes.c_uint8 * c_len)()
        c_rec = (ctypes.c_uint8 * c_len)()
        c_key = (ctypes.c_uint8 * PTRC_CRYPT_KEY_BYTES).from_buffer_copy(key)
        c_nonce = (ctypes.c_uint8 * PTRC_CRYPT_NONCE_BYTES).from_buffer_copy(nonce)
        c_aad = (ctypes.c_uint8 * len(aad)).from_buffer_copy(aad)
        c_tag = (ctypes.c_uint8 * PTRC_CRYPT_TAG_BYTES)()

        tc0 = time.perf_counter_ns()
        rc_enc = lib.ptrc_aead_encrypt(c_key, c_nonce, c_aad, len(aad), c_pt, c_len, c_ct, c_tag)
        tc1 = time.perf_counter_ns()
        rc_dec = lib.ptrc_aead_decrypt(c_key, c_nonce, c_aad, len(aad), c_ct, c_len, c_tag, c_rec)
        assert rc_enc == PTRC_CRYPT_OK and rc_dec == PTRC_CRYPT_OK
        assert bytes(c_rec) == bytes(c_pt)
        c_us = max(1, (tc1 - tc0) // 1000)
        c_bps = (c_len * 1_000_000) // c_us
        print(f"  [C11 Native AEAD]   4096 KB encrypted in {c_us:,} us (~{c_bps:,} Bytes/sec)")
    else:
        print("  [C11 Native AEAD]   Shared library not built yet (build/libptrc_crystal.so) - Python verified")

    print(f"  [Python Reference]  64 KB roundtrip in {py_us:,} us (~{py_bps:,} Bytes/sec)")


def main() -> None:
    print("=== pTRC v4.5.0 Cryptographic Security & Performance Audit ===")
    flipped, total, permille = audit_strict_avalanche_criterion()
    print(f"  [SAC Avalanche]     {flipped:,} / {total:,} bits flipped ({permille} / 1000 permille)")

    zero_st, min_c, max_c = audit_keystream_uniformity(16384)
    print(f"  [Z \\ {{0}} & Bias]   Internal zero states: {zero_st} | 256-bucket min={min_c}, max={max_c} (ideal=64)")

    audit_throughput_and_parity()
    print("=== ALL v4.5.0 CRYPTO METRIC AUDITS PASSED ===")


if __name__ == "__main__":
    main()
