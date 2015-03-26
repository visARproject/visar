from vispy.util.transforms import perspective, translate, rotate, scale, xrotate, yrotate, zrotate

from ...OpenGL.utils.transformations import quaternion_matrix, euler_from_matrix, euler_from_quaternion
from .menu_controller import Menu_Controller
from ...OpenGL.utils import Logger
from ..audio import AudioController, Parser
from ..network import NetworkState, PoseHandler
from ..interface import Interface

import os
import numpy as np
import socket, random

class State(object):
    '''Track the global state of the VisAR unit

    Notes:
        Position - ECEF
        Orientation - Quaternion
        Velocity - ECEF
        Angular Velocity - Quaternion

    '''

    absolute_file_path = os.path.dirname(os.path.realpath(__file__))

    targets = [
        (10, 10, 10),
    ]

    orientation_quaternion = (0.50155109, 0.03353513, 0.05767266, 0.86255189)
    orientation_matrix = quaternion_matrix(orientation_quaternion)
    roll, pitch, yaw = euler_from_matrix(orientation_matrix)

    position_ecef = np.array((738575.65, -5498374.10, 3136355.42))

    menu_controller = Menu_Controller()

    id_code = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWKYZ') for i in range(3)) # random 3 char id
    hostname = socket.gethostname() # get computer name for id
    network_state = NetworkState(id_code, hostname, 'default status') # create network state tracker
    audio_controller = AudioController() # create audio manager
    
    # create and start the pose update listener (default to mil)
    pose = {"position_ecef": {"x":738575.65, "y":-5498374.10, "z":3136355.42}, "orientation_ecef": {"x": 0.50155109,  "y": 0.03353513,  "z": 0.05767266, "w": 0.86255189}, "velocity_ecef": {"x": -0.06585217, "y": 0.49024074, "z": 0.8690958}, "angular_velocity_ecef": {"x": 0.11570315, "y": -0.86135956, "z": 0.4946438}} 
    
    def pose_callback(event):
        Logger.log("Pose Update %s" % (event,))
        State.pose = event # store the full value
        # call the appropriate update methods
        position = (event['position_ecef']['x'], event['position_ecef']['y'], 
                    event['position_ecef']['z'])
        State.set_position(position)
        orientation = (event['orientation_ecef']['x'], event['orientation_ecef']['y'], 
                    event['orientation_ecef']['z'], event['orientation_ecef']['w'])
        State.set_orientation(orientation)
      
    pose_handler = PoseHandler(frequency=1/30)
    pose_handler.add_callback(pose_callback)
    
    # define a network status object and callback funciton
    network_peers = network_state.peers
    
    # Callback method for the network event updates
    def network_callback(event):
      Logger.log("Network Update: %s" % (event,))
      State.network_peers = event
      
    network_state.add_callback(network_callback) # add the callback
    
    # setup and initialize the voice control/audio event handler
    def audio_callback(event):
      '''Callback funciton will call appropriate function based on Voice command'''
      Logger.log("Audio Callback: %s" % (event,))
      # if(event[0] == 'VCERR'): print 'Voice Error: ' + event[1]
      if(event[0] == 'VCCOM'):
        command = Parser.parse(event[1])
        State.args = command[1] # store the args, or None as appropriate
        State.action_dict[command[0]]() # call the command
<<<<<<< HEAD

    audio_controller.add_callback(audio_callback) # add the callback
    
=======
        
    voice_event = Interface()
    voice_event.add_callback(voice_callback)

>>>>>>> 3219bf7354b2f52bd14851a15d53eff0bedf3943
    calling = False # toggle value for call
  
    args = None # arguments for function calls

    button_dict = {}
    buttons = set()
    current_button = 3

    hide_map = False

    @classmethod
    def register_button(self, position, action):
        self.buttons = self.buttons.union({position})
        self.button_dict[position] = action

    @classmethod
    def button_up(self):
        if self.current_button < max(self.buttons):
            self.current_button += 1

    @classmethod
    def button_down(self):
        if self.current_button > min(self.buttons):
            self.current_button -= 1

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
        if call_target is None: call_target = self.id_code # default value
        if not '.' in call_target: call_ip = self.network_peers[call_target][0] # get the ip address if not one already
        else: call_ip = call_target # call target is already an ip address
        Logger.warn("Attempting to call " + call_target + " at ip " + call_ip + ".")
        self.audio_controller.start(call_ip) # start a call
        self.calling = True

    @classmethod
    def end_call(self):
        '''End the call'''
        Logger.warn('Ending Call')
        self.audio_controller.stop() # hang up
        self.calling = False # set flag appropriatley

    @classmethod
    def start_listening(self):
      '''Begin listening for voice commands'''
      self.audio_controller.start_voice()

    @classmethod
    def stop_listening(self):
      '''Stop listening to voice commands'''
      self.audio_controller.stop_voice()

    @classmethod
    def update_status(self):
      '''Change our network status to the contents the args register'''
      status = self.args # get the status from argument register
      self.args = None   # clear register
      if status is None: status = 'default status' # ensure correct value
      self.network_state.update_status(status)     # send update

    @classmethod
    def set_orientation_matrix(self, orientation_matrix):
        gl_orientation_matrix = orientation_matrix
        self.roll, self.yaw, self.pitch = euler_from_matrix(gl_orientation_matrix)

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
        self.pose_handler.destroy()
        self.network_state.destroy()
        self.audio_controller.destroy()
        
    @classmethod
    # Temporary Method, delete later
    def set_target(self):
        '''set the argument register to value from command line'''
        self.args = raw_input("Enter target value: ")
        
State.action_dict = {
        'example'       : lambda: Logger.warn("Example button pressed!"),
        'make call'     : State.make_call,
        'end call'      : State.end_call,
        'toggle map'    : State.hide_map,
        'start voice'   : State.start_listening,
        'stop voice'    : State.stop_listening,
        'list peers'    : lambda: Logger.warn("Peers: %s" % (State.network_peers,)),
        'set target'    : State.set_target,
        'update status' : State.update_status,
    }
