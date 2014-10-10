from __future__ import division

from myhdl import *
import png

from dummy_generator import InternalVideo, dummy_generator

def image_saver(sig):
    res = []
    running = Signal(bool(0))
    
    @always(sig.pixel_clock.posedge)
    def _():
        if sig.Vsync == 1:
            running.next = 1
            running_now = 1
            if res:
                res2 = [res[sig.WIDTH*3*row:sig.WIDTH*3*(row+1)] for row in xrange(sig.HEIGHT)]
                png.from_array(res2, mode='RGB', info=dict(
                    width=sig.WIDTH, height=sig.HEIGHT, bitdepth=8,
                )).save('out.png')
                print 'saved out.png'
                res[:] = []
        elif running == 1:
            running_now = 1
        else:
            running_now = 0
        
        if running_now:
            res.extend(map(int, [sig.R.val, sig.G.val, sig.B.val]))
    return _

if __name__ == '__main__':
    def test():
        sig = InternalVideo()
        
        clk150MHz = Signal(bool(0))
        @always(delay(10))
        def clkgen():
            clk150MHz.next = not clk150MHz
        
        dummy_inst = dummy_generator(sig, clk150MHz)
        
        saver_inst = image_saver(sig)
        
        return clkgen, dummy_inst, saver_inst
    
    #tb = traceSignals(test)
    sim = Simulation(test())
    sim.run(100000000)
