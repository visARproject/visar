/*
Test code will buffer/play sound from a network socket
--Lots of code stolen from linuxjournal.com
*/

/* Use the newer ALSA API */
#define ALSA_PCM_NEW_HW_PARAMS_API

#include <alsa/asoundlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>

//constants for the program
#define SAMPLE_RATE 44100
#define PERIOD      128
#define MAX_BUFFER  20
#define INPUT_PORT  19101

//useful buffer macros (x is head, y is tail)
#define BUFFER_SIZE(x,y)  (((y)-(x)>=0)?(y)-(x):MAX_BUFFER+(y)-(x))
#define BUFFER_FULL(x,y)  (BUFFER_SIZE(x,y)==(MAX_BUFFER-1))
#define BUFFER_EMPTY(x,y) ((y)==(x))

static char*  input_buffer;   //ring buffer for netwok input
static int    in_buff_start;
static int    in_buff_end;
static size_t frame_size;     //size of a frame, in bytes
static int    kill_flag;

void *reciever_thread(void *flags_ptr){
  int flags = *((int*)flags_ptr); //extract the flags
  printf("entered thread\n"); //test print

  //setup the scoket
  int sock = socket(PF_INET, SOCK_DGRAM, 0); // setup UDP socket
  struct sockaddr_in addr, client;
  addr.sin_family = AF_INET;
  addr.sin_port = htons(INPUT_PORT); //convert to correct byte format
  addr.sin_addr.s_addr = htonl(INADDR_ANY);
  bind(sock, (struct sockaddr*)&addr, sizeof(addr));
  char ack = 0;
  int len = sizeof(client);
  
  //read data from 
  while(!kill_flag){
    if(!BUFFER_FULL(in_buff_start, in_buff_end)){ //read data if space is available
      //printf("Waiting\n");
      int bytes = recvfrom(sock, input_buffer+(in_buff_end*frame_size),frame_size, 0,\
               (struct sockaddr *)&client, &len); //get an input packet
      if(bytes > 0){
        //printf("Recieved %d bytes\n", bytes);
        in_buff_end = (in_buff_end + 1) % MAX_BUFFER;
        //printf("buffer: (%d, %d, %d)\n", in_buff_start, in_buff_end, BUFFER_SIZE(in_buff_start,in_buff_end));
        bytes = sendto(sock, &ack, 1, 0, (struct sockaddr *)&client,sizeof(client));
        //printf("sent %d bytes\n", bytes);
      }
    }
  }
  close(sock);
  pthread_exit(NULL); //exit thread safetly
}

int main() {
  kill_flag = 0;  //not killed yet

  // Open PCM device for playback, check for errors
  snd_pcm_t *speaker_handle; //handler struct
  int rc = snd_pcm_open(&speaker_handle, "default",SND_PCM_STREAM_PLAYBACK, 0);
  if (rc < 0) {
    fprintf(stderr,"unable to open pcm device: %s\n",snd_strerror(rc));
    exit(1);
  }

  /* Allocate a hardware parameters object. */
  snd_pcm_hw_params_t *params;
  snd_pcm_hw_params_alloca(&params);

  /* Fill it in with default values. */
  snd_pcm_hw_params_any(speaker_handle, params);

  /* Set the desired hardware parameters. */

  /* Interleaved mode */
  snd_pcm_hw_params_set_access(speaker_handle, params, SND_PCM_ACCESS_RW_INTERLEAVED);

  /* Signed 16-bit little-endian format */
  snd_pcm_hw_params_set_format(speaker_handle, params, SND_PCM_FORMAT_S16_LE);

  /* Two channels (stereo) */
  snd_pcm_hw_params_set_channels(speaker_handle, params, 2);

  /* 44100 bits/second sampling rate (CD quality) */
  unsigned int val = SAMPLE_RATE; //assign value
  int dir; //direction (input/output)
  snd_pcm_hw_params_set_rate_near(speaker_handle, params, &val, &dir); //get closest match
  printf("rate is %d\n",val);

  /* Set period size to the constant frames. */
  size_t frames = PERIOD;
  snd_pcm_hw_params_set_period_size_near(speaker_handle, params, &frames, &dir);

  /* Write the parameters to the driver */
  rc = snd_pcm_hw_params(speaker_handle, params);
  if (rc < 0) {
    fprintf(stderr, "unable to set hw parameters: %s\n", snd_strerror(rc));
    exit(1);
  }

  /* Allocate stream buffer and input buffer */
  snd_pcm_hw_params_get_period_size(params, &frames, &dir);
  printf("Actual frames: %d\n",(int)frames);
  frame_size = frames * 4; /* 2 bytes/sample, 2 channels */
  input_buffer = (char*) malloc(frame_size * MAX_BUFFER);  //allocate buffer for network input
  in_buff_start = 0; in_buff_end = 0; //setup the queue
  
  /* create a server socket and thread to handle input */
  pthread_t thread;
  int flags = 0;
  rc = pthread_create(&thread, NULL, reciever_thread, (void*)&flags);
  if (rc){
     printf("ERROR; return code from pthread_create() is %d\n", rc);
     exit(-1);
  }

  char started = 0;  //track when to start reading data
  while(!kill_flag) { //loop until broken
    //rc = read(0, speaker_buffer, size); //read values in from console
    //wait for some buffer before starting, stop if empty
    if((!started && BUFFER_SIZE(in_buff_start,in_buff_end) < (MAX_BUFFER/2)) \
          || BUFFER_EMPTY(in_buff_start, in_buff_end)){
      //printf("Skipped (%d,%d)\n",BUFFER_SIZE(in_buff_start,in_buff_end),BUFFER_EMPTY(in_buff_start,in_buff_end));
      //if(started) printf("stopping\n");
      started = 0;
      continue; 
    }
    else {
      //if(!started) printf("starting\n");
      started = 1; //indicate that we've startd
    }
    
    //write data to speaker buffer, check responses
    rc = snd_pcm_writei(speaker_handle, input_buffer+(frame_size*in_buff_start), frames);
    //printf("wrote data to speakers\n");
    in_buff_start = (in_buff_start+1)%MAX_BUFFER;
    if (rc == -EPIPE){ /* EPIPE means underrun */
      fprintf(stderr, "underrun occurred\n");
      snd_pcm_prepare(speaker_handle);
    } else if (rc < 0) fprintf(stderr, "error from writei: %s\n", snd_strerror(rc));
    else if (rc != (int)frames) fprintf(stderr, "short write, write %d frames\n", rc);
  }

  // notify kernel to empty/close the buffers
  snd_pcm_drain(speaker_handle);
  snd_pcm_close(speaker_handle);

  free(input_buffer); //free our buffers

  kill_flag = 1;  //signal that threads should die
  pthread_exit(NULL); //exit without killing children
  return 0;
}
