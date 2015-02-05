#ifndef XBEE_H
#define XBEE_H

#include <stdint.h>

typedef enum {
    START,
    LENGTH_HIGH,
    LENGTH_LOW,
	TYPE,
    MESSAGE,
    CHECKSUM
} xbee_state_t;

typedef struct {
    uint16_t length;
    uint8_t  type;
    char  payload[128];  //XXX: what is the true maximum payload size?
                            // -- True payload field has max of 100 bytes, 
                            // for type 0x90: api(1) + addr64(8) + addr16(2) + 
                            // rcv options(1) + data(100) + checksum(1) = 113
} xbee_packet_t;

/*
struct xbee_packet_node_t; // forward declare so that the pointer can be a member
struct xbee_packet_node_t {
    xbee_packet_node_t* next;
    xbee_packet_t data;
};
typedef struct xbee_packet_node_t xbee_packet_node_t; // I hate C++ sometimes...

typedef xbee_packet_node_t* xbee_packet_node_link;
*/



/*
bool xbee_list_is_empty(xbee_packet_node_link list);
void xbee_list_push_back(xbee_packet_node_link list_tail, xbee_packet_node_link node);
void xbee_list_push_front(xbee_packet_node_link& list_head, xbee_packet_node_link node);
xbee_packet_node_link xbee_list_pop_front(xbee_packet_node_link& list_head);
*/
void xbee_assemble_tx_packet(xbee_packet_t& tx_pkt, uint64_t addr64, uint16_t addr16, char* data, uint8_t data_len);

#endif

