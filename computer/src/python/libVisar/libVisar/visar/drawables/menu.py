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

class Button(Drawable):
    '''Draw a cube'''    
    button_vertex_shader = """
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
    
    button_fragment_shader = """
        #version 120

        uniform int highlighted;
        uniform sampler2D texture;
        varying vec2 texcoord;
        uniform vec3 background_color;
        void main() {
            vec4 color = texture2D(texture, texcoord);
//            if (color.rgb == vec3(1, 1, 1)) {
//                gl_FragColor = vec4(background_color, 1);
//            } else {
//                gl_FragColor = vec4(color.rgb, 1);
//            }
            
            if (highlighted == 1){
//                gl_FragColor = vec4(1-color.r, 1-color.g, 1-color.b, 1);    
                gl_FragColor = vec4(1, .29, 0, 1);
            } else {
                gl_FragColor = vec4(color.rgb, 1);
            }

        }
    """

    name = "Button"
    def __init__(self, text, canvas, position=1, color=(0.1, 0.0, 0.7)):
        '''
        Give this the 
        - text to be written
        - main app.canvas
        - position (1-9, or which button position this should occupy)
        '''

        # State Controller
        State.register_button(position, text)

        self.position = position
        self.canvas = canvas
        self.projection = np.eye(4)
        self.view = np.eye(4)
        self.model = np.eye(4)
        height, width = 5.0, 15.0  # Meters

        orientation_vector = (1, 1, 0)
        unit_orientation_angle = np.array(orientation_vector) / np.linalg.norm(orientation_vector)

        scale_factor = 0.2
        lowest_button = -5.2 
        midset = 0.2

        scale(self.model, scale_factor)
        yrotate(self.model, -60)
        # rotate(self.model, 30, *unit_orientation_angle)
        offset = (position * ((height + midset) * scale_factor))
        translate(self.model, -7.4, lowest_button + offset, -10)

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

        self.program = Program(self.button_vertex_shader, self.button_fragment_shader)

        self.program['vertex_position'] = self.vertices
        self.program['default_texcoord'] = self.tex_coords
        self.program['view'] = self.view
        self.program['model'] = self.model
        self.program['projection'] = self.projection
        self.program['background_color'] = color

        self.program['highlighted'] = 0

        # self.texture = Texture2D(shape=(1000, 1000) + (3,))        
        # self.text_buffer = FrameBuffer(self.texture, RenderBuffer((1000, 1000)))
        self.texture = Texture2D(shape=(500, 1500) + (3,))        
        self.text_buffer = FrameBuffer(self.texture, RenderBuffer((500, 1500)))

        self.program['texture'] = self.texture
        self.text = text
        self.make_text(self.text)

        self.first = True


    def update(self):
        '''Things:
        - If selected, change color
        - Hide if I need to be hidden

        '''
        if State.current_button == self.position:
            self.program['highlighted'] = 1
        else:
            self.program['highlighted'] = 0

    def make_text(self, _string):
        self.font_size = 150
        # self.color = (.1, .1, .1, 1.0)
        self.color = (1, 1, 1, 1.0)
        self.canvas.text_renderer = visuals.TextVisual('', bold=True, color=self.color)
        self.tr_sys = visuals.transforms.TransformSystem(self.canvas)
        self.canvas.text_renderer.text = _string

        self.canvas.text_renderer.font_size = self.font_size
        # self.canvas.text_renderer.pos = 200, 200
        self.size = 500, 1500
        self.canvas.text_renderer.pos = self.size[0] * 1.5, self.size[1] // 1.9
        # Logger.log("Color: %s" % (self.canvas.text_renderer.color,))


    def make_texture(self):        
        # gloo.clear(color=True, depth=True)
        with self.text_buffer:
            # gloo.clear(color=(0.008, 0.435, 0.71))
            gloo.clear(color=(0, 0.13, 0.65))
            self.canvas.text_renderer.draw(self.tr_sys)

    def draw(self):        
        if self.first:
            self.canvas.text_renderer.text = self.text
            self.make_texture()
            self.first = False

        set_state(depth_test=False)
        self.program.draw('triangles', self.indices)
        set_state(depth_test=True)
