cmake_minimum_required(VERSION 3.16)
project(ptrc_game_collision VERSION 4.6.0 LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

foreach(demo_src IN ITEMS
    ptrc_fluid_crystal_3d
    ptrc_crystal_live_3d
    ptrc_crystal_video_1080p
)
    add_executable(${demo_src} "${demo_src}.c")
    target_include_directories(${demo_src} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
    target_compile_options(${demo_src} PRIVATE -Wall -Wextra -Werror -O2)
endforeach()
