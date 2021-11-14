cmake_minimum_required(VERSION 3.13)
# initialize the SDK based on PICO_SDK_PATH
# note: this must happen before project()
include(pico_sdk_import.cmake)
project(n46pio)
 
pico_sdk_init()

add_executable(n46pio)


pico_generate_pio_header(n46pio ${CMAKE_CURRENT_LIST_DIR}/n64.pio)


target_sources(n46pio PRIVATE
        main.c
        )

target_link_libraries(n46pio PRIVATE pico_stdio pico_stdlib hardware_i2c pico_multicore pico_time pico_sync hardware_pio)
pico_add_extra_outputs(n46pio)

# enable usb output, disable uart output
pico_enable_stdio_usb(n46pio 1)
pico_enable_stdio_uart(n46pio 0)
