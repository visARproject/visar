#include <cstdlib>
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/cm3/nvic.h>

#include "lcd.h"
#include "delay.h"
#include "xbee.h"



template <class T, size_t size>
class Queue {
	T backend[size];

	// read will point to the next item to be dequeued, write will point to first empty spot
	// -- three cases:
	// -- -- 1. read pointer less than write pointer    -- elements in queue
	// -- -- 2. read pointer greater than write pointer -- wrap-around; there remains room unless read == write
	// -- -- 3. read pointer equal to write pointer     -- empty if no wrap-around, full if wrap-around
	int read, write;

	// necessary to calculate the size, unless we use a std::array or std::vector,
	// but the first requires a known size at compile-time, and the second is overkill
	//size_t size;

	// I think there's a way to do without this if we let the read/write pointers grow
	// past the max size, but we'd have to perform modulo operations constantly for each enqueue/dequeue, which can be expensive
	// (what if we made a lookup table to precompute the possible remainders? then we'd be using another array...)
	bool wrapped;

public:
	Queue() : read(0), write(0), wrapped(false) {

	};

	bool isEmpty(){
		if(read == write && !wrapped){
			return true;
		} else {
			return false;
		}
	}

	bool isFull(){
		if(read == write && wrapped){
			return true;
		} else {
			return false;
		}
	}

	void enqueue(T in){
		if(this->isFull()){
			return; // don't try to write to a full queue!
		}

		backend[write] = in;
		if(write == size - 1){ // if we exceed the size, wrap around to zero
			write = 0;
			wrapped = true;
		} else {
			write++;
		}
	}

	T dequeue(){
		if(this->isEmpty()){
			return backend[read]; // not sure how to handle this,
								  // so let's just return the last element
								  // and not mess up the read/write pointers
		}

		int tmp = read;
		if(read == size - 1){ // if we exceed the size, reset to zero...
			read = 0;
			wrapped = false; // ... but now read is less than write and we are un-wrapped
		} else {
			read++;
		}
		return backend[tmp];
	}

	size_t current_size(){
		if(wrapped){
			return size+write-read;
		} else {
			return write-read;
		}
	}

};

extern xbee_state_t xbee_rx_state;
extern xbee_state_t xbee_tx_state;

Queue<xbee_packet_t, 10> xbee_tx_queue;

static void clock_setup(void)
{
    // Enable GPIOD clock for LED, LCD & USARTs. 
    rcc_periph_clock_enable(RCC_GPIOD);
    rcc_periph_clock_enable(RCC_GPIOE);
    rcc_periph_clock_enable(RCC_GPIOA);

    // Enable clocks for USART2.
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
//    usart_enable_rx_interrupt(USART2);

    // Finally enable the USART.
    usart_enable(USART2);
}


void usart2_isr(void)
{

    static uint8_t rx_checksum = 0x00;
    static uint8_t tx_checksum = 0x00;
    static xbee_packet_t tx_pkt;

/*
    static uint8_t data = 'A';
    // Check if we were called because of RXNE.
    if (((USART_CR1(USART2) & USART_CR1_RXNEIE) != 0) &&
        ((USART_SR(USART2) & USART_SR_RXNE) != 0)) {

        // Indicate that we got data.
        gpio_toggle(GPIOD, GPIO12);

        // Retrieve the data from the peripheral.
        data = usart_recv(USART2);

        // Enable transmit interrupt so it sends back the data.
        usart_enable_tx_interrupt(USART2);
    }
*/
    
    // Check if we were called because of TXE.
    if (((USART_CR1(USART2) & USART_CR1_TXEIE) != 0) &&
        ((USART_SR(USART2) & USART_SR_TXE) != 0)) {

        static uint16_t tx_index = 0;
        switch(xbee_tx_state) {
            case START:
                if (xbee_tx_queue.isEmpty()) {
                    usart_disable_tx_interrupt(USART2);
                } else { 
                    tx_pkt = xbee_tx_queue.dequeue();
                }
                usart_send(USART2, 0x7E); // XBEE start
                tx_index = 0;
                tx_checksum = 0;
                xbee_tx_state = LENGTH_HIGH;
                break;
            case LENGTH_HIGH:
                usart_send(USART2, (tx_pkt.length >> 8) & 0xFF);
                xbee_tx_state = LENGTH_LOW;
                break;
            case LENGTH_LOW:
                usart_send(USART2, (tx_pkt.length) & 0xFF);
                xbee_tx_state = TYPE;
                break;
            case TYPE:
            	usart_send(USART2, tx_pkt.type);
            	tx_checksum += tx_pkt.type;
                xbee_tx_state = MESSAGE;
            	break;
            case MESSAGE:
                usart_send(USART2, tx_pkt.payload[tx_index]);
                tx_checksum += tx_pkt.payload[tx_index];
                tx_index++;
                if (tx_index == tx_pkt.length-1) {
                    xbee_tx_state = CHECKSUM;
                }
                break;
            case CHECKSUM:
                usart_send(USART2, 0xFF-tx_checksum);
                xbee_tx_state = START;
                usart_disable_tx_interrupt(USART2);
                break;
        }
    }
}

int main(void)
{
/*
    for (int i = 0; i != 8; ++i) {
        xbee_list_push_front(pool_head, &packets[i]); // fill pool
    }
*/  
    clock_setup();
    gpio_setup();
    usart_setup();
    lcd_init();
    
    while (1) {
        __asm__("NOP");
        gpio_toggle(GPIOD, GPIO12);

        xbee_packet_t packet;
        xbee_assemble_tx_packet(packet, 0x000000000000FFFF, 0xFFFE, "haha", 5);
        xbee_tx_queue.enqueue(packet);
        usart_enable_tx_interrupt(USART2);
        delay_ms(100);
//        xbee_assemble_tx_packet(xbee_packet_node_link tx_pkt, uint64_t addr64, uint16_t addr16, uint8_t* data, uint8_t data_len)

    }

    return 0;
}


