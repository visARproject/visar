# Debug and rendering test for rendering.py  
import pygame
import rendering        

# wrapper to simulate main function        
def debug_wrapper():
  test_renderer = rendering.Renderer() # create the renderer
  test_drawable1 = Debug_Draw1() # get object
  test_renderer.add_module(test_drawable1) # add to render stack
  test_drawable2 = Debug_Draw2()
  test_renderer.add_module(test_drawable2)
  test_renderer.do_loop() # start renderer loop

# test class will draw a red rectangle
class Debug_Draw1:
  def draw(self, surface): # define method for renderer to call
    pygame.draw.rect(surface,(255,0,0),(100,150,100,50)) #draw rectangle
    return surface # return the updated surface

# test class will draw a green rectangle
class Debug_Draw2:
  def draw(self, surface):
    pygame.draw.rect(surface,(0,255,0),(50,200,100,50))
    return surface
  
# run debug_wrapper when called from command line
if __name__ == '__main__':
  debug_wrapper()
