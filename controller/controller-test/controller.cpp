#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/cm3/nvic.h>


#include "xbee.h"
#include "gps.h"
#include "Queue.hpp"
#include "delay.h"

#define UP (1 << 4)
#define DOWN (1 << 5)
#define LEFT (1 << 6)
#define RIGHT (1 << 7)
#define CENTER (1 << 8)
#define CTRL (1 << 9)
#define HIDE (1 << 12)

/*
 New USART mapping:
 USART2 - DEBUG   - PA2, PA3
*/

static void clock_setup(void)
{
    // Set STM32 to 72 MHz.
    rcc_clock_setup_in_hse_8mhz_out_72mhz();
    
    // Enable GPIO clocks for USARTs, USB, Reset signals, and GPS Fix/1PPS. 
    rcc_periph_clock_enable(RCC_GPIOA);
    rcc_periph_clock_enable(RCC_GPIOB);
    
    // Enable clocks for USART2 (GPS).
    rcc_periph_clock_enable(RCC_USART2);

}

static void gpio_setup(void)
{    
    // Signal       Pin     Direction
    // USB Pullup   PA1     Output
    // Up           PB4     Input
    // Down         PB5     Input
    // Left         PB6     Input
    // Right        PB7     Input
    // Center       PB8     Input
    // Ctrl         PB9     Input
    // Hide         PB12    Input
    
    gpio_set_mode(GPIOB, GPIO_MODE_INPUT, GPIO_CNF_INPUT_FLOAT, GPIO4 | GPIO5 | GPIO6 | GPIO7 | GPIO8 | GPIO9 | GPIO12);
    gpio_set_mode(GPIOA, GPIO_MODE_OUTPUT_50_MHZ, GPIO_CNF_OUTPUT_PUSHPULL, GPIO1); 
    gpio_set(GPIOA, GPIO1); // initially, both resets are false

}

static void usart_setup(void)
{
// ----BEGIN DEBUG SETUP

    // Setup GPIO pins for USART` transmit.
    gpio_set_mode(GPIOA, GPIO_MODE_OUTPUT_50_MHZ, GPIO_CNF_OUTPUT_ALTFN_PUSHPULL, GPIO_USART2_TX);

    // Setup GPIO pins for USART1 receive.
    gpio_set_mode(GPIOA, GPIO_MODE_INPUT, GPIO_CNF_INPUT_FLOAT, GPIO_USART2_RX);

    // Setup USART1 parameters.
    usart_set_baudrate(USART2, 115200);
    usart_set_databits(USART2, 8);
    usart_set_stopbits(USART2, USART_STOPBITS_1);
    usart_set_mode(USART2, USART_MODE_TX_RX);
    usart_set_parity(USART2, USART_PARITY_NONE);
    usart_set_flow_control(USART2, USART_FLOWCONTROL_NONE);

    // Finally enable the USART.
    usart_enable(USART2);

// ----END DEBUG SETUP

}

int main(void)
{

    uint16_t data_cur = 0, data_prev=0;
    char str[6];
    clock_setup();
    gpio_setup();
    usart_setup();

    while (1) {
        __asm__("NOP");
        data_prev = data_cur;
        data_cur = gpio_port_read(GPIOB) & (GPIO4 | GPIO5 | GPIO6 | GPIO7 | GPIO8 | GPIO9 | GPIO12);
        if(data_cur != data_prev) {
            if(!(data_cur & UP)) {
                sprintf(str, "U\n\r");
                for(int i = 0; i < 6; ++i) 
                    usart_send_blocking(USART2, str[i]);   
            } else if(!(data_cur & DOWN)) {
                sprintf(str, "D\n\r");
                for(int i = 0; i < 6; ++i) 
                    usart_send_blocking(USART2, str[i]);   
            } else if(!(data_cur & LEFT)) {
                sprintf(str, "L\n\r");
                for(int i = 0; i < 6; ++i) 
                    usart_send_blocking(USART2, str[i]);   
            } else if(!(data_cur & RIGHT)) {
                sprintf(str, "R\n\r");
                for(int i = 0; i < 6; ++i) 
                    usart_send_blocking(USART2, str[i]);   
            } else if(!(data_cur & CENTER)) {
                sprintf(str, "C\n\r");
                for(int i = 0; i < 6; ++i) 
                    usart_send_blocking(USART2, str[i]);   
            } else if(!(data_cur & CTRL)) {
                sprintf(str, "E\n\r");
                for(int i = 0; i < 6; ++i) 
                    usart_send_blocking(USART2, str[i]);   
            } else if(!(data_cur & HIDE)) {
                sprintf(str, "H\n\r");
                for(int i = 0; i < 6; ++i) 
                    usart_send_blocking(USART2, str[i]);   
            }
        }
        delay_us(500);


    } // while(1)

    return 0;
}

