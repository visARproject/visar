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
  uint8 utt_started = FALSE;
  uint8 in_speech;
  int32 k;
  char const *hyp;
  int16 buffer[2048];

  cmd_ln_t *config = cmd_ln_init(NULL, ps_args(), TRUE,
    "-hmm", MODELDIR "/en-us/en-us",
    "-lm", MODELDIR "/en-us/en-us.lm.dmp"
    "-dict", MODELDIR "/en-us/cmudict-en-us.dict",
    NULL);

  ps_decoder_t *ps = ps_init(config);

  int rv = ps_start_utt(ps);

  while((k = read(fd[0], buffer, 2048)) > 0) {
    char *sentence = "";

    ps_process_raw(ps, buffer, k, FALSE, FALSE);

    in_speech = ps_get_in_speech(ps);

    if(in_speech && !utt_started) {
      utt_started = TRUE;
    }

    if(!in_speech && utt_started) {
      ps_end_utt(ps);
      hyp = ps_get_hyp(ps, NULL);

      if(hyp == NULL) {
        sentence = "VCERR:decoding error\n";
      } else if(ps_start_utt(ps) < 0) {
        sentence = "VCERR:Failed to start utterance\n";
      } else {
        strcat(sentence, "VCCOM:");
        strcat(sentence, hyp);
        strcat(sentence, "\n");
      }

      write(fd[1], sentence, 80);

      utt_started = FALSE;
    }
  }

  close(fd[1]);
}