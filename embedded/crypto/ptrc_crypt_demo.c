/* ==============================================================================
 * pTRC Framework - Discrete 1-Bit Integer Physics Engine
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


#include <stdio.h>
#include <string.h>
#include "ptrc_crystal.h"

int main(void) {
    const char *master_seed = "GKW369-PRIMORDIAL-SEED-1836";
    const char *kdf_context = "SESSION:01|NODE:ALPHA";
    const char *header_aad  = "NODE:01|RING:P15-MACRO|TAKT:137";
    const char *plaintext   = "MINT-Matrix-Core-Initialized: True. 512-Bit Primorial Macro-Cascade v4.0 Active.";

    uint8_t derived_key[PTRC_KEY_BYTES] = {0};
    uint8_t derived_nonce[PTRC_NONCE_BYTES] = {0};
    uint8_t encrypted[256] = {0};
    uint8_t decrypted[256] = {0};
    uint8_t slip_tag[SLIP_TAG_BYTES] = {0};

    size_t len = strlen(plaintext);
    size_t aad_len = strlen(header_aad);

    printf("\n===========================================================================\n");
    printf("  pTRC FRAMEWORK // v4.0 512-BIT PRIMORIAL MACRO-CASCADE AEAD & KDF        \n");
    printf("===========================================================================\n\n");

    ptrc_kdf_derive((const uint8_t *)master_seed, strlen(master_seed),
                    (const uint8_t *)kdf_context, strlen(kdf_context),
                    derived_key, derived_nonce);

    printf("512-BIT KEY (Hex): ");
    for (size_t i = 0; i < PTRC_KEY_BYTES; i++) printf("%02x", derived_key[i]);
    printf("\n128-BIT NONCE    : ");
    for (size_t i = 0; i < PTRC_NONCE_BYTES; i++) printf("%02x", derived_nonce[i]);
    printf("\n");

    ptrc_aead_encrypt(derived_key, derived_nonce, (const uint8_t *)header_aad, aad_len,
                      (const uint8_t *)plaintext, encrypted, len, slip_tag);

    printf("ENCRYPTED   (Hex): ");
    for (size_t i = 0; i < len; i++) printf("%02x", encrypted[i]);
    printf("\nSLIP-MAC    (Hex): ");
    for (size_t i = 0; i < SLIP_TAG_BYTES; i++) printf("%02x", slip_tag[i]);
    printf("\n\n");

    int ok = ptrc_aead_decrypt(derived_key, derived_nonce, (const uint8_t *)header_aad, aad_len,
                               encrypted, decrypted, len, slip_tag);
    decrypted[len] = '\0';

    printf("RESTORED OUTPUT  : '%s'\n", (char *)decrypted);
    printf("SLIP-MAC AUDIT   : %s\n", ok ? "[ AUTHENTIC - 100% BIT-EXACT ]" : "[ TAMPER DETECTED ]");

    encrypted[0] ^= 0x01;
    int tamper_ok = ptrc_aead_decrypt(derived_key, derived_nonce, (const uint8_t *)header_aad, aad_len,
                                      encrypted, decrypted, len, slip_tag);
    printf("1-BIT TAMPER     : %s\n", (!tamper_ok) ? "[ REJECTED & BUFFER WIPED ]" : "[ FAILED ]");
    printf("===========================================================================\n\n");

    return 0;
}

