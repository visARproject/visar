/* 
 * File handles the the speaker/mic control interface
 *  Program expects control inputs from stdin (done via redirects) 
 * TODO: multiple streams?
 * BUGS: Starting comms while in vc mode breaks program
 *       Errors when stopping and resuming vc_mode (^likely related)
 *       Segfault on ARM stop command
 */
 
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <alsa/asoundlib.h>
#include <signal.h>
#include <fcntl.h>

#include "audio_controller.h"
#include "buffer.h"
#include "comms.h"
#include "sound.h"
#include "encode.h"

#define DEFAULT_RATE 16000   //encoder uses narrowband audio
#define DEFAULT_CHNS 1
#define DEFAULT_PORT 19101
#define DEFAULT_ADDR "127.0.0.1"

#define FIFO_NAME "/tmp/vsr_audio_pipe"

int global_kill = 0;  //global program kill flag, will stop all threads if set
int vc_pipe;          //voice control pipe
int vc_flag;          //voice control active flag
int vc_hold_flag;     //voice control pipe active flag
static int reciever_kill_flag; //kill flag for network reciever thread
static int period;    //period (samples/frame) required by the codecs

//main function for the program, listens on stdin for commands
int main(int argc, char** argv){  
  char input[80];   //buffer for commands
    
  //start the voice process before doing anything significant
  setup_voice_control();
  
  //default the flags to not started
  mic_kill_flag = 1;
  speaker_kill_flag = 1;
     
  period = setup_codecs(); //setup the codecs and get the period size  
  
  //FILE* debug_fd = fopen("debug.log", "w"); //DEBUG
  
  //handler loop, runs until program is killed
  while(!global_kill){
    if(fgets(input, 80, stdin)){ //get a command from stdin
      //printf("Echo: %s",input);
      //fprintf(debug_fd, "%s", input); //DEBUG
      
      char* token = strtok(input, "\n"); //split string to ignore newline
      token = strtok(input, " "); //split string on whitespace, get command
      
      //Start Command
      if(0 == strcmp(token, "start")){
        int direction = 0;
        char* addr = 0;
        int port = 0;
        unsigned int rate = 0;
        int channels = 0;
        
        while(token = strtok(0," ")){   //parse next token
          if(0 == strcmp(token, "mic"))        direction = 1; //direction is input only
          else if(0 == strcmp(token, "spk"))   direction = 2; //output only
          else if(0 == strcmp(token, "both"))  direction = 3; //both directions
          else if(0 == strcmp(token, "-host")) addr = strtok(0," "); //get hostname from next input
          else if(0 == strcmp(token, "-port")) port = atoi(strtok(0," ")); //parse the integer port from next input
          else if(0 == strcmp(token, "-rate")) rate = atoi(strtok(0," ")); //parse the rate 
          else if(0 == strcmp(token, "-ch"))   channels = atoi(strtok(0," ")); //parse the channel count
          else{
            printf("Audio Controller: Bad command argument: \"%s\"\n",token);
            continue;
          }
        }
      
        //handle missing information via defaults (rate/chn are fixed with codecs
        addr     = addr?:     DEFAULT_ADDR;
        port     = port?:     DEFAULT_PORT;
        //rate     = rate?:     DEFAULT_RATE;
        //channels = channels?: DEFAULT_CHNS;
        rate     = DEFAULT_RATE;
        channels = DEFAULT_CHNS;
      
        printf("Rate: %d, Channels: %d, Period: %d\n", rate, channels, period);
      
        //setup the speaker
        if((direction & 2) && speaker_kill_flag){
          snd_pcm_t* handle = start_snd_device(period, rate, (channels==2), PLAYBACK_DIR); //start the device
          audiobuffer* spk_buf = create_speaker_thread(handle, period, 2*channels); //spawn the speaker thread
          reciever_kill_flag = 0;  //reset the kill flag
          if(start_reciever(port, spk_buf, &reciever_kill_flag)){ //start the reciever thread
            printf("Audio Controller: Could not start speaker\n");
            speaker_kill_flag = 1; //kill the mic device thread
          }
          printf("Audio Controller: Started speaker server\n");
        }
        
        //setup the mic
        if((direction & 1) && mic_kill_flag){ 
          if(vc_flag){
            vc_flag = 0;    //stop voice control
            printf("Audio Controller: Stopping VC for comms setup\n");
            wait(TIMEOUT);  //let thread die
          }
          snd_pcm_t* handle = start_snd_device(period, rate, (channels==2), CAPTURE_DIR); //start the device
          sender_handle* sndr = start_sender(addr, port, 0, 0); //setup partial sender
          create_mic_thread(handle, sndr, period, 2*(channels), 0); //spawn the thread
          printf("Audio Controller: Started microphone transmission\n");
        }
      
      //Stop Command
      } else if(0 == strcmp(token, "stop")){
        int direction = 0;
        int kill_f = 0;
        while(token = strtok(0," ")){   //parse next token
          if(0 == strcmp(token, "mic"))        direction = 1; //direction is input only
          else if(0 == strcmp(token, "spk"))   direction = 2; //output only
          else if(0 == strcmp(token, "both"))  direction = 3; //both directions
          else if(0 == strcmp(token, "-f"))    kill_f = 1;    //immediate kill flag
          else{
            printf("Audio Controller: Bad command argument: \"%s\"\n",token);
            continue;
          }
        }
        
        //issue shutdown signals to the threads
        if(direction & 1) mic_kill_flag = 1;      //assert microphone kill flag
        if(direction & 2) speaker_kill_flag = 1;  //assert speaker kill flag
        if(!kill_f) sleep(TIMEOUT);  //wait for data to finish processing
        if(direction & 2) reciever_kill_flag = 1; //assert server kill flag
        printf("Audio Controller: Devices shutdown\n");
      
      } else if(0 == strcmp(token, "shutdown")){
        shutdown_prog();
        break;
        
      //Start voice_control
      } else if(0 == strcmp(token, "voice_start")){
        vc_flag = 1; //signal that threads should send data to controller
        if(mic_kill_flag){
          snd_pcm_t* handle = start_snd_device(period, DEFAULT_RATE, DEFAULT_CHNS==2, CAPTURE_DIR); //start the device
          //sender_handle* sndr = (sender_handle*) malloc(sizeof(sender_handle)); // 20150309 mseese: not necessary as its only needed for voice control
          create_mic_thread(handle, NULL, period, 2*DEFAULT_CHNS, 1); //spawn the thread
          printf("Audio Controller: Started microphone transmission\n");
        }
      
      //Stop voice_control
      } else if(0 == strcmp(token, "voice_stop")){
        vc_flag = 0; //signal threads to stop sending data

      //set option
      } else if(0 == strcmp(token, "set")){
        int vol = -1;
        while(token = strtok(0," ")){   //parse next token
          if(0 == strcmp(token, "-volume")) vol = atoi(strtok(0," ")); //get hostname from next input
          else{
            printf("Audio Controller: Bad command argument: \"%s\"\n",token);
            continue;
          }
        }
        
        change_volume(vol); //issue the command
        printf("Audio Controller: Volume set to %d\n",vol);

      //other input
      } else {
        printf("Audio Controller: Unrecognized command: \"%s\" \n", token);  
      }
    } else {  //could not read from stdin
      if(!global_kill){ //if global kill is 0, it was an actual error
        printf("Audio Controller: Error when reading input, terminating\n");
        shutdown_prog();
      }
      break; //break so program can exit
    }
  }
  
  destroy_codecs();        //clean up the encoder
  destroy_voice_control(); //shutdown the voice controller
  sleep(TIMEOUT);          //wait for process to exit
  
  printf("Audio Controller: Exiting\n");
  return 0;
}

