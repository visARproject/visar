from __future__ import division

import numpy
import scipy.misc


import ram_test
rp = ram_test.RAMPoker()

LEFT_CAMERA_MEMORY_LOCATION = 0*1024*1024
RIGHT_CAMERA_MEMORY_LOCATION = 32*1024*1024


CAMERA_WIDTH = 1600
CAMERA_HEIGHT = 1200
CAMERA_STEP = 2048

def go(loc, filename):
    res = numpy.zeros((CAMERA_HEIGHT, CAMERA_WIDTH), dtype=numpy.uint8)

    for y in xrange(CAMERA_HEIGHT):
        print filename, y/CAMERA_HEIGHT
        for x in xrange(0, CAMERA_WIDTH, 4):
            d = rp.read(loc + y * CAMERA_STEP + x)
            for i in xrange(4):
                res[y, x+i] = d % 256
                d //= 256

    scipy.misc.imsave(filename, res)

go(LEFT_CAMERA_MEMORY_LOCATION, 'left.png')
go(RIGHT_CAMERA_MEMORY_LOCATION, 'right.png')
