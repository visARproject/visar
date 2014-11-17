# visAR interface controller:
#   manages system information, calls updates


class Controller:
  def __init__(self, pose_source):
    self.ping_updates = [] # update functions with no arguments (ping each frame)
    self.pose_updates = [] # update functions which require pose information
    self.pose_source = pose_source # the pose source
    
  # get the information, push updates
  def do_update(self):
    for update in self.ping_updates: update() # call the void updates

    #pose = pose_source.get_affine() # get the transformation matrix      
    pose = self.pose_source.position # Debug, get position only
    for update in self.pose_updates: update(pose) # call the pose_updates  
    
  
  # function to add an update call with no arguments
  def add_update(self, update):
    self.ping_updates.append(update)
    
  # function adds a position listner
  def add_pose_update(self, update):
    self.pose_updates.append(update)
