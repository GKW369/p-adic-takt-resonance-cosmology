/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Cryptographic Engine v4.0
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

/* File: embedded/crypto/ptrc_crystal.h */

#ifndef PTRC_CRYSTAL_H
#define PTRC_CRYSTAL_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ==============================================================================
 * pTRC v4.0 CRYPTOGRAPHIC CONSTANTS (STRICTLY Z \ {0}, ZERO-TABLE, ZERO-FLOAT)
 * ============================================================================== */
#define PTRC_CRYPT_KEY_BYTES         64U     /* 512-Bit Master Key */
#define PTRC_CRYPT_NONCE_BYTES       16U     /* 128-Bit Nonce */
#define PTRC_CRYPT_TAG_BYTES         24U     /* 192-Bit SLIP-MAC Tag */
#define PTRC_CRYPT_FACETS            144U    /* 144 Outer Triangular Facets */
#define PTRC_CRYPT_JUNCTIONS         24U     /* 24-Clock Control Ring */
#define PTRC_CRYPT_INNER_RINGS       3U      /* 3 Dynamic Coprime Inner CRT Rings */
#define PTRC_MACRO_CASCADE_STAGES    4U      /* 4-Stage 64-Bit Primorial Macro-Cascade */
#define PTRC_KEYGEN_PRIME_RINGS      8U      /* 8 Pairwise Coprime 1-Byte Prime Rings */
#define PTRC_PRIMORIAL_210           210ULL  /* Base Primorial P4 = 2 * 3 * 5 * 7 */
#define PTRC_PRIMORIAL_P15           614889782588491410ULL /* P15 = Product of first 15 primes */
#define PTRC_TAKT_137                137ULL  /* Fine-Structure Mirror Render Pulse */
#define PTRC_CRYPT_OK                1       /* Success in Z \ {0} (no zero return) */
#define PTRC_CRYPT_ERR               (-1)    /* Error / Auth Failure in Z \ {0} */

/* ==============================================================================
 * ZERO-MALLOC BARE-METAL CONTEXT (~660 BYTES STATIC STACK)
 * ============================================================================== */
typedef struct {
    uint64_t macro_mod[PTRC_MACRO_CASCADE_STAGES];
    uint64_t macro_state[PTRC_MACRO_CASCADE_STAGES];
    uint32_t inner_mod[PTRC_CRYPT_INNER_RINGS];
    int32_t  sponge[PTRC_CRYPT_FACETS];
    uint64_t takt_counter;
    uint32_t clock_phase_24;
    uint32_t session_salt;
} ptrc_crystal_ctx_t;

/* Initializes the 512-bit Primorial Macro-Cascade & 144-Facet Crystal in Z \ {0} */
int ptrc_crystal_init(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t key[PTRC_CRYPT_KEY_BYTES],
    const uint8_t nonce[PTRC_CRYPT_NONCE_BYTES]
);

/* Deterministic 8-Prime CRT Key & Nonce Generator (period > 1.09 * 10^19 takts) */
int ptrc_primorial_keygen(
    uint64_t session_takt,
    const uint8_t *domain_seed,
    size_t seed_len,
    uint8_t out_key[PTRC_CRYPT_KEY_BYTES],
    uint8_t out_nonce[PTRC_CRYPT_NONCE_BYTES]
);

/* 512-Bit pTRC-KDF Key & Nonce Derivation Function */
int ptrc_kdf_derive(
    const uint8_t *master_seed,
    size_t seed_len,
    const uint8_t *context_info,
    size_t info_len,
    uint8_t out_key[PTRC_CRYPT_KEY_BYTES],
    uint8_t out_nonce[PTRC_CRYPT_NONCE_BYTES]
);

/* Streaming XOR Keystream Transformation */
int ptrc_crystal_xor_stream(
    ptrc_crystal_ctx_t *ctx,
    const uint8_t *input,
    uint8_t *output,
    size_t len
);

/* Authenticated Encryption with Associated Data (512-Bit Key / 192-Bit SLIP-MAC) */
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

/* Authenticated Decryption with Constant-Time Tag Verification (returns PTRC_CRYPT_OK or PTRC_CRYPT_ERR) */
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

/* Constant-Time Memory Comparison (returns PTRC_CRYPT_OK if equal, PTRC_CRYPT_ERR otherwise) */
int ptrc_ct_memcmp(const uint8_t *a, const uint8_t *b, size_t len);

/* Volatile SRAM Zeroization -> Restores Z \ {0} Ground State (-1 / 0xFF) */
void ptrc_crystal_wipe(ptrc_crystal_ctx_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* PTRC_CRYSTAL_H */
