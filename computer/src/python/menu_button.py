# define the class that handles menu buttons

import pygame
from pygame.locals import *
import rendering

class Menu(rendering.Drawable):
  def __init__(self):
    listOfButtons = []
    listOfButtons.append((Button(""), None))
    listOfButtons.append((Button("Call"), ""))
    listOfButtons.append((Button("Options"), ""))
    listOfButtons.append((Button("Hide All"), ""))
    listOfButtons.append((Button("Call"), "Options"))

    for x in range(0, len(listOfButtons)):
      if(listOfButtons[x][1] != None):
        for y in range(0, x):
          if(listOfButtons[y][0].getName() == listOfButtons[x][1]):

            listOfButtons[y][0].setChild(listOfButtons[x][0])
            listOfButtons[x][0].setParent(listOfButtons[y][0])
            break

    self.current = []


    for x in listOfButtons:
      if (x[0].getParent() == None):
        self.current = x[0].getChildren()
        break

    self.active = self.current[0]
    self.active.setActive()

    self.lastKeys = None

    self.see = True

  def update(self, book):
    keys = book.keys

    if (keys != self.lastKeys):
      if (keys[K_a]):
        if (self.active.getParent().getParent() != None):
          grandparent = self.active.getParent().getParent()
          self.current = grandparent.getChildren()
          self.newActive(self.current[0])
      elif (keys[K_d]):
        if (len(self.active.getChildren()) > 0):
          self.current = self.active.getChildren()
          self.newActive(self.current[0])
      elif (keys[K_w]):
        i = self.current.index(self.active)
        if i == 0:
          self.newActive(self.current[len(self.current) - 1])
        else:
          self.newActive(self.current[i - 1])
      elif (keys[K_s]):
        i = self.current.index(self.active)
        if i == len(self.current) - 1:
          self.newActive(self.current[0])
        else:
          self.newActive(self.current[i + 1])
      elif (keys[K_q]):
        self.see = False
      elif (keys[K_e]):
        self.see = True

    self.lastKeys = keys

  def draw(self, surface_size):
    surface = pygame.Surface(surface_size)

    if(self.see):
      button_width = int(surface_size[0] * .05)
      button_height = int(surface_size[1] * .05)
      
      gap = surface_size[0] * .01
      align = surface_size[1] * .05

      total_width = button_width
      total_height = (len(self.current) - 1) * (gap + button_height) + (2 * button_height)

      top = int(surface_size[1] / 2) - int(total_height / 2)

      check = False
      
      for x in range(0, len(self.current)):
        y = top + x*(gap + button_height)

        if check:
          y += button_height

        if self.current[x].isActive():
          check = True

        surface.blit(self.current[x].getSurface(button_width, button_height), (align, y))

    return rendering.Render_Surface(surface) # See Josh

  def newActive(self, button):
    self.active.setInactive()
    self.active = button
    self.active.setActive()

class Button:
  def __init__(self, name = "0", size = (2, 1)):
    self.opName = name  
    name = name.replace(" ", "_")
    self.name = "images/" + name + "_Button.png"

    if (name != ""):
      self.surface = pygame.image.load(self.name)
    
    self.width = size[0]
    self.height = size[1]
    self.parent = None
    self.children = []
  
  def setParent(self, parent):
    self.parent = parent

  def getParent(self):
    return self.parent

  def setChild(self, child):
    self.children.append(child)

  def getChildren(self):
    return self.children

  def getName(self):
    return self.opName

  def getSurface(self, width, height):
    self.surface = pygame.image.load(self.name)
    self.surface = pygame.transform.scale(self.surface, (width * self.width, height * self.height))
    return self.surface

  def setActive(self):
    self.name = self.name.replace(".png", "_Selected.png")
    self.width *= 2
    self.height *= 2

  def setInactive(self):
    self.name = self.name.replace("_Selected.png", ".png")
    self.width /= 2
    self.height /= 2

  def isActive(self):
    if self.height > 1:
      return True
    else:
      return False
