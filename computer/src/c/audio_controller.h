/* Header file for the audio controller interface */

extern int global_kill; //define the global kill flag

//Function prototypes
int start_voice_control(); //fork off a voice controller subprocess
int stop_voice_control();  //kill the output pipe, stop transmitting data
//int main(); -program's main funciton is defined in .c file

/* Audio Control Protocol Documentation */
/* Command messages use the following format:
 *  TYPE <Option1> <Option2>... <Option n>\n
 * Supported Commands include:
 *  start [mic/spk/both] [-host <addr>] [-port <port>] [-rate <sample_rate>] [-ch <1/2>]
 *    -Starts a device and begins listening/transmiting
 *    -Host is only needed in mic mode, but port is needed in any mode
 *  stop [-dir mic/spk/both] [-f]
 *    -Stop a device, will let buffers empty first (if dir is ommitted, will stop all devices).
 *    -Stops processing immediately instead if -f is present.
 *  voice_start/voice_stop
 *    -Start/Stop the voice control module (consult val for specifics)
 *
 *  TODO: handle starting/stopping additional inputs/outputs
 */

