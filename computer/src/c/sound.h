/* Header file that defines the sound deivice management */

//define the sound thread kill flag events
extern int speaker_kill_flag;
extern int mic_kill_flag;

//define a struct to package the device handler and buffer
typedef struct{
  snd_pcm_t   *pcm_handle; //device handler
  audiobuffer *buf;        //buffer
} snd_pcm_package;

//open a sound device with specified period, rate, channels(0=mono,1=stereo) 
//  and direction(0=playback,1=capture), returns the handler/buffer package
snd_pcm_package open_snd_pcm(size_t period, unsigned int rate, int stereo, int direction);

//thread function pointers (grab/send data over network)
void *speaker_thread(void* ptr);
void *mic_thread(void* ptr);
