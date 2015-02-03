# NOTES: FPS is not very good, need to find a better backend
#  Research: collections and scene canvases seem like alternatives
import vispy

import numpy as np
from vispy.gloo import Program, gl
from vispy import app, gloo
import threading
from libVisar.OpenGL.shaders import make_distortion


HUD_DEPTH = 0.2 # minimum depth
FPS = 60 # Maximum FPS (how often needs_update is checked)

# test shaders
VERT_SHADER_TEX = """ //texture vertex shader
uniform   mat4 model;
attribute vec3 position;
attribute vec2 texcoord;
varying   vec2 v_texcoord;

void main(void){
    v_texcoord = texcoord; //send tex coordinates
    gl_Position = model * vec4(position.xyz, 1.0);
}"""

FRAG_SHADER_TEX = """ // texture fragment shader
uniform sampler2D texture;
varying vec2 v_texcoord;

void main(){
     vec4 color = texture2D(texture, v_texcoord);
     if(color.a == 0) discard; //manually handle alphas
     gl_FragColor = color;
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
  def __init__(self, size=(1600, 900)):    
    self.renderList = [] # list of modules to render
    self.key_listener = None
    self.needs_update = False
    
    # initialize gloo context
    app.Canvas.__init__(self, keys='interactive')
    self.size = size # get the size    
    # create texture rendering program
    self.tex_program = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)  
    # create texture to render modules to
    shape = self.size[1], self.size[0]
    self.left_eye_tex = gloo.Texture2D(shape=(4096, 4096) + (3,))
  
    # create Frame Buffer Object, attach color/depth buffers
    self.left_eye_buffer = gloo.FrameBuffer(self.left_eye_tex, gloo.RenderBuffer(shape))
    
    # create texture rendering program
    self.tex_program = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)
  
    # create program to render the results (TEST ONLY, same as before)

    self.left_eye_program, self.left_eye_indices = make_distortion(self.left_eye_tex)

    # set an update timer to run every FPS
    self.interval = 1/FPS
    self._timer = app.Timer('auto',connect=self.on_timer, start=True)
  
  def on_resize(self, event):
    width, height = event.size
    gloo.set_viewport(0,0,width,height)
    
  def on_draw(self, event):
    # draw scene to FBO instead of output buffer
    with self.left_eye_buffer:
      gloo.set_clear_color('black')
      gloo.clear(color=True, depth=True)
      gloo.set_viewport(0,0, *self.size)
      # render each of the modules
      for module in self.renderList:   
        if(module.rendering):  # make sure it's ready
          module.program.draw('triangle_strip')     # draw the module
    
    # draw to full screen
    # gloo.set_clear_color('black')
    gloo.clear(color=True,depth=True)
    self.left_eye_program.draw('triangles', self.left_eye_indices)
  
  # update the display
  @renderLock  
  def on_timer(self, event):
    if self.needs_update:
      self.update() # update self    
      self.needs_update = False
    
  # define keyboard listeners  
  def on_key_press(self, event):
    if self.key_listener is not None:
      self.key_listener.notify(event,'down')
  def on_key_release(self, event):
    if self.key_listener is not None:
      self.key_listener.notify(event,'up')
    
  # run preliminary update, then start rendering
  def startRender(self):
    self.show()
    app.run()
    
  def addListener(self, listener, target='keys'):
    if (target == 'keys'):
      self.key_listener = listener
      
  # callback funciton for FPS (prints update() calls / second)
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
  # init must have verticies, and either a texture or the data for a texture
  def __init__(self, verticies=None, texture=None, tex_data=None, position=None, UI=False, start=True):
    self.program = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)
    self.program['texcoord'] = gloo.VertexBuffer(vTexcoord_full) # assume full usage
    
    # set the verticies
    if(verticies is None): # check for valid input
      print 'Error: drawable created with no valid texture'
      return None # no useful data
    for row in verticies: # force vertecies to 3d shape
      if len(row) < 3:
        row.append(HUD_DEPTH)
    self.program['position'] = gloo.VertexBuffer(verticies)    
    
    # set the texture
    self.program['texcoord'] = gloo.VertexBuffer(vTexcoord_full) # assume full usage
    if(texture is not None): self.program['texture'] = texture
    elif(tex_data is not None): self.program['texture'] = gloo.Texture2D(tex_data)
    else:
      print 'Error: drawable created with no valid texture'
      return None # no useful data
    self.program['texture'].interpolation = 'linear'
    
    # model position matrix
    if(position is not None): self.position = position
    else: self.position = np.eye(4, dtype=np.float32)
    self.program['model'] = self.position

    self.is_UI = UI
    self.rendering = start
    renderer.renderList.append(self) # add to render stack
    renderer.needs_update = True # notify renderer to redraw
  
  # move an object
  @renderLock
  def setPosition(self, position):
    self.position = position
    self.program['model'] = position
    renderer.needs_update = True # notify renderer to redraw
    
  # pull render off of stack (would put in destructor, but wouldn't get called)
  @renderLock
  def pauseRender(self):
    self.rendering = False
    renderer.needs_update = True
  
  # resume a paused render
  @renderLock
  def resumeRender(self):
    self.rendering = True
    renderer.needs_update = True

  # stop rendering this module, cannot be restarted
  @renderLock
  def stopRender(self):
    renderer.renderList.remove(self)
