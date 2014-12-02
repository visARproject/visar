import pygame
from pygame.locals import *
import rendering

class Pop_Up(rendering.Drawable):
  def __init__(self):
    rendering.Drawable.__init__(self)
    
    self.name = ""
    pygame.font.init()
    self.font = pygame.font.Font("./font.ttf", 100)
    self.check = True
    self.surface_size = (0, 0)

  def update(self, book):
    if self.check == True:
      self.check = False
      self.name = book.audio_manager.connection.remote_name
      self.connection = book.audio_manager.connection.connected
      self.surface_size = book.eye_size

      self.set_draw_target(self.draw())

    if self.surface_size != book.eye_size:
      self.surface_size = book.eye_size
      self.set_draw_target(self.draw(self.surface_size))

    if self.connection != book.audio_manager.connection.connected:
      self.connection = book.audio_manager.connection.connected
      self.name = book.audio_manager.connection.remote_name
      self.set_draw_target(self.draw())

  def draw(self):
    surface = pygame.Surface(self.surface_size)

    if self.connection == True:
      gap_x = self.surface_size[0] * .1
      gap_y = self.surface_size[1] * .1

      button_width = self.surface_size[0] * .2
      button_height = self.surface_size[1] * .1

      button_x = self.surface_size[0] - gap_x - button_width
      button_y = gap_y

      text_width = button_width * .9
      text_height = button_height * .9

      text_left_margin = button_width * .025
      text_top_margin = button_height * .025

      s = pygame.Surface((button_width, button_height))
      s.fill((0, 138, 254))

      #!!text = self.font.render(self.name, True, (1, 1, 1))
      text = self.font.render("Call: " + self.name, True, (1, 1, 1))
      text = pygame.transform.scale(text, (int(text_width), int(text_height)))

      surface.blit(s, (button_x, button_y))
      surface.blit(text, (button_x + text_left_margin, button_y + text_top_margin))
    return rendering.Render_Surface(surface)



    
