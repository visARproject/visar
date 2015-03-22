from vispy.util.transforms import perspective, translate, rotate, scale, xrotate, yrotate, zrotate

from ...OpenGL.utils.transformations import quaternion_matrix, euler_from_matrix, euler_from_quaternion
from .menu_controller import Menu_Controller
from ...OpenGL.utils import Logger
from ..audio import AudioController
from ..audio import Parser
from ..network import NetworkState
from ..interface import Interface

import os
import numpy as np
import socket

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

    network_state = NetworkState(socket.gethostname(), 'testname', 'status') # create network state tracker
    audio_controller = AudioController() # create audio manager
    
    # define a network status object and callback funciton
    peers = None
    
    @classmethod
    def network_callback(event):
      self.network_peers = event
      
    network_state.add_callback(network_callback) # add the callback
    
    # setup and initialize the voice control event handler
    @classmethod
    def voice_callback(event):
      '''Callback funciton will call appropriate function based on Voice command'''
      Logger.warn("Voice Callback: " + event[0] + "--" + event[1])
      if(event[0] == 'VCERR'): print 'Voice Error: ' + event[1]
      elif(event[0] == 'VCCOM'):
        command = Parser.parse(event[1])
        self.args = command[1] # store the args, or None as appropriate
        self.action_dict[command[0]]() # call the command no arguments

    voice_event = Interface()
    voice_event.add_callback(self.voice_event)

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
        Logger.warn("Attempting to make a call")
        # end call first
        if self.calling:
            self.end_call()
            
        # call the target specified in the args register
        call_target = args
        if args is None: call_target = '127.0.0.1' # default value
        self.audio_controller.start(call_target) # start a call
        self.calling = True

    @classmethod
    def end_call(self):
        '''End the call'''
        self.audio_controller.stop() # hang up
        self.calling = False # set flag appropriatley

    @classmethod
    def start_listening(self):
      '''Begin listening for voice commands'''
      self.audio_controller.start_voice(self.voice_listener)

    @classmethod
    def stop_listening(self):
      '''Stop listening to voice commands'''
      self.audio_controller.stop_voice()

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
        self.network_state.destroy()
        self.audio_controller.destroy()

State.action_dict = {
        'example': lambda: Logger.log("Example button pressed!"),
        'make call': State.make_call,
        'toggle map': State.hide_map,
        'end call': State.end_call,
    }
