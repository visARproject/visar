import os

DEBUG_FIFO = '/tmp/vsr_debug'

print "here0"

try:
  os.mkfifo(DEBUG_FIFO)
except:
  os.unlink(DEBUG_FIFO)
  os.mkfifo(DEBUG_FIFO)

print "here1"

debug_pipe = os.open(DEBUG_FIFO, os.O_RDONLY)

while True:
  out = os.read(debug_pipe, 80)
  print out

os.close(debug_pipe)