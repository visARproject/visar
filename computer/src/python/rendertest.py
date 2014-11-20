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
  square1 = Debug_Static() # create a render module
  renderer.add_module(square1) # add module to render stack
  
  # setup dynamic (moving) square object (rendertest)
  square2 = Debug_Dynamic() # create another module
  visar_controller.add_update(square2.update) # add pose listener
  renderer.add_module(square2) # add drawable to render stack
  
  # setup a static square object with depth (from rendertest)
  square3 = Debug_Depth() # create a render module
  renderer.add_module(square3) # add module to render stack
  
  #run the renderer
  renderer.do_loop()
  
# test class will draw a red rectangle in a dynamic location
class Debug_Dynamic(rendering.Drawable):
  def __init__(self, location=(100,150), size=(100,50)):
    self.location = location
    self.size = size
  # define method for renderer to call, draws a rectangle
  def draw(self, size):
    surface = pygame.Surface(self.size) # create the surface 
    surface.fill((255,0,0)) # fill it with red
    # return a Render_Surface at specified location
    return rendering.Render_Surface(surface,position=self.location) 
  # update the location  
  def update(self, book):
    pose = book.pose_source.position
    self.location = (int(-pose[0]),int(-pose[1])) # grab x/y from pose, convert to int

# test class will draw a green rectangle
class Debug_Static(rendering.Drawable):
  def draw(self, size):
    surface = pygame.Surface((100,50)) # create the surface 
    surface.fill((0,255,0)) # make it green
    # return a Render_Surface at (50,200)
    return rendering.Render_Surface(surface,position=(50,200)) 
    
# test class will draw a blue rectangle
class Debug_Depth(rendering.Drawable):
  def draw(self, size):
    surface = pygame.Surface((100,50)) # create the surface 
    surface.fill((0,0,255)) # make it blue
    # return a 3d Render_Surface (has a depth=500)
    return rendering.Render_Surface(surface,(200,300),200)
  
# run debug_wrapper when called from command line
if __name__ == '__main__':
  debug_wrapper()
