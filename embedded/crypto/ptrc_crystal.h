/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.5.0
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

/* File: embedded/crypto/ptrc_crystal.h (Complete - v4.5.0 Constant-Time Unbiased AEAD) */

#ifndef PTRC_CRYSTAL_H
#define PTRC_CRYSTAL_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PTRC_CRYPT_KEY_BYTES        64U
#define PTRC_CRYPT_NONCE_BYTES      16U
#define PTRC_CRYPT_TAG_BYTES        24U
#define PTRC_CRYPT_FACETS           144U
#define PTRC_CRYPT_JUNCTIONS        24U
#define PTRC_CRYPT_INNER_RINGS      3U
#define PTRC_MACRO_CASCADE_STAGES   4U
#define PTRC_KEYGEN_PRIME_RINGS     8U

#define PTRC_PRIMORIAL_210          210ULL
#define PTRC_PRIMORIAL_P15          614889782588491410ULL
#define PTRC_TAKT_137               137ULL

#define PTRC_CRYPT_OK               1
#define PTRC_CRYPT_ERR              -1

/* Backward-compatible aliases */
#define PTRC_KEY_BYTES              PTRC_CRYPT_KEY_BYTES
#define PTRC_NONCE_BYTES            PTRC_CRYPT_NONCE_BYTES
#define PTRC_TAG_BYTES              PTRC_CRYPT_TAG_BYTES

/* 672-byte static stack context (< 1 KB SRAM, zero malloc) */
typedef struct {
    uint64_t macro_mod[PTRC_MACRO_CASCADE_STAGES];
    uint64_t macro_state[PTRC_MACRO_CASCADE_STAGES];
    uint32_t inner_mod[PTRC_CRYPT_INNER_RINGS];
    int32_t  sponge[PTRC_CRYPT_FACETS];
    uint64_t takt_counter;
    uint32_t clock_phase_24;
    uint32_t session_salt;
} ptrc_crystal_ctx_t;

int ptrc_crystal_init(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t key[PTRC_CRYPT_KEY_BYTES],
    const uint8_t nonce[PTRC_CRYPT_NONCE_BYTES]
);

int ptrc_crystal_xor_stream(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t *input,
    uint8_t *output,
    size_t len
);

int ptrc_aead_encrypt(
    const uint8_t key[PTRC_CRYPT_KEY_BYTES],
    const uint8_t nonce[PTRC_CRYPT_NONCE_BYTES],
    const uint8_t *aad,
    size_t aad_len,
    const uint8_t *plaintext,
    size_t pt_len,
    uint8_t *ciphertext,
    uint8_t tag[PTRC_CRYPT_TAG_BYTES]
);

int ptrc_aead_decrypt(
    const uint8_t key[PTRC_CRYPT_KEY_BYTES],
    const uint8_t nonce[PTRC_CRYPT_NONCE_BYTES],
    const uint8_t *aad,
    size_t aad_len,
    const uint8_t *ciphertext,
    size_t ct_len,
    const uint8_t tag[PTRC_CRYPT_TAG_BYTES],
    uint8_t *plaintext
);

int ptrc_kdf_derive(
    const uint8_t *master_seed,
    size_t seed_len,
    const uint8_t *context_info,
    size_t info_len,
    uint8_t out_key[PTRC_CRYPT_KEY_BYTES],
    uint8_t out_nonce[PTRC_CRYPT_NONCE_BYTES]
);

int ptrc_primorial_keygen(
    uint64_t session_takt,
    const uint8_t *domain_seed,
    size_t seed_len,
    uint8_t out_key[PTRC_CRYPT_KEY_BYTES],
    uint8_t out_nonce[PTRC_CRYPT_NONCE_BYTES]
);

int ptrc_ct_memcmp(const uint8_t *a, const uint8_t *b, size_t len);

void ptrc_crystal_wipe(ptrc_crystal_ctx_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* PTRC_CRYSTAL_H */
