from ...OpenGL.utils.transformations import quaternion_matrix, euler_from_matrix, euler_from_quaternion
from .menu_controller import Menu_Controller
from ...OpenGL.utils import Logger
from ..audio import AudioController
from ..network import NetworkState

import numpy as np

class State(object):
    '''Track the global state of the VisAR unit

    Notes:
        Position - ECEF
        Orientation - Quaternion
        Velocity - ECEF
        Angular Velocity - Quaternion

    '''

    targets = [
        (10, 10, 10),
    ]

    orientation_quaternion = (0.50155109, 0.03353513, 0.05767266, 0.86255189)
    orientation_matrix = quaternion_matrix(orientation_quaternion)
    roll, pitch, yaw = euler_from_matrix(orientation_matrix)

    position_ecef = np.array((738575.65, -5498374.10, 3136355.42))

    menu_controller = Menu_Controller()

    network_state = NetworkState() # create network state tracker
    audio_controller = AudioController() # create audio manager
    
    # define a network status object and callback funciton
    peers = None
    def network_callback(event):
      network_peers = event
    network_state.add_callback(network_callback) # add the callback

    call_target = '127.0.0.1' # default call target is ourselves
  
    current_button = 3

    @classmethod
    def button_up(self):
        pass

    @classmethod
    def button_down(self):
        pass

    @classmethod
    def make_call(self):
        '''JOSH PUT STUFF HERE'''
        Logger.warn("Attempting to make a call")
        audio_controller.start(call_target) # start a call

    @classmethod
    def end_call(self):
        audio_controller.stop() # hang up

    @classmethod
    def set_orientation(self, quaternion):
        self.orientation_quaternion = quaternion
        self.orientation_matrix = quaternion_matrix(quaternion)

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

