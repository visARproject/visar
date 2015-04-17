from socket import *
import json
import threading
from ..interface import Interface
import time

POSE_PORT    = 19107 # port to communicate with pose server
TIMEOUT      = 1     # timeout for socket read (in seconds)

class PoseHandler(Interface):
  ''' Class connects to the standalone pose server and reads/stores
        this units location, orientaion, and velocity info (a Pose)
      Updates will be a tuple with either 'LOCAL' or 'REMOTE' and that update
      Local Updates will consist of a nested dictionary containing our pose information, formatted as: 
        {"position_ecef": {"x", "y", "z"}, "orientation_ecef": {"x", "y", "z", "w"}, 
         "velocity_ecef": {"x", "y", "z"}, "angular_velocity_ecef": {"x", "y", "z"}}
      Remote Unit Updates will be a dictionary of {ID : position_ecef}
  '''

  def __init__(self, frequency = 1.0/60.0):
    ''' Create the object, and connect to the server '''
    Interface.__init__(self) # call superclass init
    
    # setup the object vars
    self.pose = None          # this units current pose
    self.kill_flag = False    # kill flag for threads
    self.timer = time.clock() # get system time for update timer
    self.freq = frequency  # update frequency
    
    # Remotes
    self.remotes = {} # initialize dictionary for remote units
    
    try:    # setup socket and start the update thread
      self.sock = socket(AF_INET, SOCK_STREAM) # create the client socket
      self.sock.connect(('127.0.0.1',POSE_PORT)) # connect to servers
      self.updater = threading.Thread(target=self.update_thread) 
      self.updater.start()
    except: # exit on failure
      print 'Failed to start Pose Listener'
      self.kill_flag = True
    
  def destroy(self):
    ''' signal theads to die and shutdown the module '''
    self.kill_flag = True # signal thread to die
    print 'Shutting down pose module'  
    
  def update_thread(self):
    ''' Thread will listen on specified port and issue updates as appropriate '''
    line_buffer = '' # buffer for socket input
    while (not self.kill_flag): # loop until killed
      line_buffer += self.sock.recv(4096)
      lines = line_buffer.split('\r\n')
      
      if len(lines) > 1: # line data is avaliable
        # extract the json object from most recent full line
        for line in lines[0:len(lines)-2]:
          beacon  = json.loads(line) # parse the line
          try:
            #TODO: Check Protocol
            if beacon['id'] == 'self': # update this units pose
              self.pose = beacon['data'] 
            else: # update the remote units pose
              self.remotes['id'] = beacon['data'] 
          except: pass # ignore bad updates
        
        line_buffer = lines[len(lines) - 1] # put unfinished line into buffer
        
      # issue update at if timer is expired
      if (time.clock() - self.timer) > self.freq:
        self.timer = time.clock()  # reset the timer
        self.do_updates(('LOCAL',self.pose)) # issue the local  
        self.do_updates(('REMOTE',self.remotes)) # issue the remote update
      
    self.sock.close() # close the socket on exit
    
    
