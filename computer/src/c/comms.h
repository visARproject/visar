/* Header file that defines the socket handler threads */

//package an address/port with a buffer for comms threads
typedef struct{
  int addr; //target address (0 for recievers)
  int port; //target port
  audiobuffer* buf; //audio buffer
  int* flag; //thread kill flag
} comms_package;

//thread functions for sending/recieving data
void *reciever_thread(void *ptr);
void *sender_thread(void *ptr);

