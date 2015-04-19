# coding=utf-8

# requires python-xbee from git@github.com:thom-nic/python-xbee.git

import serial
from xbee import DigiMesh
import struct


def hexify(str):
    return ':'.join(x.encode('hex') for x in str)


serial_port = serial.Serial('/dev/XBEE_SERIAL', 115200)
xbee = DigiMesh(serial_port)

while True:
    try:
        #print serial_port.readline()
        frame = xbee.wait_read_frame()
        data = frame['data']
        seq_num = struct.unpack('B', data[1])[0]
        message_part = struct.unpack('B', data[2])[0]
        message_part_total = struct.unpack('B', data[3])[0]
        message_data = data[4:]
        num_sats = 0
        if len(message_data) > 2 and (message_data[0] == '\xdd'): ##or message_data[0] == '\xde'):
            num_sats = struct.unpack('B', message_data[2])[0]
        print hexify(data)
#        print seq_num, message_part, message_part_total, num_sats, len(data[4:]), hexify(message_data)

    except KeyboardInterrupt:
        break

serial_port.close()
