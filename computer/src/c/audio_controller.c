/* 
 * File handles the the speaker/mic control interface
 *  Program expects control inputs from stdin (done via redirects) 
 * TODO: multiple streams, voice_control, compression
 */
 
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <alsa/asoundlib.h>

#include "audio_controller.h"
#include "buffer.h"
#include "comms.h"
#include "sound.h"
#include "voice_control.h"
#include "encode.h"

#define DEFAULT_RATE 16000   //encoder uses narrowband audio
#define DEFAULT_CHNS 1
#define DEFAULT_PORT 19101
#define DEFAULT_ADDR "127.0.0.1"

int global_kill = 0;  //global program kill flag, will stop all threads if set
static int sender_kill_flag;
static int reciever_kill_flag;

//main function for the program, listens on stdin for commands
int main(int argc, char** argv){  
  char input[80]; //buffer for commands
  
  int period = setup_codecs(); //setup the codecs and get the period size  
  
  //handler loop, runs until program is killed
  while(!global_kill){
    if(fgets(input, 80, stdin)){ //get a command from stdin
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
        if(direction & 2){
          audiobuffer* spk_buf = start_snd_device(period, rate, (channels==2), 0); //start the device
          reciever_kill_flag = 0;  //reset the kill flag
          if(start_reciever(port, spk_buf, &reciever_kill_flag)){
            printf("Audio Controller: Could not start speaker\n");
            speaker_kill_flag = 1; //kill the mic device thread
          }
          printf("Audio Controller: Started speaker server\n");
        }
        
        //setup the mic
        if(direction & 1){ 
          audiobuffer* mic_buf = start_snd_device(period, rate, (channels==2), 1); //start the device
          sender_kill_flag = 0;  //reset the kill flag
          if(start_sender(addr, port, mic_buf, &sender_kill_flag)){
            printf("Audio Controller: Could not start mic\n");
            mic_kill_flag = 1; //kill the mic device thread
          }
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
        
        //shutdown the producers, wait if requested, then shutdown consumers
        if(direction & 1) mic_kill_flag = 1;      //assert microphone kill flag
        if(direction & 2) reciever_kill_flag = 1; //assert server kill flag
        if(!kill_f) sleep(TIMEOUT);  //wait for data to finish processing
        if(direction & 2) speaker_kill_flag = 1;  //assert speaker kill flag
        if(direction & 1) sender_kill_flag = 1;   //assert sender kill flag
        printf("Audio Controller: Devices shutdown\n");
      
      } else if(0 == strcmp(token, "shutdown")){
        //shutdown the producers, wait, then shutdown consumers
        mic_kill_flag = 1;      //assert microphone kill flag
        reciever_kill_flag = 1; //assert server kill flag
        sleep(TIMEOUT);         //wait for data to finish processing
        speaker_kill_flag = 1;  //assert speaker kill flag
        sender_kill_flag = 1;   //assert sender kill flag
        global_kill = 1;        //assert global kill flag (just in case)
        sleep(TIMEOUT);         //wait for data to finish processing
        printf("Audio Controller: Devices shutdown\n");
        
      //TODO: Start voice_control
      } else if(0 == strcmp(token, "voice_start")){
        
      
      //TODO: Stop voice_control
      } else if(0 == strcmp(token, "voice_stop")){
      
      
      } else {
        printf("Audio Controller: Unrecognized command: \"%s\" \n", token);  
      }
    } else {  //could not read from stdin
      printf("Audio Controller: Error when reading input, terminating\n");
      global_kill = 1;  //assert global kill signal
      sleep(TIMEOUT);
      break;
    }
  }
  
  //clean up the encoder
  destroy_codecs();
  
  return 0;
}

//fork off a voice controller subprocess
int start_voice_control(){
  

}

//kill the output pipe, stop 
int stop_voice_control(){


}
