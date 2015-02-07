#ifndef XBEE_H
#define XBEE_H

#include <stdint.h>

typedef enum {
    XBEE_START,
    XBEE_LENGTH_HIGH,
    XBEE_LENGTH_LOW,
	XBEE_TYPE,
    XBEE_MESSAGE,
    XBEE_CHECKSUM
} xbee_state_t;

typedef struct {
    uint16_t length;
    uint8_t  type;
    char  payload[128];  //XXX: what is the true maximum payload size?
                            // -- True payload field has max of 100 bytes, 
                            // for type 0x90: api(1) + addr64(8) + addr16(2) + 
                            // rcv options(1) + data(100) + checksum(1) = 113
} xbee_packet_t;

void xbee_assemble_tx_packet(xbee_packet_t& tx_pkt, uint64_t addr64, uint16_t addr16, char* data, uint8_t data_len);

#endif
