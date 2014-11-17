# define the class that handles the rendering
# individual modules should pass it an object with
#   a draw(surface) method which will returns a surface
import pygame
from pygame.locals import *

FPS = 30 # run at 30FPS

class Renderer:
  def __init__(self, controller=None):
    self.draws = [] # list of draw methods from modules
    self.controller = controller # controller object for the visAR program 
    # initialize a fullscreen display
    self.display_surface = pygame.display.set_mode((0,0),pygame.FULLSCREEN,0)
    #self.display_surface = pygame.display.set_mode((400,300)) #DEBUG
    self.clock = pygame.time.Clock() # timer for fpsing

  # method contains a loop running at 30hz
  def do_loop(self):
    pygame.display.set_caption('visAR')
    done = False
    while not done: # main game loop
      # check exit conditions
      if pygame.key.get_pressed()[K_ESCAPE]: done = True
      for event in pygame.event.get():
        if event.type == QUIT: done = True
      if(done): 
        pygame.quit()
        break
      
      # call controller update
      if(self.controller is not None): self.controller.do_update()
      
      # get and combine each modules's drawn output
      self.display_surface.fill((0,0,0)) # wipe the buffer
      renders = map(self.draw_map,self.draws) # call the draw's
      for img in renders:
        self.display_surface.blit(img,(0,0)) #combine the images

      pygame.display.update() # update the display
      self.clock.tick(FPS) # wait for next frame

  # function wrapper for mapping onto drawables
  def draw_map(self, draw):
    temp_surface = self.display_surface.copy() # copy surface
    img = draw(temp_surface) # call the module's draw
    temp_surface.set_colorkey((0,0,0)) # tell blit to ignore black
    return temp_surface
        
  # add a drawable object to the list     
  def add_module(self, module_draw):
    self.draws.append(module_draw)
