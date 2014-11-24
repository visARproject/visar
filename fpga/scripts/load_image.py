import struct
import sys

from scipy import misc

import ram_test


img = misc.imread(sys.argv[1])
rp = ram_test.RAMPoker()

for y in xrange(1080):
    print y
    for x in xrange(1920):
        a = img[y, x]
        data = struct.pack('BBBB', a[0], a[1], a[2], 0)
        rp.write(((1919-x) * 2048 + y) * 4, struct.unpack('<I', data)[0])
