import numpy as np
import os, sys
'''
    distortion_data = np.zeros(_len,
        dtype=[
            ('screen_pos', np.float32, 2),
            ('red_xy', np.float32, 2),
            ('green_xy', np.float32, 2),
            ('blue_xy', np.float32, 2),
        ]
'''

fpath = os.path.dirname(os.path.realpath(__file__))
def read():
    '''read() -> i_buffers, v_buffers
    This function reads and returns the actual distortion mesh used by the oculus rift
    '''
    f = open(os.path.join(fpath, 'mesh.dat'), 'r')
    states = ['left_vertices', 'right_vertices', 'left_indices', 'right_indices']

    vertex_ct = 4225
    left_buffer = np.zeros(
        vertex_ct, 
        dtype=[
            ('pos', np.float32, 2),
            ('red_xy', np.float32, 2),
            ('green_xy', np.float32, 2),
            ('blue_xy', np.float32, 2),
            ('vignette', np.float32, 1),
        ]
    )
    right_buffer = np.zeros(
        vertex_ct, 
        dtype=[
            ('pos', np.float32, 2),
            ('red_xy', np.float32, 2),
            ('green_xy', np.float32, 2),
            ('blue_xy', np.float32, 2),
            ('vignette', np.float32, 1),
        ]
    )

    type_map = {
        'V': 'pos',
        'R': 'red_xy',
        'G': 'green_xy',
        'B': 'blue_xy',
        'w': 'vignette',
    }

    i_buffers = {
        'left_indices': [], 
        'right_indices': [],
    }

    line_ct = 0
    for dirty_line in f:
        line = dirty_line.strip()
        if line in states:
            line_ct = 0
            state = line
        elif 'indices' in state:
            i_buffers[state].append(int(line))
        else:
            elements = line.split(';')
            for element in elements:
                _type, values = element.split(':')
                if 'left' in state:
                    left_buffer[type_map[_type]][line_ct] = np.array(values.split(','), dtype=np.float32)
                elif 'right' in state:
                    right_buffer[type_map[_type]][line_ct] = np.array(values.split(','), dtype=np.float32)

            # print line_ct, ':', left_buffer[type_map[_type]][line_ct]
            line_ct += 1

    return i_buffers, {'left_buffer': left_buffer, 'right_buffer': right_buffer}
    
if __name__ == '__main__':
    read()
