import interface
import rendering

# keyboard listener, notify arguments are [event]
class KeyboardListener(interface.Interface):
  def __init__(self, renderer):
    interface.Interface.__init__(self)
    renderer.addListener(self,'keys')
  
  # callback for the keypresses, forward events to modules
  def notify(self, event):
    self.do_updates(event)
    
# consider adding key-specific updates at some point
