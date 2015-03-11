/* 
 * File handles sound processing (start/stop/buffer structure)
 * TODO: multiplexing, volume
 * BUGS: speaker underruns on ARM, can't recover
 *         -seems to destabalize with time
 *         -time to failure is shorter with usleep in spin loop
 *       
 */

//library includes 
#include <alsa/asoundlib.h> //libasound2-dev
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

//project includes
#include "audio_controller.h"
#include "buffer.h"
#include "comms.h"
#include "sound.h"

//predefined constants (basically guesses)
#define MAX_BUFFER 20   //total ring buffer size
#define MIN_BUFFER 10   //buffered frames needed to initiate playback

//externally defined global variables
int speaker_kill_flag;
int mic_kill_flag;

//open a sound device with specified period, rate, channels(0=mono,1=stereo or MONO_SOUND/STEREO_SOUND) 
//  and direction(0=playback,1=capture), returns the buffer (also PLAYBACK_DIR/CAPTURE_DIR)
snd_pcm_t* start_snd_device(size_t period, unsigned int rate, int stereo, int direction){
  //Open PCM device for playback/capture, check for errors
  snd_pcm_t *pcm_handle; //handler struct
  int dir = (direction)? SND_PCM_STREAM_CAPTURE:SND_PCM_STREAM_PLAYBACK;
  int rc = snd_pcm_open(&pcm_handle, "default",dir, 0);
  if (rc < 0){ //make sure it landed
    fprintf(stderr,"unable to open pcm device: %s\n",snd_strerror(rc));
    return 0; //return null pointer
  }

  //Setup the hardware parameters
  snd_pcm_hw_params_t *params;  //create pointer
  snd_pcm_hw_params_alloca(&params); //allocate struct
  snd_pcm_hw_params_any(pcm_handle, params); //fill with defaults
  snd_pcm_hw_params_set_access(pcm_handle, params, SND_PCM_ACCESS_RW_INTERLEAVED); //interleaved mode
  snd_pcm_hw_params_set_format(pcm_handle, params, SND_PCM_FORMAT_S16_LE); //signed 16-bit LE
  snd_pcm_hw_params_set_channels(pcm_handle, params, (stereo+1)); //stereo mode
  unsigned int rate2 = rate; //copy rate (will be overwritten on mismatch)
  int err_dir = 0; //try to set rate exactly
  snd_pcm_hw_params_set_rate_near(pcm_handle, params, &rate2, &err_dir); //get closest match
  if(rate != rate2) printf("Rate mismatch, %d give, %d set\n",rate,rate2);
  size_t frames = period; //once again,copy value in case of mismatch
  snd_pcm_hw_params_set_period_size_near(pcm_handle, params, &period, &dir); //set the period
  if(period != frames) printf("Period size mismatch, %d given, %d set", (int)period, (int)frames);
 
  //Write the parameters to the driver
  rc = snd_pcm_hw_params(pcm_handle, params);
  if (rc < 0){ //make sure it landed
    fprintf(stderr, "unable to set hw parameters: %s\n", snd_strerror(rc));
    return 0; //return null
  }
  
  return pcm_handle;
}

//spawn a speaker thread
audiobuffer* create_speaker_thread(snd_pcm_t* pcm_handle, size_t period, size_t frame_size){
  //create a buffer struct (frame size is frames/period * channels * sample width)
  audiobuffer* buffer = create_buffer(period, frame_size, MAX_BUFFER); //16-bit channels
  
  //package the information for the thread
  spk_pcm_package* pkg = (spk_pcm_package*)malloc(sizeof(spk_pcm_package));
  pkg->pcm_handle = pcm_handle;
  pkg->buffer = buffer;

  speaker_kill_flag = 0;  //reset the kill signal
  
  //create thread and send it the package
  pthread_t thread; //thread handler
  int rc = pthread_create(&thread, NULL, speaker_thread, (void*)pkg);
  if (rc) printf("ERROR: Could not create device thread, rc=%d\n", rc); //print errors
  
  return buffer; //return the device's audio buffer
}

void create_mic_thread(snd_pcm_t* pcm_handle, sender_handle* sender, size_t period, size_t frame_size, int vc_only){
  //allocate a microphone buffer (just one period)
  char* buffer = (char*)malloc(period*frame_size);
  
  if(sender != NULL) {
    //finish populating the sender info
    sender->buf = buffer;
    sender->len = period*frame_size;
  }
    
  mic_kill_flag = !vc_only;  //reset the kill on normal operations
  
  //store in package
  mic_pcm_package* pkg = (mic_pcm_package*)malloc(sizeof(mic_pcm_package));
  pkg->pcm_handle = pcm_handle; //store the device handler
  pkg->buffer = buffer; //store the buffer pointer
  pkg->period = period; //store the period size
  pkg->length = period*frame_size; //buffer size
  pkg->snd_handle = sender; //store the handler

  if(!vc_only) mic_kill_flag = 0;  //reset the kill signal

  //create thread and send it the package
  pthread_t thread; //thread handler
  int rc = pthread_create(&thread, NULL, mic_thread, (void*)pkg);
  if (rc) printf("ERROR: Could not create device thread, rc=%d\n", rc); //print errors
  
}

