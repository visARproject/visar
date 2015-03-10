/*
 *  File handles the voice control interface
 *  Program expects input from the audio controller
 *  Program sends decoded audio stream to the audio controller
 */

#include <pocketsphinx.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>

void start_voice(int* fd) {
  uint8 utt_started = FALSE; //a new utterance check
  uint8 in_speech; //currently taking in speech
  int32 k; //number of frames read
  char const *hyp; //hypothesis of decoding, i.e. what pocketsphinx thinks was said
  int16 buffer[2048]; //buffer used to store input
  char new_hyp[2048]; //memory for the hypothesis
  char time_gate_pass = 0;
  int f;

  //initial configuration for pocketsphinx
  cmd_ln_t *config = cmd_ln_init(NULL, ps_args(), TRUE,
    "-hmm", MODELDIR "/en-us/en-us",
    "-lm", MODELDIR "/en-us/en-us.lm.dmp",
    "-dict", MODELDIR "/en-us/cmudict-en-us.dict",
    "-logfn", "/dev/null",
    NULL);

  //setup decoder
  ps_decoder_t *ps = ps_init(config);

  //begin utterance
  ps_start_utt(ps);

  time_t start_time_in_speech;
  time_t current_time;
  struct tm * timeinfo;

  f = open("audio_data.raw", O_CREAT | O_WRONLY, 0666);
  printf("%d\n", f);

  //go as long as there's a pipe
  while((k = read(fd[0], buffer, 2048)) > 0) {
    write(f, buffer, k);
    // printf("%d\n", k);

    char *sentence; //output

    ps_process_raw(ps, buffer, k, FALSE, FALSE); //begins decoding using the number of frames it could read

    in_speech = ps_get_in_speech(ps); //checks to see if there's silence

    //when speech is introduced in each new utterance
    if(in_speech && !utt_started) {
      utt_started = TRUE;
      time(&start_time_in_speech);
      printf("Listening...\n");
    }
    else if(utt_started) {
      // printf("Time elapsed: %d\n", time(0) - start_time_in_speech );
      if( time(0) - start_time_in_speech > 5 ) {
        time_gate_pass = 1;
        printf("No longer listening.\n");
      }
    }

    //once speech is done and utterance has started
    if(!in_speech && utt_started && time_gate_pass) {
      ps_end_utt(ps); //end the utterance
      hyp = ps_get_hyp(ps, NULL); //get the hypothesis
      memcpy(new_hyp, hyp, 2048); //transfer hyp to prevent corruption

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

      write(fd[1], sentence, strlen(sentence)); //send results to output pipe

      utt_started = FALSE; //reset check back to FALSE
      time_gate_pass = 0;
    }

    //usleep(100000);
    memset(buffer, 0, 2048);
  }

  close(fd[1]); //close output pipe
}