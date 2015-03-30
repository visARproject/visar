import sys

with open(sys.argv[1]) as f:
    print '''constant edid_data : edid_t := (''' + ', '.join('x"%02x"'%ord(a) for a in f.read()) + ''');'''
