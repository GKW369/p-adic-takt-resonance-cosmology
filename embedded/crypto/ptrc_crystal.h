# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
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

# -*- coding: utf-8 -*-

#ifndef PTRC_CRYSTAL_H
#define PTRC_CRYSTAL_H

#include <stdint.h>
#include <stddef.h>

#define MOD_BASE            210ULL                  /* P4 Primorial Ring (2*3*5*7) */
#define PRIMORIAL_P15       614889782588491410ULL   /* P15 Primorial (Primes 2..47) */
#define CONTROL_TAKT        24                      /* 24 Physical Contact Junctions */
#define FREE_FACETS         120                     /* 120 Free Outer Facets */
#define KEY_SHIFT           48                      /* Euler-Phi Constant: phi(210)=48 */
#define INVARIANT_LIMIT     156                     /* Wirminghaus Invariant Limit */
#define RENDER_TAKT_137     137                     /* Fine-Structure Prime Pulse */
#define SLIP_TAG_BYTES      24                      /* 24-Byte (192-Bit) SLIP-MAC */
#define PTRC_KEY_BYTES      64                      /* 512-Bit Master/Session Key */
#define PTRC_NONCE_BYTES    16                      /* 128-Bit Nonce */

typedef struct {
    uint64_t macro_mod[4];          /* 4 pTRC-encoded 64-bit Primorial Cascade Moduli */
    uint64_t macro_state[4];        /* 4 Macro-Cascade Running Phases */
    uint8_t junctions[CONTROL_TAKT];
    uint8_t outer_facets[FREE_FACETS];
    uint32_t takt_counter;
    uint16_t dyn_ring_1;
    uint16_t dyn_ring_2;
    uint16_t dyn_ring_3;
    uint16_t crt_phase_1;
    uint16_t crt_phase_2;
    uint16_t crt_phase_3;
} ptrc_crystal_ctx_t;

void ptrc_crystal_init(ptrc_crystal_ctx_t *ctx, const uint8_t key[PTRC_KEY_BYTES], const uint8_t nonce[PTRC_NONCE_BYTES]);
void ptrc_crystal_wipe(ptrc_crystal_ctx_t *ctx);

void ptrc_kdf_derive(
    const uint8_t *master_seed, size_t seed_len,
    const uint8_t *context_info, size_t info_len,
    uint8_t out_key[PTRC_KEY_BYTES], uint8_t out_nonce[PTRC_NONCE_BYTES]
);

void ptrc_aead_encrypt(
    const uint8_t key[PTRC_KEY_BYTES], const uint8_t nonce[PTRC_NONCE_BYTES],
    const uint8_t *aad, size_t aad_len,
    const uint8_t *plaintext, uint8_t *ciphertext, size_t length,
    uint8_t tag_out[SLIP_TAG_BYTES]
);

int ptrc_aead_decrypt(
    const uint8_t key[PTRC_KEY_BYTES], const uint8_t nonce[PTRC_NONCE_BYTES],
    const uint8_t *aad, size_t aad_len,
    const uint8_t *ciphertext, uint8_t *plaintext, size_t length,
    const uint8_t expected_tag[SLIP_TAG_BYTES]
);

#endif /* PTRC_CRYSTAL_H */
