import rendering
import numpy as np
import cv2
from vispy import app
import threading
import time
import random

im1 = cv2.cvtColor(np.flipud(cv2.imread('Red_Apple.jpg')), cv2.COLOR_BGR2RGB)
FPS = 60

renderer = rendering.getRenderer() # init the renderer

# create two modules (using a test image)
d1 = rendering.Drawable() 
d1.setTexture(im1)
d1.setVerticies([[-1,-1],[0,-1],[-1,0],[0,0]]) # no depth (automatically set at min)

d2 = rendering.Drawable()
d2.setTexture(im1)
d2.setVerticies([[-.2,-.2,0],[1,-.2,0],[-.2,1,0],[1,1,0]]) # has depth=0

# make function to randomly move d1 (will be spastic)
def move_stuff():
  while True:
    time.sleep(1/FPS*20)
    d1.setVerticies([[random.uniform(-1,1),random.uniform(-1,1)],
      [random.uniform(-1,1),random.uniform(-1,1)],
      [random.uniform(-1,1),random.uniform(-1,1)],
      [random.uniform(-1,1),random.uniform(-1,1)]])
  
# start thread to move stuff
t = threading.Thread(target=move_stuff)
t.daemon = True # not good behavior, too lazy to implement things properly
t.start()
print 'Note: The spastic apple is actually correct behavior.'

# start the renderer (will be packaged elsewhere later)
renderer.startRender()
