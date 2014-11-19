# define the class that handles the rendering
# individual modules should pass it an object with
#   a draw(surface) method which will return a surface or a Surface_3D
# Surface depth factor (f*b/2*Pxmax*cot(FOV/2)) is also stored in renderer
import pygame
from pygame.locals import *
import numpy as np

FPS = 30 # run at 30FPS or so

# 3D transformation constants defined here
EYE_DISTANCE = .06 # (might be dynamic later? 60mm)
FOCAL_LENGTH = .022 # internet says 22mm for human eyes, confirm later
FOV_DEGREES = 100.0 # display FOV in degrees
FOV_RADIANS = FOV_DEGREES / 180.0 * np.pi # convert to radians
HUD_DEPTH = 3.0 # hud is located at 3m

class Renderer:
  def __init__(self, controller=None, debug=False):
    self.draws_2d = [] # list of draw methods from 2d modules
    self.draws_3d = [] # list of draw methods from 3d modules
    self.controller = controller # controller object for the visAR program 
    # initialize a fullscreen display
    self.display_surface = pygame.display.set_mode((0,0),pygame.FULLSCREEN,0)
    #self.display_surface = pygame.display.set_mode((400,300)) #DEBUG
    self.eye_size = (self.display_surface.get_width()/2, self.display_surface.get_height())
    self.eye_surface = pygame.Surface(self.eye_size) # eye surface template
    if(debug): self.eye_surface = self.display_surface.copy()
    else: self.eye_surface.fill((0,0,0)) # fill with zero
    self.clock = pygame.time.Clock() # timer for fpsing
    self.debug_mode = debug # debug mode only displays left eye
    # define the depth_factor and HUD_offset amount and store in class
    self.depth_factor = (FOCAL_LENGTH * EYE_DISTANCE) / (2.0 * np.tan(FOV_RADIANS/2.0)) * self.eye_size[0]
    self.HUD_offset = int(self.depth_factor / (HUD_DEPTH*HUD_DEPTH) / 2.0)

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
        left, right = img.eye_surfaces(self.depth_factor)
        left_eye.blit(left,(0,0))
        right_eye.blit(right, (0,0))
      
      # get and combine each 2d modules's drawn output, will be drawn at focal depth
      renders = map(self.draw_2d_map,self.draws_2d) # call the draws
      for img in renders:
        # combine the images (both eyes are equal)
        left, right = self.eye_surfaces_2d(img)
        left_eye.blit(left,(0,0))
        right_eye.blit(right,(0,0))

      # debug mode only shows one eye, with no distortion
      if(self.debug_mode):
        self.display_surface.blit(left_eye,(0,0))
        pygame.display.update()
        self.clock.tick(FPS)
        continue

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
  
  # function shifts images to HUD_offset  
  def eye_surfaces_2d(self, img):
    left = img.copy()
    right = img.copy()
    left.scroll(dx=self.HUD_offset)   # move right, dx 
    right.scroll(dx=-self.HUD_offset) # move left, -dx
    return left, right

# class for wrapping around 3d surfaces
class Surface_3D:
  def __init__(self, surface, depth=0):  
    self.surface = surface
    self.depth = depth
    # bound the minimum depth, don't let things inside hud
    if(depth < HUD_DEPTH): depth = HUD_DEPTH
      
  # return the surface for both eyes
  def eye_surfaces(self, depth_factor):
    left = self.surface.copy()
    right = self.surface.copy()
    shift_amt = int(depth_factor / (self.depth*self.depth) / 2.0) # get the shift amount
    left.scroll(dx=shift_amt)   # move right, dx 
    right.scroll(dx=-shift_amt) # move left, -dx
    return left, right
  


