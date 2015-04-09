import serial
import threading
import time
from ..interface import Interface

# device names (defined as udev rules)
PWR_NAME = ''
CON_NAME = ''

# device info
BAUD = 115200

FREQ = 1/30 # update time
TIMEOUT = 1 # timeout listen after 1 second
KILL_TIME = 10000 # give system 15 seconds to shutdown

# list of control characters and thier functions
CONTROL_DICT = {"A":"Example"}

class device_handler(Interface):
  def __init__(self):
    '''setup the serial device handler once this object is created, 
          you must call destroy() before exiting.
       Updates are one typles in one of three formats:   
         ('BATTERY',  <battery level>)  # system battery level
         ('SHUTDOWN', None)             # system has recieved a shutdown command
         ('CONTROL', <control update>)  # button press
    '''

    self.kill_flag = False
    self.battery = 100 # current battery level
    self.controls = None # current control state
    self.do_shutdown = True # flag for shutting down unit on destroy()

    # try to open the serial ports and handler threads
    try:
      # serial port uses long reads to block and timeouts to wake back up
      self.pwr_port = serial.Serial(PWR_NAME, timeout=FREQ, writeTimeout=FREQ)
      self.pwr_port.baudrate = BAUD
      thread = threading.Thread(target=self.pwr_thread)
      thread.start()
    except: print 'Could not open power device'
    
    try:
      # conn port uses a similar structure, timeouts determine how long to block for
      self.con_port = serial.Serial(CON_NAME, timeout=TIMEOUT, writeTimeout=TIMEOUT)
      self.con_port.baudrate = BAUD
      thread = threading.Thread(target=self.con_thread)
      thread.start()
    except: print 'Could not open controller device'
    
    
  def destroy(self, shutdown=True):
    '''shutdown the module and issue shutdown command if specified'''
    self.kill_flag = True
    self.do_shutdown = shutdown
    
  def pwr_thread(self):
    '''Poll device for updates at regular interval'''
    try:
      while not self.kill_flag:
        self.pwr_port.write('s')
        data = self.read(20) # read an input, use timeout to block for specified frequency
        datas = data..split('\n')[0].split(' ') # split input across space and ignore newline
        battery = int(datas[0]) # get the battery level
        if battery is int and not battery == self.battery:
          self.battery = battery
          self.do_update(('BATTERY',battery)) # Issue battery update
        if not datas[1] == '1':
          self.do_update(('SHUTDOWN','')) # Issue shutdown command
    except: print 'Error communicating with Power device'
    
    if self.do_shutdown:
      try:  
        self.pwr_port.write('k' + str(KILL_TIME)) # TODO: check protocol
      except: print 'Could not write shutdown command'
    
    self.pwr_port.close()

  def con_thread(self):
    '''Listen for status updates from controller device'''
    while not self.kill_flag:
      try: 
        data = self.cnt_port.read(1) # read in a single character from port
        self.do_update('CONTROL', CONTROL_DICT[data]) # issue update
      except: pass # timeout occured, ignore it
    
