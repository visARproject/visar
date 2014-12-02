# main method for visar screen thingy, should set things up, then call rendering

import rendering
import rendertest
import user_pose
import controller
import menu_button
import sys
import arrows
import pygame

def visar():
  debug_mode = False;

  if len(sys.argv) > 1:
    if sys.argv[1] == '--debug':
      debug_mode = True # check for debug mode

  # initialize things
  pygame.init()
  pose_source = user_pose.FPS_Pose() # initialize position source
  visar_controller = controller.Controller(pose_source) # initialize controller
  renderer = rendering.Renderer(visar_controller,debug_mode) # initialize renderer
  
  # arrows
  arrows_ = arrows.Arrows()
  renderer.add_module(arrows_)

  # menu buttons 
  menu = menu_button.Menu()
  renderer.add_module(menu)

  # add pose source to update stack
  visar_controller.add_update(pose_source.update)
  visar_controller.add_update(menu.update)
  visar_controller.add_update(arrows_.update)
  
  # start the controller (new thread)
  visar_controller.do_loop() #temporarily disabled
  
  # run the renderer (same thread)
  renderer.do_loop(visar_controller.kill_flag)
  
  # cleanup
  pygame.quit()
  
# make file executable
if __name__ == '__main__':
  visar()
