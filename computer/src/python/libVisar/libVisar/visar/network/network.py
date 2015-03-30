import sys, time
from socket import *
import threading
import copy
from ..interface import Interface

BROADCAST_PORT = 19105  # UDP port for status broadcast
UPDATE_PORT    = 19106  # UDP port for status update
TIMEOUT        = 1      # socket timeout (seconds)    
UPDATE_TIMER   = 30     # how often to send updates/ping dead clients
BIND_ADDR      = '' 
BROADCAST_ADDR = '192.168.1.255' # TODO: find this dynamically

class NetworkState(Interface):
  ''' Class maintains a list of all peers on the network and polls for updates.
      Interface event consists of the entire peer dictionary at every update. '''
       
  def __init__(self, id_code, name, status=''):
    Interface.__init__(self)
  
    # setup the sockets
    self.b_sock = socket(AF_INET, SOCK_DGRAM) # broadcast socket, publishes status info
    self.c_sock = socket(AF_INET, SOCK_DGRAM) # client socket, pings peers to see if alive
    self.s_sock = socket(AF_INET, SOCK_DGRAM) # server socket, handles pings/broadcasts
    self.b_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) # enable broadcasting
    self.c_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # allow socket to rebind
    self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # allow socket to rebind
    self.b_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # allow socket to rebind
    self.b_sock.bind((BIND_ADDR,0)) # bind to correct interface with any port
    
    
    # setup other object details
    self.kill_flag = False
    self.id_code = id_code
    self.name = name
    self.status = status
    self.peers = {id_code : ('127.0.0.1', name, '')} # list of peers as dictionary
    self.lock = threading.RLock() # lock object
    
    # setup and start the treads
    self.blistener = threading.Thread(target=self.broadcast_listener) 
    self.ulistener = threading.Thread(target=self.update_thread) 
    self.blistener.start()
    self.ulistener.start()
    self.send_update() # send initial update

  def destroy(self):
    '''set the kill flag to signal threads to shutdown, clean up socket'''
    self.kill_flag = True
    self.b_sock.close()
    
  def send_update(self):
    '''Broadcast an update'''
    #print 'Sending Broadcast'
    self.lock.acquire()
    self.peers[self.id_code] = ('127.0.0.1', self.name, self.status) # update our status
    self.lock.release()
    self.b_sock.sendto(self.id_code + '~' + self.name + '~' + self.status, (BROADCAST_ADDR,BROADCAST_PORT))

  def broadcast_listener(self):
    '''Thread listens for broadcasts/pings and updates peer list as new information is avliable'''
    self.s_sock.bind((BIND_ADDR,BROADCAST_PORT)) # attach to the port
    self.s_sock.settimeout(TIMEOUT)       # set the timeout
    while(not self.kill_flag):
      try: data, addr = self.s_sock.recvfrom(1024) # get updates
      except: continue # loop on timeouts
      update = data.split('~') # split input on newline
      if update[0] == self.id_code: continue # ignore local traffic
      self.s_sock.sendto(self.id_code,addr) # send an ack with our id code
      #print 'sent ack', addr
      if len(update) < 3: 
        #print 'Ignored: %s' % (update,)
        continue # ping, ignore it
      
      #print 'Updated: %s' % (update,)
      # update the peer's info
      self.lock.acquire()
      # try to get old peer info, set to None if nonexistent
      try: old_peer = self.peers[update[0]] 
      except: old_peer = None
      self.peers[update[0]] = (addr[0],update[1],update[2]) # update peer info
      self.lock.release()
      if(not old_peer == self.peers[update[0]]): # don't send frivilous updates
        self.lock.acquire()
        peer_copy = copy.deepcopy(self.peers) # copy the peer list
        self.lock.release()
        self.do_updates(peer_copy) # send an update event
      
    #print 'b_listner thread shutdown'      
    self.s_sock.close() # shutdown, close the socket
      
  def update_thread(self):
    '''Update thread pings known peers to see if they're still alive.
        Also calls send_update to braodcast. Long waits between updates '''
    self.c_sock.bind((BIND_ADDR,UPDATE_PORT)) # bind to the update port
    self.c_sock.settimeout(TIMEOUT)    # set the timeout
    
    while(not self.kill_flag):
      time.sleep(UPDATE_TIMER/2) # wait before doing the ping
      if(self.kill_flag): break
      removal_list = []
      self.lock.acquire()
      peer_copy = copy.deepcopy(self.peers)
      self.lock.release()
      for peer in peer_copy:
        if peer==self.id_code: continue # don't ping ourselves
        #print 'pinging', peer
        self.c_sock.sendto('ping',(peer_copy[peer][0], BROADCAST_PORT))
        try: 
          data, addr = self.c_sock.recvfrom(16) # get the ack
          if not peer in data:
            removal_list.append(peer) # remove the entry if code doesnt match
          #print 'got ack', peer
        except: 
          removal_list.append(peer) # no response, peer is dead
          #print 'ack timeout', peer
      
      self.lock.acquire()
      for key in removal_list: del self.peers[key] # remove dead peers
      peer_copy = copy.deepcopy(self.peers) # copy list of peers
      self.lock.release()
      
      if len(removal_list) > 0: self.do_updates(peer_copy) # send an event
      
      time.sleep(UPDATE_TIMER/2) # wait again
      if(self.kill_flag): break
      self.send_update() # send an update
    
    #print 'update thread shutdown'
    self.c_sock.close() # shutdown, close the socket
    
  def update_status(self, status):
    '''update our current status'''
    self.lock.acquire()
    self.status = status
    self.peers[self.id_code] = ('127.0.0.1', self.name, self.status)
    peer_copy = copy.deepcopy(self.peers)
    self.lock.release()
    self.send_update()
    self.do_updates(peer_copy)
