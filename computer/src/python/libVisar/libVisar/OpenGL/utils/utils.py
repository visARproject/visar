import numpy as np

def find(key, _list, value):
    return filter(lambda o: key(o) == value)
    

def checkerboard(grid_num=8, grid_size=32):
    ''' Make an example-style checkerboard for visualizing uniform meshes and shaders
    Returns a numpy array that can behave as a texture
    '''
    row_even = grid_num // 2 * [0, 1]
    row_odd = grid_num // 2 * [1, 0]
    Z = np.row_stack(grid_num // 2 * (row_even, row_odd)).astype(np.uint8)
    return 255 * Z.repeat(grid_size, axis=0).repeat(grid_size, axis=1)
