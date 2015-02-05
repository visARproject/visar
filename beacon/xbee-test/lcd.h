#ifndef LCD_H
#define LCD_H

void lcd_init(void);
void lcd_string(char* str);

inline void lcd_command(uint8_t cmd);
inline void lcd_data(uint8_t data);

inline void lcd_write_byte(uint8_t b, bool rs_data);
void lcd_poll_busy(void);

#endif
