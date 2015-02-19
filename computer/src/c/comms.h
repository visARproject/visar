/* Header file that defines the socket handler threads */

//package an address/port with a buffer for comms threads
typedef struct{
  char* addr; //target address (0 for recievers)
  int port; //target port
  audiobuffer* buf; //audio buffer
  int* flag; //thread kill flag
} comms_package;

//funcitons to spawn network send/recieve threads
int start_reciever(int port, audiobuffer* buf, int* flag);
int start_sender(char* addr, int port, audiobuffer* buf, int* flag);

//thread target functions for sending/recieving data (only for use with pthread_create)
void *reciever_thread(void *ptr);
void *sender_thread(void *ptr);

