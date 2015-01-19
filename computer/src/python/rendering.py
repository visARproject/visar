import numpy as np
import vispy.gloo as gloo
from vispy.gloo import Program, gl
from vispy import app

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
                           [-1.0, +1.0, 0.0], [+1.0, +1.0, 0.0, ]], np.float32)
vTexcoord_full = np.array([[0.0, 0.0], [0.0, 1.0],
                           [1.0, 0.0], [1.0, 1.0]], np.float32)

HUD_DEPTH = 0.7 # minimum depth

                      
class Renderer(app.Canvas): # canvas is a GUI object
  def __init__(self, size=(560,420)):
    app.Canvas.__init__(self, keys='interactive')
    self.size = size # get the size
    self.renderList = [] # list of modules to render
    
    # create texture to render modules to
    shape = self.size[1], self.size[0]
    self._rendertex = gloo.Texture2D(shape=shape+(3,),dtype='uint8')
  
    # create Frame Buffer Object, attach color/depth buffers
    self._fbo = gloo.FrameBuffer(self._rendertex, gloo.DepthBuffer(shape))
    
    # create texture rendering program
    self.tex_program = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)
  
    # create program to render the results (TEST ONLY, same as before)
    self._program2 = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)
    self._program2['position'] = gloo.VertexBuffer(vPosition_full)
    self._program2['texcoord'] = gloo.VertexBuffer(vTexcoord_full)
    self._program2['texture']  = self._rendertex
  
  def on_resize(self, event):
    width, height = event.size
    gloo.set_viewport(0,0,width,height)
    
  def on_draw(self, event):
    # draw scene to FBO instead of output buffer
    with self._fbo:
      gloo.set_clear_color('black')
      gloo.clear(color=True, depth=True)
      gloo.set_viewport(0,0, *self.size)
      for module in self.renderList:
        module.program.draw('triangle_strip')
    
    # draw to full screen
    gloo.set_clear_color('black')
    gloo.clear(color=True,depth=True)
    self._program2.draw('triangle_strip')

  # add drawable (might change scope later)
  def addModule(self, drawable):
    self.renderList.append(drawable)
  
# class for texture rendering  
class Drawable:
  def __init__(self):
    self.program = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)
    self.program['texcoord'] = gloo.VertexBuffer(vTexcoord_full) # assume full usage
  
  # set the texture
  def setTexture(self, data):
    self.program['texture'] = gloo.Texture2D(data) # set the texture
  
  # set the verticies, make sure they're 3d and less than the hud depth
  def setVerticies(self, verticies):
    for v in verticies:
      if(len(v) < 3): v.append(HUD_DEPTH)
      elif(v[2] < HUD_DEPTH): v[2] = HUD_DEPTH
    self.program['position'] = gloo.VertexBuffer(verticies) # define the position
  

