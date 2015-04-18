#ifndef GPS_H
#define GPS_H

#include <stdint.h>

const uint8_t GPS_CONF_OUTPUT_FORMAT = 0x09;
const uint8_t GPS_CONF_OUTPUT_RATE = 0x12;
const uint8_t GPS_GET_ALMANAC = 0x11;
const uint8_t GPS_GET_EPHIMERIS = 0x30;
const uint8_t GPS_SW_VER = 0x80;
const uint8_t GPS_SW_CRC = 0x81;
const uint8_t GPS_ACK = 0x83;
const uint8_t GPS_NACK = 0x84;
const uint8_t GPS_ALMANAC = 0x87;
const uint8_t GPS_EPHEMERIS = 0x87;
const uint8_t GPS_MEAS_TIME = 0xDC;
const uint8_t GPS_RAW_MEAS = 0xDD;
const uint8_t GPS_SV_CH_STATUS = 0xDE;
const uint8_t GPS_RCV_STATE = 0xDF;
const uint8_t GPS_SUBFRAME = 0xE0;

typedef enum {
    GPS_START1,
	GPS_START2,
    GPS_LENGTH_HIGH,
    GPS_LENGTH_LOW,
    GPS_MESSAGE,
    GPS_CHECKSUM,
    GPS_END1,
	GPS_END2
} gps_state_t;

typedef struct {
    uint16_t length;
    //uint8_t  type;
    char  payload[256];     //XXX: what is the true maximum payload size?
                            // -- This is currently a guess based on some sample packets captured
} gps_packet_t;

#endif
