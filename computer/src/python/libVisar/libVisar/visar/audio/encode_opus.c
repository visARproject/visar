
/* 
 * File handles sound codec management, encoding and decoding
 */


#include <opus/opus.h> //package:libopus-dev
#include <stdio.h>
#include "encode.h"

#define QUALITY       8     //codec quality settings (higher is better, but more bandwidth)
#define SAMPLE_RATE   16000 //sample rate of the audio foramt
#define FRAME_SIZE    160   //number of samples per frame
#define APP_MODE      OPUS_APPLICATION_AUDIO //application target mode (voip vs. general audio)

//encoder/decoder state structs    
OpusEncoder *enc_state; 
OpusDecoder *dec_state;

//function sets up the encoder/decoder structs and buffers, returns required samples/frame
int setup_codecs(){
  //create the encoder and decoder state structs
  int error = 0;
  if(!(enc_state = opus_encoder_create(SAMPLE_RATE,1,APP_MODE,&error)))
    printf("Error Creating Encoder: %d\n",error);
  if(!(dec_state = opus_decoder_create(SAMPLE_RATE,1,&error)))
    printf("Error Creating Decoder: %d\n",error);
  
  opus_encoder_ctl(enc_state, OPUS_SET_COMPLEXITY(QUALITY));
  
  return FRAME_SIZE;  //return the frame size (
}

//clean up the structs, prepare for shutdown
void destroy_codecs(){
  opus_encoder_destroy(enc_state); 
  opus_decoder_destroy(dec_state); 
}

//function encodes input buffer, stores in output buffer, return number of compressed bytes
int encode(char* in, char* out, int max_bytes){
  return opus_encode(enc_state, (opus_int16*)in, FRAME_SIZE, out, max_bytes);
}

//function decodes input buffer of length bytes, and stores output in out
void decode(char* in, char* out, int bytes){
  bytes = opus_decode(dec_state, in, bytes, (opus_int16*)out, FRAME_SIZE, 0);
}

