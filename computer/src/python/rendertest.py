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
FPS = 60

renderer = rendering.getRenderer() # init the renderer

# create two modules (using a test image)
d1 = rendering.Drawable(verticies=[[-1,-1],[0,-1],[-1,0],[0,0]], tex_data=im1)

# d2/d3 alternate between apple textures
d2 = rendering.Drawable([[-.2,-.2],[1,-.2],[-.2,1],[1,1]], tex_data=im1)
d3 = rendering.Drawable([[-.2,-.2],[1,-.2],[-.2,1],[1,1]], tex_data=im2)

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
    d1.setPosition(np.random.ranf([4,4]))

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
