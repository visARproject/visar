# Debug and rendering test for rendering.py  
import pygame
import rendering        

# wrapper to simulate main function        
def debug_wrapper():
  test_renderer = rendering.Renderer() # create the renderer
  test_drawable1 = Debug_Static() # get object
  test_renderer.add_module(test_drawable1.draw) # add to render stack
  test_drawable2 = Debug_Dynamic()
  test_renderer.add_module(test_drawable2.draw)
  test_renderer.do_loop() # start renderer loop

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
  
# run debug_wrapper when called from command line
if __name__ == '__main__':
  debug_wrapper()
