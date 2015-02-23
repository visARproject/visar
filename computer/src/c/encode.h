/* Header file for the speex codec management */

//funciton prototypes
int setup_codecs();
void destroy_codecs();
int encode(char* in, char* out, int max_bytes);
void decode(char* in, char* out, int bytes);
