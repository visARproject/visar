import numpy as np
from socket import *
import time
import json

POSE_PORT = 19107 # netowrk port to listen on
FREQUENCY = 1000  # update frequency, in Hz

def generate_pose():
  # encode the mil location data as a json text string
  mil =  {"id":"self","data":{"position_ecef": {"x":738575.65, "y":-5498374.10, "z":3136355.42}, "orientation_ecef": {"x": 0.50155109,  "y": 0.03353513,  "z": 0.05767266, "w": 0.86255189}, "velocity_ecef": {"x": -0.06585217, "y": 0.49024074, "z": 0.8690958}, "angular_velocity_ecef": {"x": 0.11570315, "y": -0.86135956, "z": 0.4946438}}}
  target = {"id":"other","data":{"position_ecef": {"x":738575.65, "y":-5498374.10, "z":3136355.42}}}
  mil_text = json.dumps(mil)
  target_text = json.dumps(target)
  print mil_text
  print target_text

  sock = socket(AF_INET, SOCK_STREAM)
  sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
  sock.bind(('',19107)) # bind to server port
  sock.listen(1)
  print 'Updated Target'
  
  while True:
    conn, addr = sock.accept()
    done = False
    
    while not done:
      try:
        conn.send(mil_text + '\r\n')
        conn.send(target_text + '\r\n')
      except: done = True
      time.sleep(1.0/FREQUENCY)

  sock.close()

if __name__ == '__main__':
  generate_pose()

