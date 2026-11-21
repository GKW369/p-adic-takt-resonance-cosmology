#!/usr/bin/env bash
# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program (see the LICENSE file in the root directory).
# If not, see <https://gnu.org>.
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
