/* Header file for the audio controller interface */

//constants used elsewhere
#define TIMEOUT      1       //socket timeout is 1 second
#define PERIOD_UTIME 20000   //codec needs frame time of 20ms

extern int global_kill;  //define the global kill flag
extern int vc_pipe[2];   //define the voice controller's output pipe
extern int vc_flag;      //tell mic thread if voice control is active
extern int vc_hold_flag; //mic thread is currently writing to pipe

//Function prototypes
int start_voice_control(); //fork off a voice controller subprocess
int stop_voice_control();  //kill the output pipe, stop transmitting data
//int main(); --program's main funciton is defined in .c file

/* Audio Control Protocol Documentation */
/* Command messages use the following format:
 *  TYPE <Option1> <Option2>... <Option n>\n
 * Supported Commands include:
 *  start [mic/spk/both] [-host <addr>] [-port <port>] [-rate <sample_rate>] [-ch <1/2>]
 *    -Starts a device and begins listening/transmiting
 *    -Host is only needed in mic mode, but port is needed in any mode
 *    -Rate/Channels are depreciated, codec requires 16k mono audio
 *  stop [-dir mic/spk/both] [-f]
 *    -Stop a device, will let buffers empty first (if dir is ommitted, will stop all devices).
 *    -Stops processing immediately instead if -f is present.
 *  shutdown
 *    -Kills all operations, program exits
 *  voice_start/voice_stop
 *    -Start/Stop the voice control module (consult val for specifics)
 *
 *  TODO: handle starting/stopping additional inputs/outputs
 */

