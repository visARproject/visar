/* 
 * File handles sound processing (start/stop/buffer structure)
 */

//library includes 
#include <alsa/asoundlib.h>
#include <pthread.h>

//project includes
#include "buffer.h"
#include "sound.h"

//predefined constants (basically guesses)
#define MAX_BUFFER 20   //total ring buffer size
#define MIN_BUFFER 10   //buffered frames needed to initiate playback

//externally defined global variables
int speaker_kill_flag;
int mic_kill_flag;

//open a sound device with specified period, rate, channels(0=mono,1=stereo) 
//  and direction(0=playback,1=capture), returns the handler/buffer package
snd_pcm_package open_snd_pcm(size_t period, unsigned int rate, int stereo, int direction){
  //Open PCM device for playback/capture, check for errors
  snd_pcm_t *pcm_handle; //handler struct
  int dir = (direction)? SND_PCM_STREAM_CAPTURE:SND_PCM_STREAM_PLAYBACK;
  int rc = snd_pcm_open(&pcm_handle, "default",dir, 0);
  if (rc < 0){ //make sure it landed
    fprintf(stderr,"unable to open pcm device: %s\n",snd_strerror(rc));
    return rc; //return the failure
  }

  //Setup the hardware parameters
  snd_pcm_hw_params_t *params;  //create pointer
  snd_pcm_hw_params_alloca(&params); //allocate struct
  snd_pcm_hw_params_any(pcm_handle, params); //fill with defaults
  snd_pcm_hw_params_set_access(pcm_handle, params, SND_PCM_ACCESS_RW_INTERLEAVED); //interleaved mode
  snd_pcm_hw_params_set_format(pcm_handle, params, SND_PCM_FORMAT_S16_LE); //signed 16-bit LE
  snd_pcm_hw_params_set_channels(pcm_handle, params, 2); //stereo mode
  unsigned int rate2 = rate; //copy rate (will be overwritten on mismatch)
  int err_dir = 0; //try to set rate exactly
  snd_pcm_hw_params_set_rate_near(pcm_handle, params, &rate2, &err_dir); //get closest match
  if(rate != rate2) printf("Rate mismatch, %d give, %d set\n",rate,rate2);
  size_t frames = period; //once again,copy value in case of mismatch
  snd_pcm_hw_params_set_period_size_near(pcm_handle, params, &period, &dir); //set the period
  if(period != frames) printf("Period size mismatch, %d given, %d set", period, frames);
 
  //Write the parameters to the driver
  rc = snd_pcm_hw_params(pcm_handle, params);
  if (rc < 0){ //make sure it landed
    fprintf(stderr, "unable to set hw parameters: %s\n", snd_strerror(rc));
    return rc; //return the failure
  }

  //create a buffer struct (frame size is frames/period * channels * sample width)
  audiobuffer* buffer = create_buffer(frames*2*2, MAX_BUFFER); //2 16-bit channels
  
  //package the results
  snd_pcm_package out = {pcm_handle, buffer};
  return out;
}

void *speaker_thread(void* ptr){
  audiobuffer buf = *(((snd_pcm_package*)ptr)->buffer); //cast pointer, get buffer struct
  snd_pcm_t speaker_handle = ((snd_pcm_package*)ptr)->pcm_handle; //cast pointer, get device pointer
  speaker_kill = 0;  //reset the kill signal (small race condition, not concerned)
  
  char started = 0;  //track when to start reading data
  while(!kill_flag && !speaker_kill_flag) { //loop until program stops us
    //wait until adequate buffer is achieved
    if((!started && BUFFER_SIZE(buf) < (MAX_BUFFER/2)) || BUFFER_EMPTY(buf)){
      started = 0;  //stop if already started
      //TODO: Consider adding a wait statement (less CPU use)
      continue;     //don't start yet
    } else started = 1; //indicate that we've startd
    
    //write data to speaker buffer, check responses
    rc = snd_pcm_writei(speaker_handle, GET_QUEUE_HEAD(buf), buf.size);
    INC_QUEUE_HEAD(buf);
    if (rc == -EPIPE){ //Catch underruns (not enough data)
      fprintf(stderr, "underrun occurred\n");
      snd_pcm_prepare(speaker_handle); //reset speaker
    } else if (rc < 0) fprintf(stderr, "error from writei: %s\n", snd_strerror(rc)); //other errors
    else if (rc != (int)buf.size) fprintf(stderr, "short write, write %d frames\n", rc);
  }

  //TODO: find way to combine multiple audio streams
  
  // notify kernel to empty/close the speakers
  snd_pcm_drain(speaker_handle);
  snd_pcm_close(speaker_handle);
  
  pthread_exit(NULL); //exit thread safetly
}

void *mic_thread(void* ptr){
  audiobuffer buf = *(((snd_pcm_package*)ptr)->buffer); //cast pointer, get buffer struct
  snd_pcm_t mic_handle = ((snd_pcm_package*)ptr)->pcm_handle; //cast pointer, get device pointer
  mic_kill = 0;  //reset the kill signal (small race condition, not concerned)
  
  while(!kill_flag && !mic_kill_flag) { //loop until program stops us
    //wait until there's space in the buffer
    if(BUFFER_FULL(buf)) continue; //do nothing (TODO: consider wait)
    
    //write data to speaker buffer, check response codes
    rc = snd_pcm_readi(mic_handle, GET_QUEUE_TAIL(buf), buf.size);
    INC_QUEUE_TAIL(buf);
    if (rc == -EPIPE) { //catch overruns (too much data)
      fprintf(stderr, "overrun occurred\n");
      snd_pcm_prepare(mic_handle); //reset handler
    //other errors
    } else if (rc < 0) fprintf(stderr, "error from read: %s\n", snd_strerror(rc));
    else if (rc != (int)frames) fprintf(stderr, "short read, read %d frames\n", rc);
    
    //TODO: implement way of handling multiple buffers (and also pipes)
    //        abstract the buffer push operation
  }

  // notify kernel to empty/close the speakers
  snd_pcm_drain(mic_handle);
  snd_pcm_close(mic_handle);
  
  pthread_exit(NULL); //exit thread safetly
}