// create an alsa mixer and use it to set the system volume
// TODO: Make this work on the embedded board
void change_volume(long volume){
  if(volume > 100 || volume < 0) return; //check range

  /* Code taken from stackexchange */
  long min, max;
  snd_mixer_t *handle;
  snd_mixer_selem_id_t *sid;
  const char *card = "default";
  const char *selem_name = "Master";

  snd_mixer_open(&handle, 0);
  snd_mixer_attach(handle, card);
  snd_mixer_selem_register(handle, NULL, NULL);
  snd_mixer_load(handle);

  snd_mixer_selem_id_malloc(&sid);
  snd_mixer_selem_id_set_index(sid, 0);
  snd_mixer_selem_id_set_name(sid, selem_name);
  snd_mixer_elem_t* elem = snd_mixer_find_selem(handle, sid);

  snd_mixer_selem_get_playback_volume_range(elem, &min, &max);
  snd_mixer_selem_set_playback_volume_all(elem, volume * max / 100);

  snd_mixer_close(handle);
}

//setup the pipe
int setup_voice_control(){
  vc_flag = 0;      //voice control is not active
  vc_hold_flag = 0; //nor is the voice control pipe

  //create fifo and get fd
  mkfifo(FIFO_NAME, 0666);
  vc_pipe = open(FIFO_NAME, O_WRONLY);

  printf("Audio Controller: Voice Controller Started\n");
  return 0;
}

//kill the output pipe, stop 
void destroy_voice_control(){
  if(!vc_flag) return;  //nothing to do
  
  vc_flag = 0;          //signal thread to stop writing data
  while(vc_hold_flag);  //wait for pending writes to finish
  close(vc_pipe);       //close the pipe, signaling that child should close
  //sleep(TIMEOUT);     //wait for child to respond
  unlink(FIFO_NAME);    //destroy the pipe
  
  printf("Audio Controller: Voice Controller Shutdown\n");
}

//cleanly shutdown the program
void shutdown_prog(){
  //shutdown the producers, wait, then shutdown consumers
  printf("Audio Controller: Shutting down...\n");
  mic_kill_flag = 1;      //assert microphone kill flag
  reciever_kill_flag = 1; //assert server kill flag
  sleep(TIMEOUT);         //wait for data to finish processing
  speaker_kill_flag = 1;  //assert speaker kill flag
  global_kill = 1;        //assert global kill flag (just in case)
  //sleep(TIMEOUT);       //wait for data to finish processing
  printf("Audio Controller: Devices shutdown\n");
}

