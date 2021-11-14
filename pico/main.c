#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#include "tusb.h"
#include "hardware/gpio.h"
#include "hardware/timer.h"
#include "hardware/i2c.h"

#include "n64.pio.h"

uint32_t seconds_since_boot()
{
    return to_ms_since_boot(get_absolute_time()) / 1000;
}
uint32_t ms_since_boot()
{
    return to_ms_since_boot(get_absolute_time());
}

#include <math.h>
#include <stdio.h>

#define INPUT_UP 240
#define INPUT_LEFT 241
#define INPUT_DOWN 242
#define INPUT_RIGHT 243
#define INPUT_B 244
#define INPUT_A 245
#define INPUT_START 246

#define IINPUT_UP 0
#define IINPUT_LEFT 1
#define IINPUT_DOWN 2
#define IINPUT_RIGHT 3
#define IINPUT_B 4
#define IINPUT_A 5
#define IINPUT_START 6

volatile uint8_t buttons = 0;
volatile int8_t steering_c = 0;

void read_ser()
{
    while (1)
    {
        unsigned int steering_input = getchar_timeout_us(1000);
        if (steering_input != PICO_ERROR_TIMEOUT)
        {
            if (steering_input == 0xff)
            {
                buttons = getchar_timeout_us(10000);
                uint8_t steering_raw = getchar_timeout_us(10000);
                steering_c = ((int)steering_raw) - 128;
                // steering_c = getchar_timeout_us(0);
            }
        }
    }
}

int main()
{
    int button_counter[7] = {0};
    gpio_init(1);
    gpio_pull_up(1);
    gpio_set_dir(1, GPIO_IN);
    stdio_init_all();

    // Choose which PIO instance to use (there are two instances)
    PIO pio = pio0;

    // Our assembled program needs to be loaded into this PIO's instruction
    // memory. This SDK function will find a location (offset) in the
    // instruction memory where there is enough space for our program. We need
    // to remember this location!
    uint offset = pio_add_program(pio, &n64_program);

    // Find a free state machine on our chosen PIO (erroring if there are
    // none). Configure it to run our program, and start it, using the
    // helper function we included in our .pio file.
    uint sm = pio_claim_unused_sm(pio, true);
    pio_sm_config c = n64_program_init(pio, sm, offset, 0, 16.625);

    uint32_t gas_counter = 0;
    float steering_correction = 0;

    printf("Controller enabled.\n");

    multicore_reset_core1();
    multicore_launch_core1(read_ser);

    while (1)
    {
        uint32_t value = pio_sm_get_blocking(pio, sm);
        value = value >> 1;

        if (value == 0x0)
        {
            uint32_t msg =
                reverse(0x05) |
                ((reverse(0x00)) << 8) |
                ((reverse(0x02)) << 16);

            pio_sm_put_blocking(pio, sm, 23);
            pio_sm_put_blocking(pio, sm, msg);
        }
        else if (value == 0x1)
        {

            uint32_t msg = 0;

            msg =
                reverse(buttons) |
                ((reverse(0)) << 8) |
                ((reverse(steering_c)) << 16) |
                ((reverse(0)) << 24);

            pio_sm_put_blocking(pio, sm, 31);
            pio_sm_put_blocking(pio, sm, msg);
        }

        printf("GOTDATA %u\n", value);
    }
    return 0;
}
