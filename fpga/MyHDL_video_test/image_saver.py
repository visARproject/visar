from __future__ import division

from myhdl import *

from dummy_generator import InternalVideo, dummy_generator

def image_saver(sig):
    pos = Signal(intbv(min=0, max=len(rle_count)))
    count = Signal(intbv(min=0, max=max(rle_count)+1))
    
    @always(sig.pixel_clock.posedge)
    def _():
        sig.Vsync.next = 0
        if count == 0:
            if pos == len(rle_count) - 1:
                sig.Vsync.next = 1
                pos.next = 0
            else:
                pos.next = pos + 1
            count.next = rle_count[pos.next]
        else:
            count.next = count - 1
        sig.R.next = rle_r[pos]
        sig.G.next = rle_g[pos]
        sig.B.next = rle_b[pos]
    return _

if __name__ == '__main__':
    def test():
        sig = InternalVideo()
        
        clk150MHz = Signal(bool(0))
        @always(delay(10))
        def clkgen():
            clk150MHz.next = not clk150MHz
        
        dummy_inst = dummy_generator(sig, clk150MHz)
        
        return clkgen, dummy_inst
    
    tb = traceSignals(test)
    sim = Simulation(tb)
    sim.run(100000000)
