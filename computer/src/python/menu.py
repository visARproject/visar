import keyboard
import numpy as np
import PIL
import rendering
import sys
import vispy
import xml.etree.ElementTree as ET

from PIL import Image, ImageFont, ImageDraw
from vispy import app, scene
from vispy.util.transforms import translate, scale

class Menu():
  def __init__(self):
    self.button_color = (0, 33, 165) ## gator blue
    self.outline_color = (255, 255, 255) ## white

    ## xml tree
    tree = ET.parse('menu_buttons.xml')

    ## root button
    root_xml = tree.getroot()
    self.root_button = None

    ## individual button size
    self.button_size = (.2, .1)

    ## default vertex locations for inactive buttons
    self.init_left_x_inactive = -(self.button_size[0] / 2)
    self.init_right_x_inactive = self.button_size[0] / 2
    self.init_bottom_y_inactive = -(self.button_size[1] / 2)
    self.init_top_y_inactive = self.button_size[1] / 2

    ## default vertex locations for inactive buttons
    self.init_left_x_active = -(self.button_size[0])
    self.init_right_x_active = self.button_size[0]
    self.init_bottom_y_active = -(self.button_size[1])
    self.init_top_y_active = self.button_size[1]

    ## gap info
    self.left_gap = .05 ## gap from side
    self.tb_gap = .025 ## gap between buttons

    self.listOfActives = [] ## Used for keeping track of active buttons while going through options

    ## creates each button
    self.setup(None, xml_node=root_xml)

    ## assign current tier as children of ""
    self.current = self.root_button.children

    ## assume the top button is being hovered over
    self.active = self.current[0]

    ## draw only the top layer menu
    for x in self.current:
      x.render.resumeRender()

    ## move buttons to correct place
    self.move()

  ## create placement of buttons
  def setup(self, parent_node, xml_node=None, text=None):
    ## place buttons default in the center
    pos = [[self.init_left_x_inactive, self.init_bottom_y_inactive]
    , [self.init_left_x_inactive, self.init_top_y_inactive]
    , [self.init_right_x_inactive, self.init_bottom_y_inactive]
    , [self.init_right_x_inactive, self.init_top_y_inactive]]

    ## text is used primarily to put in a back button
    if text != None:
      img = self.tex(name=text) ## get the texture of the button
      b = Button(text, parent_node, img, pos, False) ## create button instance
      parent_node.set_child(b) ## add current button to parent's child list
    else:
      img = self.tex(xml_node=xml_node) ## get the texture of the button
      b = Button(xml_node.get('name'), parent_node, img, pos, xml_node.get('function')) ## create button instance
      if xml_node.get('name') == "":
        self.root_button = b ## set root button as such
      else:
        parent_node.set_child(b) ## add current button to parent's child list

      ## recursively go through all of the children
      for child in xml_node:
        self.setup(b, xml_node=child) 

      ## setup back button
      if parent_node != None and len(xml_node) > 0:
        self.setup(b, text="< Back")

  ## create the texture for the button
  def tex(self, xml_node=None, name=None):
    if name == None:
      children_count = len(xml_node)
      if children_count > 0:
        text = xml_node.get('name') + " >"
      else:
        text = xml_node.get('name')
    else:
      text = name

    image_size = [400, 100] ## size of the image of the button
    outline_width = 10
    inner_size = [image_size[0] - outline_width, image_size[1] - outline_width]

    ## blank button creation (eventually the outline)
    img = Image.new("RGBA", image_size, self.outline_color)
    draw = ImageDraw.Draw(img)

    ## draw inner color
    x0 = outline_width
    y0 = outline_width
    x1 = inner_size[0]
    y1 = inner_size[1]
    draw.rectangle([x0, y0, x1, y1], fill=self.button_color)

    ## add text only if not root button
    if text != "":
      ## font information for the text
      font_size = 1
      f = ImageFont.FreeTypeFont("font.ttf", font_size)
      y = f.getoffset(text)[1]
      wh = f.getsize(text) ## size of the text in the current font

      while (wh[0] < inner_size[0] - outline_width) and (wh[1] < inner_size[1] - outline_width - y):
        font_size += 1
        f = ImageFont.FreeTypeFont("font.ttf", font_size)
        y = f.getoffset(text)[1]
        wh = f.getsize(text) ## size of the text in the current font

      font_size -= 2
      f = ImageFont.FreeTypeFont("font.ttf", font_size)
      y = f.getoffset(text)[1]
      wh = f.getsize(text) ## size of the text in the current font

      ## calculate top-left corner of text in order to center it
      tx = ((outline_width + inner_size[0]) / 2) - wh[0]/2
      ty = ((outline_width + inner_size[1] - 2*y) / 2) - wh[1]/2

      ## add text to the button (name)
      draw.text([tx, ty], text, self.outline_color, font=f)

    ## rotate the finished product
    img = img.rotate(180)
    img = img.transpose(PIL.Image.FLIP_LEFT_RIGHT)

    return img

  ## moves the current set of buttons to the correct place
  def move(self):
    ## total height for all the buttons
    total_height = (len(self.current) - 1) * (self.button_size[1] + self.tb_gap) + (2 * self.button_size[1])

    active_check = False

    for x in xrange(len(self.current)):
      b = self.current[x] ## current button

      ## positioning info for the current button
      ## note: active buttons have twice the height and width as normal buttons
      active_multi = 1 ## active multiplier
      if self.active.path == b.path:
        top_y = (total_height / 2) - x * (self.button_size[1] + self.tb_gap)
        bottom_y = top_y - (2 * self.button_size[1])
        active_check = True
        active_multi = 2
      elif active_check:
        top_y = (total_height / 2) - x * (self.button_size[1] + self.tb_gap) - self.button_size[1]
        bottom_y = top_y - self.button_size[1]
      else:
        top_y = (total_height / 2) - x * (self.button_size[1] + self.tb_gap)
        bottom_y = top_y - self.button_size[1]
      left_x = -1 + self.left_gap
      right_x = left_x + (self.button_size[0] * active_multi)

      ## calculate the difference between where the buttons should be and the initial positions
      if active_multi == 2:
        diff_x = left_x - self.init_left_x_active
        diff_y = top_y - self.init_top_y_active
      else:
        diff_x = left_x - self.init_left_x_inactive
        diff_y = top_y - self.init_top_y_inactive

      b.move_button(diff_x, diff_y, active_multi)

  def key_stuff(self, event, direction):
    if direction == "down":
      if event.text == "w":
        self.change_keys("up")
      elif event.text == "s":
        self.change_keys("down")
      elif event.text == "a":
        self.change_keys("back")
      elif event.text == "d":
        self.change_keys("forward")

  def change_keys(self, dir):
    if dir == "up": ## go if 'w' is pressed; go up in the list
      i = self.current.index(self.active)
      if i == 0:
        self.active = self.current[len(self.current) - 1]
      else:
        self.active = self.current[i - 1]
    elif dir == "down": ## go if 's' is pressed; go down in the list
      i = self.current.index(self.active)
      if i == len(self.current) - 1:
        self.active = self.current[0]
      else:
        self.active = self.current[i + 1]
    elif dir == "back": ## go if 'a' is pressed; go back a level
      ## Go if not top tier
      if (self.active.parent.parent != None):
        self.pause()
        grandparent = self.active.parent.parent
        self.current = grandparent.children
        self.active = self.listOfActives.pop()
        self.resume()
    elif dir == "forward": ## go if 'd' is pressed; 'Select' active button
      ## Go if a child exists for the active button
      if (len(self.active.children) > 0):
        self.pause()
        self.current = self.active.children
        self.listOfActives.append(self.active)
        self.active = self.current[0]
        self.resume()
      elif self.active.functional:
        print self.active.name, "was pressed!"
    self.move()

  ## pause the current menu
  def pause(self):
    for x in self.current:
      x.render.pauseRender()

  ## resume the current menu
  def resume(self):
    for x in self.current:
      x.render.resumeRender()

class Button:
  def __init__(self, name, parent, tex, verts, functional):
    self.name = name ## the button's name
    self.children = [] ## sub-menu that appears when button is pressed
    self.parent = parent ## button that leads to current button
    self.functional = functional
    self.path = [self.name] ## create a path to the button

    if parent != None:
      self.path.extend(parent.path)

    self.render = rendering.Drawable(verticies=verts, tex_data=tex, start=False) ## set up render

  def set_child(self, child):
    self.children.append(child)
    
  def move_button(self, diff_x, diff_y, s):
    a = np.eye(4)
    scale(a, s) ## scale by some 's'
    translate(a, diff_x, diff_y) ## translate button by some 'x' and 'y'
    self.render.setPosition(a)