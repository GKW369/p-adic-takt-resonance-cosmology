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
