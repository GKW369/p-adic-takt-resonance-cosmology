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

cmake_minimum_required(VERSION 3.16)
project(pTRC_Framework_C11 C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CRYPTO_DIR "${CMAKE_CURRENT_SOURCE_DIR}/embedded/crypto")
set(AI_DIR     "${CMAKE_CURRENT_SOURCE_DIR}/embedded/ai")
set(SRC_DIR    "${CMAKE_CURRENT_SOURCE_DIR}/src")

# Output shared libraries and 00_ executables directly to build/
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")

# ==============================================================================
# 1. CRYPTO v4.0 — 512-Bit Zero-Table Primorial AEAD & KDF
# ==============================================================================
add_library(ptrc_crystal SHARED
    "${CRYPTO_DIR}/ptrc_crystal.c"
)
target_include_directories(ptrc_crystal PUBLIC "${CRYPTO_DIR}")

add_executable(00_ptrc_crypt_demo
    "${SRC_DIR}/00_ptrc_crypt_demo.c"
    "${CRYPTO_DIR}/ptrc_crystal.c"
)
target_include_directories(00_ptrc_crypt_demo PRIVATE "${CRYPTO_DIR}")

# ==============================================================================
# 2. AI v2.0 — 1-Bit Resonant BitNet Crystalline Inference Engine
# ==============================================================================
add_library(ptrc_bitnet SHARED
    "${AI_DIR}/ptrc_bitnet_engine.c"
)
target_include_directories(ptrc_bitnet PUBLIC "${AI_DIR}")

add_executable(00_ptrc_bitnet_demo
    "${SRC_DIR}/00_ptrc_bitnet_demo.c"
    "${AI_DIR}/ptrc_bitnet_engine.c"
)
target_include_directories(00_ptrc_bitnet_demo PRIVATE "${AI_DIR}")

# ==============================================================================
# STRICT COMPILER FLAGS (ZERO WARNINGS)
# ==============================================================================
foreach(target ptrc_crystal 00_ptrc_crypt_demo ptrc_bitnet 00_ptrc_bitnet_demo)
    if(MSVC)
        target_compile_options(${target} PRIVATE /W4 /O2)
    else()
        target_compile_options(${target} PRIVATE -O3 -Wall -Wextra -Wpedantic)
    endif()
endforeach()

