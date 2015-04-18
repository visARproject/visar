#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <errno.h>
#include <unistd.h>
#include <cmath>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/stm32/adc.h>

#include "delay.h"

#define UP (1 << 4)
#define DOWN (1 << 5)
#define LEFT (1 << 6)
#define RIGHT (1 << 7)
#define CENTER (1 << 8)
#define CTRL (1 << 9)
#define HIDE (1 << 12)

#define USART_CONSOLE USART2



/*
 New USART mapping:
 USART2 - DEBUG   - PA2, PA3
*/

static void clock_setup(void)
{
    // Set STM32 to 72 MHz.
    rcc_apb1_frequency = 8000000;
    //rcc_clock_setup_in_hse_8mhz_out_72mhz();
    
    // Enable GPIO clocks for USARTs, USB, Reset signals, and GPS Fix/1PPS. 
    rcc_periph_clock_enable(RCC_GPIOA);
    rcc_periph_clock_enable(RCC_GPIOB);
    
    // Enable clocks for USART2 (GPS).
    rcc_periph_clock_enable(RCC_USART2);
    
    rcc_periph_clock_enable(RCC_ADC1);

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
    gpio_set_mode(GPIOA, GPIO_MODE_OUTPUT_10_MHZ, GPIO_CNF_OUTPUT_ALTFN_PUSHPULL, GPIO_USART2_TX);
    gpio_set_mode(GPIOA, GPIO_MODE_INPUT, GPIO_CNF_INPUT_FLOAT, GPIO_USART2_RX);


    usart_set_baudrate(USART_CONSOLE, 115200);
    usart_set_databits(USART_CONSOLE, 8);
    usart_set_stopbits(USART_CONSOLE, USART_STOPBITS_1);
    usart_set_mode(USART_CONSOLE, USART_MODE_TX_RX);
    usart_set_parity(USART_CONSOLE, USART_PARITY_NONE);
    usart_set_flow_control(USART_CONSOLE, USART_FLOWCONTROL_NONE);

    /* Finally enable the USART. */
    usart_enable(USART_CONSOLE);
}


static void adc_setup(void)
{
    gpio_set_mode(GPIOA, GPIO_MODE_INPUT, GPIO_CNF_INPUT_ANALOG, GPIO0);
    //gpio_set_mode(GPIOA, GPIO_MODE_INPUT, GPIO_CNF_INPUT_ANALOG, GPIO1);

    /* Make sure the ADC doesn't run during config. */
    adc_off(ADC1);

    /* We configure everything for one single conversion. */
    adc_disable_scan_mode(ADC1);
    adc_set_single_conversion_mode(ADC1);
    adc_disable_external_trigger_regular(ADC1);
    adc_set_right_aligned(ADC1);
    adc_set_sample_time_on_all_channels(ADC1, ADC_SMPR_SMP_28DOT5CYC);

    adc_power_on(ADC1);

    /* Wait for ADC starting up. */
    int i;
    for (i = 0; i < 800000; i++) /* Wait a bit. */
        __asm__("nop");

    adc_reset_calibration(ADC1);
    adc_calibration(ADC1);
}

static uint16_t read_adc_naiive(uint8_t channel)
{
    uint8_t channel_array[16];
    channel_array[0] = channel;
    adc_set_regular_sequence(ADC1, 1, channel_array);
    adc_start_conversion_direct(ADC1);
    while (!adc_eoc(ADC1));
    uint16_t reg16 = adc_read_regular(ADC1);
    return reg16;
}


float get_voltage(void) {
    float voltage = 0;

    for(int i = 0; i < 20; ++i) {
        voltage += 6*(read_adc_naiive(0)*(3/4095.0));
    }

    return voltage/20.0;
}

int get_percentage(void) {
    return (51.02*get_voltage() - 535.71);

}

int get_kill_status(void) {
    return 0;
}

int main(void) {
    clock_setup();
    
    delay_ms(200);
    
    gpio_clear(GPIOA, GPIO4); // latch power on
    gpio_set_mode(GPIOA, GPIO_MODE_OUTPUT_2_MHZ, GPIO_CNF_OUTPUT_PUSHPULL, GPIO4);
    
    usart_setup();
    adc_setup();
    
    delay_ms(2800);
    
    gpio_set(GPIOA, GPIO5); // use pullup
    gpio_set_mode(GPIOA, GPIO_MODE_INPUT, GPIO_CNF_INPUT_PULL_UPDOWN, GPIO5);
    
    while(true) {
        if(!gpio_get(GPIOA, GPIO5)) break;
        delay_ms(10);
        float voltage = get_voltage();
        if(voltage < 9.5) break;
        char str[100];
        sprintf(str, "voltage: %f\r\n", voltage);
        for(unsigned int i = 0; i < strlen(str); i++) {
            usart_send_blocking(USART_CONSOLE, str[i]);
        }
    }
    //send shutdown signal
    char str[100];
    sprintf(str, "shutdown\r\n");
    for(unsigned int i = 0; i < strlen(str); i++) {
        usart_send_blocking(USART_CONSOLE, str[i]);
    }
    delay_ms(12000);
    // power off
    gpio_set_mode(GPIOA, GPIO_MODE_INPUT, GPIO_CNF_INPUT_FLOAT, GPIO4);
while(true);

    gpio_setup();
    usart_setup();
    adc_setup();

    while(true) {

        char menu_choice = usart_recv_blocking(USART2);
        switch(menu_choice) {
            case 's': {
                int percentage = get_percentage();
                int kill = get_kill_status();
                char str[100];
                sprintf(str, "%i %i\n\r", percentage, kill);
                for(int i = 0; i < 20; ++i) {
                    if(str[i] == 0) break;
                    usart_send_blocking(USART2, (uint16_t)str[i]);
                }
                break;
            }
            case 'k': {
                int shutdown_delay = 0;
                char tmp = usart_recv_blocking(USART2);
                for(int i = 0; tmp != '^';){
                    shutdown_delay *= 10;
                    shutdown_delay += (tmp - 48);
                    tmp = usart_recv_blocking(USART2);
                }
                char str[100];
                sprintf(str, "Kill in %ims\n\r", shutdown_delay);
                for(int i = 0; i < 20; ++i) {
                    if(str[i] == 0) break;
                    usart_send_blocking(USART2, (uint16_t)str[i]);
                }

                delay_ms(shutdown_delay);

                sprintf(str, "Killing.\n\r");
                for(int i = 0; i < 20; ++i) {
                    if(str[i] == 0) break;
                    usart_send_blocking(USART2, (uint16_t)str[i]);
                }

                shutdown_delay = 0;

                break;
            }
            default: break;
        }


        //sprintf(str, "%i\n\r", adc_dat);

        //for(int i = 0; i < 20; ++i) {
        //    if(str[i] == 0) break;
        //    usart_send_blocking(USART2, (uint16_t)str[i]);
        //}

        //delay_ms(10);


    } // while(1)

    return 0;
}

