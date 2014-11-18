# Debug and rendering test for rendering.py  
# imports for drawable classes
import pygame
import rendering       
# imports for main program execution 
import controller
import user_pose

# wrapper to simulate main function        
def debug_wrapper():
  # initialize things
  pose_source = user_pose.FPS_Pose(two_d=True) # initialize position source
  visar_controller = controller.Controller(pose_source) # initialize controller
  renderer = rendering.Renderer(visar_controller) # initialize renderer
  
  # add pose source to update stack
  visar_controller.add_update(pose_source.update) 
  
  # setup a static square object (from rendertest)
  square1 = rendertest.Debug_Static() # create a render module
  renderer.add_2d_module(square1.draw) # add module's draw to render stack
  
  # setup dynamic (moving) square object (rendertest)
  square2 = rendertest.Debug_Dynamic() # create another module
  visar_controller.add_update(square2.update) # add pose listener
  renderer.add_2d_module(square2.draw) # add draw method to render stack
  
  # setup a static square object with depth (from rendertest)
  square3 = rendertest.Debug_Depth() # create a render module
  renderer.add_3d_module(square3.draw) # add module's draw to render stack
  
  #run the renderer
  renderer.do_loop()
  
# test class will draw a red rectangle in a dynamic location
class Debug_Dynamic:
  def __init__(self, location=(100,150), size=(100,50)):
    self.location = location
    self.size = size
  # define method for renderer to call, draws a rectangle
  def draw(self, surface): 
    pygame.draw.rect(surface,(255,0,0),self.location+self.size) #draw rectangle
    return surface # return the updated surface
  # update the location  
  def update(self, book):
    pose = book.pose_source.position
    self.location = (int(-pose[0]),int(-pose[1])) # grab x/y from pose, convert to int

# test class will draw a green rectangle
class Debug_Static:
  def draw(self, surface):
    pygame.draw.rect(surface,(0,255,0),(50,200,100,50))
    return surface
    
# test class will draw a blue rectangle
class Debug_Depth:
  def draw(self, surface):
    pygame.draw.rect(surface,(0,0,255),(200,300,100,50))
    return rendering.Surface_3D(surface,depth=.01)
  
# run debug_wrapper when called from command line
if __name__ == '__main__':
  debug_wrapper()
