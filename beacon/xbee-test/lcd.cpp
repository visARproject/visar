#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>

#include "delay.h"
#include "lcd.h"

void lcd_init(void)
{
    // Setup GPIO pins for LCD.
    gpio_mode_setup(GPIOD, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, 0xFF); // DB7-0 
    gpio_mode_setup(GPIOE, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, 0b00000111); // RS, R/W, E 

    lcd_write_byte(0x38, false);
    delay_ms(40);
    lcd_write_byte(0x0F, false);
    delay_ms(40);
    lcd_write_byte(0x01, false);
    delay_ms(40);

}

void lcd_string(char* str){
    while (*str != 0x00) {
        lcd_data(*str++);
    }
}

inline void lcd_command(uint8_t cmd)
{
    lcd_write_byte(cmd, false);
    delay_us(40);    
    //lcd_poll_busy();
}

inline void lcd_data(uint8_t data)
{
    lcd_write_byte(data, true);
    delay_us(40);  
    //lcd_poll_busy(); // XXX: not working, replaced by above delay -- do I care?
}

inline void lcd_write_byte(uint8_t b, bool rs_data)
{
    //place data
    gpio_port_write(GPIOD, (gpio_port_read(GPIOD) & ~0xFF) | (b & 0xFF));
    //R/W = write
    gpio_clear(GPIOE, GPIO1);
    // rs_data = true --> R/S = 1, else 0
    if (rs_data) {
        gpio_set(GPIOE, GPIO2);    
    } else {
        gpio_clear(GPIOE, GPIO2);
    }
    //set E=true
    gpio_set(GPIOE, GPIO0);
    //wait 500ns or more before falling edge of E
    delay_us(1);
    gpio_clear(GPIOE, GPIO0);
}

void lcd_poll_busy(void)
{
    delay_us(40);
    // set DB7-0 as input temporarily
    gpio_mode_setup(GPIOD, GPIO_MODE_INPUT, GPIO_PUPD_NONE, 0xFF);
    // set R/W to "read"
    gpio_set(GPIOE, GPIO1);
    // set RS to "command"
    gpio_clear(GPIOE, GPIO2);
    uint8_t res = 0;
    do {
        gpio_set(GPIOE, GPIO0); // set enable
        res = gpio_port_read(GPIOD) & (1<<7); // read command register
        delay_us(40); // wait between reads
        gpio_clear(GPIOE, GPIO0); // clear enable            
    } while (res != 0);

    // restore DB7-0 as output
    gpio_mode_setup(GPIOD, GPIO_MODE_INPUT, GPIO_PUPD_NONE, 0xFF);
    // set R/W to "write"
    gpio_clear(GPIOE, GPIO1);
}




