# define the class that handles menu buttons

import pygame
from pygame.locals import *
import rendering

class Menu(rendering.Drawable):
  def __init__(self):
    rendering.Drawable.__init__(self)
    
    #Temporary list of buttons
    #List of tuples (Button:button, String:parent_name)
    listOfButtons = []

    #DO NOT REMOVE, use "" as parent for top tier
    listOfButtons.append((Button(""), None)) 

    #Begin list of buttons here
    listOfButtons.append((Button("Call"), ""))
    listOfButtons.append((Button("Options"), ""))
    listOfButtons.append((Button("Hide All"), ""))
    listOfButtons.append((Button("Menu Button 1"), "Options"))
    listOfButtons.append((Button("Menu Button 2"), "Options"))
    listOfButtons.append((Button("Menu Button 3"), "Options"))
    listOfButtons.append((Button("Menu Button 4"), "Options"))
    listOfButtons.append((Button("Menu Button 1"), "Menu Button 1"))
    listOfButtons.append((Button("Menu Button 2"), "Menu Button 1"))

    #Assigns parents and children using information from list
    for x in range(0, len(listOfButtons)):
      if(listOfButtons[x][1] != None):
        for y in range(0, x):
          if(listOfButtons[y][0].getName() == listOfButtons[x][1]):
            listOfButtons[y][0].setChild(listOfButtons[x][0])
            listOfButtons[x][0].setParent(listOfButtons[y][0])
            break

    #Assign current tier as children of ""
    for x in listOfButtons:
      if (x[0].getParent() == None):
        self.current = x[0].getChildren()
        break

    #Assign active button as first button in current list
    self.active = self.current[0]
    self.active.setActive()

    #Used as a check for keyboard changes
    self.lastKeys = None

    #Used as a check to allow menu to be visible
    self.see = True

    #Used for keeping track of active buttons while going through options
    self.listOfActives = []

  def update(self, book):
    #Current selection of keyboard keys
    keys = book.keys

    surface_size = book.eye_size

    #Go if the current set of keys and the previous set of keys are different
    #i.e. go if pressed (once)
    if (keys != self.lastKeys):
      #Go if 'a' is pressed
      #'Select' active button
      if (keys[K_a]):
        #Go if not top tier
        if (self.active.getParent().getParent() != None):
          grandparent = self.active.getParent().getParent()
          self.current = grandparent.getChildren()
          self.newActive(self.listOfActives.pop())
      #Go if 'd' is pressed
      #Go back a level
      elif (keys[K_d]):
        #Go if a child exists for the active button
        if (len(self.active.getChildren()) > 0):
          self.current = self.active.getChildren()
          self.listOfActives.append(self.active)
          self.newActive(self.current[0])
      #Go if 'w' is pressed
      #Go up in the list
      elif (keys[K_w]):
        i = self.current.index(self.active)
        if i == 0:
          self.newActive(self.current[len(self.current) - 1])
        else:
          self.newActive(self.current[i - 1])
      #Go if 's' is pressed
      #Go down in the list
      elif (keys[K_s]):
        i = self.current.index(self.active)
        if i == len(self.current) - 1:
          self.newActive(self.current[0])
        else:
          self.newActive(self.current[i + 1])
      #Go if 'q' is pressed
      elif (keys[K_q]):
        self.see = False
      #Go if 'e' is pressed
      elif (keys[K_e]):
        self.see = True

    self.lastKeys = keys

    self.set_draw_target(self.draw(surface_size))

  def draw(self, surface_size):
    surface = pygame.Surface(surface_size)

    if(self.see):
      listOfRender = []

      button_width = surface_size[0] * .05
      button_height = surface_size[1] * .05

      text_height = button_height * .9
      text_width = button_width * .6
      
      gap = surface_size[0] * .01
      align = surface_size[1] * .05

      text_left_margin = button_width * .1
      text_top_margin = button_height * .05

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
        surface.blit(self.current[x].getText(text_width, text_height),
         (align + text_left_margin, y + text_top_margin))
        listOfRender.append(rendering.Render_Surface(surface))

    return listOfRender

  def newActive(self, button):
    self.active.setInactive()
    self.active = button
    self.active.setActive()

class Button:
  def __init__(self, name = ""):
    self.name = name
    self.width = 2
    self.height = 1
    self.parent = None
    self.children = []
    pygame.font.init()
  
  def setParent(self, parent):
    self.parent = parent

  def getParent(self):
    return self.parent

  def setChild(self, child):
    self.children.append(child)

  def getChildren(self):
    return self.children

  def hasChildren(self):
    if (len(self.children) > 0):
      return True
    return False

  def getName(self):
    return self.name

  def getText(self, width, height):
    font = pygame.font.Font(None, 100)
    if(self.hasChildren()):
      self.text = font.render(self.name + " >", True, (1, 1, 1))
    else:
      self.text = font.render(self.name, True, (1, 1, 1))
    self.text = pygame.transform.scale(self.text, (int(width) * self.width, int(height) * self.height))
    return self.text

  def getSurface(self, width, height):
    surface = pygame.Surface((int(width) * self.width, int(height) * self.height))
    if self.isActive():
      surface.fill((0, 138, 254))
    else:
      surface.fill((0, 35, 63))
    return surface

  def getMoreBox(self, width, height):
    moreBox = pygame.Surface((int(width) * self.width, int(height) * self.height))
    moreBox.fill((1, 1, 1))
    return moreBox

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
