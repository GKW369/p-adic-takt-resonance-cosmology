/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics & Post-Quantum Ring-KEM v4.2
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

/* File: embedded/crypto/ptrc_pq_kem.h */

#ifndef PTRC_PQ_KEM_H
#define PTRC_PQ_KEM_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Non-Mersenne Lattice Prime Modulus: 7681 = 15 * 512 + 1, gcd(7681, 210) == 1 */
#define PTRC_KEM_Q              7681
#define PTRC_KEM_HALF_Q         3840
#define PTRC_KEM_QUARTER_Q      1920

/* Module-Lattice Parameters (k = 2, n = 256 -> 512-dimensional integer lattice) */
#define PTRC_KEM_K              2U
#define PTRC_KEM_N              256U
#define PTRC_KEM_FACETS         144U
#define PTRC_KEM_TAKT_137       137U
#define PTRC_KEM_PRIMORIAL_210  210U

/* Key & Ciphertext Wire Sizes (Bytes) */
#define PTRC_KEM_SEED_BYTES     32U
#define PTRC_KEM_MSG_BYTES      32U
#define PTRC_KEM_SS_BYTES       64U     /* 512-Bit Shared Secret for ptrc_crystal_init */
#define PTRC_KEM_PK_BYTES       1056U   /* 32B seed_a + 2 * 256 * 2B public vector b */
#define PTRC_KEM_SK_BYTES       1024U   /* 2 * 256 * 2B secret vector s */
#define PTRC_KEM_CT_BYTES       1152U   /* 2 * 256 * 2B vector u + 256 * 4-bit compressed v */

#define PTRC_KEM_OK             1
#define PTRC_KEM_ERR            (-1)

/* Static stack context for Z \ {0} Post-Quantum Ring-KEM (zero malloc) */
typedef struct {
    int32_t  sponge[PTRC_KEM_FACETS];
    uint64_t takt_counter;
    uint32_t quadrant_phase;
} ptrc_kem_ctx_t;

/* Generate an asymmetric Post-Quantum Public/Secret Keypair in Z \ {0} */
int ptrc_kem_keygen(
    uint8_t pk_out[PTRC_KEM_PK_BYTES],
    uint8_t sk_out[PTRC_KEM_SK_BYTES],
    const uint8_t seed[PTRC_KEM_SEED_BYTES]
);

/* Encapsulate a fresh 512-bit shared secret using recipient's Public Key (pk) */
int ptrc_kem_encaps(
    uint8_t ct_out[PTRC_KEM_CT_BYTES],
    uint8_t ss_out[PTRC_KEM_SS_BYTES],
    const uint8_t pk[PTRC_KEM_PK_BYTES],
    const uint8_t coins[PTRC_KEM_SEED_BYTES]
);

/* Decapsulate the 512-bit shared secret using recipient's Secret Key (sk) */
int ptrc_kem_decaps(
    uint8_t ss_out[PTRC_KEM_SS_BYTES],
    const uint8_t ct[PTRC_KEM_CT_BYTES],
    const uint8_t sk[PTRC_KEM_SK_BYTES]
);

/* Scrub KEM context / secret buffers back to Z \ {0} ground state (-1 / 0xFF) */
void ptrc_kem_wipe(void *ptr, size_t len);

#ifdef __cplusplus
}
#endif

#endif /* PTRC_PQ_KEM_H */
