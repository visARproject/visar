# visAR interface controller:
#   manages system information, calls updates

class Controller:
  def __init__(self, pose_source):
    self.updates = [] # update function references
    self.book = Controller_Book(pose_source) # init book
    
  # get the information, push updates
  def do_update(self):
    for update in self.ping_updates: 
      update(self.book) # call the updates
  
  # function to add an update listener
  def add_update(self, update):
    self.updates.append(update)


# Controller book stores state information, add things as nessecarry
class Controller_Book:
  def __init__(self, pose_source):
    self.pose_source = pose_source # position information
    
    # menu botton information (will probably transition to tree structure)
    self.menu_level = 0 # active menu sub-level (0 is none)
    self.active_menu = '' # text string for active menu button
    
  def get_pose(self):
    return pose_source.get_pose()
