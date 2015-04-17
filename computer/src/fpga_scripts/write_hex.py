from __future__ import division

import sys

import ram_test
import intelhex

ih = intelhex.IntelHex(sys.argv[1])
rp = ram_test.RAMPoker()

keys = sorted(set(x//4*4 for x in ih._buf))

for i, addr in enumerate(keys):
    if i % 1000 == 0:
        print "%.1f%%" % (100*i/len(keys),)
    rp.write(addr, ih._buf[addr] | (ih._buf[addr+1]<<8) | (ih._buf[addr+2]<<16) | (ih._buf[addr+3]<<24))
