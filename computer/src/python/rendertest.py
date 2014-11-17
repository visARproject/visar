# Debug and rendering test for rendering.py  
import pygame
import rendering        
        
def debug_wrapper():
  test_renderer = rendering.Renderer()
  test_drawable1 = Debug_Draw1()
  test_renderer.add_module(test_drawable1)
  test_drawable2 = Debug_Draw2()
  test_renderer.add_module(test_drawable2)
  test_renderer.do_loop()
  
class Debug_Draw1:
  def draw(self, surface):
    pygame.draw.rect(surface,(255,0,0),(100,150,100,50))
    return surface

class Debug_Draw2:
  def draw(self, surface):
    pygame.draw.rect(surface,(0,255,0),(50,200,100,50))
    return surface
  
if __name__ == '__main__':
  debug_wrapper()
