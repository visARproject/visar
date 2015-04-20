import numpy as np
from ...OpenGL.utils import Logger


class Menu_Controller(object):
    '''Structure: 
        Menu Section: {
            button title: button_action

    Change to OrderedDict if order is important
    '''

    menu_hierarchy = {
        'Main Menu': {
            'Example': 'example',
            'Toggle Map': 'toggle map',
            'Voice': {
                'Start Voice': 'start voice',
                'End Voice': 'stop voice',
                'Make Call': 'make call',
                'End Call': 'end call',
                'List Peers': 'list peers',
                'Update Status': 'update status',
            },
            'Map': {
                'Toggle Map': 'toggle map',
                'Set Target': 'set target',
            }
        }
    }
