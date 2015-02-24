/* Header file that defines the socket handler threads */

//package an address/port with a buffer for comms threads
typedef struct{
  char* addr; //target address (0 for recievers)
  int port; //target port
  audiobuffer* buf; //audio buffer
  int* flag; //thread kill flag
} comms_package;

typedef struct{
  int    sock;
  char*  buf;
  size_t len;
  struct sockaddr_in dest;
} sender_handle;

//funcitons to spawn networking treads/objects
int start_reciever(int port, audiobuffer* buf, int* flag);      //start recv thread
sender_handle* setup_sender(char* addr, int port, char* buf, size_t len);  //setup socket and get handle
void destroy_sender(sender_handle* snd);  //cleanup the sender handle, reciever handles itself
int send_packet(sender_handle* snd); //send a single packet using the handler
void *reciever_thread(void *ptr); //thread target funciton for recieving data, ptr is a comms_package. does it's own cleanup

