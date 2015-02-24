/* 
 * File handles network send/recieve threads (via UDP)
 */

#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>

#include "audio_controller.h"
#include "buffer.h"
#include "comms.h"
#include "encode.h"

//function for recieving audio
void *reciever_thread(void *ptr){
  audiobuffer* buf = ((comms_package*)ptr)->buf; //extract the buffer
  int port = ((comms_package*)ptr)->port; //get the port
  int* flag = ((comms_package*)ptr)->flag; //get the kill flag
  free(ptr); //free the package's memory
  
  //setup the scoket
  int sock = socket(PF_INET, SOCK_DGRAM, 0); // setup UDP socket
  struct sockaddr_in addr, client; //create address structs for socket/clients
  addr.sin_family = AF_INET;  //using internet protocols
  addr.sin_port = htons(port); //convert to correct byte format
  addr.sin_addr.s_addr = htonl(INADDR_ANY); //socket is server, must accept any connection
  bind(sock, (struct sockaddr*)&addr, sizeof(addr)); //bind socket
  struct timeval tv;  //setup the timeout
  tv.tv_sec = 1;
  tv.tv_usec = 0;
  setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO,&tv,sizeof(tv)); //set the timeout
  int true = 1;
  setsockopt(sock,SOL_SOCKET,SO_REUSEADDR,&true,sizeof(int)); //allow socket reuse
  
  
  char ack = 0; //define an ack message (have to give pointer)
  int len = sizeof(client);  //recieve needs struct length to get client info
  char decode_buf[buf->per_size]; //allocate buffer for recieving data pre decode
  
  //read data from socket until killed
  while(!(*flag) && !global_kill){
    if(!BUFFER_FULL(*buf)){ //read data if space is available
      int bytes = recvfrom(sock, decode_buf, buf->per_size, 0, (struct sockaddr *)&client, &len); //get an input packet
      //printf("%d\n",bytes); 
      //TODO: timeouts
      if(bytes > 0){ //ack successful packets, report error otherwise
        decode(decode_buf, GET_QUEUE_TAIL(*buf), bytes); //decode the input
        //write(stdout, GET_QUEUE_TAIL(*buf), buf->per_size); //DEBUG
        INC_QUEUE_TAIL(*buf); //increment if successful
        //bytes = sendto(sock, &ack, 1, 0, (struct sockaddr *)&client,sizeof(client)); //send an ack
      } else printf("Error, bad socket read: %d\n",bytes); //report the error
      //printf("buffer: (%d, %d, %d)\n", buf->start, buf->end, BUFFER_SIZE(*buf));
    } else {
      //printf("Waiting\n");
      usleep(PERIOD_UTIME/2);
    }
  }
  
  close(sock);
  free_buffer(buf);  //free the buffer (TODO: examine placement)
  printf("Audio Controller: Reciever Thread shutdown\n");
  pthread_exit(NULL); //exit thread safetly
}

//function for sending audio
void *sender_thread(void *ptr){
  audiobuffer* buf = ((comms_package*)ptr)->buf; //extract the buffer
  char* host = ((comms_package*)ptr)->addr; //get the address
  int port = ((comms_package*)ptr)->port; //get the port
  int* flag = ((comms_package*)ptr)->flag; //get the kill flag
  free(ptr); //free the package's memory
  
  //setup the scoket
  int sock = socket(PF_INET, SOCK_DGRAM, 0); // setup UDP socket
  struct sockaddr_in addr, dest; //create address structs for socket
  addr.sin_family = AF_INET;  //using internet protocols
  addr.sin_port = htons(0);   //port doesn't matter
  addr.sin_addr.s_addr = htonl(INADDR_ANY); //don't care what our address is
  bind(sock, (struct sockaddr*)&addr, sizeof(addr)); //bind socket
  dest.sin_family = AF_INET;  //setup the target address
  dest.sin_port = htons(port); //set the destination port
  inet_aton(host, &dest.sin_addr); //set the target address
  char encode_buf[buf->per_size]; //allocate buffer for encoded data
  int true = 1;
  setsockopt(sock,SOL_SOCKET,SO_REUSEADDR,&true,sizeof(int)); //allow socket reuse
  
  
  //read data from 
  while(!(*flag) && !global_kill){
    if(!BUFFER_FULL(*buf)){ //read data if space is available  
      int bytes = encode(GET_QUEUE_HEAD(*buf), encode_buf, buf->per_size); //encode the data
      INC_QUEUE_HEAD(*buf); //increment queue head
      bytes = sendto(sock, encode_buf, bytes, 0, (struct sockaddr *)&dest, sizeof(dest)); //send the packet
    } else {
      usleep(PERIOD_UTIME/2);
    }
  }
  
  close(sock);
  free_buffer(buf);  //free the buffer (TODO: examine placement)
  printf("Audio Controller: Sender Thread shutdown\n");
  pthread_exit(NULL); //exit thread safetly
}

//spawn a reciever thread, requires an input port, buffer, and thread; returns the pthread status code
int start_reciever(int port, audiobuffer* buf, int* flag){
  //package the info needed by the handler
  comms_package* pkg = (comms_package*)malloc(sizeof(comms_package));
  pkg->addr = 0;
  pkg->port = port;
  pkg->buf  = buf;
  pkg->flag = flag;
  
  //create thread and send it the package
  pthread_t thread; //thread handler
  int rc = pthread_create(&thread, NULL, reciever_thread, (void*)pkg);
  if (rc) printf("ERROR: Could not create reciever thread, rc=%d\n", rc); //print errors
  
  return rc; //return the response code
}

//start the sender therad, requires address, port, buffer, and kill flag; returns the pthread status code
int start_sender(char* addr, int port, audiobuffer* buf, int* flag){
  //package the info needed by the handler
  comms_package* pkg = (comms_package*)malloc(sizeof(comms_package));
  pkg->addr = addr;
  pkg->port = port;
  pkg->buf  = buf;
  pkg->flag = flag;
  
  //create thread and send it the package
  pthread_t thread; //thread handler
  int rc = pthread_create(&thread, NULL, sender_thread, (void*)pkg);
  if (rc) printf("ERROR: Could not create reciever thread, rc=%d\n", rc); //print errors
  
  return rc; //return the response code
}
