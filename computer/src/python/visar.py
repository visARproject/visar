import rendering
import sys

def visar():
  renderer = rendering.getRenderer() # init the renderer
  
  #Add modules here
  
  
  # keyboard listner, prints keypresses/releases
  def key_exit(event):
    if(event.key == vispy.keys.ESCAPE): exit()

  # create keyboard listener and add a callback
  key = keyboard.KeyboardListener(renderer)
  key.add_callback(key_stuff)



