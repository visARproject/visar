import pygame
from pygame.locals import *
import rendering
import math

class Arrows(rendering.Drawable):
  def __init__(self):
    rendering.Drawable.__init__(self)

    arrows = []
    list_of_red_arrows = self.get_arrows("Red")
    list_of_green_arrows = self.get_arrows("Green")
    list_of_blue_arrows = self.get_arrows("Blue")
    list_of_yellow_arrows = self.get_arrows("Yellow")

    self.list_of_arrows = []
    self.list_of_arrows.append(["Red", list_of_red_arrows])
    self.list_of_arrows.append(["Green", list_of_green_arrows])
    self.list_of_arrows.append(["Blue", list_of_blue_arrows])
    self.list_of_arrows.append(["Yellow", list_of_yellow_arrows])

    self.check = True
    self.surface_size = (0, 0)
    self.image_size = 0.1

  def get_arrows(self, color):
    color = color.lower()
    color = color.capitalize()
    surface = pygame.image.load("images/" + color 
      + "_Arrow.png")
    list_of_arrows = []
    list_of_arrows.append(['b', surface])
    list_of_arrows.append(['bl', self.rot_center(surface, -45)])
    list_of_arrows.append(['l', self.rot_center(surface, -90)])
    list_of_arrows.append(['ul', self.rot_center(surface, -135)])
    list_of_arrows.append(['u', self.rot_center(surface, -180)])
    list_of_arrows.append(['ur', self.rot_center(surface, -225)])
    list_of_arrows.append(['r', self.rot_center(surface, -270)])
    list_of_arrows.append(['br', self.rot_center(surface, -315)])

    return list_of_arrows

  def rot_center(self, image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

  def get_actual_image_size(self):
    if self.surface_size[0] >= self.surface_size[1]:
      return int(self.surface_size[1] * self.image_size)
    else:
      return int(self.surface_size[0] * self.image_size)

  def set_size(self):
    for x in self.list_of_arrows:
      for y in x[1]:
        size = self.get_actual_image_size()
        y[1] = pygame.transform.scale(y[1], (size, size))

  def update(self, book):
    if self.check == True:
      self.check = False

      self.surface_size = book.eye_size

      self.far_left = 0.05 * self.surface_size[0]
      self.far_right = self.surface_size[0] - self.far_left
      self.far_top = 0.05 * self.surface_size[1]
      self.far_bottom = self.surface_size[1] - self.far_top

      temp = book.arrow_locations

      self.set_size()
      self.arrows = []

      for x in temp:
        self.arrows.append(Arrow(x, self.list_of_arrows))

      self.set_draw_target(self.draw())

    else:
      if self.surface_size != book.eye_size:
        self.surface_size = book.eye_size

        self.far_left = 0.05 * self.surface_size[0]
        self.far_right = self.surface_size[0] - self.far_left
        self.far_top = 0.05 * self.surface_size[1]
        self.far_bottom = self.surface_size[1] - self.far_top

        self.set_size()
        self.set_draw_target(self.draw())
      temp = book.arrow_locations

      if len(temp) != len(self.arrows):
        self.arrows = []
        for x in temp:
          self.arrows.append(Arrow(x, self.list_of_arrows))

        self.set_draw_target(self.draw())
      else:
        a = True
        for x in range(0, len(temp)):
          location = self.arrows[x].location
          if (location[0] != temp[x][0]) \
          or (location[1] != temp[x][1]):
            a = False
            break
        if a == False:
          self.arrows = []
          for x in temp:
            self.arrows.append(Arrow(x, self.list_of_arrows))

          self.set_draw_target(self.draw())

  def draw(self):
    surface = pygame.Surface(self.surface_size)
    list_of_render = []  
    
    for x in self.arrows:
      pos_x = float(self.surface_size[0] * x.location[0])
      pos_y = float(self.surface_size[1] * x.location[1])
      size = self.get_actual_image_size()
      
      pos_x -= size / 2
      pos_y -= size

      if pos_y <= self.far_top and pos_x <= self.far_left:
        x.set_dir('ul')
        pos_y = self.far_top
        pos_x = self.far_left
      elif pos_y <= self.far_top and pos_x >= self.far_right:
        x.set_dir('ur')
        pos_y = self.far_top
        pos_x = self.far_right - size
      elif pos_y >= self.far_bottom and pos_x <= self.far_left:
        x.set_dir('bl')
        pos_y = self.far_bottom - size
        pos_x = self.far_left
      elif pos_y >= self.far_bottom and pos_x >= self.far_right:
        x.set_dir('br')
        pos_y = self.far_bottom - size
        pos_x = self.far_right - size
      elif pos_y <= self.far_top:
        x.set_dir('u')
        pos_y = self.far_top
      elif pos_y >= self.far_bottom:
        x.set_dir('b')
        pos_y = self.far_bottom - size
      elif pos_x <= self.far_left:
        x.set_dir('l')
        pos_x = self.far_left
      elif pos_x >= self.far_right:
        x.set_dir('r')
        pos_x = self.far_right - size

      surface.blit(x.get_surface(self.surface_size), (int(pos_x), int(pos_y)))
      list_of_render.append(rendering.Render_Surface(surface))

    return list_of_render

  def get_points(self, book):
    points = book.points
    surface_size = book.eye_size
    width = surface_size[0]
    height = surface_size[1]

    aspect = width / height

    fov_x = 100

    fov_y = fov_x * width / height

    f = math.atan(fov_y / 2)

    z_near = 1.5

    z_far = 100

class Arrow:
  def __init__(self, information, list_of_arrows):
    x = information[0]
    y = information[1]
    self.color = information[2].lower().capitalize()

    self.arrows = list_of_arrows

    self.location = (x, y)

    self.dir = 'b'

    self.surface = pygame.Surface((0, 0))

  def set_dir(self, dir):
    self.dir = dir

  def get_surface(self, surface_size):
    for x in self.arrows:
      if x[0] == self.color:
        for y in x[1]:
          if self.dir == 'b' and y[0] == 'b':
            self.surface = y[1]
            break
          elif self.dir == 'bl' and y[0] == 'bl':
            self.surface = y[1]
            break
          elif self.dir == 'l' and y[0] == 'l':
            self.surface = y[1]
            break
          elif self.dir == 'ul' and y[0] == 'ul':
            self.surface = y[1]
            break
          elif self.dir == 'u' and y[0] == 'u':
            self.surface = y[1]
            break
          elif self.dir == 'ur' and y[0] == 'ur':
            self.surface = y[1]
            break
          elif self.dir == 'r' and y[0] == 'r':
            self.surface = y[1]
            break
          elif self.dir == 'br' and y[0] == 'br':
            self.surface = y[1]
            break
        break
        
    return self.surface