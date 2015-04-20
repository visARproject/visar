/*
**  File handles the voice control interface
**  Program expects input from the audio controller
**  Program sends decoded audio stream to the audio controller
**/

#include <pocketsphinx.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <time.h>

#define IN_NAME "/tmp/vsr_audio_pipe"
#define OUT_NAME "/tmp/vsr_vc_pipe"
#define DEBUG_FIFO "/tmp/vsr_debug"

void *write_vc(void *fd);

static int write_available = 0; //tells the thread to attempt to write

static int thread_kill = 0; //kill flag for thread

static int thread_err = 0; //err flag for thread

static ps_decoder_t *ps;

static int buffer_size;

int main(int argc, char **argv) {
  buffer_size = 640;

  int fd[2];

  do {
    usleep(50000);
  } while((fd[0] = open(IN_NAME, O_RDONLY)) < 0);
  fd[1] = open(OUT_NAME, O_WRONLY);

  int debug_out = 0;
  debug_out = open(DEBUG_FIFO, O_WRONLY);

  if(debug_out > 0) {
    char *debug_output = "Debug Pipe Created";
    write(debug_out, debug_output, strlen(debug_output));
  }

  int32 k; //number of frames read
  int16 buffer[buffer_size]; //buffer used to store input

  cmd_ln_t *config = cmd_ln_init(NULL, ps_args(), 1,
    "-hmm", MODELDIR "/en-us/en-us",
    "-lm", "./dictionary.lm",
    "-dict", "./dictionary.dic",
    "-logfn", "/dev/null",
    NULL);

  //setup decoder
  ps = ps_init(config);

  //tell thread error 1
  if(ps_start_utt(ps) < 0) {
    thread_err = 1;
  }

  pthread_t thread;
  int rc = pthread_create(&thread, NULL, write_vc, (void *) &fd[1]);

  //tell thread error 2
  if(rc) {
    thread_err = 2;
  }

  //go as long as there's a pipe
  while((k = read(fd[0], buffer, buffer_size)) > 0) {
    write_available = (write_available + 1) % 16; // go between 0 - 15
    ps_process_raw(ps, buffer, k/2, 0, 0); //begins decoding using the number of frames it could read
    write_available = (write_available + 1) % 16; // go between 0 - 15
  }

  thread_kill = 1;

  fd[0].close();
  fd[1].close();

  if(debug_out > 0) {
    debug_out.close();
  }

  return 0;
}

void *write_vc(void *fd) {
  char const *hyp; //hypothesis of decoding, i.e. what pocketsphinx thinks was said
  char new_hyp[640]; //memory for the hypothesis

  int pipe = *((int*) fd);
  char *sentence; //output
  // time_t t = time_sleeper;

  int write_check = 1;

  int c = write_available;

  if(thread_err == 1) {
    sentence = "VCERR:Failed to start utterance\n";
    write(pipe, sentence, strlen(sentence));
  }

  if(thread_err == 2) {
    sentence = "VCERR:Could not create reciever thread\n";
    write(pipe, sentence, strlen(sentence));
  }

  while(!thread_kill) {
    if(c == write_available) {
      if(!write_check) {
        ps_end_utt(ps); //end the utterance
        hyp = ps_get_hyp(ps, NULL); //get the hypothesis
        memcpy(new_hyp, hyp, buffer_size/2); //transfer hyp to prevent corruption
        //if there was no hypothesis, then error
        if(hyp == NULL) {
          sentence = "VCERR:decoding error\n";
        }
        
        if(ps_start_utt(ps) < 0) { //if a new utterance can't begin, then error
          sentence = "VCERR:Failed to start utterance\n";
        } else { //place command in correct form
          sentence = malloc(strlen("VCCOM:") + strlen(new_hyp) + strlen("\n") + 1);
          strcpy(sentence, "VCCOM:");
          strcat(sentence, new_hyp);
          strcat(sentence, "\n");
        }

        write(pipe, sentence, strlen(sentence)); //send results to output pipe
        
        write_check = 1;
      } else {
        usleep(250000);
      }
    } else {
      c = write_available;
      if(write_check) {
        write_check = 0;
      }
      usleep(250000);
    }
  }
}