from __future__ import division

import sys

import numpy
import scipy.misc

import constants


with open(sys.argv[1], 'rb') as f:
    d_orig = numpy.load(f)

NONE, LEFT, RIGHT = xrange(3)

d = numpy.zeros((constants.V_DISPLAY_END, constants.H_DISPLAY_END, 3, 3), dtype=numpy.int32)
d[:,:,:,:2] = d_orig
d[:,:,:,2] = numpy.where(numpy.logical_and(d_orig[:,:,:,0] == -1, d_orig[:,:,:,1] == -1), NONE, LEFT)

# generate right side of map from flipped left side
for x in xrange(1920//2, 1920):
    for y in xrange(1080):
        d[x, y] = d[1919-x, y]
        for COLOR in xrange(3):
            d[x, y][COLOR][1] = constants.CAMERA_ROWS-1 - d[x, y][COLOR][1]
            d[x, y][COLOR][2] = {NONE: NONE, LEFT: RIGHT}[d[x, y][COLOR][2]]

d[1910:,:] = [[0, 0, NONE]]*3

'''
# swap cameras
for x in xrange(1920):
    for y in xrange(1080):
        for COLOR in xrange(3):
            if tuple(map(int, d[x, y][COLOR])) != (-1, -1):
                d[x, y][COLOR][1] = (d[x, y][COLOR][1] + constants.CAMERA_ROWS) % (constants.CAMERA_ROWS*2)
'''

CENTER_BLANK = 8
assert CENTER_BLANK % 2 == 0
# clear centermost CENTER_BLANK lines to allow opposite eye time to buffer
for x in xrange(1920//2-CENTER_BLANK//2, 1920//2+CENTER_BLANK//2):
    for y in xrange(1080):
        for COLOR in xrange(3):
            d[x, y][COLOR][2] = NONE

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

# change coordinates to what interpolation would yield
d2 = numpy.zeros((constants.V_DISPLAY_END, constants.H_DISPLAY_END, 3, 3), dtype=numpy.int32)
for y in xrange(constants.V_MAX):
    for x in xrange(0, constants.H_MAX, SIZE):
        ox = 1919-y
        oy = x
        if not (0 <= ox < 1920 and 0 <= oy < 1080): continue
        
        src = tuple(map(int, d[ox, oy][COLOR]))
        
        try:
            src2 = tuple(map(int, d[ox, oy+SIZE-1][COLOR]))
        except IndexError:
            src2 = (0, 0, 0)
        
        if src[2] == NONE or src2[2] == NONE:
            for i in xrange(SIZE):
                if oy+i == constants.H_DISPLAY_END: break
                d2[ox, oy+i] = 0, 0, 0
            continue
        
        assert src[2] == src2[2]
        for i in xrange(SIZE):
            interp = (src[0] * (SIZE-1) + (src2[0]-src[0])*i + S)//(SIZE-1), (src[1] * (SIZE-1) + (src2[1]-src[1])*i+S)//(SIZE-1)
            d2[ox, oy+i] = interp[0], interp[1], src[2]

# generate initial schedule with every event happening at latest possible time

READ_LENGTH = 3*16
BEFORENESS = 1000
X_REQUIRED_RANGE = -1, 2 # half open
Y_REQUIRED_RANGE = -1, 2 # half open

res = [] # pairs of (time, pos)
present = set()
t = -1
for y in xrange(constants.V_MAX):
    for x in xrange(constants.H_MAX):
        t += 1
        ox = 1919-y
        oy = x
        if not (0 <= ox < 1920 and 0 <= oy < 1080): continue
        
        src = tuple(map(int, d2[ox, oy][COLOR]))
        if src[2] == NONE: continue
        
        for dx in xrange(*X_REQUIRED_RANGE):
            for dy in xrange(*Y_REQUIRED_RANGE):
                src2 = src[0] + dx, src[1] + dy, src[2]
                if src2[0] < 0 or src2[0] >= constants.CAMERA_COLUMNS: continue
                if src2[1] < 0 or src2[1] >= constants.CAMERA_ROWS: continue
                
                if src2 not in present:
                    choice = src2[0]-src2[0]%READ_LENGTH, src2[1], src2[2]
                    for i in xrange(READ_LENGTH):
                        present.add((choice[0]+i, choice[1], choice[2]))
                    #print 'ack', t, choice, src
                    res.append((t-BEFORENESS, choice))

# push events back to ensure minimum spacing

assert READ_LENGTH % 3 == 0
SPACING = 23
res2 = list(res)
last_time = 1e99
for i in reversed(xrange(len(res2))):
    t, choice = res2[i]
    t = min(t, last_time - SPACING)
    res2[i] = t, choice
    last_time = t

# print events
print 'events:'

for i, x in enumerate(res2):
    print i, x, x[0] - res2[max(0, i-1)][0]

# simulate schedule, making sure that data is still there when we need it (having not been overwritten)

BUFFER_THICKNESS = 64

res3 = list(res2)
res3.reverse()
present = [[None]*BUFFER_THICKNESS for i in xrange(256*8)]
t = -1
good = 0
bad = 0
for y in xrange(constants.V_MAX):
    for x in xrange(constants.H_MAX):
        t += 1
        ox = 1919-y
        oy = x
        if not (0 <= ox < 1920 and 0 <= oy < 1080): continue
        
        src = tuple(map(int, d2[ox, oy][COLOR]))
        if src[2] == NONE: continue
        
        while res3 and t >= res3[-1][0]:
            load_pos = res3.pop()[1]
            for i in xrange(READ_LENGTH):
                this = load_pos[0]+i, load_pos[1], load_pos[2]
                present[this[0]][this[1]%BUFFER_THICKNESS] = this
        
        for dx in xrange(*X_REQUIRED_RANGE):
            for dy in xrange(*Y_REQUIRED_RANGE):
                src2 = src[0] + dx, src[1] + dy, src[2]
                if src2[0] < 0 or src2[0] >= constants.CAMERA_COLUMNS: continue
                if src2[1] < 0 or src2[1] >= constants.CAMERA_ROWS: continue
                if present[src2[0]][src2[1]%BUFFER_THICKNESS] != src2:
                    print 'error at', (ox, oy), src2, present[src2[0]][src2[1]%BUFFER_THICKNESS]
                    bad += 1
                else:
                    good += 1
print good, bad
if bad: assert False

# convert events to commands with repetitions to effect longer delays

res4 = [(100, (0, 0, RIGHT))]
t = -5000 + 1+2**9-1 + sum(1+c[0] for c in res4) # time at end of last command
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

import intelhex

class HEXWriter(object):
    def __init__(self):
        self._d = {}
    def write(self, addr, value):
        for i in xrange(4):
            self._d[addr+i] = (value>>(8*i))&0xFF
    def save(self, filename):
        intelhex.IntelHex(self._d).write_hex_file(filename)
rp = HEXWriter()

print 'writing prefetcher table...'

def safediv(a, b):
    q, r = divmod(a, b)
    assert r == 0, (a, b, q, r)
    return q

write_pos = constants.DISTORTER_PREFETCHER_TABLE_MEMORY_LOCATION
for cmd_delay, cmd_pos in res4:
    print cmd_pos
    data = '{0:10b}{1:011b}{2:011b}'.format(cmd_delay, cmd_pos[1] + {LEFT: 0, RIGHT: constants.CAMERA_ROWS}[cmd_pos[2]], safediv(cmd_pos[0], 3))
    rp.write(write_pos, int(data, 2))
    write_pos += 4

print 'done'

print 'writing map...'

left = scipy.misc.imread('left.png')
right = scipy.misc.imread('right.png')
test = numpy.zeros((1080, 1920, 3), dtype=numpy.uint8)

COLOR = 1
write_pos = constants.DISTORTER_MAP_MEMORY_LOCATION
for v_cnt in xrange(1920):
    for h_cnt in xrange(0, 1089, SIZE):
        x = 1919 - v_cnt
        y = h_cnt
        
        src = tuple(map(int, d[x, y][COLOR]))
        
        try:
            src2 = tuple(map(int, d[x, y+(SIZE-1)][COLOR]))
        except IndexError:
            src2 = 0, 0, 0
        
        if src[2] == NONE or src2[2] == NONE:
            csrc = csrc2 = 0, 0, 0
        else:
            assert src[2] == src2[2]
            
            print 'aa', src[2], src2[2]
            
            csrc  = src [0], src [1] + {LEFT: 0, RIGHT: constants.CAMERA_ROWS}[src [2]]
            csrc2 = src2[0], src2[1] + {LEFT: 0, RIGHT: constants.CAMERA_ROWS}[src2[2]]
        
        data = '{lastbluey:011b}{lastbluex:012b}{lastgreeny:011b}{lastgreenx:012b}{lastredy:011b}{lastredx:012b}{firstbluey:011b}{firstbluex:012b}{firstgreeny:011b}{firstgreenx:012b}{firstredy:011b}{firstredx:012b}'.format(
            lastbluey=0, lastbluex=0, lastgreeny=csrc2[1], lastgreenx=csrc2[0], lastredy=0, lastredx=0,
            firstbluey=0, firstbluex=0, firstgreeny=csrc[1], firstgreenx=csrc[0], firstredy=0, firstredx=0)
        assert len(data) == 138
        data = '0'*(5*32-138) + data
        
        if src[2] != NONE and src2[2] != NONE:
            assert src[2] == src2[2]
            #print src, src2, data
            
            for i in xrange(SIZE):
                if h_cnt+i < 1080:
                    interp = (src[0] * (SIZE-1) + (src2[0]-src[0])*i + 16)//(SIZE-1), (src[1] * (SIZE-1) + (src2[1]-src[1])*i+16)//(SIZE-1)
                    img = {LEFT: left, RIGHT: right}[src[2]]
                    test[y+i, x, 0] = img[interp[1]//2*2+0, interp[0]//2*2+0]
                    test[y+i, x, 1] = img[interp[1]//2*2+0, interp[0]//2*2+1]
                    test[y+i, x, 2] = img[interp[1]//2*2+1, interp[0]//2*2+1]
        
        for i in xrange(5):
            rp.write(write_pos, int(data[len(data)-i*32-32:len(data)-i*32], 2))
            write_pos += 4

scipy.misc.imsave('test.png', test)

rp.save(sys.argv[2])
print 'done'
