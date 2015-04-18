import serial
import time
import subprocess
import struct
import random

wide = False

class RAMPoker(object):
    def __init__(self):
        self._s = serial.Serial('/dev/FPGA_SERIAL', 4000000)
        subprocess.check_call(['stty', '-F', '/dev/FPAG_SERIAL', '4000000']) # WHYY
        time.sleep(.2)
        self._s.read(self._s.inWaiting())
    
    def _read(self, n):
        while self._s.inWaiting() < n: pass
        assert self._s.inWaiting() == n
        return self._s.read(n)
    
    def _run(self, cmd):
        assert len(cmd) == (13 if wide else 9)
        self._s.write('\xda' + cmd)
    
    def read(self, addr):
        assert not self._s.read(self._s.inWaiting())
        self._run(struct.pack('<BIQ' if wide else '<BII', 0, addr, 0))
        res, = struct.unpack('<Q' if wide else '<I', self._read(8 if wide else 4))
        return res
    
    def write(self, addr, data):
        self._run(struct.pack('<BIQ' if wide else '<BII', 1, addr, data))

if __name__ == '__main__':
    x = RAMPoker()


    while True:
        p = random.randrange(2**32)
        v = random.randrange(2**64 if wide else 2**32)
        print '{0:032b}'.format(p)
        print ('{0:064b}' if wide else '{0:032b}').format(v)
        x.write(p, v)
        r = x.read(p)
        print ('{0:064b}' if wide else '{0:032b}').format(r)
        print ('{0:064b}' if wide else '{0:032b}').format(r^v)
        print ('{0:064b}' if wide else '{0:032b}').format(2**32-1)
        if r == v:
            print '{0:032b}'.format(p), 'good'
            for i in xrange(31, -1, -1):
                if x.read(p^(2**i)) == v:
                    print 'mir', i
        else:
            print '{0:032b}'.format(p), 'bad', hex(v)
            acxza
        print
