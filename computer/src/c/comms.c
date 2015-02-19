/* 
 * File handles network send/recieve threads (via UDP)
 */

#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <stdio.h>

#include "audio_controller.h"
#include "buffer.h"
#include "comms.h"

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
  char ack = 0; //define an ack message (have to give pointer)
  int len = sizeof(client); //recieve needs struct length to get client info
  
  //read data from socket until killed
  while(!(*flag) && !global_kill){
    if(!BUFFER_FULL(*buf)){ //read data if space is available
      int bytes = recvfrom(sock, GET_QUEUE_TAIL(*buf),buf->frame_size, 0,\
               (struct sockaddr *)&client, &len); //get an input packet          
      //TODO: look into timeouts
      if(bytes == buf->frame_size){ //ack successful packets, report error otherwise
        bytes = sendto(sock, &ack, 1, 0, (struct sockaddr *)&client,sizeof(client));
        INC_QUEUE_TAIL(*buf); //increment if successful
      } else printf("Error, bad socket read\n"); //report the error
    } else printf("Waiting\n");
  }
  
  close(sock);
  free_buffer(buf);  //free the buffer (TODO: examine placement)
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
  
  //read data from 
  while(!(*flag) && !global_kill){
    if(!BUFFER_FULL(*buf)){ //read data if space is available      
      int bytes = sendto(sock, GET_QUEUE_HEAD(*buf), buf->frame_size, 0,\
          (struct sockaddr *)&dest, sizeof(dest)); //send the packet
      INC_QUEUE_HEAD(*buf); //don't care if it sent or not, assume it did
    }
  }
  
  close(sock);
  free_buffer(buf);  //free the buffer (TODO: examine placement)
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
