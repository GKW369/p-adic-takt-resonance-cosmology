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
Module 16: Cryptographic Resonance (Anti-Side-Channel Integer Stream & AEAD).
File: src/crypt_resonance.py (Complete)

Integrates the v4.5.0 512-bit constant-time Primorial AEAD engine into the
17-module pTRC First-Principles Verification Suite without floating-point ops.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ptrc_crystal_aead import (
    PTRC_CRYPT_KEY_BYTES,
    PTRC_CRYPT_NONCE_BYTES,
    PTRC_CRYPT_OK,
    PTRC_CRYPT_TAG_BYTES,
    PtrcCrystalContext,
    ptrc_aead_decrypt,
    ptrc_aead_encrypt,
    ptrc_primorial_keygen,
)


@dataclass(frozen=True)
class CryptResonanceMetrics:
    key_bits: int
    nonce_bits: int
    tag_bits: int
    zero_states_internal: int
    roundtrip_verified: bool
    tamper_rejected: bool
    sram_context_bytes: int


def run_crypt_resonance_verification() -> Dict[str, object]:
    """Executes deterministic v4.5.0 AEAD & Primorial Keygen verification."""
    domain_seed = b"pTRC_MODULE_16_FIRST_PRINCIPLES_SEED_2026"
    key, nonce = ptrc_primorial_keygen(137210, domain_seed)

    assert len(key) == PTRC_CRYPT_KEY_BYTES
    assert len(nonce) == PTRC_CRYPT_NONCE_BYTES

    ctx = PtrcCrystalContext(key, nonce)
    zero_internal = 0
    for _ in range(1024):
        st = ctx.next_keystream_state()
        if st <= 0 or st > 256:
            zero_internal += 1

    plaintext = b"pTRC v4.5.0: Zero-Float Coprime Resonance Stream in Z \\ {0}!"
    aad = b"HEADER_MOD_210_TAKT_24_PULSE_137"

    ciphertext, tag = ptrc_aead_encrypt(key, nonce, plaintext, aad=aad)
    assert len(tag) == PTRC_CRYPT_TAG_BYTES

    rc_ok, recovered = ptrc_aead_decrypt(key, nonce, ciphertext, tag, aad=aad)
    roundtrip_ok = (rc_ok == PTRC_CRYPT_OK) and (recovered == plaintext)

    tampered_ct = bytearray(ciphertext)
    tampered_ct.__setitem__(0, tampered_ct.__getitem__(0) ^ 0x01)
    rc_bad, _ = ptrc_aead_decrypt(key, nonce, bytes(tampered_ct), tag, aad=aad)
    tamper_rejected = rc_bad != PTRC_CRYPT_OK

    metrics = CryptResonanceMetrics(
        key_bits=PTRC_CRYPT_KEY_BYTES * 8,
        nonce_bits=PTRC_CRYPT_NONCE_BYTES * 8,
        tag_bits=PTRC_CRYPT_TAG_BYTES * 8,
        zero_states_internal=zero_internal,
        roundtrip_verified=roundtrip_ok,
        tamper_rejected=tamper_rejected,
        sram_context_bytes=672,
    )

    assert metrics.zero_states_internal == 0, "Zero state leaked into Z \\ {0} crystal"
    assert metrics.roundtrip_verified, "AEAD roundtrip decryption failed"
    assert metrics.tamper_rejected, "AEAD failed to reject tampered ciphertext"

    return {
        "module": "16_crypt_resonance",
        "version": "4.5.0",
        "key_bits": metrics.key_bits,
        "nonce_bits": metrics.nonce_bits,
        "tag_bits": metrics.tag_bits,
        "zero_states_internal": metrics.zero_states_internal,
        "roundtrip_verified": metrics.roundtrip_verified,
        "tamper_rejected": metrics.tamper_rejected,
        "sram_context_bytes": metrics.sram_context_bytes,
    }


if __name__ == "__main__":
    res = run_crypt_resonance_verification()
    print("[Module 16 - Cryptographic Resonance v4.5.0] Verified:", res)
