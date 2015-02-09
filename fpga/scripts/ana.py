from __future__ import division

import numpy
import struct
import sys

with open(sys.argv[1], 'rb') as f:
    d = f.read()
    d = list(struct.unpack('>%iI' % (len(d)//4,), d))

sync = []
data = [[], [], [], []]
times = []

for i, x in enumerate(d):
    if i % 10000 == 0: print i/len(d)
    #print i, x>>25, ((x>>25)-i)%128
    b = '{0:032b}'.format(x)[7:]
    sync.extend(b[::5][::-1])
    times.extend([(i, x>>25)]*5)
    #times.extend(xrange((x>>25)*5, ((x>>25)+1)*5))
    for i in xrange(4):
        data[i].extend(b[1+i::5][::-1]) # XXX

assert len(times) == len(sync)

sync = [1-x for x in map(int, sync)]
for i in xrange(4):
    data[i] = map(int, data[i])
data[2] = [1-x for x in map(int, data[2])]
data[3] = [1-x for x in map(int, data[3])]

#for i in xrange(100):
#    a = sync[10*i:10*(i+1)]
#    print a#, hex(int(''.join(map(str, a)), 2))

train = map(int, '{0:010b}'.format(0x3a6))
black = map(int, '{0:010b}'.format(0x015))
valid = map(int, '{0:010b}'.format(0x035))
crc   = map(int, '{0:010b}'.format(0x059))

def to_int(x):
    res = 0
    for y in x:
        res *= 2
        res += y
    return res



def handle_valid_data(p):
    global x
    if frame is not None:
        a, b = divmod(x, 4)
        if b == 0:
            frame[y, 16*a+0] = to_int(data[0][p:p+10])
            frame[y, 16*a+2] = to_int(data[1][p:p+10])
            frame[y, 16*a+4] = to_int(data[2][p:p+10])
            frame[y, 16*a+6] = to_int(data[3][p:p+10])
        elif b == 1:
            frame[y, 16*a+1] = to_int(data[0][p:p+10])
            frame[y, 16*a+3] = to_int(data[1][p:p+10])
            frame[y, 16*a+5] = to_int(data[2][p:p+10])
            frame[y, 16*a+7] = to_int(data[3][p:p+10])
        elif b == 2:
            frame[y, 16*a+7+8] = to_int(data[0][p:p+10])
            frame[y, 16*a+5+8] = to_int(data[1][p:p+10])
            frame[y, 16*a+3+8] = to_int(data[2][p:p+10])
            frame[y, 16*a+1+8] = to_int(data[3][p:p+10])
        elif b == 3:
            frame[y, 16*a+6+8] = to_int(data[0][p:p+10])
            frame[y, 16*a+4+8] = to_int(data[1][p:p+10])
            frame[y, 16*a+2+8] = to_int(data[2][p:p+10])
            frame[y, 16*a+0+8] = to_int(data[3][p:p+10])
        x += 1
        print 'handle_valid_data', y, x

p = 0
badcount = 0
frame = None
imgcount = 0
while sync[p:p+10]:
    if sync[p:p+10] == train:
        print 'train good'#, times[p:p+10]
        for i in xrange(4):
            print data[i][p:p+10], data[i][p:p+10] == train
            assert data[i][p:p+10] == train
        p += 10
    elif sync[p:p+10][3:] == [0, 1, 0, 1, 0, 1, 0] and sync[p:p+10][:3] == [1, 0, 1]:
        print 'frame sync - frame start'
        frame = numpy.full((1024, 1280), numpy.nan)
        y = 0
        x = 0
        handle_valid_data(p)
        p += 10
        print sync[p:p+10]#, times[p:p+10]
        handle_valid_data(p)
        p += 10
    elif sync[p:p+10][3:] == [0, 1, 0, 1, 0, 1, 0] and sync[p:p+10][:3] == [1, 1, 0]:
        print 'frame sync - frame end'
        handle_valid_data(p)
        p += 10
        print sync[p:p+10]#, times[p:p+10]
        handle_valid_data(p)
        if frame is not None:
            del x
            numpy.save('out%i.npy' % (imgcount,), frame)
            imgcount += 1
            frame = None
        p += 10
    elif sync[p:p+10][3:] == [0, 1, 0, 1, 0, 1, 0] and sync[p:p+10][:3] == [0, 0, 1]:
        print 'frame sync - line start'
        if frame is not None:
            x = 0
        handle_valid_data(p)
        p += 10
        print sync[p:p+10]#, times[p:p+10]
        handle_valid_data(p)
        p += 10
    elif sync[p:p+10][3:] == [0, 1, 0, 1, 0, 1, 0] and sync[p:p+10][:3] == [0, 1, 0]:
        print 'frame sync - line end'
        handle_valid_data(p)
        p += 10
        print sync[p:p+10]#, times[p:p+10]
        handle_valid_data(p)
        if frame is not None:
            y += 1
            del x
        p += 10
    elif sync[p:p+10] == black:
        print 'black'#, times[p:p+10]
        p += 10
    elif sync[p:p+10] == valid:
        print 'valid', p#, times[p:p+10]
        handle_valid_data(p)
        p += 10
    elif sync[p:p+10] == crc:
        print 'crc'#, times[p:p+10]
        p += 10
    else:
        badcount += 1
        print 'bad', sync[p:p+10], badcount#, times[p:p+10]
        p += 1
        continue
    badcount = 0

#for i in xrange(0, len(d), 2):
#    print '{0:025b} {1:025b}'.format(d[i], d[i+1])
