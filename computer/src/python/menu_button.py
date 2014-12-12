## define the class that handles menu buttons
## extra # is comment

import pygame
from pygame.locals import *
import rendering

class Menu(rendering.Drawable):
  def __init__(self):
    rendering.Drawable.__init__(self) ## Call super class init

    self.list_of_buttons = [] ## Temporary list of buttons; List of tuples (Button:button, String:parent_name)

    self.list_of_buttons.append((Button(""), None)) ## DO NOT REMOVE, use "" as parent for top tier

    ## Begin list of buttons here
    self.list_of_buttons.append((Button("Call"), ""))
    self.list_of_buttons.append((Button("Options"), ""))
    self.list_of_buttons.append((Button("Hide All"), ""))
    self.list_of_buttons.append((Button("Menu Button 1"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 2"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 3"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 4"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 1"), "Menu Button 1"))
    self.list_of_buttons.append((Button("Menu Button 2"), "Menu Button 1"))

    for x in range(0, len(self.list_of_buttons)): ## Assigns parents and children using information from list
      if self.list_of_buttons[x][1] != None : ## Look for top tier
        for y in range(0, x): ## Once found, find children
          if self.list_of_buttons[y][0].name == self.list_of_buttons[x][1]: 
            self.list_of_buttons[y][0].set_child(self.list_of_buttons[x][0])
            self.list_of_buttons[x][0].parent = self.list_of_buttons[y][0]
            break

    self.longest_word_length = 0 ## Longest number of chars in button title

    ## Assign current tier as children of ""
    for x in self.list_of_buttons:
      if (x[0].parent == None):
        self.current = x[0].children
      if len(x[0].children) > 0:
        if len(x[0].name) + 2 > self.longest_word_length:
          self.longest_word_length = len(x[0].name) + 2
      else:
        if len(x[0].name) > self.longest_word_length:
          self.longest_word_length = len(x[0].name)

    ## Assign active button as first button in current list
    self.active = self.current[0]
    self.active.active = True

    self.lastKeys = None ## Used as a check for keyboard changes

    self.see = True ## Used as a check to allow menu to be visible

    self.listOfActives = [] ## Used for keeping track of active buttons while going through options

    self.check = True ## Used as a check for first run through
    
    self.screen_width = 0 ## Init screen width to 0
    self.screen_height = 0 ## Init screen height to 0
    self.screen_size = (self.screen_width, self.screen_height) ## Init screen size to 0

    self.button_size_per = .05 ## Percent of screen for button, relative to width and height
    self.inner_surface_size_per = self.button_size_per * .9 ## Perecent of screen for inner button
    self.inner_surface_mar_per = self.button_size_per * .05 ## Percent of screen for inner margin
    self.gap_x_per = .05 ## Percent of screen width for button indentation
    self.gap_y_per = .01 ## Percent of screen height for gap between buttons
    self.text_size_per = self.inner_surface_size_per * .9 ## Percent of screen for text
    self.text_mar_per = self.inner_surface_size_per * .05 ## Percent of screen for text margins in button

    self.width_ratio = 2
    self.height_ratio = 1

  ## Used as update function
  def update(self, book):
    ## If first run through
    if self.check == True:
      self.check = False ## Set as false, i.e. never come back here after beginning
      self.screen_width = book.eye_size[0] ## Set width of screen
      self.screen_height = book.eye_size[1] ## Set height of screen
      self.screen_size = book.eye_size ## Set size of screen
      for x in self.list_of_buttons: ## Run through buttons and set them up correctly
        x[0].setup(self.screen_size, self.longest_word_length, self.button_size_per, \
          self.inner_surface_size_per, self.text_size_per)
      self.set_draw_target(self.draw()) ## Draw objects


    ## Run any time the screen size changes
    if self.screen_size != book.eye_size:
      self.screen_width = book.eye_size[0] ## Set width of screen
      self.screen_height = book.eye_size[1] ## Set height of screen
      self.screen_size = book.eye_size ## Set size of screen
      for x in self.list_of_buttons: ## Run through the buttons and set up buttons again
        x[0].setup(self.screen_size, self.longest_word_length, self.button_size_per, \
          self.inner_surface_size_per, self.text_size_per, self.width_ratio)
      self.set_draw_target(self.draw()) ## Draw Objects

    ## Current selection of keyboard keys
    keys = book.keys

    ## Go if the current set of keys and the previous set of keys are different
    ## i.e. go if pressed (once)
    if (keys != self.lastKeys):
      ## Go if 'a' is pressed
      ## Go back a level
      if (keys[K_a]):
        ## Go if not top tier
        if (self.active.parent.parent != None):
          grandparent = self.active.parent.parent
          self.current = grandparent.children
          self.new_active(self.listOfActives.pop())
      ## Go if 'd' is pressed
      ## 'Select' active button
      elif (keys[K_d]):
        ## Go if a child exists for the active button
        if (len(self.active.children) > 0):
          self.current = self.active.children
          self.listOfActives.append(self.active)
          self.new_active(self.current[0])
      ## Go if 'w' is pressed
      ## Go up in the list
      elif (keys[K_w]):
        i = self.current.index(self.active)
        if i == 0:
          self.new_active(self.current[len(self.current) - 1])
        else:
          self.new_active(self.current[i - 1])
      ## Go if 's' is pressed
      ## Go down in the list
      elif (keys[K_s]):
        i = self.current.index(self.active)
        if i == len(self.current) - 1:
          self.new_active(self.current[0])
        else:
          self.new_active(self.current[i + 1])
      ## Go if 'q' is pressed
      ## Hide list
      elif (keys[K_q]):
        self.see = False
      ## Go if 'e' is pressed
      ## Present lists, if hidden
      elif (keys[K_e]):
        self.see = True

      ## Draw Objects
      self.set_draw_target(self.draw())

    ## Set keys to current set
    self.lastKeys = keys

  ## Used to draw buttons
  def draw(self):
    ## Init surface as screen
    surface = pygame.Surface(self.screen_size)

    ## List of buttons that need to be rendered
    list_of_render = []

    ## If the list is not hidden
    if(self.see):
      button_width = self.screen_width * self.button_size_per ## Button width
      button_height = self.screen_height * self.button_size_per ## Button height

      gap_x = self.screen_width * self.gap_x_per ## Button indentation
      gap_y = self.screen_height * self.gap_y_per ## Gap between buttons

      inner_left_margin = self.screen_width * self.inner_surface_mar_per * self.width_ratio ## 'Center' inner horizontally
      inner_top_margin = self.screen_height * self.inner_surface_mar_per * self.height_ratio## 'Center' inner vertically

      text_left_margin = self.screen_width * self.text_mar_per * self.width_ratio ## 'Center' text horizontally
      text_top_margin = self.screen_height * self.text_mar_per * self.height_ratio ## 'Center' text vertically

      total_width = button_width ## Width of returning surface
      total_height = (len(self.current) - 1) * (gap_y + button_height) + (2 * button_height) ## Height of returning surface

      top = int(self.screen_height / 2) - int(total_height / 2) ## Top position of buttons

      active_check = False ## Check if active button has been passed
      
      ## Run through current buttons and render them
      for x in range(0, len(self.current)):
        ## Find y_position of button
        y = top + (x * (gap_y + button_height))

        if active_check == True:
          y += button_height

        if self.current[x].active == True:
          surface.blit(self.current[x].get_surface(), (gap_x, y)) ## Position button
          surface.blit(self.current[x].get_inner(), (gap_x + (inner_left_margin * 2) \
          , y + (inner_top_margin * 2))) ## Position inner
          surface.blit(self.current[x].get_text(), (gap_x + (inner_left_margin * 2) + (text_left_margin * 2) \
          , y + (inner_top_margin * 2) + (text_top_margin * 2))) ## Position text in button
          active_check = True
        else:
          surface.blit(self.current[x].get_surface(), (gap_x, y)) ## Position button
          surface.blit(self.current[x].get_inner(), (gap_x + inner_left_margin, y + inner_top_margin)) ## Position inner
          surface.blit(self.current[x].get_text(), (gap_x + inner_left_margin + text_left_margin \
          , y + inner_top_margin + text_top_margin)) ## Position text in button
        
        list_of_render.append(rendering.Render_Surface(surface)) ## Append current button

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

  def setup(self, screen_size, word_length, outer_per, inner_per, text_per):
    outer_color = (0, 33, 165)
    inner_color = (255, 255, 255)

    button_width = screen_size[0] * outer_per
    button_height = screen_size[1] * outer_per

    self.surface_inactive = pygame.Surface((int(button_width * self.width) \
    , int(button_height * self.height)))
    self.surface_active = pygame.Surface((int(button_width * self.width) * 2 \
    , int(button_height * self.height) * 2))
    self.surface_active.fill(inner_color)
    self.surface_inactive.fill(inner_color)

    inner_width = screen_size[0] * inner_per
    inner_height = screen_size[1] * inner_per

    self.inner_inactive = pygame.Surface((int(inner_width * self.width) \
    , int(inner_height * self.height)))
    self.inner_active = pygame.Surface((int(inner_width * self.width) * 2 \
    , int(inner_height * self.height) * 2))
    self.inner_active.fill(outer_color)
    self.inner_inactive.fill(outer_color)

    text_width = screen_size[0] * text_per
    text_height = screen_size[1] * text_per

    spaces = ""

    i = word_length - len(self.name) - len(self.arrow_kids)
    while i > 0:
      spaces += " "
      i -= 1

    self.text = self.font.render(self.name + self.arrow_kids + spaces, True, inner_color)
    self.text_inactive = pygame.transform.scale(self.text, (int(text_width * self.width) \
    , int(text_height * self.height)))
    self.text_active = pygame.transform.scale(self.text, (int(text_width * self.width) * 2 \
    , int(text_height * self.height) * 2))
  
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

  def get_inner(self):
    if self.active == True:
      return self.inner_active
    else:
      return self.inner_inactive