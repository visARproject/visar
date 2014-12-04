from __future__ import division

import numpy
import scipy.misc


import ram_test
rp = ram_test.RAMPoker()

import constants

def go(loc, filename):
    res = numpy.zeros((constants.CAMERA_HEIGHT, constants.CAMERA_WIDTH), dtype=numpy.uint8)

    for y in xrange(constants.CAMERA_HEIGHT):
        print filename, y/constants.CAMERA_HEIGHT
        for x in xrange(0, constants.CAMERA_WIDTH, 4):
            d = rp.read(loc + y * constants.CAMERA_STEP + x)
            for i in xrange(4):
                res[y, x+i] = d % 256
                d //= 256

    scipy.misc.imsave(filename, res)

go(constants.LEFT_CAMERA_MEMORY_LOCATION, 'left.png')
go(constants.RIGHT_CAMERA_MEMORY_LOCATION, 'right.png')
