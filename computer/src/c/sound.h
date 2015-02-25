/* Header file that defines the sound deivice management */

#define PLAYBACK_DIR 0
#define CAPTURE_DIR  1
#define MONO_SOUND   0
#define STEREO_SOUND 1

//define the sound thread kill flag events
extern int speaker_kill_flag;
extern int mic_kill_flag;

//define a struct to package the device handler and buffer
typedef struct{
  snd_pcm_t   *pcm_handle; //device handler
  audiobuffer *buffer;     //buffer
} spk_pcm_package;

typedef struct{
  snd_pcm_t*      pcm_handle; //device handler
  char*           buffer;     //buffer for device
  size_t          period;     //length of the buffer
  sender_handle*  snd_handle; //sender handler
} mic_pcm_package;

//open a sound device with specified period, rate, channels(0=mono,1=stereo or MONO_SOUND/STEREO_SOUND) 
//  and direction(0=playback,1=capture), returns the buffer (also PLAYBACK_DIR/CAPTURE_DIR)
snd_pcm_t* start_snd_device(size_t period, unsigned int rate, int stereo, int direction);

audiobuffer* create_speaker_thread(snd_pcm_t* pcm_handle, size_t period, size_t frame_size);
void create_mic_thread(snd_pcm_t* pcm_handle, sender_handle* sender, size_t period, size_t frame_size);

//thread functions (grab/send data over network); pointer should be a snd_pcm_package
void *speaker_thread(void* ptr);
void *mic_thread(void* ptr);
