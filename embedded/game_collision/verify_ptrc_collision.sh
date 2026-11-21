#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "${BUILD_DIR}"' EXIT

echo "[1/1] Pruefe C11 3D-Crystal-Collision Targets (-Wall -Wextra -Werror)..."
for src in ptrc_fluid_crystal_3d ptrc_crystal_live_3d ptrc_crystal_video_1080p; do
    echo "  -> Kompiliere ${src}.c..."
    gcc -std=c11 -O2 -Wall -Wextra -Werror \
        -I"${SCRIPT_DIR}" \
        "${SCRIPT_DIR}/${src}.c" \
        -o "${BUILD_DIR}/${src}"
done

echo "[PASS] embedded/game_collision Build-Audit erfolgreich!"
