# class to handle user pose generation/storage
import numpy as np
import pygame
from pygame.locals import *

class Fps_Pose:
  # static definitions for velocity
  LIN_VELOCITY = .01      # linear speed
  ANG_VELOCITY = np.pi/10 # angluar speed base
  
  def __init__(self, position=[0,0,0], angle=[0,0,0]):
    self.position = np.array(position,dtype=float)
    self.angle = np.array(angle,dtype=float)

  # compose and return an affine transform
  def get_affine(self):
    translation = np.array([[1,0,0,position[0]],[0,1,0,position[1]],
      [0,0,1,position[2]],[0,0,0,1]],dtype=float)
    return np.dot(translation, angle_rotation_matrix(self.angle))
  
  # call for updates
  def update(self):
    info = pygame.display.Info()  # get display informaton for mouse
    width  = info.current_w # window width
    height = info.current_h # window height
    
    # create movement vector (to be rotated later)
    temp_position = np.array([0,0,0,0],dtype=float)
    keys = pygame.key.get_pressed() # get all pressed keys
    if(keys[K_LEFT]):  temp_position[0] += Fps_Pose.LIN_VELOCITY
    if(keys[K_RIGHT]): temp_position[0] -= Fps_Pose.LIN_VELOCITY
    if(keys[K_UP]):    temp_position[2] -= Fps_Pose.LIN_VELOCITY
    if(keys[K_DOWN]):  temp_position[2] += Fps_Pose.LIN_VELOCITY            
    
    # adjust angles
    mouse = pygame.mouse.get_pos() # get mouse position
    # check tolerance boundarys, update angle relative to position
    if(mouse[0] > width/2 + width/5 or mouse[0] < width/2 - width/5):
      self.angle[1] += Fps_Pose.ANG_VELOCITY * (mouse[0] - width/2) / width
    if(mouse[1] > height/2 + height/5 or mouse[1] < height/2 - height/5):
      self.angle[0] += Fps_Pose.ANG_VELOCITY * (mouse[1] - height/2) / height
      
    # wrap horizontal angle (angle 1) in [0,2pi)
    if(self.angle[1] >= 2*np.pi): self.angle[1] -= 2*np.pi
    if(self.angle[1] < 0):        self.angle[1] += 2*np.pi
    
    # bound vertical angle (angle 0) to [-pi,pi]
    if(self.angle[1] >  np.pi): self.angle[0] = np.pi
    if(self.angle[1] < -np.pi): self.angle[0] = -np.pi
      
    #move the position based on the current heading (dot is somehow multiply)
    self.position += np.dot(angle_rotation_matrix(self.angle), temp_position)[:3]
  
# Function to compose a series of 3 angle rotations
# Rotation matricies are composed using Euler-Rodrigez
def angle_rotation_matrix(angles):
  # roll is around x axis (uses a and b)
  a = np.cos(angles[0]/2)
  b = np.sin(angles[0]/2)
  roll = np.array([[1,0,0,0],
    [0,a*a-b*b,2*a*b,0],
    [0,-2*a*b,a*a-b*b,0],
    [0,0,0,1]],dtype=float)

  # pitch is around y axis
  a = np.cos(angles[1]/2)
  c = np.sin(angles[1]/2)
  pitch = np.array([[a*a-c*c,0,-2*a*c,0],
    [0,1,0,0],
    [2*a*c,0,a*a-c*c,0],
    [0,0,0,1]],dtype=float)
    
  # yaw is z axis
  a = np.cos(angles[2]/2)
  d = np.sin(angles[2]/2)
  yaw = np.array([[a*a-d*d,2*a*d,0,0],
    [-2*a*d,a*a-d*d,0,0],
    [0,0,1,0],
    [0,0,0,1]],dtype=float)
    
  return np.dot(roll,pitch,yaw) # get the result (dot is somehow multiply)

