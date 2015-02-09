# coding=utf-8

from __future__ import division

import struct
import time

import ram_test

class SPIer(object):
    def __init__(self):
        self._r = ram_test.RAMPoker()
        self._drive = 0b110100000011
        self._drive |= 1<<31
        self._pins = 0b110100000011
        self._r.write(0xFFFFFFF4, self._pins)
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
    def do_spi(self, nCS_pin, MISO_pin, bits, read=True):
        MOSI_pin = 11
        SCLK_pin = 8
        
        self.set_pin(SCLK_pin)
        self.clear_pin(nCS_pin)
        res = []
        for b in bits:
            self.clear_pin(SCLK_pin)
            if b:
                self.set_pin(MOSI_pin)
            else:
                self.clear_pin(MOSI_pin)
            if read:
                res.append(self.read_pin(MISO_pin))
            self.set_pin(SCLK_pin)
        self.set_pin(nCS_pin)
        
        if read:
            return res
    def do_camera_spi(self, nCS_pin, MISO_pin, bits, read=True):
        MOSI_pin = 11
        SCLK_pin = 8
        
        self.clear_pin(SCLK_pin)
        self.clear_pin(nCS_pin)
        res = []
        for b in bits:
            if b:
                self.set_pin(MOSI_pin)
            else:
                self.clear_pin(MOSI_pin)
            self.set_pin(SCLK_pin)
            if read:
                res.append(self.read_pin(MISO_pin))
            self.clear_pin(SCLK_pin)
        self.set_pin(nCS_pin)
        
        if read:
            return res

s = SPIer()
assert s.do_spi(10, 9, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]) == [1, 0, 1, 0, 0, 1, 1, 0, 0, 1]
'''while True:
    print '{0:025b}'.format(s._r.read(32*1024*1024))
    time.sleep(.1)'''
assert s.do_spi(10, 9, [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]) == [1, 0, 1, 0, 0, 1, 1, 0, 0, 1]
assert s.do_spi(10, 9, [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]) == [1, 0, 1, 0, 0, 1, 1, 0, 0, 1]
assert s.do_spi(10, 9, [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]) == [1, 0, 1, 0, 0, 1, 1, 0, 0, 1]
assert s.do_spi(10, 9, [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]) == [1, 0, 1, 0, 0, 1, 1, 0, 0, 1]

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

def camera_read(addr):
    x = s.do_camera_spi(1, 3, int_to_list(addr, 9) + [0] + [0]*16)
    #print x
    return x[-16:]
def camera_write(addr, value):
    s.do_camera_spi(1, 3, int_to_list(addr, 9) + [1] + int_to_list(value, 16), read=False)

assert camera_read(0) == int_to_list(0x560D, 16)

# V1-SN/SE 10-bit mode without PLL

# ENABLE CLOCK MANAGEMENT REGISTER UPLOAD − PART 1
camera_write( 2, 0x0001)
camera_write(32, 0x2000)
camera_write(20, 0x0001)
# ENABLE CLOCK MANAGEMENT REGISTER UPLOAD − PART 2
camera_write( 9, 0x0000)
camera_write(32, 0x2002)
camera_write(34, 0x0001)
# REQUIRED REGISTER UPLOAD
camera_write( 41, 0x085A)
camera_write(129, list_to_int(camera_read(129)) & 0b1101111111111111)
camera_write( 65, 0x288B)
camera_write( 66, 0x53C5)
camera_write( 67, 0x0344)
camera_write( 68, 0x0085)
camera_write( 70, 0x4800)
camera_write(128, 0x4710)
camera_write(197, 0x0103)
camera_write(176, 0x00F5)
camera_write(180, 0x00FD)
camera_write(181, 0x0144)
camera_write(387, 0x549F)
camera_write(388, 0x549F)
camera_write(389, 0x5091)
camera_write(390, 0x1011)
camera_write(391, 0x111F)
camera_write(392, 0x1110)
camera_write(431, 0x0356)
camera_write(432, 0x0141)
camera_write(433, 0x214F)
camera_write(434, 0x214A)
camera_write(435, 0x2101)
camera_write(436, 0x0101)
camera_write(437, 0x0B85)
camera_write(438, 0x0381)
camera_write(439, 0x0181)
camera_write(440, 0x218F)
camera_write(441, 0x218A)
camera_write(442, 0x2101)

camera_write(443, 0x0100)
camera_write(447, 0x0B55)
camera_write(448, 0x0351)
camera_write(449, 0x0141)
camera_write(450, 0x214F)
camera_write(451, 0x214A)
camera_write(452, 0x2101)
camera_write(453, 0x0101)
camera_write(454, 0x0B85)
camera_write(455, 0x0381)
camera_write(456, 0x0181)
camera_write(457, 0x218F)
camera_write(458, 0x218A)
camera_write(459, 0x2101)
camera_write(460, 0x0100)
camera_write(469, 0x2184)
camera_write(472, 0x1347)
camera_write(476, 0x2144)
camera_write(480, 0x8D04)
camera_write(481, 0x8501)
camera_write(484, 0xCD04)
camera_write(485, 0xC501)
camera_write(489, 0x0BE2)
camera_write(493, 0x2184)
camera_write(496, 0x1347)
camera_write(500, 0x2144)
camera_write(504, 0x8D04)
camera_write(505, 0x8501)
camera_write(508, 0xCD04)
camera_write(509, 0xC501)
# SOFT POWER UP REGISTER UPLOADS FOR MODE DEPENDENT REGISTERS
camera_write( 32, 0x2003)
camera_write( 10, 0x0000)
camera_write( 64, 0x0001)
camera_write( 72, 0x0203)
camera_write( 40, 0x0003)
camera_write( 48, 0x0001)
camera_write(112, 0x0007)
# ENABLE SEQUENCER REGISTER UPLOAD
camera_write(192, list_to_int(camera_read(192)) | 0b1)


# enable temperature sensor
camera_write(96, 1)


for i in xrange(1500):
    print i, list_to_int(camera_read(97)), '{0:025b}'.format(s._r.read(32*1024*1024))
    if i == 1000:
        s.set_pin(31)

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
