# main method for visar screen thingy, should set things up, then call rendering

import rendering
import rendertest
import user_pose
import controller
import menu_button

def visar():
  # initialize things
  pose_source = user_pose.FPS_Pose(two_d=True) # initialize position source
  visar_controller = controller.Controller(pose_source) # initialize controller
  renderer = rendering.Renderer(visar_controller) # initialize renderer
  
  # add pose source to update stack
  visar_controller.add_update(pose_source.update) 
  
  # setup a static square object (from rendertest)
  square1 = rendertest.Debug_Static() # create a render module
  renderer.add_module(square1.draw) # add module's draw to render stack
  
  # setup dynamic (moving) square object (rendertest)
  square2 = rendertest.Debug_Dynamic() # create another module
  visar_controller.add_pose_update(square2.update) # add pose listener
  renderer.add_module(square2.draw) # add draw method to render stack

  menu = menu_button.Menu()
  renderer.add_module(menu.draw)
  
  # run the renderer
  renderer.do_loop()
  
  
# make file executable
if __name__ == '__main__':
  visar()
