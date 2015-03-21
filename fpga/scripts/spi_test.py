# coding=utf-8

from __future__ import division

import struct
import time

import ram_test

class SPIer(object):
    def __init__(self):
        self._r = ram_test.RAMPoker()
        self._drive = 0b1110101000011
        self._drive |= 1<<31
        self._pins = 0b0110100000011
        self._r.write(0xFFFFFFF4, self._pins)
        self.set_pin(12) # arbiter request
        #assert self.read_pin(13) == 1
        self._r.write(0xFFFFFFF8, self._drive)
    def _read_pins(self):
        self._r.write(0xFFFFFFFC, 0)
        return self._r.read(0xFFFFFFFC)
    def set_pin(self, n):
        assert ((self._drive >> n) & 1)
        self._pins = self._pins | (1<<n)
        self._r.write(0xFFFFFFF4, self._pins)
    def clear_pin(self, n):
        assert ((self._drive >> n) & 1)
        self._pins = ~(~self._pins | (1<<n))
        self._r.write(0xFFFFFFF4, self._pins)
    def read_pin(self, n):
        assert not ((self._drive >> n) & 1)
        return (self._read_pins() >> n) & 1
    def set_SCLK(self, x):
        assert x in [0, 1]
        if x == 0:
            self.clear_pin(31)
        else:
            self.set_pin(31)
    def do_spi(self, nCS_pin, MISO_pin, bits, read=True):
        MOSI_pin = 11
        
        self.set_SCLK(1)
        self.clear_pin(nCS_pin)
        res = []
        for b in bits:
            self.set_SCLK(0)
            if b:
                self.set_pin(MOSI_pin)
            else:
                self.clear_pin(MOSI_pin)
            if read:
                res.append(self.read_pin(MISO_pin))
            self.set_SCLK(1)
        self.set_pin(nCS_pin)
        
        if read:
            return res
    def do_camera_spi(self, nCS_pin, MISO_pin, bits, read=True):
        MOSI_pin = 11
        
        self.set_SCLK(0)
        self.clear_pin(nCS_pin)
        res = []
        for b in bits:
            if b:
                self.set_pin(MOSI_pin)
            else:
                self.clear_pin(MOSI_pin)
            self.set_SCLK(1)
            if read:
                res.append(self.read_pin(MISO_pin))
            self.set_SCLK(0)
        self.set_pin(nCS_pin)
        
        if read:
            return res
    def close(self):
        self.clear_pin(12) # arbiter request
        self._r.write(0xFFFFFFF8, 0) # drive

def read_cpld():
    x = s.do_spi(10, 9, [0]*20)
    assert x[:10] == [1, 0, 1, 0, 0, 1, 1, 0, 0, 1]
    return x[10:]
def write_cpld(x):
    assert len(x) == 10
    y = s.do_spi(10, 9, [1, 0, 1, 0, 0, 1, 1, 0, 0, 1] + x)
    assert y[:10] == [1, 0, 1, 0, 0, 1, 1, 0, 0, 1]
    assert read_cpld() == x, (read_cpld(), x)

s = SPIer()

cpld_state = read_cpld()
write_cpld(cpld_state)


def int_to_list(x, n):
    res = []
    for i in xrange(n):
        res.append(x & 1)
        x >>= 1
    assert not x
    res.reverse()
    return res
assert int_to_list(5, 8) == [0, 0, 0, 0, 0, 1, 0, 1]

def list_to_int(x):
    res = 0
    for y in x:
        res = 2 * res + (1 if y else 0)
    return res
assert list_to_int([0, 0, 0, 0, 0, 1, 0, 1]) == 5

