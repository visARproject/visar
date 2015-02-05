#include <string.h>
#include "xbee.h"

xbee_state_t xbee_rx_state = START;
xbee_state_t xbee_tx_state = START;

/*
xbee_packet_node_t packets[8];
xbee_packet_node_link tx_head   = nullptr; // push_back and push_front to tx and rx lists
xbee_packet_node_link tx_tail   = nullptr; 
xbee_packet_node_link rx_head   = nullptr;
xbee_packet_node_link rx_tail   = nullptr;
xbee_packet_node_link pool_head = nullptr; // push_front only to pool head


bool xbee_list_is_empty(xbee_packet_node_link list)
{
    return (list == nullptr) ? true : false;
}

void xbee_list_push_back(xbee_packet_node_link list_tail, xbee_packet_node_link node)
{
    list_tail->next = node;
    node->next = nullptr;
}

void xbee_list_push_front(xbee_packet_node_link& list_head, xbee_packet_node_link node)
{
    node->next = list_head;
    list_head = node;
}

xbee_packet_node_link xbee_list_pop_front(xbee_packet_node_link& list_head)
{
    xbee_packet_node_link tmp = list_head;
    list_head = tmp->next;
    return tmp;
}

*/

void xbee_assemble_tx_packet(xbee_packet_t& tx_pkt, uint64_t addr64, uint16_t addr16, char* data, uint8_t data_len)
{
    tx_pkt.type  = 0x10; // type = transmit request
    tx_pkt.payload[0]  = 0x01; // XXX: FrameID 0x01 -- there ought to be a better thing to put here
    tx_pkt.payload[1]  = (addr64 >> 56) & 0xFF;
    tx_pkt.payload[2]  = (addr64 >> 48) & 0xFF;
    tx_pkt.payload[3]  = (addr64 >> 40) & 0xFF;
    tx_pkt.payload[4]  = (addr64 >> 32) & 0xFF;
    tx_pkt.payload[5]  = (addr64 >> 24) & 0xFF;
    tx_pkt.payload[6]  = (addr64 >> 16) & 0xFF;
    tx_pkt.payload[7]  = (addr64 >> 8 ) & 0xFF;
    tx_pkt.payload[8]  = (addr64      ) & 0xFF;
    tx_pkt.payload[9] = (addr16 >> 8 ) & 0xFF;
    tx_pkt.payload[10] = (addr16      ) & 0xFF;
    tx_pkt.payload[11] = 0x00; // radius
    tx_pkt.payload[12] = 0x00; // options
    memcpy(&(tx_pkt.payload[13]), data, data_len);
    tx_pkt.length = data_len + 14;

    
}

/*
typedef struct {
    uint16_t length;
    uint8_t  type; // should be 0x10 for Transmit Request
    uint8_t  frame_id; // Identifies the UART data frame for the host to match with a subsequent response. If zero, no response is requested.
    uint8_t  addr64[8];
    uint8_t  addr16[2];
    uint8_t  radius;
    uint8_t  options;
    uint8_t  data[100];
    // checksum calculated as packet is sent from usart to radio 
} xbee_tx_packet_t;
*/


