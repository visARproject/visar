#ifndef XBEE_H
#define XBEE_H

#include <stdint.h>

const int MAX_FRAG_LENGTH = 245;// max bytes of payload used for fragmented packet
                                //     needs to take into account the 1 byte packet type,
                                //     1 byte packet ID, and 2 bytes of "X of Y" fragment identifier
                                // XXX: calculate the correct length (this is empirically chosen?)

const uint8_t TYPE_SKYTRAQ = 0xAC;  // chosen by random survey

const size_t INDEX_TYPE = 13;
const size_t INDEX_ID = 14;
const size_t INDEX_X = 15;
const size_t INDEX_Y = 16;
const size_t INDEX_SKYTRAQ_START = 17;

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
    uint8_t type;
    char payload[256];     //XXX: what is the true maximum payload size?
                           // -- True payload field has max of 100 bytes,
                           // for type 0x90: api(1) + addr64(8) + addr16(2) +
                           // rcv options(1) + data(100) + checksum(1) = 113
} xbee_packet_t;

void xbee_assemble_tx_packet(xbee_packet_t& tx_pkt, uint64_t addr64,
        uint16_t addr16, char* data, uint8_t data_len);

void xbee_build_header(xbee_packet_t& tx_pkt, uint8_t radius = 0x00, uint8_t options = 0x00);
void xbee_set_dest_addr(xbee_packet_t& tx_pkt, uint64_t addr64, uint16_t addr16);

#endif
