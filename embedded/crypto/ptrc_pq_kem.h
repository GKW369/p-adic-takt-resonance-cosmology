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

/* File: embedded/crypto/ptrc_pq_kem.h (Complete - Post-Quantum Ring-KEM v4.5.0 FO-CCA2 + comp5) */

#ifndef PTRC_PQ_KEM_H
#define PTRC_PQ_KEM_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Cyclotomic ring Z_q[X]/(X^256 + 1) over non-Mersenne prime q = 7681 (gcd(7681, 210) == 1) */
#define PTRC_KEM_N                  256U
#define PTRC_KEM_Q                  7681U
#define PTRC_KEM_ETA                2U
#define PTRC_KEM_SEED_BYTES         32U
#define PTRC_KEM_POLY_BYTES         512U
#define PTRC_KEM_SS_BYTES           64U
#define PTRC_KEM_MSG_BYTES          32U

/* v4.5.0: 5-bit ciphertext v-compression (256 * 5 / 8 = 160 bytes) halves rounding noise to +-120 */
#define PTRC_KEM_V_COMP_BITS        5U
#define PTRC_KEM_V_COMP_BYTES       160U

/* Profile A (512-Dim Standard, k = 2) */
#define PTRC_KEM_K_STD              2U
#define PTRC_KEM_PK_BYTES_STD       (PTRC_KEM_SEED_BYTES + PTRC_KEM_K_STD * PTRC_KEM_POLY_BYTES)              /* 1056 */
#define PTRC_KEM_SK_BYTES_STD       (PTRC_KEM_K_STD * PTRC_KEM_POLY_BYTES + PTRC_KEM_PK_BYTES_STD + 32U)      /* 2112 */
#define PTRC_KEM_CT_BYTES_STD       (PTRC_KEM_K_STD * PTRC_KEM_POLY_BYTES + PTRC_KEM_V_COMP_BYTES)            /* 1184 */

/* Profile B (256-Dim Ultra-Light IoT, k = 1) */
#define PTRC_KEM_K_LIGHT            1U
#define PTRC_KEM_PK_BYTES_LIGHT     (PTRC_KEM_SEED_BYTES + PTRC_KEM_K_LIGHT * PTRC_KEM_POLY_BYTES)            /* 544  */
#define PTRC_KEM_SK_BYTES_LIGHT     (PTRC_KEM_K_LIGHT * PTRC_KEM_POLY_BYTES + PTRC_KEM_PK_BYTES_LIGHT + 32U)    /* 1088 */
#define PTRC_KEM_CT_BYTES_LIGHT     (PTRC_KEM_K_LIGHT * PTRC_KEM_POLY_BYTES + PTRC_KEM_V_COMP_BYTES)          /* 672  */

/* Default aliases mapped to Profile A (512-Dim Standard) */
#define PTRC_KEM_K                  PTRC_KEM_K_STD
#define PTRC_KEM_PK_BYTES           PTRC_KEM_PK_BYTES_STD
#define PTRC_KEM_SK_BYTES           PTRC_KEM_SK_BYTES_STD
#define PTRC_KEM_CT_BYTES           PTRC_KEM_CT_BYTES_STD

/* Maximum static stack dimensions across all profiles */
#define PTRC_KEM_MAX_K              2U
#define PTRC_KEM_MAX_PK_BYTES       PTRC_KEM_PK_BYTES_STD
#define PTRC_KEM_MAX_SK_BYTES       PTRC_KEM_SK_BYTES_STD
#define PTRC_KEM_MAX_CT_BYTES       PTRC_KEM_CT_BYTES_STD

#define PTRC_KEM_OK                 1
#define PTRC_KEM_ERR                -1

/* Profile-parameterized Fujisaki-Okamoto CCA2 KEM API (k in {1, 2}) */
int ptrc_kem_keygen_ex(
    uint32_t k,
    const uint8_t seed[PTRC_KEM_SEED_BYTES],
    uint8_t *pk,
    uint8_t *sk
);

int ptrc_kem_encaps_ex(
    uint32_t k,
    const uint8_t *pk,
    const uint8_t coins[PTRC_KEM_SEED_BYTES],
    uint8_t *ct,
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
);

int ptrc_kem_decaps_ex(
    uint32_t k,
    const uint8_t *sk,
    const uint8_t *ct,
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
);

/* Profile A (k = 2) convenience wrappers */
int ptrc_kem_keygen(
    const uint8_t seed[PTRC_KEM_SEED_BYTES],
    uint8_t pk[PTRC_KEM_PK_BYTES_STD],
    uint8_t sk[PTRC_KEM_SK_BYTES_STD]
);

int ptrc_kem_encaps(
    const uint8_t pk[PTRC_KEM_PK_BYTES_STD],
    const uint8_t coins[PTRC_KEM_SEED_BYTES],
    uint8_t ct[PTRC_KEM_CT_BYTES_STD],
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
);

int ptrc_kem_decaps(
    const uint8_t sk[PTRC_KEM_SK_BYTES_STD],
    const uint8_t ct[PTRC_KEM_CT_BYTES_STD],
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
);

/* Profile B (k = 1 Ultra-Light IoT) convenience wrappers */
int ptrc_kem_keygen_light(
    const uint8_t seed[PTRC_KEM_SEED_BYTES],
    uint8_t pk[PTRC_KEM_PK_BYTES_LIGHT],
    uint8_t sk[PTRC_KEM_SK_BYTES_LIGHT]
);

int ptrc_kem_encaps_light(
    const uint8_t pk[PTRC_KEM_PK_BYTES_LIGHT],
    const uint8_t coins[PTRC_KEM_SEED_BYTES],
    uint8_t ct[PTRC_KEM_CT_BYTES_LIGHT],
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
);

int ptrc_kem_decaps_light(
    const uint8_t sk[PTRC_KEM_SK_BYTES_LIGHT],
    const uint8_t ct[PTRC_KEM_CT_BYTES_LIGHT],
    uint8_t shared_secret[PTRC_KEM_SS_BYTES]
);

/* Constant-time buffer scrub back to -1 (0xFF) */
void ptrc_kem_wipe(void *buf, size_t len);

#ifdef __cplusplus
}
#endif

#endif /* PTRC_PQ_KEM_H */
