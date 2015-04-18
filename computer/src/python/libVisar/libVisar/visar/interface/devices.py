import serial, threading, time
from interface import Interface

# device names (defined as udev rules)
PWR_NAME = '/dev/P_SERIAL' 
CON_NAME = '/dev/C_SERIAL'

# device info
BAUD = 115200

TIMEOUT = 1 # timeout listens after 1 second

BATT_LOW   = 9.6  # low (0%) value for battery voltage
BATT_HIGH  = 12.6 # high (100%) value for battery voltage

# list of control characters and thier functions
CONTROL_DICT = {'H':"Map", 'E':"Voice", 'C':"Select",
                'U':"Up", 'D':"Down", 'L':"Left", 'R':"Right"}

class DeviceHandler(Interface):
  def __init__(self):
    '''setup the serial device handler once this object is created, 
          you must call destroy() before exiting.
       Updates are typles in one of three formats:   
         ('BATTERY',  <battery level>)  # system battery level
         ('SHUTDOWN', None)             # system has recieved a shutdown command
         ('CONTROL', <control update>)  # button press
    '''

    Interface.__init__(self)

    self.kill_flag = False
    self.battery = 100 # current battery level
    self.controls = None # current control state
    self.do_shutdown = True # flag for shutting down unit on destroy()

    # try to open the serial ports and handler threads
    try:
      # serial port uses long reads to block and timeouts to wake back up
      self.pwr_port = serial.Serial(PWR_NAME, timeout=TIMEOUT, writeTimeout=TIMEOUT)
      self.pwr_port.baudrate = BAUD
      thread = threading.Thread(target=self.pwr_thread)
      thread.start()
    except: print 'Could not open power device' 
    
    '''
    try:
      # conn port uses a similar structure, timeouts determine how long to block for
      self.con_port = serial.Serial(CON_NAME, timeout=TIMEOUT, writeTimeout=TIMEOUT)
      self.con_port.baudrate = BAUD
      thread = threading.Thread(target=self.con_thread)
      thread.start()
    except: print 'Could not open controller device'
    '''
    
  def destroy(self):
    '''shutdown the module and issue shutdown command if specified'''
    self.kill_flag = True
    
  def pwr_thread(self):
    '''Poll device for updates at regular interval'''
    try:
      while not self.kill_flag:
        data = self.pwr_port.readline() # read an input
        datas = data.split('\r\n')[0].split(' ') # split input across space and ignore newline
        if datas[0] == 'voltage:':
          voltage = float(datas[1]) # get the battery level
          battery = int(100.0 * (voltage - BATT_LOW) / (BATT_HIGH - BATT_LOW))
          # issue the update if new value is significantly different
          if battery < (self.battery-1) or battery > (self.battery+1):
            self.battery = battery
            self.do_updates(('BATTERY',battery)) # Issue battery update
        elif datas[0] == 'shutdown':
          self.do_updates(('SHUTDOWN','')) # Issue shutdown command
          break
    except: print 'Error communicating with Power device'
    
    
    self.pwr_port.close()

  def con_thread(self):
    '''Listen for status updates from controller device'''
    while not self.kill_flag:
      try: 
        data = self.con_port.read(1) # read in a single character from port
        self.do_updates(('CONTROL', CONTROL_DICT[data])) # issue update
      except: pass # timeout/key-error occured, ignore it
    
