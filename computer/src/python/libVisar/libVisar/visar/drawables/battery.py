import numpy as np
from ...OpenGL import utils
from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate, scale, xrotate, yrotate, zrotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer, RenderBuffer, set_viewport, set_state)
from vispy import app, visuals, gloo

from ...OpenGL.drawing import Drawable
from ...OpenGL.utils import Logger
from ..globals import State

import time

class Battery(Drawable):
    '''Draw a cube'''    
    vertex_shader = """
        #version 120
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        attribute vec3 vertex_position;
        attribute vec2 default_texcoord;

        varying vec2 texcoord;

        void main() {
            texcoord = default_texcoord;
            gl_Position = projection * view * model * vec4(vertex_position, 1.0);
        }
    """
    
    fragment_shader = """
        #version 120
        uniform sampler2D texture;
        varying vec2 texcoord;
        void main() {
            gl_FragColor = texture2D(texture, texcoord);
        }
    """
    
    tex_vert_shader = """
        #version 120
        attribute vec3 vertex_position;
        attribute vec2 default_texcoord;

        varying vec2 texcoord;

        void main() {
            texcoord = default_texcoord;
            gl_Position = vec4(vertex_position, 1.0);
        }
    """
    def __init__(self):        
        self.projection = np.eye(4)
        self.view = np.eye(4)
        self.model = np.eye(4)
        
        # VAL: ALTER THESE TO GET SIZING/POSITION CORRECT
        height, width = 5.0, 25.0  
        scale_factor  = .2
        x_offset      = 5
        y_offset      = 5

        orientation_vector = (1, 1, 0)
        unit_orientation_angle = np.array(orientation_vector) / np.linalg.norm(orientation_vector)
        
        scale(self.model, scale_factor) # scale the object
        yrotate(self.model, 60)         # tilt opposite direction from menu
        translate(self.model, x_offset, y_offset, -10) # move in space

        pixel_to_length = 10 # essentially the resolution
        self.size = map(lambda o: pixel_to_length * o, [width, height])

        # Add texture coordinates
        # Rectangle of height height
        self.vertices = np.array([
            [-width / 2, -height / 2, 0],
            [ width / 2, -height / 2, 0],
            [ width / 2,  height / 2, 0],
            [-width / 2,  height / 2, 0],
        ], dtype=np.float32)

        self.tex_coords = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],

        ], dtype=np.float32)

        # Triangle indices from previous coordinates
        self.indices = IndexBuffer([
            0, 1, 2,
            2, 3, 0,
        ])
        
        # Render Program
        self.program = Program(self.vertex_shader, self.fragment_shader)
        self.program['vertex_position'] = self.vertices
        self.program['default_texcoord'] = self.tex_coords
        self.program['view'] = self.view
        self.program['model'] = self.model
        self.program['projection'] = self.projection
        self.size = (int(height*100), int(width*100))

        # Create the texture to which we will render
        self.texture = Texture2D(shape=self.size + (3,))        
        self.text_buffer = FrameBuffer(self.texture, RenderBuffer(self.size))
        self.program['texture'] = self.texture

        # Create program to rendure to texture
        self.tex_program = Program(self.tex_vert_shader, self.fragment_shader)
        self.tex_program['vertex_position'] = self.vertices
        self.tex_program['default_texcoord'] = self.tex_coords
        
        # Create a default, empty texture buffer
        # This is only done since the program needs a texture
        #    or it will draw garbage. You can replace this with an actual texture later
        self.default_tex = Texture2D(shape=self.size + (3,))        
        self.default_buf = FrameBuffer(self.texture, RenderBuffer(self.size))
        
        # Set the initialization flag
        self.first = True
        
        # Battery State (selects an image)
        self.battery_state = None

    def update(self):
        '''Redraw the texture when battery level changes '''
        
        battery_level = State.battery # get current battery level
        
        # VAL: Implement proper range checking here
        #     try to build in tolerance around edges
        #     in order to prevent rapid state changes
        
        # Example, only updates once ever
        image_to_draw = "Some Texture, IDK how this part works"
        if self.battery_state == None: 
            self.make_texture(image_to_draw) 

    def make_texture(self, tex):        
        ''' Draw to the texture buffer'''
        with self.text_buffer:
            gloo.clear(color=(0, 0, 0)) # Wipe old data
            self.text_program['texture'] = tex
            self.text_program.draw()

    def draw(self):
        if self.first: # handle initialization
            # Clear the temp default texture
            #  (remove this if you use an actual default)
            with self.default_buff: 
                gloo.clear(color=(0, 0, 0))

            # Draw the initial texture (don't remove this)
            self.make_texture(self.default_tex)
            self.first = False
            
        # draw the entire thing            
        set_state(depth_test=False)
        self.program.draw('triangles', self.indices)
        set_state(depth_test=True)
