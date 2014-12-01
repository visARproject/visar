# define the class that handles the rendering
# individual modules should pass it an object with
#   a draw(surface) method which will return a surface or a Surface_3D
# Surface depth factor (f*b/2*Pxmax*cot(FOV/2)) is also stored in renderer
import pygame
from pygame.locals import *
import numpy as np
import cv

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
  def do_loop(self, kill_flag):
    pygame.display.set_caption('visAR')
    done = False
    while not kill_flag.is_set(): # main game loop      
      # create new surfaces (one per eye)
      left_eye = self.eye_surface.copy()
      right_eye = self.eye_surface.copy()
      
      # get and combine each modules's drawn output
      draw_map = lambda x: x.get_draw_target() # get the surface
      renders = map(draw_map, self.draws) # call the draws
      
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
        pygame.display.flip()
        self.clock.tick(FPS)
        continue

      # Make the mat headers
      left_mat = Render_Surface(left_eye).get_opencv_mat()
      right_mat = Render_Surface(right_eye).get_opencv_mat()
                  
      # JAKE: DO OCULUS DISTORTION HERE
      
      # retrieve the data from the mats
      left_eye = pygame.image.frombuffer(left_mat.tostring(), cv.GetSize(left_mat),"RGB")
      right_eye = pygame.image.frombuffer(right_mat.tostring(), cv.GetSize(right_mat),"RGB")  
      
      # resize images to output dimensions
      left_eye = pygame.transform.scale(left_eye, self.eye_size)
      right_eye = pygame.transform.scale(right_eye, self.eye_size)          

      # clear the display buffer, then combine the eyes
      self.display_surface.fill((0,0,0))
      self.display_surface.blit(left_eye,(0,0))
      self.display_surface.blit(right_eye,(self.eye_size[0],0))

      pygame.display.update() # update the display
      self.clock.tick(FPS) # wait for next frame
           
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
      
  def copy(self): # deep-copy the render surface
    new_render = Render_Surface(self.surface.copy(), self.position, self.depth)
    new_render.is_3d = self.is_3d # 3d-ness must be set
    return new_render # return the copy
      
  # return the surface for both eyes (debating resizing here vs. in method)
  def draw_eye_surfaces(self, left_eye, right_eye, depth_factor):
    shift_amt = int(depth_factor / (self.depth*self.depth) / 2.0) # get the shift amount
    left_eye.blit(self.surface, (self.position[0]+shift_amt,self.position[1]))  # shift right
    right_eye.blit(self.surface, (self.position[0]-shift_amt,self.position[1])) # shift left
    return left_eye, right_eye
    
  # convert this into an opengl texture (not used, have to rewrite huge portions of code)
  def make_opengl_texture(self):
    # convert to string buffer
    textureData = pygame.image.tostring(self.surface, "RGB", 1)
    width = self.surface.get_width()
    height = self.surface.get_height()
   
    # bind buffer to OpenGL texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGB,
      GL_UNSIGNED_BYTE, textureData)
    return texture
  
  # convert surface to opencv matrix  
  def get_opencv_mat(self):
    surf_data = pygame.image.tostring(self.surface, "RGB") # get the data
    mat = cv.CreateImageHeader(self.surface.get_size(), cv.IPL_DEPTH_8U, 3) # create Mat header
    cv.SetData(mat,surf_data) # set the data
    return mat # return Mat
  

# Drawable class is used by renderer to get surfaces each frame
class Drawable:
  def __init__(self): # setup the lock object and draw_target surface
    self.draw_target = None

  # return the render surfaces, no thread locking
  def get_draw_target(self): 
    return self.draw_target
            
  # set the render surfaces, no thread locking  
  # call this method with updated surfaces
  def set_draw_target(self, render):
    self.draw_target = render.copy() # setting reference is atomic
