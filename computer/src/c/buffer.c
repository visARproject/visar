/* 
 * File handles the buffers, not much happening here
 */
 
#include <stdio.h>
#include "buffer.h"
 
//function to create/allocate an empty buffer
audiobuffer* create_buffer(size_t frame_size, size_t frames){
  //Setup the input data buffer
  buf = (audiobuffer*) malloc(sizeof(audiobuffer), 1);
  buf->data = (char*) malloc(frame_size * frames);  //allocate buffer for network input
  buf->frame_size = frame_size;
  buf->size = frames;
  buf->start = 0; 
  buf->end = 0;
  return buf;
}

//free the buffer
void free_buffer(audiobuffer* buf){
  free(buf->data);
  free(buf);
}