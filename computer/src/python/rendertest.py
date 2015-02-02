import numpy as np
from vispy import app, io
import threading
import time
import random
import vispy
import rendering
import keyboard

im1 = np.flipud(np.fliplr(io.imread('images/Red_Apple.jpg')))
im2 = np.flipud(np.fliplr(io.imread('images/Blue_Apple.jpg')))
FPS = 10

renderer = rendering.getRenderer() # init the renderer

# create two modules (using a test image)
d1 = rendering.Drawable() 
d1.setTexture(im1)
d1.setVerticies([[-1,-1],[0,-1],[-1,0],[0,0]]) # no depth (automatically set at min)

# d2/d3 alternate between apple textures
# swapping prebuilt drawables is SIGNIFICANTLY more efficent than changing textures
d2 = rendering.Drawable()
d2.setTexture(im1)
d2.setVerticies([[-.2,-.2,0],[1,-.2,0],[-.2,1,0],[1,1,0]]) # has depth=0

d3 = rendering.Drawable()
d3.setTexture(im2)
d3.setVerticies([[-.2,-.2,0],[1,-.2,0],[-.2,1,0],[1,1,0]]) # has depth=0

# keyboard listner, prints keypresses/releases
def key_stuff(event, direction):
  if(direction == 'down' and not event.text == ''): 
    print event.text
  if(event.key == vispy.keys.ESCAPE): exit()

# create keyboard listener and add a callback
key = keyboard.KeyboardListener(renderer)
key.add_callback(key_stuff)

# make function to randomly move d1 (will be spastic)
def move_stuff():
  count = 0
  while True:
    renderer.measure_fps(1, renderer.print_fps)
    count += 1
    time.sleep(1.0/FPS)
    
    # change the verticies in the first image (use setVerticies)
    d1.setVerticies([[random.uniform(-1,1),random.uniform(-1,1)],
      [random.uniform(-1,1),random.uniform(-1,1)],
      [random.uniform(-1,1),random.uniform(-1,1)],
      [random.uniform(-1,1),random.uniform(-1,1)]])

    # swap the second image every 5 frames
    # Note: Use multiple drawables instead of setTexture for efficency
    if count % 10 == 0:
      d2.pauseRender()
      d3.resumeRender()
      count = 0
    elif count % 5 == 0:
      d3.pauseRender()
      d2.resumeRender()
  
# start thread to move stuff
t = threading.Thread(target=move_stuff)
t.daemon = True # not good behavior, too lazy to implement things properly for test
t.start()
print 'Note: The spastic apple is actually correct behavior.'

# start the renderer (will be packaged elsewhere later)
renderer.startRender()
