import time
import socket
import threading

BROADCAST_PORT = 19105  # UDP port for status broadcast
TIMEOUT        = 1      # socket timeout (seconds)    
UPDATE_TIMER   = 60     # how often to send updates/ping dead clients

class network_state(interface):
  ''' Class maintains a list of all peers on the network and polls for updates.
      Interface event consists of the entire peer dictionary at every update. '''
       
  def __init__(self, id, name, status=''):
    # setup the sockets
    self.b_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # broadcast socket, publishes status info
    self.c_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # client socket, pings peers to see if alive
    self.s_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # server socket, handles pings/broadcasts
    self.b_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) # enable broadcasting
    
    # setup other object details
    self.kill_flag = False
    self.id = id
    self.name = name
    self.status = status
    self.peers = {id : ('self', name, '')} # list of peers as dictionary
    self.lock = threading.RLock() # lock object
    
    # setup and start the treads
    self.blistener = threading.Thread(target=broadcast_listener) 
    self.ulistener = threading.Thread(target=update_thread) 
    self.blistener.start()
    self.ulistener.start()
    self.send_update() # send initial update

  def destroy(self):
    '''set the kill flag to signal threads to shutdown, clean up socket'''
    self.kill_flag = True
    self.b_sock.close()
    
  def send_update(self):
    '''Broadcast an update'''
    self.lock.acquire()
    peers[id] = (self.id, self.name, status) # update our status
    status = self.status
    self.lock.release()
    self.b_sock.sendto(self.id + '~' + self.name + '~' + status + '\n', ('<broadcast>',BROADCAST_PORT))

  def broadcast_listener(self):
  '''Thread listens for broadcasts/pings and updates peer list as new information is avliable'''
    self.s_sock.bind(('',BROADCAST_PORT)) # attach to the port
    self.s_sock.settimeout(TIMEOUT)       # set the timeout
    while(not self.kill_flag):
      try: data, addr = self.s_sock.recvfrom(1024) # get updates
      except: continue # loop on timeouts
      update = data.split('~') # split input on newline
      self.s_sock.sendto('ack',addr) # send an ack
      if len(update) < 3: continue # ping, ignore it
      
      self.lock.acquire()
      self.peers[update[0]] = (addr[0],update[1],update[2]) # update peer info
      peer_copy = self.peers
      self.lock.release()
      
      self.do_update(peer_copy) # send an update event
      
    self.s_sock.close() # shutdown, close the socket
      
  def update_thread(self):
    '''Update thread pings known peers to see if they're still alive.
        Also calls send_update to braodcast. Long waits between updates '''
    self.c_sock.bind(('',UPDATE_PORT)) # bind to the update port
    self.c_sock.settimeout(TIMEOUT)    # set the timeout
    
    while(not self.kill_flag):
      time.sleep(UPDATE_TIMER/2) # wait before doing the ping
      removal_list = []
      for peer in self.peers:
        self.c_sock.sendto('ping',(self.peers[peer][0], BROADCAST_PORT)
        try: data, addr = self.c_sock.recvfrom(16) # get the ack
        except: removal_list.append(peer) # no response, peer is dead
      
      self.lock.acquire()
      for key in removal_list: del self.peers[key] # remove dead peers
      peer_copy = self.peers # copy list of peers
      self.lock.release()
      
      if len(removal_list) > 0: self.do_update(peer_copy) # send an event
      
      time.sleep(UPDATE_TIMER/2) # wait again
      self.send_update() # send an update
      
    self.c_sock.close() # shutdown, close the socket
    
  def update_status(self, status):
    '''update our current status'''
    self.lock.acquire()
    self.status = status
    self.lock.release()