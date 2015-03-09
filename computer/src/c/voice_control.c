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

void start_voice(int* fd) {
  uint8 utt_started = FALSE; //a new utterance check
  uint8 in_speech; //currently taking in speech
  int32 k; //number of frames read
  char const *hyp; //hypothesis of decoding, i.e. what pocketsphinx thinks was said
  int16 buffer[2048]; //buffer used to store input

  //initial configuration for pocketsphinx
  cmd_ln_t *config = cmd_ln_init(NULL, ps_args(), TRUE,
    "-hmm", MODELDIR "/en-us/en-us",
    "-lm", MODELDIR "/en-us/en-us.lm.dmp",
    "-dict", MODELDIR "/en-us/cmudict-en-us.dict",
    NULL);

  //setup decoder
  ps_decoder_t *ps = ps_init(config);

  //begin utterance
  ps_start_utt(ps);

  //go as long as there's a pipe
  while((k = read(fd[0], buffer, 2048)) > 0) {
    char *sentence; //output

    ps_process_raw(ps, buffer, k, FALSE, FALSE); //begins decoding using the number of frames it could read

    in_speech = ps_get_in_speech(ps); //checks to see if there's silence

    //when speech is introduced in each new utterance
    if(in_speech && !utt_started) {
      utt_started = TRUE;
    }

    //once speech is done and utterance has started
    if(!in_speech && utt_started) {
      ps_end_utt(ps); //end the utterance
      hyp = ps_get_hyp(ps, NULL); //get the hypothesis

      //if there was no hypothesis, then error
      if(hyp == NULL) {
        sentence = "VCERR:decoding error\n";
        printf("here0\n");
      } else if(ps_start_utt(ps) < 0) { //if a new utterance can't begin, then error
        printf("here1\n");
        sentence = "VCERR:Failed to start utterance\n";
      } else { //place command in correct form
        sentence = malloc(strlen("VCCOM:") + strlen(hyp) + strlen("\n") + 1);
        printf("%s\n", "here2\n");
        strcpy(sentence, "VCCOM:");
        strcat(sentence, hyp);
        strcat(sentence, "\n");
        printf("%s\n", "1");
      }

      printf("%s\n", sentence);

      // write(fd[1], sentence, 80); //send results to output pipe

      utt_started = FALSE; //reset check back to FALSE
    }

    // usleep(7500);
    memset(buffer, 0, 2048);
  }

  close(fd[1]); //close output pipe
}