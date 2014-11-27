import pygame
from pygame.locals import *
import rendering

class Arrows(rendering.Drawable):
  def __init__(self):
    self.listOfArrows = []

    locations = [(0, 0.05, "red"), (1, .05, "red"), 
      (1, 1, "red"), (0, 1, "blue"), (0, .5, "green"),
      (.5, .5, "yellow")]

    self.arrows = []

    for x in locations:
      self.arrows.append(Arrow(x))

  def draw(self, surface_size):
    surface = pygame.Surface(surface_size)
    
    for x in self.arrows:
      size = x.getSize()
      surface_width = surface_size[0]
      surface_height = surface_size[1]

      pos_x = float(surface_width * x.getLocation()[0])
      pos_y = float(surface_height * x.getLocation()[1])

      if surface_width < surface_height:
        pos_x -= float(size[0] * surface_width / 2)
        pos_y -= float(size[1] * surface_width)
      elif surface_width > surface_height:
        pos_x -= float(size[0] * surface_height / 2)
        pos_y -= float(size[1] * surface_height)

      surface.blit(x.getSurface(surface_size), (int(pos_x), int(pos_y)))

    return rendering.Render_Surface(surface)    

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

  def getLocation(self):
    return self.location

  def getSize(self):
    return (self.width, self.height)

  def getSurface(self, surface_size):
    width = surface_size[0]
    height = surface_size[1]

    if(width < height):
      height = width
    elif(width > height):
      width = height

    width *= self.width
    height *= self.height

    self.surface = pygame.transform.scale(self.surface, 
      (int(width), int(height)))

    return self.surface