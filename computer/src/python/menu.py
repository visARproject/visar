import cv2
import keyboard
import numpy as np
import PIL
import rendering
import sys
import vispy

from PIL import Image, ImageFont, ImageDraw
from vispy import app, scene
from vispy.color import ColorArray
from vispy.scene.visuals import Text

class Menu():
  def __init__(self):
    self.button_color = (0, 33, 165)
    self.outline_color = (255, 255, 255)

    self.button_texture = np.array([[self.button_color]], np.uint8)
    self.outline_texture = np.array([[self.outline_color]], np.uint8)

    self.list_of_buttons = [] ## temp list of buttons
    self.list_of_buttons.append((Button(""), None)) ## DO NOT REMOVE, use "" as parent for top tier

    ## begin list of buttons here
    self.list_of_buttons.append((Button("Call"), ""))
    self.list_of_buttons.append((Button("Options"), ""))
    self.list_of_buttons.append((Button("Hide All"), ""))
    self.list_of_buttons.append((Button("Menu Button 1"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 2"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 3"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 4"), "Options"))
    self.list_of_buttons.append((Button("Menu Button 1"), "Menu Button 1"))
    self.list_of_buttons.append((Button("Menu Button 2"), "Menu Button 1"))

    for x in range(0, len(self.list_of_buttons)):
      if self.list_of_buttons[x][1] != None:
        for y in range(0, x):
          if self.list_of_buttons[y][0].name == self.list_of_buttons[x][1]:
            self.list_of_buttons[y][0].set_child(self.list_of_buttons[x][0])
            self.list_of_buttons[x][0].parent = self.list_of_buttons[y][0]
            break

    ## assign current tier as children of ""
    for x in self.list_of_buttons:
      if (x[0].parent == None):
        self.current = x[0].children

    ## assign active button as first button in current list
    self.active = self.current[0]
    self.active.active = True

    ## individual button size
    self.button_size = (.2, .1)

    ## gap info
    self.left_gap = .05 ## gap from side
    self.tb_gap = .025 ## gap between buttons

    self.cur_set = [] ## current set of buttons

    self.listOfActives = [] ## Used for keeping track of active buttons while going through options

    ## draw the current set of buttons
    self.draw()

  def draw(self):
    active_check = False ## check if active was already positioned

    ## total height for all the buttons
    total_height = (len(self.current) - 1) * (self.button_size[1] + self.tb_gap) + (2 * self.button_size[1])

    for x in xrange(len(self.current)):
      ## size of the image of the button
      image_size = (400, 100)

      b = self.current[x] ## current button

      ## positioning info for the current button
      active_multi = 1 ## active multiplier
      if b.active:
        top_y = (total_height / 2) - x*(self.button_size[1] + self.tb_gap)
        bottom_y = top_y - (2 * self.button_size[1])
        active_check = True
        active_multi = 2
      elif active_check:
        top_y = (total_height / 2) - x*(self.button_size[1] + self.tb_gap) - self.button_size[1]
        bottom_y = top_y - self.button_size[1]
      else:
        top_y = (total_height / 2) - x*(self.button_size[1] + self.tb_gap)
        bottom_y = top_y - self.button_size[1]
      left_x = -1 + self.left_gap
      right_x = left_x + (self.button_size[0] * active_multi)

      text = b.get_name() ## text for the button

      ## font information for the text
      font_size = 45
      font = ImageFont.truetype("font.ttf", font_size)
      wh = font.getsize(text) ## size of the text in the current font

      ## blank button creation
      img = Image.new("RGBA", image_size, self.button_color)
      draw = ImageDraw.Draw(img)

      ## outline size
      if b.active:
        outline_width = 30
      else:
        outline_width = 15

      ## draw the outline on the blank button
      draw.line((0, 0, 0, image_size[1]), fill = self.outline_color, width = outline_width)
      draw.line((0, 0, image_size[0], 0), fill = self.outline_color, width = outline_width)
      draw.line((image_size[0], 0, image_size[0], image_size[1]), fill = self.outline_color, width = outline_width)
      draw.line((0, image_size[1], image_size[0], image_size[1]), fill = self.outline_color, width = outline_width)

      ## add text to the button (name)
      draw.text((image_size[0]/2 - wh[0]/2, image_size[1]/2 - wh[1]), text, (255,255,255), font=font)
      draw = ImageDraw.Draw(img)

      ## rotate the finished product
      img = np.rot90(img, 3)

      ## draw the current button
      c1 = rendering.Drawable()
      # c2.setVerticies([[left_x, bottom_y], [right_x, bottom_y], [left_x, top_y], [right_x, top_y]])
      c1.setVerticies([[bottom_y, left_x], [bottom_y, right_x], [top_y, left_x], [top_y, right_x]])
      c1.setTexture(img)

      self.cur_set.append(c1) ## add texture to the current set of rendering

  ## unrender the current set
  def unset(self):
    for x in self.cur_set:
      x.pauseRender()

  def change_keys(self, dir):
    if dir == "up": ## go if 'w' is pressed; go up in the list
      self.unset()
      i = self.current.index(self.active)
      if i == 0:
        self.new_active(self.current[len(self.current) - 1])
      else:
        self.new_active(self.current[i - 1])
    elif dir == "down": ## go if 's' is pressed; go down in the list
      self.unset()
      i = self.current.index(self.active)
      if i == len(self.current) - 1:
        self.new_active(self.current[0])
      else:
        self.new_active(self.current[i + 1])
    elif dir == "back": ## go if 'a' is pressed; go back a level
      ## Go if not top tier
      if (self.active.parent.parent != None):
        self.unset()
        grandparent = self.active.parent.parent
        self.current = grandparent.children
        self.new_active(self.listOfActives.pop())
    elif dir == "forward": ## go if 'd' is pressed; 'Select' active button
      ## Go if a child exists for the active button
      if (len(self.active.children) > 0):
        self.unset()
        self.current = self.active.children
        self.listOfActives.append(self.active)
        self.new_active(self.current[0])
    self.draw()

  ## switches active buttons
  def new_active(self, button):
    self.active.active = False
    self.active = button
    self.active.active = True

class Button:
  def __init__(self, name=""):
    self.name = name ## name of button
    self.parent = None ## button that leads to current button
    self.children = [] ## sub-menu that appears when button is pressed
    self.arrow_kids = "" ## concatenate an arrow if children are available
    self.active = False ## true if current button is active, i.e. hovered over

  def set_child(self, child):
    self.children.append(child)

  def get_name(self):
    if len(self.children) > 0:
      return self.name + " >"
    else:
      return self.name