/* VAL: I'll define a start/stop voice interface in the audio controller,
 *    anything beond that is for you to manage.
 * This file defines how to start your program. (define the prototyped function)
 * The fd is for a pipe which mirrors the audio input, handle it however.
 * If I get a shutdown, the pipe will close (EOF), be able to handle that.
 * Close the pipe and exit when you're done. 
 * Ask me for any further questions. -Josh  */
 
//Function prototype, fd is the input pipe's file descriptor
void start_voice(int fd);
