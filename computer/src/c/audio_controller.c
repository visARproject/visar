/* 
 * File handles the the speaker/mic control interface
 */

#include <stdio.h>

#include "buffer.h"
#include "comms.h"
#include "sound.h"
#include "audio_controller.h"

//function sets up and starts a controller thread
int start_controller(){
  

}

//start the control listener which will accept commands from the main vispy program
//exact protocol is still tbd, should use a pipe to communicate (python can redirect to stdio?)
//should support start, stop, configure and voice_control start/stop options.
void* controller_thread(void* ptr){
  

}

//fork off a voice controller subprocess
int start_voice_control(){


}

//kill the output pipe, stop 
int stop_voice_control(){


}