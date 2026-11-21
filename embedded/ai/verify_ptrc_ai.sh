#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "${BUILD_DIR}"' EXIT

echo "[1/2] Pruefe C11 BitNet-Engine (-Wall -Wextra -Werror)..."
gcc -std=c11 -O2 -Wall -Wextra -Werror -shared -fPIC \
    -I"${SCRIPT_DIR}" \
    "${SCRIPT_DIR}/ptrc_bitnet_engine.c" \
    -o "${BUILD_DIR}/libptrc_bitnet_engine.so"

echo "[2/2] Starte Python Neural-Network Demo/Audit..."
python3 "${SCRIPT_DIR}/00_ptrc_neural_network_demo.py"
echo "[PASS] embedded/ai Build- & Demo-Audit erfolgreich!"
