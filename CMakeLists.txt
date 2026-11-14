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
project(pTRC_Crystal_Crypto C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CRYPTO_DIR "${CMAKE_CURRENT_SOURCE_DIR}/embedded/crypto")

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")

# 1. Shared C11 library (for Python ctypes parity & benchmark verification)
add_library(ptrc_crystal SHARED
    "${CRYPTO_DIR}/ptrc_crystal.c"
)

target_include_directories(ptrc_crystal PUBLIC
    "${CRYPTO_DIR}"
)

if(MSVC)
    target_compile_options(ptrc_crystal PRIVATE /W4 /O2)
else()
    target_compile_options(ptrc_crystal PRIVATE -O3 -Wall -Wextra -Wpedantic)
endif()

# 2. Standalone C11 v4.0 512-bit AEAD & KDF demonstration executable
add_executable(ptrc_hardware_demo
    "${CRYPTO_DIR}/ptrc_crypt_demo.c"
    "${CRYPTO_DIR}/ptrc_crystal.c"
)

target_include_directories(ptrc_hardware_demo PRIVATE
    "${CRYPTO_DIR}"
)

if(MSVC)
    target_compile_options(ptrc_hardware_demo PRIVATE /W4 /O2)
else()
    target_compile_options(ptrc_hardware_demo PRIVATE -O3 -Wall -Wextra -Wpedantic)
endif()
