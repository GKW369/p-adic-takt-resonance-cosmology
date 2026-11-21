# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Observer Windtunnel v4.6.0
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
# License: GNU Affero General Public License v3.0 (AGPL-3.0)
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
