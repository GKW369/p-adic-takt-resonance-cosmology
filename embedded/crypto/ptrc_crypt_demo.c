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

/* File: embedded/crypto/ptrc_crypt_demo.c */

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "ptrc_crystal.h"

#define DEMO_BUF_MAX 256U

int main(void) {
    const uint8_t domain_seed[] = "pTRC-v4.0-BARE-METAL-PRIMORIAL-DOMAIN-210";
    uint8_t key[PTRC_CRYPT_KEY_BYTES];
    uint8_t nonce[PTRC_CRYPT_NONCE_BYTES];

    if (ptrc_primorial_keygen(137210144ULL, domain_seed, sizeof(domain_seed) - 1U, key, nonce) != PTRC_CRYPT_OK) {
        printf("ERROR: Keygen failed.\n");
        return 1;
    }

    const uint8_t aad[] = "HDR:pTRC-AEAD-v4.0|512BIT|192MAC";
    const uint8_t msg[] = "Discrete Integer Physics Z \\ {0}: Zero-Table Primorial Macro-Cascade AEAD.";
    const size_t  msg_len = sizeof(msg) - 1U;

    uint8_t ciphertext[DEMO_BUF_MAX];
    uint8_t decrypted[DEMO_BUF_MAX];
    uint8_t tag[PTRC_CRYPT_TAG_BYTES];

    ptrc_crystal_ctx_t inspect_ctx;
    ptrc_crystal_init(&inspect_ctx, key, nonce);

    printf("===============================================================================\n");
    printf("  pTRC CRYPTO ENGINE v4.0 — BARE-METAL C11 512-BIT PRIMORIAL AEAD VERIFICATION\n");
    printf("  Context RAM  : %zu bytes static stack | 144 Facets | Zero malloc | Z \\ {0}\n", sizeof(inspect_ctx));
    printf("  Macro-Rings  : M0=%llu | M1=%llu\n",
           (unsigned long long)(*(inspect_ctx.macro_mod + 0)),
           (unsigned long long)(*(inspect_ctx.macro_mod + 1)));
    printf("===============================================================================\n");
    ptrc_crystal_wipe(&inspect_ctx);

    if (ptrc_aead_encrypt(key, nonce, aad, sizeof(aad) - 1U, msg, msg_len, ciphertext, tag) != PTRC_CRYPT_OK) {
        printf("ERROR: AEAD encryption failed.\n");
        return 1;
    }

    int dec_ok = ptrc_aead_decrypt(key, nonce, aad, sizeof(aad) - 1U, ciphertext, msg_len, tag, decrypted);
    int match_ok = (dec_ok == PTRC_CRYPT_OK && memcmp(msg, decrypted, msg_len) == 0) ? PTRC_CRYPT_OK : PTRC_CRYPT_ERR;
    printf(" + Authentic Decryption & 192-Bit SLIP-MAC : %s\n", (match_ok == PTRC_CRYPT_OK) ? "PASS" : "FAIL");

    /* Tamper test: flip 1 bit in tag -> must reject with PTRC_CRYPT_ERR (-1) */
    uint8_t bad_tag[PTRC_CRYPT_TAG_BYTES];
    memcpy(bad_tag, tag, PTRC_CRYPT_TAG_BYTES);
    *(bad_tag + 0) ^= 0x01U;
    int tamper_rc = ptrc_aead_decrypt(key, nonce, aad, sizeof(aad) - 1U, ciphertext, msg_len, bad_tag, decrypted);
    int tamper_ok = (tamper_rc == PTRC_CRYPT_ERR) ? PTRC_CRYPT_OK : PTRC_CRYPT_ERR;
    printf(" + Tampered Tag Rejection (Constant-Time)  : %s\n", (tamper_ok == PTRC_CRYPT_OK) ? "PASS" : "FAIL");

    printf("-------------------------------------------------------------------------------\n");
    printf("  CRYPTO v4.0 VERIFICATION: %s | SRAM Restored to -1\n",
           (match_ok == PTRC_CRYPT_OK && tamper_ok == PTRC_CRYPT_OK) ? "ALL CHECKS PASSED" : "FAILED");
    printf("===============================================================================\n");
    return (match_ok == PTRC_CRYPT_OK && tamper_ok == PTRC_CRYPT_OK) ? 0 : 1;
}
