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
project(ptrc_light_universe VERSION 4.6.0 LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

find_package(Threads REQUIRED)

add_library(ptrc_light_universe STATIC
    ptrc_light_universe.c
    ptrc_light_universe.h
)

add_library(ptrc_light_universe_shared SHARED
    ptrc_light_universe.c
)

set_target_properties(ptrc_light_universe_shared PROPERTIES
    OUTPUT_NAME "ptrc_light_universe"
    POSITION_INDEPENDENT_CODE ON
)

foreach(target_name IN ITEMS ptrc_light_universe ptrc_light_universe_shared)
    target_include_directories(${target_name} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
    target_compile_options(${target_name} PRIVATE
        -Wall
        -Wextra
        -Werror
        -Wpedantic
        -O2
    )
    target_link_libraries(${target_name} PRIVATE
        Threads::Threads
        ${CMAKE_DL_LIBS}
    )
endforeach()