void *speaker_thread(void* ptr){
  audiobuffer* buf = ((spk_pcm_package*)ptr)->buffer; //cast pointer, get buffer struct
  snd_pcm_t* speaker_handle = ((spk_pcm_package*)ptr)->pcm_handle; //cast pointer, get device pointer
  free(ptr); //free message memory
    
  char started = 0;  //track when to start reading data
  while(!global_kill && !speaker_kill_flag) { //loop until program stops us
    //wait until adequate buffer is achieved
    if((!started && BUFFER_SIZE(*buf) < (MIN_BUFFER)) || BUFFER_EMPTY(*buf)){
      //printf("Speaker Waiting\n");
      usleep(PERIOD_UTIME/2); //wait to reduce CPU usage
      continue;     //don't start yet
    } else {
      if(!started) snd_pcm_prepare(speaker_handle); //reset speaker
      started = 1; //indicate that we've startd
    }
    
    //write data to speaker buffer, check responses
    int rc = snd_pcm_writei(speaker_handle, GET_QUEUE_HEAD(*buf), buf->period);
    INC_QUEUE_HEAD(*buf);
    if (rc == -EPIPE){ //Catch underruns (not enough data)
      fprintf(stderr, "underrun occurred\n");
      started = 0;  //stop and wait for buffer to buildup
    } else if (rc < 0) fprintf(stderr, "error from writei: %s\n", snd_strerror(rc)); //other errors
    else if (rc != (int)buf->period) fprintf(stderr, "short write, write %d frames\n", rc);
    //else fprintf(stderr, "audio written correctly\n");
    snd_pcm_wait(speaker_handle, 1000); //wait for IO to be ready
  }
  
  // notify kernel to empty/close the speakers
  snd_pcm_drain(speaker_handle);  //finish transferring the audio
  snd_pcm_close(speaker_handle);  //close the device
  printf("Audio Controller: Speaker Thread shutdown\n");
  
  pthread_exit(NULL); //exit thread safetly
}

void *mic_thread(void* ptr){
  char* buf = ((mic_pcm_package*)ptr)->buffer; //cast pointer, get buffer struct
  size_t period  = ((mic_pcm_package*)ptr)->period;  //cast pointer, get period size
  sender_handle* snd_handle = ((mic_pcm_package*)ptr)->snd_handle; //cast pointer, get handler
  snd_pcm_t* mic_handle = ((mic_pcm_package*)ptr)->pcm_handle; //cast pointer, get device pointer
  size_t length = ((mic_pcm_package*)ptr)->length; //get the buffer size
  free(ptr); //clean up memory
  
  while(!global_kill && (!mic_kill_flag || vc_flag)) { //loop until program stops us
    //write data to speaker buffer, check response codes
    int rc = snd_pcm_readi(mic_handle, buf, period);
    //printf("Mic Data Read\n");
    if (rc == -EPIPE) { //catch overruns (too much data for buffer)
      fprintf(stderr, "overrun occurred\n");
      snd_pcm_prepare(mic_handle); //reset handler
    //other errors
    } else if (rc < 0) fprintf(stderr, "error from read: %s\n", snd_strerror(rc));
    else if (rc != (int)period) fprintf(stderr, "short read, read %d frames\n", rc);
    else{ //read was good, send the data
      if(!mic_kill_flag && snd_handle != NULL) send_packet(snd_handle); //send the packet over network
      if(vc_flag){ //write to voice control pipe if flag set
        vc_hold_flag = 1; //start of write
        //printf("Writing data to pipe...\n"); //DEBUG
        write(vc_pipe, buf, length); //write data
        //printf("Data written to pipe\n"); //DEBUG
        vc_hold_flag = 0; //end of write
      }
    }
  }

  // notify kernel to empty/close the speakers, free the buffer
  snd_pcm_drain(mic_handle);
  snd_pcm_close(mic_handle);
  if(snd_handle != NULL) destroy_sender(snd_handle); //cleans up the sender socket and buffer
  printf("Audio Controller: Microphone Thread shutdown\n");
  
  pthread_exit(NULL); //exit thread safetly
}
