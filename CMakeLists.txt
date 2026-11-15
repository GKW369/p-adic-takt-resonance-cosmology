cmake_minimum_required(VERSION 3.16)
project(pTRC_Framework VERSION 4.0.0 LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

if(MSVC)
    add_compile_options(/W4 /WX)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -O3)
endif()

# ------------------------------------------------------------------------------
# 1. C11 Bare-Metal Cryptographic Engine v4.0 (Shared Library for ctypes + Demo)
# ------------------------------------------------------------------------------
add_library(ptrc_crystal SHARED
    embedded/crypto/ptrc_crystal.c
)
target_include_directories(ptrc_crystal PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/embedded/crypto
)

add_executable(ptrc_crypt_demo
    embedded/crypto/ptrc_crypt_demo.c
    embedded/crypto/ptrc_crystal.c
)
target_include_directories(ptrc_crypt_demo PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/embedded/crypto
)

# ------------------------------------------------------------------------------
# 2. C11 Bare-Metal Resonant BitNet AI Engine v2.0 (Shared Library + Demo)
# ------------------------------------------------------------------------------
add_library(ptrc_bitnet SHARED
    embedded/ai/ptrc_bitnet_engine.c
)
target_include_directories(ptrc_bitnet PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/embedded/ai
)

add_executable(00_ptrc_bitnet_demo
    src/00_ptrc_bitnet_demo.c
    embedded/ai/ptrc_bitnet_engine.c
)
target_include_directories(00_ptrc_bitnet_demo PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/embedded/ai
)

# ------------------------------------------------------------------------------
# 3. C11 Bare-Metal Physics Core (Optional build if embedded/c/ptrc_core.c exists)
# ------------------------------------------------------------------------------
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/embedded/c/ptrc_core.c")
    add_library(ptrc_core SHARED
        embedded/c/ptrc_core.c
    )
    target_include_directories(ptrc_core PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/embedded/c
    )

    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/embedded/c/main.c")
        add_executable(ptrc_demo
            embedded/c/main.c
            embedded/c/ptrc_core.c
        )
        target_include_directories(ptrc_demo PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/embedded/c
        )
    endif()
endif()
