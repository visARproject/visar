import sys

with open(sys.argv[1]) as f:
    d = f.read()
assert len(d) == 256

print '''constant edid_data : edid_t := (''' + ', '.join('x"%02x"'%ord(a) for a in d) + ''');'''
