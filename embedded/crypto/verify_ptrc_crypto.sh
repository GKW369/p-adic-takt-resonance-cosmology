#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "${BUILD_DIR}"' EXIT

echo "[1/2] Pruefe C11-Crypto-Bibliothek & Post-Quantum KEM (-Wall -Wextra -Werror)..."
gcc -std=c11 -O2 -Wall -Wextra -Werror \
    -I"${SCRIPT_DIR}" \
    "${SCRIPT_DIR}/ptrc_crystal.c" \
    "${SCRIPT_DIR}/ptrc_pq_kem.c" \
    "${SCRIPT_DIR}/ptrc_crypt_demo.c" \
    -o "${BUILD_DIR}/ptrc_crypt_demo"

echo "[2/2] Starte Crypto-Selbsttest (ptrc_crypt_demo)..."
"${BUILD_DIR}/ptrc_crypt_demo"
echo "[PASS] embedded/crypto Build- & Laufzeit-Audit erfolgreich!"
