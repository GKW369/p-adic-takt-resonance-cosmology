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
project(ptrc_crypto VERSION 4.6.0 LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

add_library(ptrc_crypto STATIC
    ptrc_crystal.c
    ptrc_crystal.h
    ptrc_pq_kem.c
    ptrc_pq_kem.h
)

add_library(ptrc_crypto_shared SHARED
    ptrc_crystal.c
    ptrc_pq_kem.c
)

set_target_properties(ptrc_crypto_shared PROPERTIES
    OUTPUT_NAME "ptrc_crypto"
    POSITION_INDEPENDENT_CODE ON
)

add_executable(ptrc_crypt_demo
    ptrc_crypt_demo.c
)
target_link_libraries(ptrc_crypt_demo PRIVATE ptrc_crypto)

foreach(tgt IN ITEMS ptrc_crypto ptrc_crypto_shared ptrc_crypt_demo)
    target_include_directories(${tgt} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
    target_compile_options(${tgt} PRIVATE -Wall -Wextra -Werror -Wpedantic -O2)
endforeach()
