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
  pygame.init()
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
  
  # run the controller (spawns new thread)
  #visar_controller.do_loop() # removed unused code
  
  # run the renderer (blocks until code is done)
  renderer.do_loop(visar_controller.kill_flag)
  
  # program quit, kill pygame
  pygame.quit()
  
# test class will draw a red rectangle in a dynamic location
class Debug_Dynamic(rendering.Drawable):
  def __init__(self, location=(100,150), size=(100,50)):
    rendering.Drawable.__init__(self)
    self.location = location
    self.size = size
    self.surface = pygame.Surface(self.size) # create the surface 
    self.surface.fill((255,0,0)) # fill it with red
    self.set_draw_target(rendering.Render_Surface(self.surface,position=self.location)) # create the surface
  # update the location  
  def update(self, book):
    pose = book.pose_source.position
    new_location = (int(-pose[0]),int(-pose[1])) # grab x/y from pose, convert to int
    if not (new_location == self.location): # only update surface on change
      self.location = new_location # update the location
      self.set_draw_target(rendering.Render_Surface(self.surface,position=self.location)) # update the surface

# test class will draw a green rectangle
class Debug_Static(rendering.Drawable):
  def __init__(self):
    rendering.Drawable.__init__(self)      
    surface = pygame.Surface((100,50)) # create the surface 
    surface.fill((0,255,0)) # make it green
    # return a Render_Surface at (50,200)
    self.set_draw_target(rendering.Render_Surface(surface,position=(50,200))) 
    
# test class will draw a blue rectangle
class Debug_Depth(rendering.Drawable):
  def __init__(self):
    rendering.Drawable.__init__(self)
    surface = pygame.Surface((100,50)) # create the surface 
    surface.fill((0,0,255)) # make it blue
    # return a 3d Render_Surface (has a depth=500)
    self.set_draw_target(rendering.Render_Surface(surface,(200,300),200))
  
# run debug_wrapper when called from command line
if __name__ == '__main__':
  debug_wrapper()
