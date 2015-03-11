from socket import *
import json
import threading
import interface

POSE_PORT    = 19107 # port to communicate with pose server
TIMEOUT      = 1     # timeout for socket read (in seconds)
UPDATE_COUNT = 5  # serer updates before update is issued

class Handler(interface.Interface):
  ''' Class connects to the standalone pose server and reads/stores
        this units location and orientaion (Pose) info and the GPS locaiton
        info for other units (beacons and headsets). 
      Updates will consist of a two arguments: 
        1) A tuple with this unit's GPS and Orientation (as tuples)
        2) A dictionary containg the GPS info of all avaliable units
  '''

  def __init__(self):
    ''' Create the object, and connect to the server '''
    interface.Interface.__init__(self) # call superclass init
    
    # TODO: confirm protocol once server is back up
    self.sock = socket(AF_INET, SOCK_STREAM) # create the client socket
    self.sock.connect(('127.0.0.1',POSE_PORT)) # connect to server
    self.position = None    # default position
    self.orientation = None # default orientation
    self.kill_flag = False  # kill flag for threads
    
    # setup and start the update thread
    self.updater = threading.Thread(target=self.update_thread) 
    self.updater.start()
    
  def destroy():
    ''' signal theads to die and shutdown the module '''
    self.kill_flag = True # signal thread to die
    print 'Shutting pose module'  
    
  def update_thread(self):
    ''' Thread will listen on specified port and issue updates as appropriate '''
    while (not kill_flag): # loop until killed
      print 'stuff'
      # TODO: actually code this
    
    self.sock.close() # close the socket
    
    
    
