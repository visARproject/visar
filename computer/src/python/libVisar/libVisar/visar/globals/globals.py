from vispy.util.transforms import perspective, translate, rotate, scale, xrotate, yrotate, zrotate

from ...OpenGL.utils.transformations import quaternion_matrix, euler_from_matrix, euler_from_quaternion
from .menu_controller import Menu_Controller
from ...OpenGL.utils import Logger
from ..audio import AudioController, Parser
from ..network import NetworkState, PoseHandler
from ..interface import Interface, DeviceHandler
from .actions import Actions

import numpy as np
import os, socket, random, copy

class State(object):
    '''Track the global state of the VisAR unit
       You must call State.do_init() before using this module
       State.destroy() must be called before exit if do_init() was called.

    Notes:
        Position - ECEF
        Orientation - Quaternion
        Velocity - ECEF
        Angular Velocity - Quaternion

    '''

    absolute_file_path = os.path.dirname(os.path.realpath(__file__))

    orientation_quaternion = (0.50155109, 0.03353513, 0.05767266, 0.86255189)
    orientation_matrix = quaternion_matrix(orientation_quaternion)
    roll, pitch, yaw = euler_from_matrix(orientation_matrix)

    position_ecef = np.array((738575.65, -5498374.10, 3136355.42))

    menu_controller = Menu_Controller()
    
    # create placeholder references for status objects
    network_state = None
    audio_controller = None
    pose_handler = None
    device_handler = None
    
    action_dict = None

    # Visual toast text
    toast = None
    
    # create pose update listener reference and default pose (default to mil)
    pose = {"position_ecef": {"x":738575.65, "y":-5498374.10, "z":3136355.42}, "orientation_ecef": {"x": 0.50155109,  "y": 0.03353513,  "z": 0.05767266, "w": 0.86255189}, "velocity_ecef": {"x": -0.06585217, "y": 0.49024074, "z": 0.8690958}, "angular_velocity_ecef": {"x": 0.11570315, "y": -0.86135956, "z": 0.4946438}}  
    targets = {}
    
        
    # network information    
    network_peers = None # create object reference, but don't init it yet
    id_code = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWKYZ') for i in range(3)) # random 3 char id
    hostname = socket.gethostname() # get computer name for id
  
    # device information
    battery = 100 # battery level (0-100ish)
    shutdown_flag = False # system kill flag
          
    calling = False # toggle value for call
  
    args = None # arguments for function calls

    button_dict = {}
    buttons = set()
    current_button = 3

    hide_map = False
    audio = True

    @classmethod
    def do_init(self, audio=True):
        '''Function will initialize all status listeners and controllers
           Once this function is called, you must call State.destroy() before 
              exiting or hanging threads will prevent program from closing.
        '''
        self.audio = audio
        self.action_dict = Actions.get_actions(self) # bind the avaliable actions
        
        # initialize state listeners and controllers
        self.network_state = NetworkState(self.id_code, self.hostname, 'default status') # create network state tracker

        if(audio): self.audio_controller = AudioController() # create audio manager
        
        self.pose_handler = PoseHandler(frequency=1.0/30.0)
        self.pose_count = 0

        
        self.device_handler = DeviceHandler() 

        # setup the pose handler and callback functions
        def pose_callback(event):
            # don't issue all updates
            if(self.pose_count == 0):
                Logger.log("Periodic Pose Update: %s" % (event,))
                self.pose_count = 511
            self.pose_count -= 1
            
            # call the appropriate update methods
            if event[0] == 'LOCAL':
              event = event[1]
              try:
                  position = (event['position_ecef']['x'], event['position_ecef']['y'], 
                              event['position_ecef']['z'])
                  State.set_position(position)
                  orientation = (event['orientation_ecef']['w'], event['orientation_ecef']['x'], event['orientation_ecef']['y'], 
                              event['orientation_ecef']['z'],)
                  State.set_orientation(orientation)
                  State.pose = event # store the full value
              except: Logger.log("Bad Pose Update")

            elif event[0] == 'REMOTE': # grab a copy of remote data
              self.targets = copy.deepcopy(event[1])              
        self.pose_handler.add_callback(pose_callback)


        # setup and initialize the voice control/audio event handler
        def audio_callback(event):
            '''Callback funciton will call appropriate function based on Voice command'''
            Logger.log("Audio Callback: %s" % (event,))
            # if(event[0] == 'VCERR'): print 'Voice Error: ' + event[1]
            if(event[0] == 'VCCOM'):
                command = Parser.parse(event[1])
                try:
                    State.args = command[1] # store the args, or None as appropriate
                    State.action_dict[command[0]]() # call the command
                except: Logger.log('Bad Command, expected: (func, args), got: %s' % (command,))
            
        if(audio): self.audio_controller.add_callback(audio_callback) # add the callback
        
        self.network_peers = self.network_state.peers # get the initial peers
    
        # Callback method for the network event updates
        def network_callback(event):
            Logger.log("Network Update: %s" % (event,))
            State.network_peers = event
      
        self.network_state.add_callback(network_callback) # add the callback
        
        # callback method for device handler updates
        def device_callback(event):
            Logger.log('Device Update %s' % (event,))
            if event[0] == 'BATTERY': 
                State.battery = event[1]
            elif event[0] == 'SHUTDOWN':
                State.shutdown_flag = True
            elif event[0] == 'CONTROL':
                if   event[1] == "Up"     : State.button_up()
                elif event[1] == "Down"   : State.button_down()
                # elif event[1] == "Left"   : State.button_left() #TODO: Jake, add these
                # elif event[1] == "Right"  : State.button_right() #TODO: Jake, add these
                elif event[1] == "Select" : State.press_enter()
                elif event[1] == "Voice"  : State.toggle_vc() # Toggle VC
                elif event[1] == "Map"    : State.hide_map()  # TODO: map scroll mode?
                else: Logger.warn('Bad Update %s' % (event,))
            else: Logger.warn('Bad Update %s' % (event,))
        
        self.device_handler.add_callback(device_callback) # add the callback
                  
    @classmethod
    def register_button(self, position, action):
        self.buttons = self.buttons.union({position})
        self.button_dict[position] = action

    @classmethod
    def button_up(self):
        if self.current_button < max(self.buttons):
            self.current_button += 1
        elif self.current_button == max(self.buttons):
            self.current_button = min(self.buttons)

    @classmethod
    def button_down(self):
        if self.current_button > min(self.buttons):
            self.current_button -= 1
        elif self.current_button == min(self.buttons):
            self.current_button = max(self.buttons)

    @classmethod
    def press_enter(self):
        current_button_action = self.button_dict[self.current_button]
        current_action = self.action_dict[current_button_action.lower()]
        current_action()

    @classmethod
    def hide_map(self):
        self.hide_map = not self.hide_map

    @classmethod
    def make_call(self):
        '''Funciton will make a voice call to target specified in argumets
           It will interrupt the current call if one already exists before starting another
        '''
        # end call first        
        if self.calling:
            self.end_call()
            
        # call the target specified in the args register
        call_target = self.args
        self.args = None # clear the argument register
        try:
            if call_target is None: return # dont do it, seriously
            if not '.' in call_target: call_ip = self.network_peers[call_target][0] # get the ip address if not one already
            else: call_ip = call_target # call target is already an ip address
            Logger.log("Attempting to call " + call_target + " at ip " + call_ip + ".")
            self.audio_controller.start(call_ip) # start a call
            self.calling = True
        except: Logger.warn('Could not make call: %s ' % (call_target,))
          

    @classmethod
    def end_call(self):
        '''End the call'''
        Logger.warn('Ending Call')
        self.audio_controller.stop() # hang up
        self.calling = False # set flag appropriatley

    @classmethod
    def toggle_vc(self):
        '''Stop or begin listening to voice commands'''
        self.audio_controller.stop_voice() or self.audio_controller.start_voice()

    @classmethod
    def update_status(self):
        '''Change our network status to the contents the args register'''
        status = self.args # get the status from argument register
        self.args = None   # clear register
        if status is None: status = 'default status' # ensure correct value
        self.network_state.update_status(status)     # send update

    @classmethod
    def set_orientation_matrix(self, orientation_matrix):
        # gl_orientation_matrix = orientation_matrix
        self.orientation_matrix = orientation_matrix
        # self.orientation_matrix = orientation_matrix

        # self.roll, self.pitch, self.yaw = euler_from_matrix(gl_orientation_matrix)

    @classmethod
    def set_orientation(self, quaternion):
        self.orientation_quaternion = quaternion
        self.set_orientation_matrix(quaternion_matrix(quaternion))

    @classmethod
    def set_position(self, position_ecef):
        assert np.linalg.norm(position_ecef) < 6700000.0, "You must be on the planet Earth to use Visar."
        assert len(position_ecef) == 3, "position_ecef must be XYZ in ECEF"
        self.position_ecef = np.array(position_ecef)

    @classmethod
    def bind_function(self, parameter, callback_function):
        '''Pass a string parameter and a function that you'd like to 
        This function registers a callback function with the global state tracker

        Examples:
        > Let's say you have a function called "map" that you want to be called every time a map coordinate changes.
        >> State.bind_function('position', map)

        Whenever the 'position' parameter is changed, your function "map" will be called on it.

        You can use this to change some state inside your class, or do something weird with a drawable

        '''
        return NotImplemented
    
    @classmethod
    def destroy(self):  
        '''Signal modules to die and expire handler threads'''
        self.pose_handler.destroy()
        self.network_state.destroy()
        if(self.audio): self.audio_controller.destroy()
        self.device_handler.destroy() 
        
    @classmethod
    # Temporary Method, delete later
    def set_target(self):
        '''set the argument register to value from command line'''
        self.args = raw_input("Enter target value: ")
        self.toast = 'Args: %s' % (self.args,) # pop a toast too


