# Extensible class for interfaces between modules
# Manages callabck functions and updates
class Interface(object):
  def __init__(self):
    self.update_list = []
    
  # add a callback function to the list
  def add_callback(self, update):
    self.update_list.append(update)
    
  # notify the callbacks (arguments specified in subclass)
  def do_updates(self, *args, **kwargs):
    for update in self.update_list:
      update(*args, **kwargs) # send the update
