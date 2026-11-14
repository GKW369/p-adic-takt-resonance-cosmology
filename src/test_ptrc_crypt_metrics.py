"""
pTRC Framework - Cryptographic Avalanche (SAC) & Byte Distribution Benchmark (v3.3)
100% Pure Integer Metrics (Basis Points: 10000 BP = 100.00%).
"""

import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from ptrc_crystal_aead import PTRCHardenedCrystalAEAD


def popcount_bytes(buf_a: bytes, buf_b: bytes) -> int:
    total_diff_bits = 0
    for a, b in zip(buf_a, buf_b):
        total_diff_bits += (a ^ b).bit_count()
    return total_diff_bits


def run_crypto_metrics() -> int:
    print("=" * 78)
    print("  pTRC v3.3 METRICS // AVALANCHE (SAC) & UNIFORM DISTRIBUTION AUDIT")
    print("=" * 78)

    base_key, base_nonce = PTRCHardenedCrystalAEAD.derive_key_and_nonce(
        b"GKW369-BENCHMARK-SEED-1836", b"AUDIT:SAC:2026"
    )
    payload = bytes((i * 13 + 7) & 0xFF for i in range(256))
    aad = b"BENCHMARK|RING:210|TAKT:137"

    # 1. Strict Avalanche Criterion (Key Bit-Flip Test across all 256 key bits)
    ref_ct, ref_tag = PTRCHardenedCrystalAEAD.encrypt(base_key, base_nonce, payload, aad=aad)
    total_bits_tested = 0
    total_bits_flipped = 0

    for byte_idx in range(32):
        for bit_idx in range(8):
            mod_key = bytearray(base_key)
            mod_key[byte_idx] ^= (1 << bit_idx)
            ct_test, tag_test = PTRCHardenedCrystalAEAD.encrypt(bytes(mod_key), base_nonce, payload, aad=aad)

            total_bits_flipped += popcount_bytes(ref_ct, ct_test) + popcount_bytes(ref_tag, tag_test)
            total_bits_tested += (len(ref_ct) + len(ref_tag)) * 8

    # Integer Basis Points (10000 = 100.00%, ideal SAC = 5000 BP)
    avalanche_bp = (total_bits_flipped * 10000) // total_bits_tested
    avalanche_whole = avalanche_bp // 100
    avalanche_frac = avalanche_bp % 100

    # 2. Byte Uniformity & Throughput over 65,536-Byte Stream
    stream_len = 65536
    zero_stream = bytes(stream_len)
    t0 = time.perf_counter_ns()
    keystream_sample, _ = PTRCHardenedCrystalAEAD.encrypt(base_key, base_nonce, zero_stream, aad=b"STREAM")
    t1 = time.perf_counter_ns()

    counts = * 256
    for b in keystream_sample:
        counts[b] += 1

    min_count = min(counts)
    max_count = max(counts)
    ideal_count = stream_len // 256  # Exactly 256 occurrences per byte value
    ns_per_byte = (t1 - t0) // stream_len

    print(f"  • Tested Key Bit-Flips     : 256 single-bit mutations")
    print(f"  • Key Avalanche Effect     : {avalanche_whole}.{avalanche_frac:02d}% ({avalanche_bp} BP | Ideal: 50.00%)")
    print(f"  • 64 KiB Byte Frequency    : Min={min_count}, Max={max_count} (Ideal Mean={ideal_count})")
    print(f"  • Pure Python Throughput   : {ns_per_byte} ns / byte")
    print("=" * 78)

    # Pass if avalanche is within [48.50%, 51.50%] (4850..5150 BP)
    passed = 4850 <= avalanche_bp <= 5150
    print(f" -> AUDIT RESULT: {'[ PASS - CRYPTOGRAPHIC DIFFUSION VERIFIED ]' if passed else '[ WARN - CHECK DIFFUSION ]'}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(run_crypto_metrics())
