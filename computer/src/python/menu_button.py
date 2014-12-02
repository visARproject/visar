# define the class that handles menu buttons

import pygame
from pygame.locals import *
import rendering

class Menu(rendering.Drawable):
  def __init__(self):
    rendering.Drawable.__init__(self)
    
    #Temporary list of buttons
    #List of tuples (Button:button, String:parent_name)
    self.list_of_buttons = []

    #DO NOT REMOVE, use "" as parent for top tier
    self.list_of_buttons.append((Button(""), None)) 

    #Begin list of buttons here
    self.list_of_buttons.append((Button("Call"), ""))
    self.list_of_buttons.append((Button("Options"), ""))
    self.list_of_buttons.append((Button("Hide All"), ""))
    self.list_of_buttons.append((Button("Menu Button 1"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 2"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 3"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 4"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 1"), "Menu Button 1"))
    self.list_of_buttons.append((Button("Menu Button 2"), "Menu Button 1"))

    #Assigns parents and children using information from list
    for x in range(0, len(self.list_of_buttons)):
      if(self.list_of_buttons[x][1] != None):
        for y in range(0, x):
          if(self.list_of_buttons[y][0].name == self.list_of_buttons[x][1]):
            self.list_of_buttons[y][0].set_child(self.list_of_buttons[x][0])
            self.list_of_buttons[x][0].parent = self.list_of_buttons[y][0]
            break

    self.longest_word_length = 0

    #Assign current tier as children of ""
    for x in self.list_of_buttons:
      if (x[0].parent == None):
        self.current = x[0].children
      if len(x[0].children) > 0:
        if len(x[0].name) + 2 > self.longest_word_length:
          self.longest_word_length = len(x[0].name) + 2
      else:
        if len(x[0].name) > self.longest_word_length:
          self.longest_word_length = len(x[0].name)

    #Assign active button as first button in current list
    self.active = self.current[0]
    self.active.active = True

    #Used as a check for keyboard changes
    self.lastKeys = None

    #Used as a check to allow menu to be visible
    self.see = True

    #Used for keeping track of active buttons while going through options
    self.listOfActives = []

    self.check = True
    self.surface_size = (0, 0)

  def update(self, book):
    if self.check == True:
      self.check = False
      self.surface_size = book.eye_size
      for x in self.list_of_buttons:
        x[0].setup(self.surface_size, self.longest_word_length)

    if self.surface_size != book.eye_size:
      self.surface_size = book.eye_size
      for x in self.list_of_buttons:
        x[0].setup(self.surface_size, self.longest_word_length)
        self.set_draw_target(self.draw(surface_size))

    #Current selection of keyboard keys
    keys = book.keys

    #Go if the current set of keys and the previous set of keys are different
    #i.e. go if pressed (once)
    if (keys != self.lastKeys):
      #Go if 'a' is pressed
      #'Select' active button
      if (keys[K_a]):
        #Go if not top tier
        if (self.active.parent.parent != None):
          grandparent = self.active.parent.parent
          self.current = grandparent.children
          self.new_active(self.listOfActives.pop())
      #Go if 'd' is pressed
      #Go back a level
      elif (keys[K_d]):
        #Go if a child exists for the active button
        if (len(self.active.children) > 0):
          self.current = self.active.children
          self.listOfActives.append(self.active)
          self.new_active(self.current[0])
      #Go if 'w' is pressed
      #Go up in the list
      elif (keys[K_w]):
        i = self.current.index(self.active)
        if i == 0:
          self.new_active(self.current[len(self.current) - 1])
        else:
          self.new_active(self.current[i - 1])
      #Go if 's' is pressed
      #Go down in the list
      elif (keys[K_s]):
        i = self.current.index(self.active)
        if i == len(self.current) - 1:
          self.new_active(self.current[0])
        else:
          self.new_active(self.current[i + 1])
      #Go if 'q' is pressed
      elif (keys[K_q]):
        self.see = False
      #Go if 'e' is pressed
      elif (keys[K_e]):
        self.see = True

      self.set_draw_target(self.draw())

    self.lastKeys = keys

  def draw(self):
    surface = pygame.Surface(self.surface_size)

    if(self.see):
      list_of_render = []

      button_width = self.surface_size[0] * .05
      button_height = self.surface_size[1] * .05

      text_height = button_height * .9
      text_width = button_width * .9
      
      gap = self.surface_size[0] * .01
      align = self.surface_size[1] * .05

      text_left_margin = button_width * .1
      text_top_margin = button_height * .05

      total_width = button_width
      total_height = (len(self.current) - 1) * (gap + button_height) + (2 * button_height)

      top = int(self.surface_size[1] / 2) - int(total_height / 2)

      check = False
      
      for x in range(0, len(self.current)):
        y = top + (x * (gap + button_height))

        if check == True:
          y += button_height

        if self.current[x].active == True:
          check = True

        surface.blit(self.current[x].get_surface(), (align, y))
        surface.blit(self.current[x].get_text(), (align + text_left_margin, y + text_top_margin))
        list_of_render.append(rendering.Render_Surface(surface))

    return list_of_render

  def new_active(self, button):
    self.active.active = False
    self.active = button
    self.active.active = True

class Button:
  def __init__(self, name = ""):
    self.name = name
    self.arrow_kids = ""
    self.width = 2
    self.height = 1
    self.parent = None
    self.children = []
    pygame.font.init()
    self.check = True
    self.font = pygame.font.Font("./font.ttf", 100)
    self.active = False

  def set_child(self, child):
    self.children.append(child)
    if self.check == True:
      self.check = False
      self.arrow_kids = " >"

  def setup(self, surface_size, word_length):
    button_width = surface_size[0] * .05
    button_height = surface_size[1] * .05

    self.surface_inactive = pygame.Surface((int(button_width) * self.width \
    , int(button_height) * self.height))
    self.surface_active = pygame.Surface((int(button_width) * self.width * 2 \
    , int(button_height) * self.height * 2))
    self.surface_active.fill((0, 138, 254))
    self.surface_inactive.fill((0, 35, 63))

    text_height = button_height * .9
    text_width = button_width * .9

    spaces = ""

    if self.arrow_kids == "":
      i = word_length - len(self.name)
      while i > 0:
        spaces += " "
        i -= 1
    else:
      i = word_length - len(self.name) - 2
      while i > 0:
        spaces += " "
        i -= 1

    self.text = self.font.render(self.name + self.arrow_kids + spaces, True, (1, 1, 1))
    self.text_inactive = pygame.transform.scale(self.text, (int(text_width) * self.width \
    , int(text_height) * self.height))
    self.text_active = pygame.transform.scale(self.text, (int(text_width) * self.width * 2 \
    , int(text_height) * self.height * 2))
  
  def get_text(self):
    if self.active == True:
      return self.text_active
    else:
      return self.text_inactive

  def get_surface(self):
    if self.active == True:
      return self.surface_active
    else:
      return self.surface_inactive