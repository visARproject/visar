from __future__ import division
import numpy as np
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer)
from vispy import gloo
from vispy import app

from ..OpenGL.utils.transformations import quaternion_matrix
from ..OpenGL.utils import Logger
from ..OpenGL.shaders import Distorter

# Presets
HUD_DEPTH = 5 # Minimum depth (Specified by Oculus docs)
FPS = 60 # Maximum FPS (how often needs_update is checked)

vPosition_full = np.array([[-1.0, -1.0, 0.0], [+1.0, -1.0, 0.0],
                           [-1.0, +1.0, 0.0], [+1.0, +1.0, 0.0]], np.float32)
vTexcoord_full = np.array([[0.0, 0.0], [0.0, 1.0],
                           [1.0, 0.0], [1.0, 1.0]], np.float32)

def main():
    ex_quat = {"x": 0.50155109,  "y": 0.03353513,  "z": 0.05767266, "w": 0.86255189}
    orientation_quaternion = (0.50155109, 0.03353513, 0.05767266, 0.86255189)
    matrix =  quaternion_matrix(orientation_quaternion)
    Logger.set_verbosity('log')
    Logger.log( matrix )
    Logger.log( type(matrix) )
    Logger.warn( matrix.shape )

class Renderer(app.Canvas): # Canvas is a GUI object
    def __init__(self, size=(1600, 900)):    
        self.renderList = [] # List of modules to render
        self.key_listener = None
        self.needs_update = False
        
        # Initialize gloo context
        app.Canvas.__init__(self, keys='interactive')
        self.size = size # Get the size    
        # Create texture rendering program
        self.tex_program = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)  
        # Create texture to render modules to
        self.left_eye_tex = gloo.Texture2D(shape=(4096, 4096) + (3,))
      
        # Create Frame Buffer Object, attach color/depth buffers
        self.left_eye_buffer = gloo.FrameBuffer(self.left_eye_tex, gloo.RenderBuffer(self.size))
        
        # Create texture rendering program
        self.tex_program = gloo.Program(VERT_SHADER_TEX, FRAG_SHADER_TEX)
        
        self.Distorter = Distorter(self.size)

        # Set an update timer to run every FPS
        self.interval = 1 / FPS
        self._timer = app.Timer('auto',connect=self.on_timer, start=True)
  
    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0,0,width,height)
    
    def on_draw(self, event):
        # Draw each drawable using the distorter
        self.Distorter.draw(self.renderList)

        ''' The plan here is to contruct a new view matrix for the targets each frame
        As for the map and other UI elements, they don't need a view matrix
        '''

    
if __name__ == '__main__':
    
    main()