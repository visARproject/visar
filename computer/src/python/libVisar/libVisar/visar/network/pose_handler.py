from socket import *
import json
import threading
import interface
import time

POSE_PORT    = 19107 # port to communicate with pose server
TIMEOUT      = 1     # timeout for socket read (in seconds)
UPDATE_TIMER = 1/60  # time between issued updates

class PoseHandler(interface.Interface):
  ''' Class connects to the standalone pose server and reads/stores
        this units location, orientaion, and velocity info (a Pose)
      Updates will consist of a nested dictionary containing our pose information, formatted as: 
        {"position_ecef": {"x", "y", "z"}, "orientation_ecef": {"x", "y", "z", "w"}, 
         "velocity_ecef": {"x", "y", "z"}, "angular_velocity_ecef": {"x", "y", "z"}}
  '''

  def __init__(self, UPDATE_TIMER = 1/60):
    ''' Create the object, and connect to the server '''
    interface.Interface.__init__(self) # call superclass init
    
    # setup the object vars
    self.pose = None          # this units current pose
    self.kill_flag = False    # kill flag for threads
    self.line_buffer = ''     # input line buffer
    self.timer = time.clock() # get system time for update timer
    self.freq = UPDATE_TIMER  # update frequency
    
    # setup socket and start the update thread
    self.sock = socket(AF_INET, SOCK_STREAM) # create the client socket
    self.sock.connect(('127.0.0.1',POSE_PORT)) # connect to servers
    self.updater = threading.Thread(target=self.update_thread) 
    self.updater.start()
    
  def destroy():
    ''' signal theads to die and shutdown the module '''
    self.kill_flag = True # signal thread to die
    print 'Shutting pose module'  
    
  def update_thread(self):
    ''' Thread will listen on specified port and issue updates as appropriate '''
    while (not kill_flag): # loop until killed
      line_buffer += sock.recv(4096)
      lines = line_buffer.split('\r\n')
      
      if len(lines) > 1: # line data is avaliable
        # extract the json object from most recent full line
        self.pose = json.loads(lines[len(lines) - 2])
        self.line_buffer = lines[len(lines)] # put unfinished line into buffer
      
      # issue update at if timer is expired
      if (time.clock() - self.timer) > self.freq:
        self.timer = time.clock()  # reset the timer
        self.do_updates(self.pose) # issue the update
      
    self.sock.close() # close the socket on exit
    
    
