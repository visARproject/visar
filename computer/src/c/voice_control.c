/*
 *  File handles the voice control interface
 *  Program expects input from the audio controller
 *  Program sends decoded audio stream to the audio controller
 */

#include <pocketsphinx.h>

void start_voice(int* fd) {
  char const *hyp;
  char buffer[80];
  int16 buf[512];
  int32 score;

  cmd_ln_t *config = cmd_ln_init(NULL, ps_args(), TRUE,
    "-hmm", MODELDIR "/en-us/en-us",
    "-lm", MODELDIR "/en-us/en-us.lm.dmp"
    "-dict", MODELDIR "/en-us/cmudict-en-us.dict",
    NULL);

  ps_decoder_t *ps = ps_init(config);

  int rv = ps_start_utt(ps);

  while(read(fd[0], buffer, 80) > 0) {
    char *sentence = "";

    while(!feof(fd[0])) {
      size_t nsamp = fread(buf, 2, 512, fd[0]);
      rv = ps_process_raw(ps, buf, nsamp, FALSE, FALSE);
    }

    rv = ps_end_utt(ps);
    hyp = ps_get_hyp(ps, &score);

    if(rv < 0) {
      sentence = "VCERR:frame searching error\n"
    } else if(hyp == NULL) {
      sentence = "VCERR:decoding error\n"
    } else {
      sentence = "VCCOM:" + hyp + "\n";
    }

    write(fd[1], sentence, 80);
  }

  ps_free(ps);
  cmd_ln_free_r(config);

  close(fd[1]);
}