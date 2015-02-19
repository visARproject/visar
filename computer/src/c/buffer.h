/* Header file for handling the auidobuffers */

//useful buffer macros
#define _BUFFER_SIZE(x,y,max) (((y)-(x)>=0)?(y)-(x):(max)+(y)-(x))
#define _BUFFER_FULL(x,y,max) (_BUFFER_SIZE(x,y,max)==((max)-1))
#define _BUFFER_EMPTY(x,y)    ((y)==(x))
#define BUFFER_SIZE(x)        _BUFFER_SIZE((x).start,(x).end,(x).size)
#define BUFFER_FULL(x)        _BUFFER_FULL((x).start,(x).end,(x).size)
#define BUFFER_EMPTY(x)       _BUFFER_EMPTY((x).start,(x).end)

//useful queue aware macros (Push/Pop increment pointers, get's just peek)
#define GET_QUEUE_HEAD(x) ((x).data+((x).start*(x).frame_size))
#define GET_QUEUE_TAIL(x) ((x).data+((x).end*(x).frame_size))
#define INC_QUEUE_HEAD(x) ((x).start = ((x).start+1 < (x).size)? (x).start+1: 0)
#define INC_QUEUE_TAIL(x) ((x).end = ((x).end+1 < (x).size)? (x).end+1: 0)

//audiobuffer struct to handle ring buffer queue
typedef struct{
  int     start;      //start of queue
  int     end;        //end of queue
  char*   data;       //data pointer
  size_t  frame_size; //size of a single frame
  size_t  size;       //number of frames
} audiobuffer;

//create/destroy functions (defined in buffer.c)
audiobuffer* create_buffer(size_t frame_size, size_t frames);
void free_buffer(audiobuffer* buf);
