import keyboard
import menu
import rendering
import sys
import target_overlay

renderer = rendering.getRenderer() # init the renderer

#Add modules here
m = menu.Menu()
overlay = target_overlay.Overlay(renderer.size)

# create keyboard listener and add a callback
key = keyboard.KeyboardListener(renderer)
key.add_callback(m.key_stuff)

renderer.startRender()
