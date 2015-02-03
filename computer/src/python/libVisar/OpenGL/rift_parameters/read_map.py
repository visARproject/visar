
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
    np.save(os.path.join(fpath, 'distortion.npy'), distortion_data)

    return my_data

def read_map():
    try:
        # Check if we have a cached version of the distortion array (if so, return it)
        return np.load(os.path.join(fpath, './distortion.npy'))

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
    # from mpl_toolkits.mplot3d import Axes3D
    # import matplotlib.pyplot as plt
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')

    # x1 = use[:, 0][::500]
    # y1 = use[:, 1][::500]
    # z1 = use[:, 3][::500]
    # z2 = use[:, 4][::500]

    # ax.scatter(x1, y1, z1, c='r', marker='.')
    # ax.scatter(x1, y1, z2, c='b', marker='.')

    # ax.set_xlabel('Oculus Screen X')
    # ax.set_ylabel('Oculus Screen Y')
    # ax.set_zlabel('Red - X/Y position')

    # plt.show()

