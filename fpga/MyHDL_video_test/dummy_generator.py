from __future__ import division

from myhdl import *
import png

class InternalVideo(object):
    WIDTH = 1920
    HEIGHT = 1080
    
    def __init__(self):
        self.pixel_clock = Signal(bool()) # data should be read on rising edge
        self.R = Signal(intbv(min=0, max=256))
        self.G = Signal(intbv(min=0, max=256))
        self.B = Signal(intbv(min=0, max=256))
        self.Vsync = Signal(bool()) # 1 for last pixel of frame

print 'RLE encoding image. Takes a few seconds...'
width, height, pixels, metadata = png.Reader(filename='standby.png').asRGBA8()
pixels = list(pixels)
assert width == InternalVideo.WIDTH
assert height == InternalVideo.HEIGHT
rle_count = []
rle_r = []
rle_g = []
rle_b = []
for row in xrange(InternalVideo.HEIGHT):
    for col in xrange(InternalVideo.WIDTH):
        c = map(int, pixels[row][col*4:col*4+3])
        if not rle_count or [rle_r[-1], rle_g[-1], rle_b[-1]] != c:
            rle_count.append(0)
            rle_r.append(c[0])
            rle_g.append(c[1])
            rle_b.append(c[2])
        else:
            rle_count[-1] += 1

rle_count = tuple(rle_count)
rle_r = tuple(rle_r)
rle_g = tuple(rle_g)
rle_b = tuple(rle_b)
print '...done.', len(rle_count), 'entries'

def dummy_generator(sig, clk150MHz):
    pos = Signal(intbv(len(rle_count) - 1, min=0, max=len(rle_count)))
    count = Signal(intbv(0, min=0, max=max(rle_count)+1))
    
    @always_comb
    def i1():
        sig.pixel_clock.next = clk150MHz
    
    @always(clk150MHz.posedge)
    def i2():
        sig.Vsync.next = 0
        if count == 0:
            if pos == len(rle_count) - 1:
                sig.Vsync.next = 1
                pos.next = 0
                count.next = rle_count[0]
            else:
                pos.next = pos + 1
                count.next = rle_count[pos + 1]
        else:
            count.next = count - 1
        sig.R.next = rle_r[pos]
        sig.G.next = rle_g[pos]
        sig.B.next = rle_b[pos]
    
    return i1, i2

if __name__ == '__main__':
    def convert():
        sig, clk150MHz = InternalVideo(), Signal(bool())
        toVHDL(dummy_generator, sig, clk150MHz)
    convert()
