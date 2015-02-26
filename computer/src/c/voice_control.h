/* VAL: I'll define a start/stop voice interface in the audio controller,
 *    anything beond that is for you to manage.
 * This file defines how to start your program. (define the prototyped function)
 * The fd is for a pipe which mirrors the audio input, handle it however.
 * If I get a shutdown, the pipe will close (EOF), be able to handle that.
 * Close the pipe and exit when you're done. 
 * Ask me for any further questions. -Josh  */
 
/* Function prototype, fd is an array of 2 file descriptors
 *   fd[0] = audio->voice_control (input pipe) 
 *     -Pipe will only ever convey audio data
  *      --Audio Format is mono 16-bit signed LE sampled at 16kHz.
 *     -On shutdown, input pipe will close (read() will return 0).
 *   fd[1] = audio<-voice_control (output pipe)
 *     -send commands/errors using one of these headings, include newline:
 *       --VCCOM: use for commands (eg. "VCCOM:mute all\n")
 *       --VCERR: use for errors
 *       --If you need more, talk to me
 *     -Make sure to close this pipe before exiting.
 */
 
void start_voice(int* fd);
