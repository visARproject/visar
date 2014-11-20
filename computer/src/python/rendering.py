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
HUD_DEPTH = 1.5 # hud is located at 3m

class Renderer:
  def __init__(self, controller=None, debug=False):
    self.draws = [] # List of drawable objects to be rendered each frame
    self.controller = controller # controller object for the visAR program 
    # initialize a fullscreen display
    self.display_surface = pygame.display.set_mode((0,0),pygame.FULLSCREEN,0)
    #self.display_surface = pygame.display.set_mode((400,300)) #DEBUG
    if(debug): self.eye_size = (self.display_surface.get_width(), self.display_surface.get_height())
    else: self.eye_size = (self.display_surface.get_width()/2, self.display_surface.get_height())
    self.eye_surface = pygame.Surface(self.eye_size) # eye surface template
    self.eye_surface.fill((0,0,0)) # fill with zero
    self.clock = pygame.time.Clock() # timer for fpsing
    self.debug_mode = debug # debug mode only displays left eye
    # define the depth_factor and HUD_offset amount and store in class
    self.depth_factor = (FOCAL_LENGTH * EYE_DISTANCE) / (2.0 * np.tan(FOV_RADIANS/2.0)) * self.eye_size[0]

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
      
      # get and combine each modules's drawn output      
      renders = map(self.draw_map,self.draws) # call the draws
      
      # draw 3d surfaces first
      for module in renders:
        # combine the images for each eye
        if(type(module) is list): # module returned list
          for surface in module: # draw each surface
            if(surface.is_3d): # only draw 3D objects here
              surface.draw_eye_surfaces(left_eye, right_eye, self.depth_factor)
        elif(module.is_3d):  # single surface, draw if 3D
          module.draw_eye_surfaces(left_eye, right_eye, self.depth_factor)
        
      # draw 2d surfaces second
      for module in renders:
        # combine the images for each eye
        if(type(module) is list): # module returned list
          for surface in module: # draw each surface
            if(not surface.is_3d): # only draw 3D objects here
              surface.draw_eye_surfaces(left_eye, right_eye, self.depth_factor)
        elif(not module.is_3d):  # single surface, draw if 3D
          module.draw_eye_surfaces(left_eye, right_eye, self.depth_factor)
      
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
  def draw_map(self, drawable):
    img = drawable.draw(self.eye_size) # call the module's draw
    return img
           
  # add a drawable object to the list     
  def add_module(self, module):
    self.draws.append(module)
  
  # function shifts images to HUD_offset  
  def eye_surfaces_2d(self, img):
    left = img.copy()
    right = img.copy()
    left.scroll(dx=self.HUD_offset)   # move right, dx 
    right.scroll(dx=-self.HUD_offset) # move left, -dx
    return left, right

# class for wrapping around 3d surfaces
class Render_Surface:
  def __init__(self, surface, position=(0,0),depth=0):  
    self.surface = surface
    self.surface.set_colorkey((0,0,0)) # make sure this is set to black
    self.depth = depth
    self.position = position
    if(depth == 0): self.is_3d = False
    else: self.is_3d = True
    # bound the minimum depth, don't let things inside hud
    if(depth < HUD_DEPTH): self.depth = HUD_DEPTH
      
  # return the surface for both eyes (debating resizing here vs. in method)
  def draw_eye_surfaces(self, left_eye, right_eye, depth_factor):
    shift_amt = int(depth_factor / (self.depth*self.depth) / 2.0) # get the shift amount
    left_eye.blit(self.surface, (self.position[0]+shift_amt,self.position[1]))  # shift right
    right_eye.blit(self.surface, (self.position[0]-shift_amt,self.position[1])) # shift left
    return left_eye, right_eye
  

# Drawable class is used by renderer to get surfaces each frame
class Drawable:
  # def __init__(self): # currently unused, might add things later

  # draw method must be overloaded for each drawable
  #   should return either a Render_Surface or a list of them
  def draw(self, screen_size):
    return None




