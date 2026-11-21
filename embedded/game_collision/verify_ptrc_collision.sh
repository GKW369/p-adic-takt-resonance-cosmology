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

echo "[1/2] Pruefe C11 Game-Collision Engine (-Wall -Wextra -Werror)..."
gcc -std=c11 -O2 -pthread -Wall -Wextra -Werror -shared -fPIC \
    -I"${SCRIPT_DIR}" \
    -I"${REPO_ROOT}/embedded/graphics" \
    "${SCRIPT_DIR}/ptrc_game_collision.c" \
    "${REPO_ROOT}/embedded/graphics/ptrc_light_universe.c" \
    -ldl \
    -o "${BUILD_DIR}/libptrc_game_collision.so"

echo "[2/2] Starte Lockstep-Determinismus- & 0-Tunneling-Audit..."
python3 "${REPO_ROOT}/src/00_ptrc_game_collision_live.py" --audit-only
echo "[PASS] embedded/game_collision Lockstep-, 0-Tunneling- & Build-Audit erfolgreich!"
