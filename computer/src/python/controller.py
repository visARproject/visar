# visAR interface controller:
#   manages system information, calls updates

import pygame
import multiprocessing
import threading
from pygame.locals import *

FPS = 30

class Controller:
  def __init__(self, pose_source):
    self.updates = [] # update function references
    self.book = Controller_Book(pose_source) # init book
    self.kill_flag = threading.Event() # setup kill event
    self.clock = pygame.time.Clock() # timer to keep from updating too much
    
  # get the information, push updates
  def do_update(self):
    for update in self.updates: 
      update(self.book) # call the updates
  
  # function to add an update listener
  def add_update(self, update):
    self.updates.append(update)
  
  # spawn thread to run control loop forever
  def do_loop(self):
    #p = multiprocessing.Process(target=self.update_loop)
    p = threading.Thread(target=self.update_loop)
    p.start() # start the process       

  # function wrapper loops around the update method
  def update_loop(self, single_thread = False):
    if(single_thread): # single-threaded mode, run once
      self.book.update()
      self.do_update()
      if(self.book.exiting): self.kill_flag.set()
    else: # multithreaded mode, run forever
      while not self.book.exiting:
        self.book.update()
        self.do_update()
        self.clock.tick(FPS)
      self.kill_flag.set() # notify rest of program to exit

# Controller book stores state information, add things as nessecarry
class Controller_Book:
  def __init__(self, pose_source, name='anonymous'):
    self.pose_source = pose_source # position information
    self.keys = pygame.key.get_pressed()
    self.last_keys = None
    self.eye_size = (0, 0)
    self.events = []
    self.count = 0
    self.exiting = False # tell threads to exit
    self.name = name # set a name/id thing
    self.audio_manager = None

    # menu botton information, stores changes
    # '', 'up', 'down', 'forward', 'back', or 'hide all'
    self.menu_status = ''
    
  # update the book's stored data (keys/events)
  def update(self):
    self.last_keys = self.keys
    self.keys = pygame.key.get_pressed()
    self.events = pygame.event.get()
    
    # check exit conditions
    if self.keys[K_ESCAPE]: self.exiting = True
    for event in self.events:
      if event.type == QUIT: self.exiting = True
    
    # audio connection (uses t, connects to predefined ip)
    if self.keys[K_t] and not self.last_keys[K_t]: # watch for keypress
      if not self.audio_manager.connection.connected: # connect voicechat
        #self.audio_manager.connect('192.168.1.16') # connect to val
        self.audio_manager.connect('127.0.0.1') # connect to localhost
      else: # disconnect voicechat
        self.audio_manager.disconnect()
    
    
  def get_pose(self):
    return pose_source.get_pose()
    
