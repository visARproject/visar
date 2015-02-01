import cv2
import keyboard
import numpy as np
import PIL
import rendering
import sys
import vispy

from PIL import Image
from vispy import app, scene

class Overlay():
  def __init__(self):
    ## pre-loaded images for red arrows
    arrow_red_up = Image.open("./images/Red_Arrow.png")
    arrow_red_left = arrow_red_up.rotate(90)
    arrow_red_down = arrow_red_up.rotate(180)
    arrow_red_right = arrow_red_up.rotate(270)

    ## pre-loaded images for blue arrows
    arrow_blue_up = Image.open("./images/Blue_Arrow.png")
    arrow_blue_left = arrow_blue_up.rotate(90)
    arrow_blue_down = arrow_blue_up.rotate(180)
    arrow_blue_right = arrow_blue_up.rotate(270)

    ## pre-loaded images for green arrows
    arrow_green_up = Image.open("./images/Green_Arrow.png")
    arrow_green_left = arrow_green_up.rotate(90)
    arrow_green_down = arrow_green_up.rotate(180)
    arrow_green_right = arrow_green_up.rotate(270)

    ## pre-loaded images for yellow arrows
    arrow_yellow_up = Image.open("./images/Yellow_Arrow.png")
    arrow_yellow_left = arrow_yellow_up.rotate(90)
    arrow_yellow_down = arrow_yellow_up.rotate(180)
    arrow_yellow_right = arrow_yellow_up.rotate(270)

    render1 = rendering.Drawable()
    render1.setTexture(arrow_red_up)
    render1.setVerticies([[-1,-1],[0,-1],[-1,0],[0,0]])

    render2 = rendering.Drawable()
    render2.setTexture(arrow_red_right)
    render2.setVerticies([[-1,0],[0,0],[-1,1],[0,1]])

    render3 = rendering.Drawable()
    render3.setTexture(arrow_red_down)
    render3.setVerticies([[0,0],[1,0],[0,1],[1,1]])

    render4 = rendering.Drawable()
    render4.setTexture(arrow_red_left)
    render4.setVerticies([[0,-1],[1,-1],[0,0],[1,0]])

    self.border = .1 ## the rendering border around the screen