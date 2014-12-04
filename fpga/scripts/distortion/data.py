from __future__ import division

import sys

import numpy
import cv2
import image_geometry
mkmat = image_geometry.cameramodels.mkmat
import scipy.misc

import constants

try:
    with open('dump', 'rb') as f:
        d = numpy.load(f)
except:
    image_array = numpy.zeros((1080, 1920, 3), dtype=numpy.uint8)
    scipy.misc.imsave('outfile.png', image_array)
    model = image_geometry.PinholeCameraModel()
    model.__dict__.clear()
    model.K = mkmat(3, 3, [1708.696467385962, 0, 799.5, 0, 1699.698456801442, 599.5, 0, 0, 1])
    model.D = mkmat(5, 1, [0.1690694920899251, -0.5050198309345741, -0.001501064571807179, -0.002772422551331286, 0])
    model.R = mkmat(3, 3, [1, 0, 0, 0, 1, 0, 0, 0, 1])
    model.P = mkmat(3, 4, [1729.883544921875, 0, 795.8956955131871, 0, 0, 1724.427978515625, 597.9395276549985, 0, 0, 0, 1, 0])
    c2 = lambda (x, y): model.project3dToPixel((-x, -y, 1))
    c = lambda (x, y): model.rectifyPoint(model.project3dToPixel((-x, -y, 1)))
    
    d = {}
    with open(sys.argv[1], 'rb') as f:
        for line in f:
            x, y, Rx, Ry, Gx, Gy, Bx, By = map(float, line.split(','))
            x = int(x)
            y = int(y)
            #if x < 1920*3//16 or x > 1920*5//16 or y < 1080*3//8 or y > 1080*5//8:
            #    continue
            #print x, y, Gx, Gy,
            
            tRx, tRy = c2((Rx, Ry))
            tGx, tGy = c2((Gx, Gy))
            tBx, tBy = c2((Bx, By))
            
            CROP = 20
            red_bad   = tRx < -CROP or tRx >= 1600+CROP or tRy < -CROP or tRy >= 1200+CROP
            green_bad = tGx < -CROP or tGx >= 1600+CROP or tGy < -CROP or tGy >= 1200+CROP
            blue_bad  = tBx < -CROP or tBx >= 1600+CROP or tBy < -CROP or tBy >= 1200+CROP
            
            #print Gx, Gy,
            
            Rx, Ry = c((Rx, Ry))
            Gx, Gy = c((Gx, Gy))
            Bx, By = c((Bx, By))
            
            #print Gx, Gy,
            
            Rx = int(round(Rx))
            Ry = int(round(Ry))
            Gx = int(round(Gx))
            Gy = int(round(Gy))
            Bx = int(round(Bx))
            By = int(round(By))
            #print Gx, Gy
            
            if not (0 <= Rx < 1600 and 0 <= Ry < 1200): red_bad = True
            if not (0 <= Gx < 1600 and 0 <= Gy < 1200): green_bad = True
            if not (0 <= Bx < 1600 and 0 <= By < 1200): blue_bad = True
            
            if not red_bad: image_array[y, x, 0] = 255
            if not green_bad: image_array[y, x, 1] = 255
            if not blue_bad: image_array[y, x, 2] = 255
            
            d[x, y] = [(Rx, Ry), (Gx, Gy), (Bx, By)]
            if red_bad:   d[x, y][0] = -1, -1
            if green_bad: d[x, y][1] = -1, -1
            if blue_bad:  d[x, y][2] = -1, -1
    d = numpy.array([[d[x, y] for y in xrange(1080)] for x in xrange(1920)])


    with open('dump', 'wb') as f:
        numpy.save(f, d)
    scipy.misc.imsave('outfile.png', image_array)

