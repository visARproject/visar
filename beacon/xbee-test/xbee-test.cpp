#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/cm3/nvic.h>

#include "lcd.h"
#include "delay.h"
#include "xbee.h"
#include "Queue.hpp"


xbee_state_t xbee_rx_state = XBEE_START;
xbee_state_t xbee_tx_state = XBEE_START;

Queue<xbee_packet_t, 10> xbee_rx_queue;
Queue<xbee_packet_t, 10> xbee_tx_queue;

static void clock_setup(void)
{
    // Enable GPIOD clock for LED, LCD & USARTs. 
    rcc_periph_clock_enable(RCC_GPIOD); // LCD Data
    rcc_periph_clock_enable(RCC_GPIOE); // LCD Control
    rcc_periph_clock_enable(RCC_GPIOA); // USART2

    // Enable clocks for USART2 (XBEE).
    rcc_periph_clock_enable(RCC_USART2);
}

static void gpio_setup(void)
{
    // Setup GPIO pin GPIO12 on GPIO port D for LED. 
    gpio_mode_setup(GPIOD, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, GPIO12);
}


static void usart_setup(void)
{
    // Enable the USART2 interrupt. 
    nvic_enable_irq(NVIC_USART2_IRQ);

    // Setup GPIO pins for USART2 transmit. 
    gpio_mode_setup(GPIOA, GPIO_MODE_AF, GPIO_PUPD_NONE, GPIO2);

    // Setup GPIO pins for USART2 receive.
    gpio_mode_setup(GPIOA, GPIO_MODE_AF, GPIO_PUPD_NONE, GPIO3);
    gpio_set_output_options(GPIOA, GPIO_OTYPE_OD, GPIO_OSPEED_25MHZ, GPIO3);

    // Setup USART2 TX and RX pin as alternate function.
    gpio_set_af(GPIOA, GPIO_AF7, GPIO2);
    gpio_set_af(GPIOA, GPIO_AF7, GPIO3);

    // Setup USART2 parameters.
    usart_set_baudrate(USART2, 57600);
    usart_set_databits(USART2, 8);
    usart_set_stopbits(USART2, USART_STOPBITS_1);
    usart_set_mode(USART2, USART_MODE_TX_RX);
    usart_set_parity(USART2, USART_PARITY_NONE);
    usart_set_flow_control(USART2, USART_FLOWCONTROL_NONE);

    // Enable USART2 Receive interrupt. 
    usart_enable_rx_interrupt(USART2);

    // Finally enable the USART.
    usart_enable(USART2);
}

void usart2_isr(void)
{

    static uint8_t rx_checksum = 0x00;
    static uint8_t tx_checksum = 0x00;
    static xbee_packet_t rx_pkt;
    static xbee_packet_t tx_pkt;

    // Check if we were called because of RXNE.
    if (((USART_CR1(USART2) & USART_CR1_RXNEIE) != 0) &&
        ((USART_SR(USART2) & USART_SR_RXNE) != 0)) {

        uint8_t data = usart_recv(USART2);
        static uint16_t rx_index = 0;

        switch (xbee_rx_state) {
            case XBEE_START:
                if (data == 0x7E) {
                    rx_index = 0;
                    rx_checksum = 0;
                    xbee_rx_state = XBEE_LENGTH_HIGH;
                }
                break;
            case XBEE_LENGTH_HIGH:
                rx_pkt.length = ((uint16_t)data << 8) & 0xFF00;
                xbee_rx_state = XBEE_LENGTH_LOW;
                break;
            case XBEE_LENGTH_LOW:
                rx_pkt.length = rx_pkt.length | data;
                xbee_rx_state = XBEE_TYPE;
                break;
            case XBEE_TYPE:
                rx_pkt.type = data;
                rx_checksum += data;
                xbee_rx_state = XBEE_MESSAGE;
                break;
            case XBEE_MESSAGE:
                rx_pkt.payload[rx_index] = data;
                rx_checksum += data;
                ++rx_index;
                if (rx_index == rx_pkt.length-1) {
                    xbee_rx_state = XBEE_CHECKSUM;
                }
                break;
            case XBEE_CHECKSUM:
                if (data == 0xFF-rx_checksum) {
                    xbee_rx_queue.enqueue(rx_pkt);
                }
                xbee_rx_state = XBEE_START;
                break;
        }
    }
    
    // Check if we were called because of TXE.
    if (((USART_CR1(USART2) & USART_CR1_TXEIE) != 0) &&
        ((USART_SR(USART2) & USART_SR_TXE) != 0)) {

        static uint16_t tx_index = 0;

        switch (xbee_tx_state) {
            case XBEE_START:
                if (xbee_tx_queue.isEmpty()) {
                    usart_disable_tx_interrupt(USART2);
                } else { 
                    tx_pkt = xbee_tx_queue.dequeue();
                }
                usart_send(USART2, 0x7E); // XBEE start
                tx_index = 0;
                tx_checksum = 0;
                xbee_tx_state = XBEE_LENGTH_HIGH;
                break;
            case XBEE_LENGTH_HIGH:
                usart_send(USART2, (tx_pkt.length >> 8) & 0xFF);
                xbee_tx_state = XBEE_LENGTH_LOW;
                break;
            case XBEE_LENGTH_LOW:
                usart_send(USART2, (tx_pkt.length) & 0xFF);
                xbee_tx_state = XBEE_TYPE;
                break;
            case XBEE_TYPE:
            	usart_send(USART2, tx_pkt.type);
            	tx_checksum += tx_pkt.type;
                xbee_tx_state = XBEE_MESSAGE;
                break;
            case XBEE_MESSAGE:
                usart_send(USART2, tx_pkt.payload[tx_index]);
                tx_checksum += tx_pkt.payload[tx_index];
                ++tx_index;
                if (tx_index == tx_pkt.length-1) {
                    xbee_tx_state = XBEE_CHECKSUM;
                }
                break;
            case XBEE_CHECKSUM:
                usart_send(USART2, 0xFF-tx_checksum);
                xbee_tx_state = XBEE_START;
                break;
        }
    }
}

int main(void)
{

    clock_setup();
    gpio_setup();
    usart_setup();
    lcd_init();
    lcd_string("------------");
    while (1) {
        __asm__("NOP");

        xbee_packet_t packet;
        if (!(xbee_rx_queue.isEmpty())) {
            gpio_toggle(GPIOD, GPIO12);
            packet = xbee_rx_queue.dequeue();
            if (packet.type != 0x90) {
                continue;
            }
            char str[17];
            strncpy(str, &(packet.payload[11]), 16);
            str[16] = 0;
            lcd_command(0x01); // clear and go home
            lcd_string(str);
        }
        //xbee_assemble_tx_packet(packet, 0x000000000000FFFF, 0xFFFE, "haha", 5);
        //xbee_tx_queue.enqueue(packet);
        //usart_enable_tx_interrupt(USART2);

    }

    return 0;
}


