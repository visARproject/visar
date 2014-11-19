# define the class that handles menu buttons

import pygame
from pygame.locals import *

class Menu:
  def __init__(self):
    self.active = None
    self.current = [self.active]

    button0 = Button("Call")
    button1 = Button("Options")
    button2 = Button("Hide All");
    button3 = Button("Call");

    self.active = button2;
    self.current = [button0, button1, button2, button3]

    self.active.setActive()

  def draw(self, surface):
    button_width = int(surface.get_width() * .05)
    button_height = int(surface.get_height() * .05)
    
    gap = surface.get_height() * .01
    align = surface.get_height() * .05

    total_width = button_width
    total_height = (len(self.current) - 1) * (gap + button_height) + (2 * button_height)

    top = int(surface.get_height() / 2) - int(total_height / 2)

    check = False

    for x in range(0, len(self.current)):
      y = top + x*(gap + button_height)

      if check:
        y = y + button_height

      if self.current[x].isActive():
        check = True

      surface.blit(self.current[x].getSurface(button_width, button_height), (align, y))
    return surface

class Button:
  def __init__(self, name = "0", size = (2, 1)):
    name = name.replace(" ", "_")
    self.name = "images/" + name + "_Button.png"
    self.surface = pygame.image.load(self.name)
    self.width = size[0]
    self.height = size[1]
    self.parent = None
    self.children = {}
  
  def setParent(parent):
    self.parent = parent

  def getParent(self):
    return self.parent

  def setChild(child):
    self.children.append(child)

  def getChildren(self):
    return self.children

  def getSurface(self, width, height):
    self.surface = pygame.image.load(self.name)
    self.surface = pygame.transform.scale(self.surface, (width * self.width, height * self.height))
    return self.surface

  def setActive(self):
    self.name = self.name.replace(".png", "_Selected.png")
    self.width = self.width * 2
    self.height = self.height * 2

  def setInactive(self):
    self.name = self.name.replace("_Selected.png", ".png")
    self.width = self.width / 2
    self.height = self.height / 2

  def isActive(self):
    if self.height > 1:
      return True
    else:
      return False