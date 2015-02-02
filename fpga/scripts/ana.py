import struct
import sys

with open(sys.argv[1], 'rb') as f:
    d = f.read()
    d = list(struct.unpack('>%iI' % (len(d)//4,), d))

sync = []
data = [[], [], [], []]

for x in d[:2000]:
    b = '{0:025b}'.format(x)
    sync.extend(b[::5])
    for i in xrange(4):
        data[i].extend(b[1+i::5])

sync = map(int, sync)
for i in xrange(4):
    data[i] = map(int, data[i])

for i in xrange(100):
    print sync[10*i:10*(i+1)]