for x in xrange(1920//2, 1920):
    for y in xrange(1080):
        d[x, y] = d[1919-x, y]
        for COLOR in xrange(3):
            if tuple(map(int, d[x, y][COLOR])) != (-1, -1):
                d[x, y][COLOR][0] = 1600 + (1600-1 - d[x, y][COLOR][0])

for x in xrange(1920):
    for y in xrange(1080):
        for COLOR in xrange(3):
            if tuple(map(int, d[x, y][COLOR])) != (-1, -1):
                d[x, y][COLOR][0] = (d[x, y][COLOR][0] + 1600) % (1600*2)

SIZE = 33 # should be a power of 2 plus 1 so that interpolation is simple
assert SIZE % 2 == 1
S = (SIZE-1)//2

if 0:
    COLOR = 2
    AXIS = 0

    s_range = 1e9, -1e9
    m_range = 1e9, -1e9
    err_range = 1e9, -1e9
    for x in xrange(1920//2):
        for y in xrange(S, 1080-S, SIZE):
            if any(tuple(d[x, y+i][COLOR]) == (-1, -1) for i in xrange(-S, S+1)):
                continue
            #Rx, Ry, Gx, Gy, Bx, By = d[x, y]
            #print d[x, y]
            s = d[x, y-S][COLOR][AXIS]
            m = d[x, y+S][COLOR][AXIS] - s
            err = [d[x, y+i][COLOR][AXIS]-round(s+m*(i+S)/(2*S)) for i in xrange(-S+1, S-1+1)]
            #print s, m, max(map(abs, err))
            err_range = min(err_range[0], *err), max(err_range[1], *err)
            s_range = min(s_range[0], s), max(s_range[1], s)
            m_range = min(m_range[0], m), max(m_range[1], m)
            #print d[x, y][1]
            #a = max(a, *map(abs, [d[x, y+j][1][i] - d[x,y][1][i] for i in xrange(2) for j in xrange(-S, S+1)]))
    print 'err_range', err_range
    print 's_range', s_range
    print 'm_range', m_range

COLOR = 1

# generate initial schedule with every event happening at latest possible time

BEFORENESS = 1000

res = [] # pairs of (time, pos)
present = set()
t = -1
for y in xrange(constants.V_MAX):
    for x in xrange(constants.H_MAX):
        t += 1
        ox = 1919-y
        oy = x
        if not (0 <= ox < 1920 and 0 <= oy < 1080): continue
        src = tuple(map(int, d[ox, oy][COLOR]))
        if src == (-1, -1): continue
        
        if src not in present:
            choice = src[0]-src[0]%32, src[1]
            for i in xrange(32):
                present.add((choice[0]+i, choice[1]))
            #print 'ack', t, choice, src
            res.append((t-BEFORENESS, choice))

# push events back to ensure minimum spacing

SPACING = 16
res2 = list(res)
last_time = 1e99
for i in reversed(xrange(len(res2))):
    t, choice = res2[i]
    t = min(t, last_time - SPACING)
    res2[i] = t, choice
    last_time = t

# print events

for i, x in enumerate(res2):
    print i, x, x[0] - res2[max(0, i-1)][0]

# simulate schedule, making sure that data is still there when we need it (having not been overwritten)

res3 = list(res2)
res3.reverse()
present = [[None]*(256*8) for i in xrange(8*8)]
t = -1
good = 0
bad = 0
for y in xrange(constants.V_MAX):
    for x in xrange(constants.H_MAX):
        t += 1
        ox = 1919-y
        oy = x
        if not (0 <= ox < 1920 and 0 <= oy < 1080): continue
        src = tuple(map(int, d[ox, oy][COLOR]))
        if src == (-1, -1): continue
        
        while res3 and t >= res3[-1][0]:
            load_pos = res3.pop()[1]
            for i in xrange(32):
                this = load_pos[0]+i, load_pos[1]
                present[this[0]%64][this[1]] = this
        
        if present[src[0]%64][src[1]] != src:
            print 'error at', src, present[src[0]%64][src[1]]
            bad += 1
        else:
            good += 1
print good, bad
if bad: assert False

# convert events to commands with repetitions to effect longer delays

res4 = [(100, (0, 0))]
t = 1+2**9-1 + sum(1+c[0] for c in res4) # time at end of last command
for cmd_t, cmd_pos in res2:
    delay_required = cmd_t - t
    assert delay_required >= 1, (t, cmd_t)
    while delay_required >= 2**9-1:
        res4.append((100, res4[-1][1]))
        t += 1 + res4[-1][0]
        delay_required = cmd_t - t
    res4.append((cmd_t-t-1, cmd_pos))
    t += 1 + res4[-1][0]
    assert t == cmd_t

for cmd_delay, cmd_pos in res4:
    assert SPACING-1 <= cmd_delay < 512, cmd_delay
    print cmd_delay, cmd_pos

# load everything into FPGA

import ram_test
rp = ram_test.RAMPoker()

print 'writing prefetcher table...'

write_pos = constants.DISTORTER_PREFETCHER_TABLE_MEMORY_LOCATION
for cmd_delay, cmd_pos in res4:
    data = '{0:09b}{1:011b}{2:012b}'.format(cmd_delay, cmd_pos[1], cmd_pos[0])
    rp.write(write_pos, int(data, 2))
    write_pos += 4

print 'done'

print 'writing map...'

import random

left = scipy.misc.imread('left.png')
right = scipy.misc.imread('right.png')
test = numpy.zeros((1080, 1920, 3), dtype=numpy.uint8)

COLOR = 1
write_pos = constants.DISTORTER_MAP_MEMORY_LOCATION
for v_cnt in xrange(1920):
    for h_cnt in xrange(0, 1089, 33):
        x = 1919 - v_cnt
        y = h_cnt
        src = tuple(map(int, d[x, y][COLOR]))
        if src == (-1, -1): src = (0, 0)
        try:
            src2 = tuple(map(int, d[x, y+32][COLOR]))
            if src2 == (-1, -1): src2 = (0, 0)
        except IndexError:
            src2 = (0, 0)
        
        
        data = '{lastbluey:011b}{lastbluex:012b}{lastgreeny:011b}{lastgreenx:012b}{lastredy:011b}{lastredx:012b}{firstbluey:011b}{firstbluex:012b}{firstgreeny:011b}{firstgreenx:012b}{firstredy:011b}{firstredx:012b}'.format(
            lastbluey=0, lastbluex=0, lastgreeny=src2[1], lastgreenx=src2[0], lastredy=0, lastredx=0,
            firstbluey=0, firstbluex=0, firstgreeny=src[1], firstgreenx=src[0], firstredy=0, firstredx=0)
        assert len(data) == 138
        data = '0'*(5*32-138) + data
        
        if src != (0, 0) and src2 != (0, 0):
            print src, src2, data
            
            for i in xrange(20):
                print 'memory(%i) <= "%s";' % (1236+i, data[len(data)-i*8-8:len(data)-i*8])
            
            for i in xrange(33):
                if h_cnt+i < 1080:
                    interp = (src[0] * 32 + (src2[0]-src[0])*i + 16)//32, (src[1] * 32 + (src2[1]-src[1])*i+16)//32
                    img = left
                    if interp[0] >= 1600:
                        interp = interp[0] - 1600, interp[1]
                        img = right
                    test[y+i, x, 0] = left[interp[1]//2*2+0, interp[0]//2*2+0]
                    test[y+i, x, 1] = left[interp[1]//2*2+0, interp[0]//2*2+1]
                    test[y+i, x, 2] = left[interp[1]//2*2+1, interp[0]//2*2+1]
        
        for i in xrange(5):
            rp.write(write_pos, int(data[len(data)-i*32-32:len(data)-i*32], 2))
            write_pos += 4

scipy.misc.imsave('test.png', test)
print 'done'
