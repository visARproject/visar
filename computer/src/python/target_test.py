import keyboard
import target_overlay
import rendering

renderer = rendering.getRenderer() ## init the renderer

overlay = target_overlay.Overlay(renderer.size)

# ## keyboard listener, prints keypresses/releases
# def key_stuff(event, direction):
#   if direction == "down":
#     if event.text == "w":
#       m.change_keys("up")
#     elif event.text == "s":
#       m.change_keys("down")
#     elif event.text == "a":
#       m.change_keys("back")
#     elif event.text == "d":
#       m.change_keys("forward")

# ## create keyboard listener and add a callback
# key = keyboard.KeyboardListener(renderer)
# key.add_callback(key_stuff)

renderer.startRender()