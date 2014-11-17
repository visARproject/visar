# define the class that handles menu buttons

import pygame
from pygame.locals import *

class Menu:
  def __init__(self):
    self.button = Button("Call_Button")

  def draw(self, surface):
    surface.blit(self.button.getSurface(), (200,200))
    return surface

class Button:
  def __init__(self, name = "0"):
    self.name = "images/" + name + ".png"
    self.surface = pygame.image.load(self.name)
  
  def getSurface(self):
    return self.surface