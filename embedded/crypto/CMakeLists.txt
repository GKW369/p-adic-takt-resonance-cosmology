<!--
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

# -*- coding: utf-8 -*-
-->

cmake_minimum_required(VERSION 3.16)
project(ptrc_crystal_aead VERSION 3.3.0 LANGUAGES C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Static Bare-Metal Library (Zero FPU, Zero Dynamic Memory)
add_library(ptrc_crystal STATIC
    ptrc_crystal.c
    ptrc_crystal.h
)

target_include_directories(ptrc_crystal PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_compile_options(ptrc_crystal PRIVATE
    -O3
    -Wall
    -Wextra
    -Wpedantic
    -Wconversion
)

# Standalone Verification Executable
add_executable(ptrc_hardware_demo
    ptrc_crypt_demo.c
)

target_link_libraries(ptrc_hardware_demo PRIVATE ptrc_crystal)

Verwende Code mit Vorsicht.

So bauen Entwickler das Modul mit CMake:

bash
cd embedded/crypto
cmake -B build && cmake --build build
./build/ptrc_hardware_demo
