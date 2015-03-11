import network
import interface
import time
import socket
  
def networkCallback(event):
  print event
  
def test():
  print 'Starting Network'
  network_state = network.NetworkState(socket.gethostname(), 'testname', 'status')
  network_state.add_callback(networkCallback)
  
  time.sleep(20)
  print 'Updating Status'
  network_state.update_status('part2')
  
  #clean up the objects
  time.sleep(100)
  print 'cleanup'
  network_state.destroy()
  
  print 'Waiting for update thread to timeout...'
  
if __name__ == '__main__':
  test()
