# main method for visar screen thingy, should set things up, then call rendering

import rendering
import rendertest
import user_pose
import controller
import menu_button
import sys

def visar():
  debug_mode = False;

  if len(sys.argv) > 1:
    if sys.argv[1] == '--debug':
      debug_mode = True # check for debug mode

  # initialize things
  pose_source = user_pose.FPS_Pose() # initialize position source
  visar_controller = controller.Controller(pose_source) # initialize controller
  renderer = rendering.Renderer(visar_controller,debug_mode) # initialize renderer
  
  # menu buttons 
  menu = menu_button.Menu()
  renderer.add_module(menu)

  # add pose source to update stack
  visar_controller.add_update(pose_source.update)
  visar_controller.add_update(menu.update)
  
  # run the renderer
  renderer.do_loop()
  
  
# make file executable
if __name__ == '__main__':
  visar()
