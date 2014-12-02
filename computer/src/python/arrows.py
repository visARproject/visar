import pygame
from pygame.locals import *
import rendering

class Arrows(rendering.Drawable):
  def __init__(self):
    rendering.Drawable.__init__(self)
    self.listOfArrows = []

    locations = [(0, 0, "red"), (1, 0, "blue"), 
      (1, 1, "yellow"), (0, 1, "green"), (.5, 0, "red"),
      (1, .5, "blue"), (.5, 1, "yellow"), (0, .5, "green"),
      (.5, .5, "red")]

    locations = [(0, 0, "red"), (.5, 0, "blue"), (1, 0, "green"),
      (1, .5, "red"), (1, 1, "blue"), (.5, 1, "green"),
      (0, 1, "red"), (0, .5, "blue"), (.5, .5, "yellow")]

    self.arrows = []

    for x in locations:
      self.arrows.append(Arrow(x))

  def update(self, book):
    surface_size = book.eye_size

    self.far_left = 0.05 * surface_size[0]
    self.far_right = surface_size[0] - self.far_left
    self.far_top = 0.05 * surface_size[1]
    self.far_bottom = surface_size[1] - self.far_top

    self.set_draw_target(self.draw(surface_size))

  def draw(self, surface_size):
    surface = pygame.Surface(surface_size)
    listOfRender = []  
    
    for x in self.arrows:
      size = x.getSize()
      surface_width = surface_size[0]
      surface_height = surface_size[1]

      pos_x = float(surface_width * x.getLocation()[0])
      pos_y = float(surface_height * x.getLocation()[1])

      width = 0
      height = 0

      if surface_width < surface_height:
        width = float(size[0] * surface_width / 2)
        height = float(size[1] * surface_width)
      elif surface_width > surface_height:
        width = float(size[0] * surface_height / 2)
        height = float(size[1] * surface_height)

      pos_x -= width / 2
      pos_y -= height

      if pos_y <= self.far_top and pos_x <= self.far_left:
        x.setDir('ul')
        pos_y = self.far_top
        pos_x = self.far_left
      elif pos_y <= self.far_top and pos_x >= self.far_right:
        x.setDir('ur')
        pos_y = self.far_top
        pos_x = self.far_right - width
      elif pos_y >= self.far_bottom and pos_x <= self.far_left:
        x.setDir('bl')
        pos_y = self.far_bottom - height
        pos_x = self.far_left
      elif pos_y >= self.far_bottom and pos_x >= self.far_right:
        x.setDir('br')
        pos_y = self.far_bottom - height
        pos_x = self.far_right - width
      elif pos_y <= self.far_top:
        x.setDir('u')
        pos_y = self.far_top
      elif pos_y >= self.far_bottom:
        pos_y = self.far_bottom - height
      elif pos_x <= self.far_left:
        x.setDir('l')
        pos_x = self.far_left
      elif pos_x >= self.far_right:
        x.setDir('r')
        pos_x = self.far_right - width

      surface.blit(x.getSurface(surface_size), (int(pos_x), int(pos_y)))
      listOfRender.append(rendering.Render_Surface(surface))

      #x.resetDir()

    return listOfRender

class Arrow:
  def __init__(self, information):
    x = information[0]
    y = information[1]
    color = information[2].capitalize()

    self.location = (x, y)

    self.surface = pygame.image.load("images/" + color 
      + "_Arrow.png")

    self.width = .05
    self.height = .05

    self.dir = 'd'

  def getLocation(self):
    return self.location

  def getSize(self):
    return (self.width, self.height)

  def setDir(self, dir):
    self.dir = dir

  def resetDir(self):
    if (self.dir == 'l'):
      self.surface = self.rot_center(self.surface, 90)
    elif (self.dir == 'u'):
      self.surface = self.rot_center(self.surface, 180)
    elif (self.dir == 'r'):
      self.surface = self.rot_center(self.surface, 270)
    elif (self.dir == 'bl'):
      self.surface = self.rot_center(self.surface, 45)
    elif (self.dir == 'ul'):
      self.surface = self.rot_center(self.surface, 135)
    elif (self.dir == 'ur'):
      self.surface = self.rot_center(self.surface, 225)
    elif (self.dir == 'br'):
      self.surface = self.rot_center(self.surface, 315)

    self.dir = 'd'

  def rot_center(self, image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

  def getSurface(self, surface_size):
    width = surface_size[0]
    height = surface_size[1]

    if(width < height):
      height = width
    elif(width > height):
      width = height

    width *= self.width
    height *= self.height

    '''self.surface = pygame.transform.scale(self.surface, 
      (int(width), int(height)))

    if (self.dir == 'l'):
      self.surface = self.rot_center(self.surface, -90)
    elif (self.dir == 'u'):
      self.surface = self.rot_center(self.surface, -180)
    elif (self.dir == 'r'):
      self.surface = self.rot_center(self.surface, -270)
    elif (self.dir == 'bl'):
      self.surface = self.rot_center(self.surface, -45)
    elif (self.dir == 'ul'):
      self.surface = self.rot_center(self.surface, -135)
    elif (self.dir == 'ur'):
      self.surface = self.rot_center(self.surface, -225)
    elif (self.dir == 'br'):
      self.surface = self.rot_center(self.surface, -315)
'''
    return self.surface
