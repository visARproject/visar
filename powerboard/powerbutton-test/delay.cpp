#include "delay.h"

constexpr uint32_t count_1us = uint32_t(72000000.0 / 1000000.0);
constexpr uint32_t count_1ms = uint32_t(72000000.0 / 1000.0);
constexpr uint32_t count_40us = 40 * count_1us;
constexpr uint32_t count_40ms = 4000 * count_1us;

inline void delay_loop(uint32_t count)
{
    for (volatile register uint32_t i = count; i != 0; --i) {
        //__asm__("nop");
    }
}

void delay_ms(unsigned long ms){
    delay_loop(ms*count_1ms);
}

void delay_us(unsigned long us){
    delay_loop(us*count_1us);
}
