from __future__ import division

import numpy
import scipy.misc
import struct
import sys

with open(sys.argv[1], 'rb') as f:
    d = f.read()
    d = list(struct.unpack('>%iI' % (len(d)//4,), d))

HEIGHT = 1024
WIDTH = 1280

res = numpy.full((HEIGHT, WIDTH), numpy.nan)
for y in xrange(HEIGHT):
    for x in xrange(WIDTH):
        b, p = divmod(x, 3)
        word = d[2048//4*y + b]
        v = (word >> (10*p)) & (2**10-1)
        res[y, x] = v
print res
res /= numpy.max(res)
assert not numpy.isnan(res).any()
scipy.misc.imsave(sys.argv[2], (res*255+.5).astype(numpy.uint8))
