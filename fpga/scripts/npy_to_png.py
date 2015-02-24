from __future__ import division

import sys

import numpy
import scipy.misc


x = numpy.load(sys.argv[1])
x = x[0::2,0::2] + x[1::2,0::2] + x[0::2,1::2] + x[1::2,1::2]
x /= numpy.max(x)
assert not numpy.isnan(x).any()
scipy.misc.imsave(sys.argv[2], (x*255+.5).astype(numpy.uint8))
