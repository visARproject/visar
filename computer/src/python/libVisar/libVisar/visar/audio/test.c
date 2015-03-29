/* Temporary replacement for voice control code to test audio controller */

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>

#define VC_FIFO    "/tmp/vsr_vc_pipe"
#define AUDIO_FIFO "/tmp/vsr_audio_pipe"

int main(int argc, char** argv){
  printf("Entered Test function\n");
  int fd[2];
  do{
    usleep(50000);
    fd[0] = open(AUDIO_FIFO, O_RDONLY);
    fd[1] = open(VC_FIFO, O_WRONLY);
  } while(fd[0]<0 || fd[1]<0);
  
  char buffer[80]; //buffer for reading data
  write(fd[1],"piggyback\n",10);  
  int rc = 0;
  while((rc = read(fd[0], buffer, 80)) > 0){
    //read operation blocks, DO NOT SLEEP.
    //printf("Read %d bytes\n",rc);
    write(fd[1],"VCCOM:Example\n",14);
  }
  printf("Exiting Test function\n");
  
  close(fd[0]); //close our side of input pipe
  close(fd[1]); //close the output pipe
  printf("Sutdown test program\n");
}

