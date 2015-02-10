#include <string.h>
#include "xbee.h"

void xbee_assemble_tx_packet(xbee_packet_t& tx_pkt, uint64_t addr64,
        uint16_t addr16, char* data, uint8_t data_len)
{
    tx_pkt.type = 0x10; // type = transmit request
    tx_pkt.payload[0] = 0x01; // XXX: FrameID 0x01 -- there ought to be a better thing to put here
    tx_pkt.payload[1] = (addr64 >> 56) & 0xFF;
    tx_pkt.payload[2] = (addr64 >> 48) & 0xFF;
    tx_pkt.payload[3] = (addr64 >> 40) & 0xFF;
    tx_pkt.payload[4] = (addr64 >> 32) & 0xFF;
    tx_pkt.payload[5] = (addr64 >> 24) & 0xFF;
    tx_pkt.payload[6] = (addr64 >> 16) & 0xFF;
    tx_pkt.payload[7] = (addr64 >> 8) & 0xFF;
    tx_pkt.payload[8] = (addr64) & 0xFF;
    tx_pkt.payload[9] = (addr16 >> 8) & 0xFF;
    tx_pkt.payload[10] = (addr16) & 0xFF;
    tx_pkt.payload[11] = 0x00; // radius
    tx_pkt.payload[12] = 0x00; // options
    memcpy(&(tx_pkt.payload[13]), data, data_len);
    tx_pkt.length = data_len + 14;
}

void xbee_build_header(xbee_packet_t& tx_pkt, uint8_t radius, uint8_t options)
{
    tx_pkt.type = 0x10; // type = transmit request
    tx_pkt.payload[0] = 0x01; // XXX: FrameID 0x01 -- there ought to be a better thing to put here
    // by default, set to addr64 to broadcast address
    tx_pkt.payload[1] = 0x00;
    tx_pkt.payload[2] = 0x00;
    tx_pkt.payload[3] = 0x00;
    tx_pkt.payload[4] = 0x00;
    tx_pkt.payload[5] = 0x00;
    tx_pkt.payload[6] = 0x00;
    tx_pkt.payload[7] = 0xFF;
    tx_pkt.payload[8] = 0xFF;
    // and addr16 to 0xFFFE
    tx_pkt.payload[9] = 0xFF;
    tx_pkt.payload[10] = 0xFE;
    tx_pkt.payload[11] = radius; // radius
    tx_pkt.payload[12] = options; // options
    tx_pkt.length = 14;
}

void xbee_set_dest_addr(xbee_packet_t& tx_pkt, uint64_t addr64, uint16_t addr16)
{
    tx_pkt.payload[1] = (addr64 >> 56) & 0xFF;
    tx_pkt.payload[2] = (addr64 >> 48) & 0xFF;
    tx_pkt.payload[3] = (addr64 >> 40) & 0xFF;
    tx_pkt.payload[4] = (addr64 >> 32) & 0xFF;
    tx_pkt.payload[5] = (addr64 >> 24) & 0xFF;
    tx_pkt.payload[6] = (addr64 >> 16) & 0xFF;
    tx_pkt.payload[7] = (addr64 >> 8) & 0xFF;
    tx_pkt.payload[8] = (addr64) & 0xFF;
    tx_pkt.payload[9] = (addr16 >> 8) & 0xFF;
    tx_pkt.payload[10] = (addr16) & 0xFF;
}
