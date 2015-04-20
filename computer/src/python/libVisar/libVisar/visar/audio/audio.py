from subprocess import *
import time, os
import threading
import socket
from ..interface import Interface

fpath = os.path.dirname(os.path.realpath(__file__))
AUDIO_PROGRAM  = os.path.join(fpath, 'audio') # path to audio module
VC_PROGRAM     = os.path.join(fpath, 'vc')    # path to vc module
CONTROL_SERVER = 19102        # TCP comms port for handshaking (server)
AUDIO_PORT     = 19103        # UDP port for audio data
VC_FIFO_NAME   = '/tmp/vsr_vc_pipe' # pipe for voice commands
AUDIO_WAIT_TM  = .05          # wait 50ms between operations
SERVER_TIMEOUT = 1            # timeout for server socket (in seconds)
VC_HOLD_TIME   = 1            # wait at least 1 second between vc presses

# thread locking
lock = threading.RLock()
def thread_lock(func):
  def locked_func(*args,**kwargs):
    global lock
    lock.acquire()
    ret = func(*args, **kwargs)
    lock.release()
    return ret
  return locked_func

# audio controller class, interfaces with other units and the standalone audio module
# interface events send string tuples (status, host/argument)
class AudioController(Interface):
  def __init__(self):
    Interface.__init__(self)
    self.connection = None    # connection state (host, port, mode)
    self.vc_active  = False   # Boolean to track when vc is active
    self.child = Popen(AUDIO_PROGRAM, bufsize=0, stdin=PIPE, stdout=PIPE, stderr=STDOUT, universal_newlines=True) # open subprocess
    self.kill_flag = False
    self.input_buffer = ''
    self.vc_timer = 0
    
    # create the socket/pipe objects
    self.c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allow socket reuse
    self.connected = False
    
    # create the fifo pipe
    try:    
      os.mkfifo(VC_FIFO_NAME) # create the fifo
    except: 
      os.unlink(VC_FIFO_NAME) # remove existing fifo
      os.mkfifo(VC_FIFO_NAME) # recreate the fifo
    
    # start the voice control program
    #program = Popen(VC_PROGRAM)
    #time.sleep(.05)
    
    # check if program has crashed
    #if program.poll() is not None:
    #  print "VC communication failed"
    #  self.vc_pipe = None
    #  return
    #else: # program didn't die
    #  self.vc_pipe = os.open(VC_FIFO_NAME, os.O_RDONLY) # open the pipe

    # backup method, less robust, but it seems like val's program wont't work otherwise
    self.vc_pipe = os.open(VC_FIFO_NAME, os.O_RDONLY) # open the pipe (will block until read from)

    # create the thread objects and start the threads
    self.comms  = threading.Thread(target=self.comms_thread)
    self.parse  = threading.Thread(target=self.parse_thread)
    self.server = threading.Thread(target=self.server_thread)
    self.comms.start()
    self.parse.start()
    self.server.start()
    
  
  def destroy(self):    
    self.stop() # stop active calls
    self.vc_timer = 0
    self.stop_voice() # stop VC
    
    self.kill_flag = True # kill the process
    
    # send shutdown to child process
    lock.acquire()
    self.child.stdin.write('shutdown\n') # shutdown thread when the module dies
    lock.release()
    
    if self.vc_pipe is not None:  os.close(self.vc_pipe) # close the pipe
    time.sleep(1) # sleep to give process things
    os.unlink(VC_FIFO_NAME) # delete the fifo
  
  # start audio communication with network device
  @thread_lock
  def start(self, host, port=AUDIO_PORT, mode='both'):
    if(self.connection is not None):
      self.do_updates(('Warn','Start() ignored due to active connection ' + str(self.connection)))
      return None;
  
    try:
      self.c_sock.connect((host,CONTROL_SERVER)) # connect to peer for handshake
      self.c_sock.send(mode + '\n')

      self.connection = (host, port, mode) # store connection information
      command = 'start ' + mode + ' -host ' + host + ' -port ' + str(AUDIO_PORT) + '\n'
      self.child.stdin.write(command) # send start command
    
      # spawn thread to listen for shutdown
      self.client = threading.Thread(target=self.client_thread)
      self.client.start()
              
      self.do_updates(('Connected', host)) # notify connection success
      return True # connection succeeded

    except:
      return False # connection failed
  
  # stop audio communication
  @thread_lock
  def stop(self):
    if(self.connection is None or self.connection[0] == 'voice'): 
      # self.do_updates('Warn', 'Stop function called with no active call')
      return  # not actually connected
    
    # disconnect from the peer
    try:
      self.c_sock.send('shutdown\n') # send shutdown command
      self.c_sock.close() # close the socket conneciton
      self.c_sock = None # nulify the socket
      self.child.stdin.write('stop both\n')    # send stop command
      if self.vc_active: self.connection = ('voice', None, 'mic') # check if voice was active (prevents shutdown)
      else: self.connection = None              # connection is no longer active
    except: pass
        
    self.connected = False
  
  @thread_lock
  def set_volume(self, volume):
    '''Set the speaker volume for the system.
       Volume must be integer between 0 and 100
    '''
    
    #check range and type of volume
    if (type(volume) is not int) or volume > 100 or volume < 0: 
      self.do_updates(('Warn','Ignored Invalid Volume: ' + str(volume)))
      return
    
    self.child.stdin.write('set -volume ' + str(volume) + ' \n')
    
    
  # start the voice controller
  def start_voice(self):
    if self.vc_active  or time.clock() < self.vc_timer + VC_HOLD_TIME: # check if already listening
      self.do_updates(('Error','VC is already active'))
      return False
    lock.acquire()
    self.child.stdin.write('voice_start\n')
    lock.release()
    self.vc_active = True
    self.vc_timer = time.clock()
    self.do_updates(('started_vc','')) # send start log
    if(self.connection is None):
      self.connection = ('voice', None, 'mic') # connection is in voice mode
    return True
  
  # stops the voice controller
  def stop_voice(self):
    if not self.vc_active or time.clock() < self.vc_timer + VC_HOLD_TIME: 
      return False # exit if not listening
    global lock
    lock.acquire()
    self.child.stdin.write('voice_stop\n')
    lock.release()
    self.do_updates(('stopped_vc','')) # send shutdown update
    self.vc_active = False # stop vc activities
    self.vc_timer = time.clock()
    if(self.connection is not None and self.connection[0] == 'voice'): 
      self.connection = None  # clear the connection state
    return True
  
  # thread to handle communicating with child process
  def comms_thread(self):    
    while(not self.kill_flag): self.do_comms() # do the comms
  
  # do the communcation to child process
  def do_comms(self):
    try: 
      #out = os.read(self.child.stdout.fileno(),80) # get data out
      out = os.read(self.vc_pipe, 80) # read from the pipe
      global lock
      lock.acquire()
      self.input_buffer += out # append responses to input buffer
      lock.release()
    except: self.do_updates(('Warn','Comms Error, Possibly the result of a shutdown'))
  
  # thread to handle parsing the output from the child process
  def parse_thread(self):
    while(not self.kill_flag): 
      time.sleep(AUDIO_WAIT_TM) # wait between operations
      self.do_parse(self.split_parse_buffer()) # parse the input
  
  # split the parse into seperate commands
  @thread_lock
  def split_parse_buffer(self):
    comms = self.input_buffer.split('\n') # split the input on newlines
    self.input_buffer = comms.pop()  # put the last result back on the buffer (might be incomplete)
    return comms    # return the comands
  
  # iterate over input and parse commands
  def do_parse(self, parse):
    for line in parse:
      part = line.split(':') # split line across colon
      if len(part) < 2: self.do_updates((line, '')) # make sure we have 2 inputs
      else: self.do_updates((part[0], part[1])) # send the event
  
  # server handler thread
  def server_thread(self):
    try: 
      self.s_sock.bind(('',CONTROL_SERVER))
    except:
      print 'Failed to start audio program, check network settings'
      self.kill_flag = True
      return
    
    self.s_sock.listen(1)
    self.s_sock.settimeout(SERVER_TIMEOUT) # timeout after 1 second
    global lock # use the global lock object
    while(not self.kill_flag):
      try: 
        conn, addr = self.s_sock.accept() # accept a connection
        conn.settimeout(SERVER_TIMEOUT)   # timeout after 1 second
      except: continue  # loop on timeout
      self.connected = True
      data = conn.recv(1024) # get input from socket
      datas = data.split('\n') # split the input args
      lock.acquire()
      self.connection = (addr[0], AUDIO_PORT, datas[0]) # setup connection
      command = 'start ' + datas[0] + ' -host ' + addr[0] + ' -port ' + str(AUDIO_PORT) + '\n'
      self.child.stdin.write(command) # send start command
      lock.release()
      self.do_updates(('Conncted',addr[0])) # notify connection termination
      while ((conn is not None) and self.connected):
        try:
          if(conn.recv(10) == 'shutdown\n'): # wait for shutdown
            conn.close() # close the socket
            conn = None # set it to none so loop exits
        except: pass # ignore timeouts
      
      if not self.connected:
        try:
          conn.send('shutdown\n')
          conn.close()
          conn = None
        except: pass
        self.connected = False
      
      # shutdown the module
      lock.acquire()
      self.child.stdin.write('stop both\n')    # send stop command
      if self.vc_active: self.connection = ('voice', None, 'mic') # check if voice was active (prevents shutdown)
      else: self.connection = None              # connection is no longer active
      lock.release()
      self.do_updates(('Disconnected',None)) # notify connection termination

  def client_thread(self):  
    # run until server shuts us down
    self.c_sock.settimeout(SERVER_TIMEOUT)   # timeout after 1 second
    while self.c_sock is not None:
      try:
        if(self.c_sock.recv(10) == 'shutdown\n'): # wait for shutdown
          self.c_sock.close() # close the socket
          self.c_sock = None # set it to none so loop exits
      except: pass # ignore timeouts
            
    global lock        
    lock.acquire()            
    self.child.stdin.write('stop both\n')    # send stop command
    if self.vc_active: self.connection = ('voice', None, 'mic') # check if voice was active (prevents shutdown)
    else: self.connection = None              # connection is no longer active
    lock.release()
    
    self.c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # get a new socket

    self.do_updates(('Disconnected',None)) # notify connection termination

