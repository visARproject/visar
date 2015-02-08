
'''
This file reads the 'data.csv' file from fpga/scripts/data.csv.bz2 -- it contains a mapping specified below

(In order of column, starting at 0, ending at 7)
RIFT SCREENSPACE:
    x pixel on rift, -- ranging - [0.0: 959.0]
    y pixel on rift, -- ranging - [0.0: 1079.0]

COORDINATES IN TANGENT SPACE:
    red x, -- ranging : [-1.54495: 1.58715]
    red y, -- ranging : [-1.77176: 1.76645]
    green x, -- ranging : [-1.625: 1.67033]
    green y, -- ranging : [-1.86462: 1.85889]
    blue x, -- ranging : [-1.72129: 1.77021]
    blue y, -- ranging : [-1.97612: 1.96991]

    x pixel on rift [0.0: 959.0]
    y pixel on rift [0.0: 1079.0]
    red x [-1.54495: 1.58715]
    red y [-1.77176: 1.76645]
    green x [-1.625: 1.67033]
    green y [-1.86462: 1.85889]
    blue x [-1.72129: 1.77021]
    blue y [-1.97612: 1.96991]


    Only care about points | x < 960


-->tangent space is an xyz vector divided by z, leaving (x, y, 1)
|
|
|
|
|
|o - - - - - (0, 0)
|
|
|
|

To use this information, create a geometry that implements the mapping
'''
import os
from time import time
import numpy as np
from .read_mesh_txt import read
from ..utils import utils

fpath = os.path.dirname(os.path.realpath(__file__))
def read_csv():
    tic = time()
    my_data = np.genfromtxt(os.path.join(fpath, './data.csv'), delimiter=',')
    toc = time() - tic
    print "Extracted distortion geometry, took:", toc, ' seconds'
    # np.save(os.path.join(fpath, 'distortion.npy'), my_data)

    use = my_data[my_data[:, 0] < 960]
    _len = max(use.shape)

    distortion_data = np.zeros(_len,
        dtype=[
            ('screen_pos', np.float32, 2),
            ('red_xy', np.float32, 2),
            ('green_xy', np.float32, 2),
            ('blue_xy', np.float32, 2),
        ]
    )
    distortion_data['screen_pos'] = use[:, 0:2]
    distortion_data['red_xy'] = use[:, 2: 4]
    distortion_data['green_xy'] = use[:, 4: 6]
    distortion_data['blue_xy'] = use[:, 6: 8]
    np.save(os.path.join(fpath, 'mapping.npy'), distortion_data)

    return my_data

def read_map():
    try:
        # Check if we have a cached version of the distortion array (if so, return it)
        return np.load(os.path.join(fpath, './mapping.npy'))

    except:
        # If we don't have a cached distortion array, generate one
        print "Could not find cached version"
        return read_csv()

if __name__ == '__main__':
    k = read_map()
    print k.shape
    columns = [
        'x pixel on rift',
        'y pixel on rift',
        'red x',
        'red y',
        'green x',
        'green y',
        'blue x',
        'blue y',
    ]
    '''
        V:-0.899429, 0.880615;R:-1.02421, -1.28603;G:-1.05865, -1.32927;B:-1.10181, -1.38347;w:0.19237
        V:-0.889412, 0.886396;R:-0.992099, -1.28656;G:-1.02521, -1.32949;B:-1.06678, -1.3834;w:0.192916
        V:-0.879161, 0.892011;R:-0.95964, -1.28665;G:-0.991429, -1.32927;B:-1.0314, -1.38286;w:0.196967
        V:-0.868751, 0.897626;R:-0.927246, -1.28684;G:-0.957737, -1.32916;B:-0.996129, -1.38244;w:0.200127
        V:-0.858245, 0.903407;R:-0.895259, -1.28763;G:-0.924494, -1.32968;B:-0.961357, -1.3827;w:0.198168
        V:-0.84745, 0.908857;R:-0.862676, -1.2876;G:-0.890644, -1.32934;B:-0.925961, -1.38205;w:0.203061
        V:-0.836501, 0.914307;R:-0.830206, -1.28773;G:-0.856932, -1.32918;B:-0.890729, -1.3816;w:0.206417
        V:-0.825396, 0.919757;R:-0.797848, -1.28805;G:-0.823359, -1.32924;B:-0.855662, -1.38139;w:0.208051
        V:-0.814109, 0.925125;R:-0.765464, -1.28836;G:-0.789776, -1.32928;B:-0.820604, -1.38117;w:0.20971
    '''

    vertices = [
        np.array([-0.899429, 0.880615], np.float32),
        np.array([-0.889412, 0.886396], np.float32),
        np.array([-0.879161, 0.892011], np.float32),
        np.array([-0.868751, 0.897626], np.float32),
        np.array([-0.858245, 0.903407], np.float32),
        np.array([-0.847450, 0.908857], np.float32),
        np.array([-0.836501, 0.914307], np.float32),
        np.array([-0.825396, 0.919757], np.float32),
        np.array([-0.814109, 0.925125], np.float32),
    ]

    for vertex in vertices:
        normalized_pos = (vertex + 1) / 2
        screen_pos = map(int, normalized_pos * np.array([1920, 1080]))
        print screen_pos
