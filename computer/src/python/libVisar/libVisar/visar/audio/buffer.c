/* 
 * File handles the buffers, not much happening here
 */
 
#include <stdio.h>
#include <stdlib.h>
#include "buffer.h"
 
//function to create/allocate an empty buffer
audiobuffer* create_buffer(size_t period, size_t frame_size, size_t size){
  //Setup the input data buffer
  audiobuffer* buf = (audiobuffer*) malloc(sizeof(audiobuffer));
  buf->data = (char*) malloc(frame_size * period * size);  //allocate buffer for network input
  buf->frame_size = frame_size;
  buf->period = period;
  buf->per_size = period*frame_size;
  buf->size = size;
  buf->start = 0; 
  buf->end = 0;
  //printf("Buffer: %d, %d, %d\n",(int)period, (int)frame_size, (int)size);
  return buf;
}

//free the buffer
void free_buffer(audiobuffer* buf){
  free(buf->data);
  free(buf);
}
