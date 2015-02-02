import cv2
import keyboard
import math
import numpy as np
import PIL
import rendering
import sys
import vispy

from PIL import Image
from vispy import app, scene

class Overlay():
  def __init__(self, size):
    self.ratio = float(size[1]) / size[0] ## aspect ratio
    print self.ratio
    fov = 100 ## field of view
    self.focal = 1 / math.tan(fov/2)
    self.near = 1 ## near boundary
    self.far = 1000 ## far boundary

    ## dictionary that will hold all of the arrows; first key is color, followed by direction
    self.arrows = {}

    ## pre-loaded images for red arrows
    self.arrows['red'] = {}
    self.arrows['red']['r'] = Image.open("./images/Red_Arrow.png")
    self.arrows['red']['ur'] = self.arrows['red']['r'].rotate(45)
    self.arrows['red']['u'] = self.arrows['red']['r'].rotate(90)
    self.arrows['red']['ul'] = self.arrows['red']['r'].rotate(135)
    self.arrows['red']['l'] = self.arrows['red']['r'].rotate(180)
    self.arrows['red']['dl'] = self.arrows['red']['r'].rotate(225)
    self.arrows['red']['d'] = self.arrows['red']['r'].rotate(270)
    self.arrows['red']['dr'] = self.arrows['red']['r'].rotate(315)

    ## pre-loaded images for blue arrows
    self.arrows['blue'] = {}
    self.arrows['blue']['r'] = Image.open("./images/Blue_Arrow.png")
    self.arrows['blue']['ur'] = self.arrows['blue']['r'].rotate(45)
    self.arrows['blue']['u'] = self.arrows['blue']['r'].rotate(90)
    self.arrows['blue']['ul'] = self.arrows['blue']['r'].rotate(135)
    self.arrows['blue']['l'] = self.arrows['blue']['r'].rotate(180)
    self.arrows['blue']['dl'] = self.arrows['blue']['r'].rotate(225)
    self.arrows['blue']['d'] = self.arrows['blue']['r'].rotate(270)
    self.arrows['blue']['dr'] = self.arrows['blue']['r'].rotate(315)

    ## pre-loaded images for green arrows
    self.arrows['green'] = {}
    self.arrows['green']['r'] = Image.open("./images/Green_Arrow.png")
    self.arrows['green']['ur'] = self.arrows['green']['r'].rotate(45)
    self.arrows['green']['u'] = self.arrows['green']['r'].rotate(90)
    self.arrows['green']['ul'] = self.arrows['green']['r'].rotate(135)
    self.arrows['green']['l'] = self.arrows['green']['r'].rotate(180)
    self.arrows['green']['dl'] = self.arrows['green']['r'].rotate(225)
    self.arrows['green']['d'] = self.arrows['green']['r'].rotate(270)
    self.arrows['green']['dr'] = self.arrows['green']['r'].rotate(315)

    ## pre-loaded images for yellow arrows
    self.arrows['yellow'] = {}
    self.arrows['yellow']['r'] = Image.open("./images/Yellow_Arrow.png")
    self.arrows['yellow']['ur'] = self.arrows['yellow']['r'].rotate(45)
    self.arrows['yellow']['u'] = self.arrows['yellow']['r'].rotate(90)
    self.arrows['yellow']['ul'] = self.arrows['yellow']['r'].rotate(135)
    self.arrows['yellow']['l'] = self.arrows['yellow']['r'].rotate(180)
    self.arrows['yellow']['dl'] = self.arrows['yellow']['r'].rotate(225)
    self.arrows['yellow']['d'] = self.arrows['yellow']['r'].rotate(270)
    self.arrows['yellow']['dr'] = self.arrows['yellow']['r'].rotate(315)

    self.border = .1 ## the rendering border around the screen

    # r = rendering.Drawable()
    # r.setTexture(self.arrows['yellow']['ur'])
    # r.setVerticies([[-1,-1],[-1,1],[1,-1],[1,1]])

    test_gps = np.array([2.0, 2.0, 2.0, 1.0])
    matrix = np.array([[self.focal, 0, 0, 0],[0, self.focal/self.ratio, 0, 0],[0, 0, -(self.far+self.near)/(self.far-self.near), -(2*self.far*self.near)/(self.far-self.near)],[0, 0, -1.0, 0]])

    points = test_gps*matrix

    print points

    # a1 = rendering.Drawable()
    # a1.setTexture(self.arrows['blue']['d'])
    # a1.setVerticies([[.25,.25],[.25,.3],[.3,.25],[.3,.3]])

    # a2 = rendering.Drawable()
    # a2.setTexture(self.arrows['blue']['d'])
    # a2.setVerticies([[-.45,-.45],[-.45,-.1],[-.1,-.45],[-.1,-.1]])

    ## gps coord (x,y,z,1) * matrix

class Target():
  def __init__(self, type="ally", pos=np.array([0,0,0])):
    self.type = "ally"
    self.pos = pos