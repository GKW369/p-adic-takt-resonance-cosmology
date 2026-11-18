/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.4.0
 * Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program (see the LICENSE file in the root directory).
 * If not, see <https://gnu.org>.
 * ============================================================================== */

/* File: embedded/crypto/ptrc_crystal.c (Part 1 of 3 - Hardened Constant-Time v4.4.0) */

#ifndef PTRC_CRYSTAL_H
#define PTRC_CRYSTAL_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PTRC_KEY_BYTES         64u
#define PTRC_NONCE_BYTES       16u
#define PTRC_TAG_BYTES         24u
#define PTRC_FACET_COUNT       144u
#define PTRC_VERSION_STRING    "4.5.0-ct-unbiased-aead"

/* Zero-free domain Z \ {0}: internal crystal state lives strictly in {1..256} */
#define PTRC_ZERO_GUARD_U64    UINT64_C(0xFFFFFFFFFFFFFFFF)
#define PTRC_ZERO_GUARD_U32    UINT32_C(0xFFFFFFFF)
#define PTRC_ZERO_GUARD_U8     UINT8_C(0xFF)

typedef struct {
    uint64_t p_ring[4];
    uint64_t p_state[4];
    uint64_t p_mult[4];
    uint32_t inner_mod[3];
    uint32_t inner_state[3];
    uint8_t  facets[PTRC_FACET_COUNT];
    uint32_t takt_24;
    uint32_t pulse_137;
    uint64_t counter;
} ptrc_crystal_ctx_t;

void ptrc_crystal_init(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t key[PTRC_KEY_BYTES],
    const uint8_t nonce[PTRC_NONCE_BYTES]
);

void ptrc_crystal_wipe(ptrc_crystal_ctx_t *ctx);

/* Returns internal non-zero state in {1..256} */
uint16_t ptrc_next_keystream_state_ct(ptrc_crystal_ctx_t *ctx);

/* Returns unbiased keystream byte in {0..255} derived from non-zero state - 1 */
uint8_t ptrc_next_keystream_byte_ct(ptrc_crystal_ctx_t *ctx);

void ptrc_xor_stream_ct(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t *in,
    uint8_t *out,
    size_t len
);

void ptrc_kdf_derive(
    const uint8_t master_key[PTRC_KEY_BYTES],
    const uint8_t salt[PTRC_NONCE_BYTES],
    const uint8_t *info,
    size_t info_len,
    uint8_t out_key[PTRC_KEY_BYTES],
    uint8_t out_nonce[PTRC_NONCE_BYTES]
);

void ptrc_primorial_keygen(
    const uint8_t *domain_seed,
    size_t seed_len,
    uint64_t counter,
    uint8_t out_key[PTRC_KEY_BYTES],
    uint8_t out_nonce[PTRC_NONCE_BYTES]
);

void ptrc_aead_encrypt(
    const uint8_t key[PTRC_KEY_BYTES],
    const uint8_t nonce[PTRC_NONCE_BYTES],
    const uint8_t *aad,
    size_t aad_len,
    const uint8_t *plaintext,
    size_t pt_len,
    uint8_t *ciphertext,
    uint8_t tag[PTRC_TAG_BYTES]
);

int ptrc_aead_decrypt(
    const uint8_t key[PTRC_KEY_BYTES],
    const uint8_t nonce[PTRC_NONCE_BYTES],
    const uint8_t *aad,
    size_t aad_len,
    const uint8_t *ciphertext,
    size_t ct_len,
    const uint8_t tag[PTRC_TAG_BYTES],
    uint8_t *plaintext_out
);

#ifdef __cplusplus
}
#endif

#endif /* PTRC_CRYSTAL_H */
