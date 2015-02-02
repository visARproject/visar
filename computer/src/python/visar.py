import keyboard
import menu
import rendering
import sys
import target_overlay

renderer = rendering.getRenderer() # init the renderer

#Add modules here
m = menu.Menu()
overlay = target_overlay.Overlay(renderer.size)

# keyboard listner, prints keypresses/releases
def key_stuff(event, direction):
  # if(event.key == vispy.keys.ESCAPE): exit()
  if direction == "down":
    if event.text == "w":
      m.change_keys("up")
    elif event.text == "s":
      m.change_keys("down")
    elif event.text == "a":
      m.change_keys("back")
    elif event.text == "d":
      m.change_keys("forward")

# create keyboard listener and add a callback
key = keyboard.KeyboardListener(renderer)
key.add_callback(key_stuff)

renderer.startRender()