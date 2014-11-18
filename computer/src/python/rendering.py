# define the class that handles the rendering
# individual modules should pass it an object with
#   a draw(surface) method which will return a surface or a Surface_3D
import pygame
from pygame.locals import *

FPS = 30 # run at 30FPS or so

class Renderer:
  def __init__(self, controller=None):
    self.draws_2d = [] # list of draw methods from 2d modules
    self.draws_3d = [] # list of draw methods from 3d modules
    self.controller = controller # controller object for the visAR program 
    # initialize a fullscreen display
    self.display_surface = pygame.display.set_mode((0,0),pygame.FULLSCREEN,0)
    #self.display_surface = pygame.display.set_mode((400,300)) #DEBUG
    self.eye_size = (self.display_surface.get_width()/2, self.display_surface.get_height())
    self.eye_surface = pygame.Surface(self.eye_size) # eye surface template
    self.eye_surface.fill((0,0,0)) # fill with zero
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

      # create new surfaces (one per eye)
      left_eye = self.eye_surface.copy()
      right_eye = self.eye_surface.copy()
      
      # get and combine each 3d modules's drawn output      
      renders = map(self.draw_3d_map,self.draws_3d) # call the draws
      for img in renders:
        # combine the images for each eye
        left_eye.blit(img.left_eye_surface(),(0,0))
        right_eye.blit(img.right_eye_surface(), (0,0))
      
      # get and combine each 2d modules's drawn output (draw on top of 3d)
      renders = map(self.draw_2d_map,self.draws_2d) # call the draws
      for img in renders:
        # combine the images (both eyes are equal)
        left_eye.blit(img,(0,0))
        right_eye.blit(img,(0,0))

      # JAKE: DO OCULUS DISTORTION HERE

      # combine the eyes
      self.display_surface.blit(left_eye,(0,0))
      self.display_surface.blit(right_eye,(self.eye_size[0],0))

      pygame.display.update() # update the display
      self.clock.tick(FPS) # wait for next frame

  # function wrapper for mapping onto drawables
  def draw_2d_map(self, draw):
    temp_surface = self.eye_surface.copy() # copy surface
    img = draw(temp_surface) # call the module's draw
    img.set_colorkey((0,0,0)) # tell blit to ignore black
    return img
    
  # function wrapper for mapping 3d drawables
  def draw_3d_map(self, draw):
    temp_surface = self.eye_surface.copy() # copy surface
    surface_3d = draw(temp_surface) # call the module's draw
    surface_3d.surface.set_colorkey((0,0,0)) # tell blit to ignore black
    return surface_3d # return the wrapper
        
  # add a drawable object to the list     
  def add_2d_module(self, module_draw):
    self.draws_2d.append(module_draw)
    
  def add_3d_module(self, module_draw):
    self.draws_3d.append(module_draw)
    


# 3D transformations defined here
EYE_DISTANCE = .06 # (might be dynamic later? 60cm)
FOCAL_LENGTH = 20 # Literally no idea, get from somebody, assume 20m

# class for wrapping around 3d surfaces
class Surface_3D:
  def __init__(self, surface, depth=0):  
    self.surface = surface
    self.depth = depth

    # derived from stereo-vision distance equation
    # Z = f*b/d -> d = f*b/Z, d = 2*shift amount
    if(depth < .001): self.shift_amt = 0; # don't divide by zero, or overdo it
    else: self.shift_amt = int(FOCAL_LENGTH * EYE_DISTANCE / depth / 2)
    print (depth, self.shift_amt)
  
  # return the surface for the left eye (move left, -dx)
  def left_eye_surface(self):
    left = self.surface.copy()
    left.scroll(dx=-self.shift_amt)
    return left
    
  # return the surface for the right eye (move right, dx)
  def right_eye_surface(self):
    right = self.surface.copy()
    right.scroll(dx=self.shift_amt)
    return right
  


