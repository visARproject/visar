# NOTES: FPS is not very good, need to find a better backend
#  Research: collections and scene canvases seem like alternatives

import numpy as np
from vispy.gloo import Program, gl
from vispy import app, gloo
import threading

HUD_DEPTH = 0.2 # minimum depth
FPS = 60 # hopefully not too optimistic (not doing anything)

VERT_SHADER_TEX = """ //texture vertex shader
attribute vec3 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;

void main(void){
    v_texcoord = texcoord; //send tex coordinates
    gl_Position = vec4(position.xyz, 1.0);
}"""

FRAG_SHADER_TEX = """ // texture fragment shader
uniform sampler2D texture;
varying vec2 v_texcoord;

void main(){
    gl_FragColor = texture2D(texture, v_texcoord);
}"""

# full renderable 2D area
vPosition_full = np.array([[-1.0, -1.0, 0.0], [+1.0, -1.0, 0.0],
                           [-1.0, +1.0, 0.0], [+1.0, +1.0, 0.0]], np.float32)
vTexcoord_full = np.array([[0.0, 0.0], [0.0, 1.0],
                           [1.0, 0.0], [1.0, 1.0]], np.float32)

renderer = None # singleton, don't reference this or declare an instance of the class
                      
# thread locking for updating stuff
renderingLock = threading.Lock()
def renderLock(func):
  def locked(*args, **kwargs):
    global renderingLock
    renderingLock.acquire()
    result = func(*args, **kwargs)
    renderingLock.release()
    return result
  return locked
                      
class Renderer(app.Canvas): # canvas is a GUI object
  def __init__(self, size=(560,420)):    
    self.renderList = [] # list of modules to render
    self.key_listener = None
    self.needs_update = False
    
    # initialize gloo context
    app.Canvas.__init__(self, keys='interactive')
    self.size = size # get the size
            
    # create texture to render modules to
    shape = self.size[1], self.size[0]
    self._rendertex = gloo.Texture2D(shape=shape+(3,))
  
    # create Frame Buffer Object, attach color/depth buffers
    self._fbo = gloo.FrameBuffer(self._rendertex, gloo.RenderBuffer(shape))
    
    # create texture rendering program
    self.tex_program = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)
  
    # create program to render the results (TEST ONLY, same as before)
    # JAKE: replace this with your shaders
    self._program2 = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)
    self._program2['position'] = gloo.VertexBuffer(vPosition_full)
    self._program2['texcoord'] = gloo.VertexBuffer(vTexcoord_full)
    self._program2['texture']  = self._rendertex
    
    # set an update timer to run every FPS
    self.interval = 1/FPS
    self._timer = app.Timer('auto',connect=self.on_timer, start=True)
  
  def on_resize(self, event):
    width, height = event.size
    gloo.set_viewport(0,0,width,height)
    
  def on_draw(self, event):
    # draw scene to FBO instead of output buffer
    with self._fbo:
      gloo.set_clear_color('black')
      gloo.clear(color=True, depth=True)
      gloo.set_viewport(0,0, *self.size)
      # render each of the modules
      for module in self.renderList:   
        if(module.textured and module.positioned):  # make sure it's ready
          module.program.draw('triangle_strip')     # draw the module
    
    # draw to full screen
    gloo.set_clear_color('black')
    gloo.clear(color=True,depth=True)
    self._program2.draw('triangle_strip')
  
  # update the display
  @renderLock  
  def on_timer(self, event):
    if self.needs_update:
      self.update() # update self    
      self.needs_update = False
    
  # define keyboard listeners  
  def on_key_press(self, event):
    if self.key_listener is not None:
      self.key_listener.notify(event)
  def on_key_release(self, event):
    if self.key_listener is not None:
      self.key_listener.notify(event)
    
  # run preliminary update, then start rendering
  def startRender(self):
    self.show()
    app.run()
    
  def addListener(self, listener, target='keys'):
    if (target == 'keys'):
      self.key_listener = listener
      
  # callback funciton for FPS
  def print_fps(self, fps):
    print ('FPS: %.2f' % fps)

# enforce singleton pattern
def getRenderer():
  global renderer
  if (renderer is None): 
    renderer = Renderer()
  return renderer
  
# class for texture rendering  
class Drawable:
  @renderLock
  def __init__(self):
    self.program = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)
    self.program['texcoord'] = gloo.VertexBuffer(vTexcoord_full) # assume full usage
    self.position = None
    self.textured = False
    self.positioned = False
    self.updates = [] # list of updates to perform
    renderer.renderList.append(self) # add to render stack
  
  # set the texture
  @renderLock
  def setTexture(self, data):
    # create new program to avoid conflicts
    new_program = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)
    new_program['texcoord'] = gloo.VertexBuffer(vTexcoord_full) # assume full usage
    new_program['texture'] = data
    if self.positioned: 
      new_program['position'] = self.position
    self.program = new_program
    self.textured = True
    renderer.needs_update = True
  
  # set the verticies, make sure they're 3d and less than the hud depth
  @renderLock
  def setVerticies(self, verticies):
    self.position = verticies
    self.program['position'] = verticies
    self.positioned = True  
    renderer.needs_update = True
  
  # pull render off of stack (would put in destructor, but wouldn't get called)
  @renderLock
  def stopRendering(self):
    renderer.renderList.remove(self)
  
  
