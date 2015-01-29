import interface
import rendering

# keyboard listener, notify arguments are [event]
class KeyboardListener(interface.Interface):
  def __init__(self, renderer):
    interface.Interface.__init__(self)
    renderer.addListener(self,'keys')
  
  # callback for the keypresses, forward events to modules
  # direction is for up or down strokes
  def notify(self, event, direction):
    self.do_updates(event, direction)
    
# consider adding key-specific updates at some point
