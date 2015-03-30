/*
 *  File handles the voice control interface
 *  Program expects input from the audio controller
 *  Program sends decoded audio stream to the audio controller
 */

// Comment these lines to disable
// #define WRITE_RAW_FILE
// #define PROCESS_INPUT_FILE

#include <pocketsphinx.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>

#define IN_NAME "/tmp/vsr_audio_pipe"
#define OUT_NAME "/tmp/vsr_vc_pipe"
int main(int argc, char** argv) {
  //FILE *fp;
  //fp = fopen("vclog.log", "w+");

  int fd[2];

  do {
    usleep(50000);
  } while((fd[0] = open(IN_NAME, O_RDONLY)) < 0);
  fd[1] = open(OUT_NAME, O_WRONLY);

  int buffer_size = 640; // buffer size
  uint8 utt_started = 0; //a new utterance check
  uint8 in_speech; //currently taking in speech
  int32 k; //number of frames read
  char const *hyp; //hypothesis of decoding, i.e. what pocketsphinx thinks was said
  int16 buffer[buffer_size]; //buffer used to store input
  char new_hyp[buffer_size]; //memory for the hypothesis
  char time_gate_pass = 0;

  // initial configuration for pocketsphinx
  // cmd_ln_t *config = cmd_ln_init(NULL, ps_args(), 1,
  //   "-hmm", MODELDIR "/en-us/en-us",
  //   "-lm", MODELDIR "/en-us/en-us.lm.dmp",
  //   "-dict", MODELDIR "/en-us/cmudict-en-us.dict",
  //   "-logfn", "/dev/null",
  //   NULL);

  cmd_ln_t *config = cmd_ln_init(NULL, ps_args(), 1,
    "-hmm", MODELDIR "/en-us/en-us",
    "-lm", "./dictionary.lm",
    "-dict", "./dictionary.dic",
    "-logfn", "/dev/null",
    NULL);

  //setup decoder
  ps_decoder_t *ps = ps_init(config);

  time_t start_time_in_speech;
  time_t current_time;
  struct tm * timeinfo;

  #ifdef PROCESS_INPUT_FILE
    FILE *f_in;
    int rv;
    int16 buf[512];
    f_in = fopen("audio_data.raw","rb");

    if(f_in == NULL)
      return;
    rv = ps_start_utt(ps);
    #ifdef WRITE_RAW_FILE
      int f_out;
      f_out = open("input_data.raw", O_TRUNC | O_CREAT | O_WRONLY, 0666);
      // printf("%d\n", f_out);
    #endif
    if (rv < 0)
        return;
          while (!feof(f_in)) {
              size_t nsamp;
              nsamp = fread(buf, 2, 512, f_in);
              #ifdef WRITE_RAW_FILE
                write(f_out, buf, nsamp*2);
              #endif
              rv = ps_process_raw(ps, buf, nsamp, 0, 0);
          }
          rv = ps_end_utt(ps);
    if (rv < 0)
      return;
    hyp = ps_get_hyp(ps, NULL);
    if (hyp == NULL)
      return;
    // printf("Recognized from input file: %s\n", hyp);
  #endif

  //begin utterance
  if(ps_start_utt(ps) < 0) { //if a new utterance can't begin, then error
    printf(fp, "%s\n", "VCERR:Failed to start utterance\n");
  }

  #ifdef WRITE_RAW_FILE
    int f;
    f = open("audio_data.raw", O_TRUNC | O_CREAT | O_WRONLY, 0666);
    // printf("%d\n", f);
  #endif

  int time_check = 0;

  //go as long as there's a pipe
  while(1) {
    int point = 0;
    int stop_check = 0;

    while(1) {
      k = read(fd[0], buffer + point, buffer_size - point);

      if(point == buffer_size) {
        break;
      } else if(k == 0) {
        stop_check = 1;
        break;
      } else {
        point += k;
      }
    }

    if(stop_check) {
      break;
    }

    //fprintf(fp, "%d\n", time_check);
    if(time_check && (time(0) - start_time_in_speech < 10)) {
      continue;
    } else {
      time_check = 0;
    }

    #ifdef WRITE_RAW_FILE
      write(f, buffer, point);
    #endif
    // printf("%d\n", k);

    char *sentence; //output
    ps_process_raw(ps, buffer, point/2, 0, 0); //begins decoding using the number of frames it could read

    //when speech is introduced in each new utterance
    // if(in_speech && !utt_started) {
    if(!utt_started) {
      utt_started = 1;
      time(&start_time_in_speech);
      // printf("Listening...\n");
    } else if(utt_started) {
      // printf("Time elapsed: %d\n", time(0) - start_time_in_speech );
      if(time(0) - start_time_in_speech > 5) {
        time_gate_pass = 1;
        //fprintf(fp, "Here\n");
        time_check = 1;
        // printf("No longer listening.\n");
      }
    }

    //once speech is done and utterance has started
    // if(!in_speech && utt_started && time_gate_pass) {
    if(utt_started && time_gate_pass) {
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

      write(fd[1], sentence, strlen(sentence)); //send results to output pipe

      utt_started = 0; //reset check back to FALSE
      time_gate_pass = 0;
    }

    //usleep(100000);
    memset(buffer, 0, buffer_size);
  }

  close(fd[0]);
  close(fd[1]); //close output pipe
  //fclose(fp);
}