class Camera(object):
    def __init__(self, name, nCS_pin, MISO_pin, base_addr, power_start):
        self.nCS_pin, self.MISO_pin = nCS_pin, MISO_pin
        
        print 'starting', name
        
        cpld_state[power_start:power_start+4] = [0]*4
        write_cpld(cpld_state)
        time.sleep(.1)
        
        for i in xrange(4):
            cpld_state[power_start+i] = 1
            write_cpld(cpld_state)
            time.sleep(.1)
        
        assert self.camera_read(0) == int_to_list(0x560D, 16)
        
        # V1-SN/SE 10-bit mode without PLL

        # ENABLE CLOCK MANAGEMENT REGISTER UPLOAD − PART 1
        self.camera_write( 2, 0x0001)
        self.camera_write(32, 0x2000)
        self.camera_write(20, 0x0001)
        # ENABLE CLOCK MANAGEMENT REGISTER UPLOAD − PART 2
        self.camera_write( 9, 0x0000)
        self.camera_write(32, 0x2002)
        self.camera_write(34, 0x0001)
        # REQUIRED REGISTER UPLOAD
        self.camera_write( 41, 0x085A)
        self.camera_write(129, list_to_int(self.camera_read(129)) & 0b1101111111111111)
        self.camera_write( 65, 0x288B)
        self.camera_write( 66, 0x53C5)
        self.camera_write( 67, 0x0344)
        self.camera_write( 68, 0x0085)
        self.camera_write( 70, 0x4800)
        self.camera_write(128, 0x4710)
        self.camera_write(197, 0x0103)
        self.camera_write(176, 0x00F5)
        self.camera_write(180, 0x00FD)
        self.camera_write(181, 0x0144)
        self.camera_write(387, 0x549F)
        self.camera_write(388, 0x549F)
        self.camera_write(389, 0x5091)
        self.camera_write(390, 0x1011)
        self.camera_write(391, 0x111F)
        self.camera_write(392, 0x1110)
        self.camera_write(431, 0x0356)
        self.camera_write(432, 0x0141)
        self.camera_write(433, 0x214F)
        self.camera_write(434, 0x214A)
        self.camera_write(435, 0x2101)
        self.camera_write(436, 0x0101)
        self.camera_write(437, 0x0B85)
        self.camera_write(438, 0x0381)
        self.camera_write(439, 0x0181)
        self.camera_write(440, 0x218F)
        self.camera_write(441, 0x218A)
        self.camera_write(442, 0x2101)

        self.camera_write(443, 0x0100)
        self.camera_write(447, 0x0B55)
        self.camera_write(448, 0x0351)
        self.camera_write(449, 0x0141)
        self.camera_write(450, 0x214F)
        self.camera_write(451, 0x214A)
        self.camera_write(452, 0x2101)
        self.camera_write(453, 0x0101)
        self.camera_write(454, 0x0B85)
        self.camera_write(455, 0x0381)
        self.camera_write(456, 0x0181)
        self.camera_write(457, 0x218F)
        self.camera_write(458, 0x218A)
        self.camera_write(459, 0x2101)
        self.camera_write(460, 0x0100)
        self.camera_write(469, 0x2184)
        self.camera_write(472, 0x1347)
        self.camera_write(476, 0x2144)
        self.camera_write(480, 0x8D04)
        self.camera_write(481, 0x8501)
        self.camera_write(484, 0xCD04)
        self.camera_write(485, 0xC501)
        self.camera_write(489, 0x0BE2)
        self.camera_write(493, 0x2184)
        self.camera_write(496, 0x1347)
        self.camera_write(500, 0x2144)
        self.camera_write(504, 0x8D04)
        self.camera_write(505, 0x8501)
        self.camera_write(508, 0xCD04)
        self.camera_write(509, 0xC501)
        # SOFT POWER UP REGISTER UPLOADS FOR MODE DEPENDENT REGISTERS
        self.camera_write( 32, 0x2003)
        self.camera_write( 10, 0x0000)
        self.camera_write( 64, 0x0001)
        self.camera_write( 72, 0x0203)
        self.camera_write( 40, 0x0003)
        self.camera_write( 48, 0x0001)
        self.camera_write(112, 0x0007)

        if False: # create black frame
            self.camera_write(219, 0x3E3E)
            self.camera_write(220, 0x6767)
        
        if False: # create grey frame
            self.camera_write(219, 0x3E2D)
            self.camera_write(220, 0x674F)
            self.camera_write(429, 0x0100)
            self.camera_write(430, 0x0B55)
            self.camera_write(431, 0x0351)
            self.camera_write(433, 0x2142)
            self.camera_write(434, 0x2142)
            self.camera_write(444, 0x0100)
            self.camera_write(463, 0x0100)
            self.camera_write(464, 0x0FE4)
            self.camera_write(465, 0x0BE2)
            self.camera_write(475, 0x2142)
            self.camera_write(476, 0x2142)
        
        self.camera_write(192, list_to_int(self.camera_read(192)) | 0b10) # enable rolling shutter
        dummy = 1041 # 60 Hz
        self.camera_write(198, dummy) # dummy lines
        self.camera_write(160, 0x0011) # enable AEC
        self.camera_write(170, dummy) # enable AEC max exposure (note relation to dummy lines)
        self.camera_write(171, 0b1111111111111101) # enable AEC max gain
        #self.camera_write(193, 0xffff) # dummy pixels
        #self.camera_write(192, list_to_int(self.camera_read(192)) | 0b100000) # enable dummy pixels 2

        # ENABLE SEQUENCER REGISTER UPLOAD
        self.camera_write(192, list_to_int(self.camera_read(192)) | 0b1)


        # enable temperature sensor
        self.camera_write(96, 1)

        outputs = set()
        for i in xrange(20):
            output = '{0:025b}'.format(s._r.read(base_addr))
            print i, list_to_int(self.camera_read(97)), output
            outputs.add(output)
        if len(outputs) == 1:
            Camera(name, nCS_pin, MISO_pin, base_addr, power_start)

    def camera_read(self, addr):
        x = s.do_camera_spi(self.nCS_pin, self.MISO_pin, int_to_list(addr, 9) + [0] + [0]*16)
        #print x
        return x[-16:]
    
    def camera_write(self, addr, value):
        s.do_camera_spi(self.nCS_pin, self.MISO_pin, int_to_list(addr, 9) + [1] + int_to_list(value, 16), read=False)

c1 = Camera('C1', 1, 3, 32*1024*1024, 2)
c2 = Camera('C2', 0, 2, 0*1024*1024, 6)

s.close()

"""
    if i == 1000:
        s.set_pin(31)

m = int(7*1024*1024//4)
for i in xrange(m):
    s._r.write(32*1024*1024+i*4, 0xffffffff)
    if i % 1000 == 0: print i/m

'''s.set_pin(31)
time.sleep(3)
x = list_to_int(camera_read(192)) | 0b1
time1 = time.time()
s.clear_pin(31)
s.set_pin(31)
camera_write(192, x)
time2 = time.time()
print time2 - time1

time.sleep(3)'''


with open('dump', 'wb') as f:
    m = int(7*1024*1024//4)
    for i in xrange(m):
        x = s._r.read(32*1024*1024+i*4)
        f.write(struct.pack('>I', x))
        if i % 1000 == 0: print i/m
"""
