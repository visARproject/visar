/* Temporary replacement for voice control code to test audio controller */

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

#include "voice_control.h"


void start_voice(int* fd){
  printf("Entered Test function\n");
  char buffer[80]; //buffer for reading data
  char* text = "Piggyback\n";
  int rc = 0;
  write(fd[1],text,11); //test the output stream
  while((rc = read(fd[0], buffer, 80)) > 0){
    //read operation blocks, DO NOT SLEEP.
    printf("Read %d bytes\n",rc);
  }
  printf("Exiting Test function\n");
  
  close(fd[0]); //close our side of input pipe
  close(fd[1]); //close the output pipe
}

