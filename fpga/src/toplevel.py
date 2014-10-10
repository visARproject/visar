from myhdl import *

def toplevel(CLK_I, LED_O):
    counter = Signal(intbv(min=0, max=2**64))
    
    @always(CLK_I.posedge)
    def logic():
        counter.next = counter + 1
        LED_O.next = counter[32:24]
    
    return logic


def convert():
    CLK_I = Signal(bool())
    LED_O = Signal(intbv()[8:])
    toVHDL(toplevel, CLK_I, LED_O)

convert()
