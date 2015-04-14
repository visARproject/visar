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

DISPLAY_TIME = 2   # display text for 2 seconds
FADE_TIME    = 0.5 # fade text over .5 seconds

class Toast(Drawable):
    '''Draw a cube'''    
    toast_vertex_shader = """
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
    
    toast_fragment_shader = """
        #version 120
        uniform sampler2D texture;
        varying vec2 texcoord;
        uniform vec4 background_color;
        uniform vec4 text_color;
        void main() {
            vec4 color = texture2D(texture, texcoord);
            if (color.r == 1 && color.g == 1 && color.b == 1) {
                gl_FragColor = text_color;
            } else {
                gl_FragColor = background_color;
            }
        }
    """

    name = "Toast"
    def __init__(self, canvas, background_color=(0,0,0,0), text_color=(1,1,1)):
        # State.register_button(position, text)
        
        self.canvas = canvas
        self.text = None
        self.tcolor = (text_color[0],text_color[1],text_color[2], 1)
        self.bcolor = background_color
        self.timer = 0
        self.fade_timer = 0
        self.projection = np.eye(4)
        self.view = np.eye(4)
        self.model = np.eye(4)
        height, width = 5.0, 25.0  # Meters

        orientation_vector = (1, 1, 0)
        unit_orientation_angle = np.array(orientation_vector) / np.linalg.norm(orientation_vector)

        scale_factor = 0.2
        lowest_button = -5.2 
        midset = 0.2
        position = -2
        
        scale(self.model, scale_factor)
        yrotate(self.model, -60)
        # rotate(self.model, 30, *unit_orientation_angle)
        offset = (position * ((height + midset) * scale_factor))
        translate(self.model, -6.4, lowest_button + offset, -10)

        pixel_to_length = 10
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

        self.indices = IndexBuffer([
            0, 1, 2,
            2, 3, 0,
        ])

        self.program = Program(self.toast_vertex_shader, self.toast_fragment_shader)

        self.program['vertex_position'] = self.vertices
        self.program['default_texcoord'] = self.tex_coords
        self.program['view'] = self.view
        self.program['model'] = self.model
        self.program['projection'] = self.projection
        self.program['background_color'] = (0,0,0,0) # no background yet
        self.program['text_color'] = (0,0,0,0) # no text yet
        self.size = (int(height*100), int(width*100))

        # self.texture = Texture2D(shape=(1000, 1000) + (3,))        
        # self.text_buffer = FrameBuffer(self.texture, RenderBuffer((1000, 1000)))
        self.texture = Texture2D(shape=self.size + (3,))        
        self.text_buffer = FrameBuffer(self.texture, RenderBuffer(self.size))

        self.program['texture'] = self.texture
        #self.program['text_color'] = self.tcolor # set the tcolor
        #self.program['background_color'] = self.bcolor # set the tcolor
        self.first = False # do not draw text until needed
        self.make_text('Default Text') # Create Empty text object

    def update(self):
        '''Redraw the text when it changes '''
        ctime = time.clock()
        if not State.toast == self.text:
            self.text = State.toast
            self.timer = time.clock() + DISPLAY_TIME
            self.fade_timer = self.timer + FADE_TIME
            self.program['text_color'] = self.tcolor # set the tcolor
            self.program['background_color'] = self.bcolor # set the tcolor
            self.canvas.text_renderer.text = self.text # set the new text
            self.make_texture() # rebuild the texture

        # text is fading out
        elif ctime > self.timer and ctime < self.fade_timer:
            # determine alpha as percentage of screen time remaining
            alpha = (self.fade_timer - ctime) / FADE_TIME
            if alpha < 0: alpha = 0 # ensure no negatives
            self.program['text_color'] = (self.tcolor[0], self.tcolor[1],self.tcolor[2], alpha)
            self.program['background_color'] = (self.bcolor[0], self.bcolor[1],self.bcolor[2], alpha)
            
        # text finished fading out, remove it
        elif ctime > self.fade_timer and self.text is not None: 
            self.program['text_color'] = (0,0,0,0) # no more text
            self.program['background_color'] = (0,0,0,0) # no more text
            self.text = None # remove the text
            State.toast = None # clear the state's toast value
            

    def make_text(self, _string):
        self.font_size = 150
        self.color = (1, 1, 1, 1.0) # white text (for easy detection)
        self.canvas.text_renderer = visuals.TextVisual('', bold=True, color=self.color)
        self.tr_sys = visuals.transforms.TransformSystem(self.canvas)
        self.canvas.text_renderer.text = _string

        self.canvas.text_renderer.font_size = self.font_size
        # self.canvas.text_renderer.pos = 200, 200
        self.canvas.text_renderer.pos = self.size[0] * 1.5, self.size[1] // 1.9
        # Logger.log("Color: %s" % (self.canvas.text_renderer.color,))


    def make_texture(self):        
        # gloo.clear(color=True, depth=True)
        with self.text_buffer:
            # gloo.clear(color=(0.008, 0.435, 0.71))
            gloo.clear(color=(0, 0, 0))
            self.canvas.text_renderer.draw(self.tr_sys)

    def draw(self):
        if self.first:
            self.canvas.text_renderer.text = 'Default Text'
            self.make_texture()
            self.first = False        
        set_state(depth_test=False)
        self.program.draw('triangles', self.indices)
        set_state(depth_test=True)
