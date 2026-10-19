cmake_minimum_required(VERSION 3.20)
project(serialscope_firmware C)
option(DEMO_MODE "Send generated ramp instead of ADC measurements" ON)
set(VREF_MV 3300 CACHE STRING "Measured ADC reference voltage in millivolts")
add_executable(serialscope src/main.c src/startup.c)
set_target_properties(serialscope PROPERTIES SUFFIX ".elf")
target_compile_options(serialscope PRIVATE -mcpu=cortex-m3 -mthumb -Os -ffreestanding -ffunction-sections -fdata-sections -Wall -Wextra -Werror)
target_compile_definitions(serialscope PRIVATE DEMO_MODE=$<BOOL:${DEMO_MODE}> VREF_MV=${VREF_MV})
target_link_options(serialscope PRIVATE -mcpu=cortex-m3 -mthumb -nostdlib -T${CMAKE_CURRENT_SOURCE_DIR}/stm32f103c8.ld -Wl,--gc-sections -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/serialscope.map)
add_custom_command(TARGET serialscope POST_BUILD
 COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:serialscope> ${CMAKE_CURRENT_BINARY_DIR}/serialscope.bin
 COMMAND ${CMAKE_SIZE} $<TARGET_FILE:serialscope>)
