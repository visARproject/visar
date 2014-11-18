# main method for visar screen thingy, should set things up, then call rendering

import rendering
import rendertest
import user_pose
import controller
import menu_button

def visar():
  # initialize things
  pose_source = user_pose.FPS_Pose() # initialize position source
  visar_controller = controller.Controller(pose_source) # initialize controller
  renderer = rendering.Renderer(visar_controller) # initialize renderer
  
  # add pose source to update stack
  visar_controller.add_update(pose_source.update) 
  
  # menu buttons 
  menu = menu_button.Menu()
  renderer.add_2d_module(menu.draw)
  
  # run the renderer
  renderer.do_loop()
  
  
# make file executable
if __name__ == '__main__':
  visar()
