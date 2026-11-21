#!/usr/bin/env bash
# ==============================================================================
# pTRC Framework - Build- & Paritaets-Audit fuer ptrc_light_universe v4.6.0
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
# License: GNU Affero General Public License v3.0 (AGPL-3.0)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "${BUILD_DIR}"' EXIT

echo "[1/4] Pruefe C11-Bibliothek mit strikten Compiler-Flags (-Wall -Wextra -Werror)..."
gcc -std=c11 -O2 -pthread -Wall -Wextra -Werror -shared -fPIC \
    -I"${SCRIPT_DIR}" \
    "${SCRIPT_DIR}/ptrc_light_universe.c" \
    -ldl \
    -o "${BUILD_DIR}/libptrc_light_universe.so"

if command -v cmake >/dev/null 2>&1; then
    echo "[2/4] Pruefe CMake-Build (Static + Shared)..."
    cmake -S "${SCRIPT_DIR}" -B "${BUILD_DIR}/cmake" >/dev/null
    cmake --build "${BUILD_DIR}/cmake" -j >/dev/null
else
    echo "[2/4] CMake nicht installiert — ueberspringe CMake-Schritt."
fi

echo "[3/4] Starte C11 <-> Python Bit-Paritaets- & Nullfreiheits-Audit (Z^3 \\ {0})..."
python3 "${REPO_ROOT}/src/00_test_ptrc_graphics_parity.py"

echo "[4/4] Kurz-Benchmark (3 Sekunden) zur Laufzeit-Verifikation..."
python3 "${REPO_ROOT}/src/00_benchmark_ptrc_graphics.py" --seconds 3

echo "[PASS] Alle Build-, Paritaets- und Laufzeit-Checks fuer v4.6.0 erfolgreich!"
