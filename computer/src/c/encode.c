/* 
 * File handles sound codec management, encoding and decoding
 * TODO: Test with mic, consider preprocessing, flexibility
 */


#include <speex/speex.h> //package:libspeex-dev
#include <stdio.h>
#include "encode.h"

static void *enc_state, *dec_state;    //encoder/decoder state structs
static SpeexBits enc_bits, dec_bits;  //encoder/decoder buffer structs

//function sets up the encoder/decoder structs and buffers, returns required samples/frame
int setup_codecs(){
  //Init the state structs in narrowband (8 kHz) mode
  enc_state = speex_encoder_init(&speex_wb_mode);
  dec_state = speex_decoder_init(&speex_wb_mode);

  //Set the quality to 8 (28 kbps)
  int tmp=8;
  speex_encoder_ctl(enc_state, SPEEX_SET_QUALITY, &tmp);
  
  //enable the perceptual enhancer (reduce noise)
  tmp = 1;
  speex_decoder_ctl(dec_state, SPEEX_SET_ENH, &tmp);  

  //Init the buffers
  speex_bits_init(&enc_bits);
  speex_bits_init(&dec_bits);
  
  //get the frame size needed for specified settings
  speex_encoder_ctl(enc_state,SPEEX_GET_FRAME_SIZE,&tmp); 
  return tmp;  //return the frame size
}

//clean up the structs, prepare for shutdown
void destroy_codecs(){
  speex_bits_destroy(&enc_bits);
  speex_encoder_destroy(enc_state); 
  speex_bits_destroy(&dec_bits);
  speex_decoder_destroy(dec_state); 
}

//function encodes input buffer, stores in output buffer, return number of compressed bytes
int encode(char* in, char* out, int max_bytes){
  int nbBytes; //track the size of compressed buffer
  speex_bits_reset(&enc_bits);  //Flush the struct's bits and prepare for next frame
  speex_encode_int(enc_state, (short*)in, &enc_bits); //encode the input
  int num_bytes = speex_bits_write(&enc_bits, out, max_bytes); //copy the encoded bytes to output stream
  return num_bytes; //return the length of the compressed buffer
}

//function decodes input buffer of length bytes, and stores output in out
void decode(char* in, char* out, int bytes){
  speex_bits_read_from(&dec_bits, in, bytes);
  speex_decode_int(dec_state, &dec_bits, (short*)out);
}


