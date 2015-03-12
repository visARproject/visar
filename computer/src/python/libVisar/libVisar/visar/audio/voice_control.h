/* VAL: I'll define a start/stop voice interface in the audio controller,
 *    anything beond that is for you to manage.
 * This file defines how to start your program. (define the prototyped function)
 * The controller will be running at all times when the audio module is running.
 * I will pause/resume sening data over the pipe, but will not close it until shutdown.
 * IMPORTANT: Do not let the reciever sleep; I'm doing synchronous writes 
 *    which means that if your read isn't ready it can slow down the sender thread.
 * Ask me for any further questions. -Josh  */
 
/* Function prototype, fd is an array of 2 file descriptors
 *   fd[0] = audio->voice_control (input pipe) 
 *     -Pipe will only ever convey audio data
 *       --Audio Format is mono 16-bit signed LE sampled at 16kHz.
 *     -Pipe will not send data when vc is disabled, but will remain open.
 *     -On shutdown, input pipe will close (read() will return 0).
 *   fd[1] = audio<-voice_control (output pipe)
 *     -send commands/errors using one of these headings, include newline:
 *       --VCCOM: use for commands (eg. "VCCOM:mute all\n")
 *       --VCERR: use for errors
 *       --If you need more, talk to me
 *     -Make sure to close this pipe before exiting.
 */
 
//Function prototypes
void start_voice(int* fd);