import numpy as np
from ...OpenGL.utils import Logger

def test_print(self):
    print "lheo"


class Menu_Controller(object):
    cur_state = {
        'Top_Level': {
            'Banana': test_print,
            'Conana': test_print,
        }
    }

    def __init__(self):
        '''Menu_Controller

        The Menu Controller takes in (a menu XML) and generates a list of buttons


        Events of importance:
            1. Menu navigation directions
            2. 

        Stretch:
            1. Recieving a call

        '''
        Logger.log("Initializing menu controller")
        pass

