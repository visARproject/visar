import numpy as np
import os
from ...OpenGL import utils
from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate, scale, xrotate, yrotate, zrotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer, RenderBuffer, set_viewport, set_state)
from vispy import app, visuals, gloo

from ...OpenGL.drawing import Drawable
from ...OpenGL.utils import Logger
from ..globals import State, Paths

from PIL import Image

class Battery(Drawable):
    battery_vertex_shader = """
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

    battery_fragment_shader = """
        #version 120

        uniform int hide;
        uniform sampler2D texture;
        varying vec2 texcoord;
        uniform vec3 background_color;

        void main() {
            vec4 color = texture2D(texture, texcoord);
            gl_FragColor = vec4(color.rgb, 1);

//            if(hide == 1) {
//                gl_FragColor = vec4(0, 0, 0, 1);
//            } else {
//                gl_FragColor = vec4(color.rgb, 1);
//            }
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

    name = "Battery"
    def __init__(self):
        self.projection = np.eye(4)
        self.view       = np.eye(4)
        self.model      = np.eye(4)

        height, width   = 3.0, 6.0
        scale_factor    = 0.2
        x_offset        = -7.4
        y_offset        = 4.5
        pixel_to_length = 10
        color           = (1.0, 1.0, 1.0)

        scale(self.model, scale_factor)
        yrotate(self.model, -60)
        translate(self.model, x_offset, y_offset, -10)
        size = (int(height*100), int(width*100))

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

        self.program = Program(self.battery_vertex_shader, self.battery_fragment_shader)

        self.texture = Texture2D(shape=size + (3,))
        self.text_buffer = FrameBuffer(self.texture, RenderBuffer(size))

        images = []
        images.append(Image.open(os.path.join(Paths.get_path_to_visar(), 'visar', 'images', 'battery', 'battery_low_color.png')))
        images.append(Image.open(os.path.join(Paths.get_path_to_visar(), 'visar', 'images', 'battery', 'battery_used_color.png')))
        images.append(Image.open(os.path.join(Paths.get_path_to_visar(), 'visar', 'images', 'battery', 'battery_full_color.png')))

        self.level_texture = {} # texture for each level

        for x in range(0, len(images)):
            default_image = images[x]
            default_image = default_image.rotate(-90)
            default_image = default_image.resize(size)
            default_image = default_image.transpose(Image.FLIP_TOP_BOTTOM)
            default_image_array = np.asarray(default_image)
            self.level_texture[x + 1] = default_image_array

        #default_image_array = imageio.imread(os.path.join(Paths.get_path_to_visar(), 'visar', 'images', 'battery', 'battery_full_color.png'))


        # self.default_tex = Texture2D(data=default_image_array)
        # self.default_tex = Texture2D(shape=size + (3,))
        # self.default_tex.set_data(self.level_texture[3])

        self.program['vertex_position']  = self.vertices
        self.program['default_texcoord'] = self.tex_coords
        self.program['view']             = self.view
        self.program['model']            = self.model
        self.program['projection']       = self.projection
        self.program['hide']             = 0

        # self.tex_program = Program(self.tex_vert_shader, self.battery_fragment_shader)

        # self.tex_program['vertex_position']  = self.vertices
        # self.tex_program['default_texcoord'] = self.tex_coords
        # self.tex_program['hide']             = 0
        # self.tex_program['texture']          = self.default_tex

        self.flag = True # flag to update the texture

        self.level = 3 # level of the battery 1 - 3
        full_middle_split = 75 # split between levels 2 and 3
        middle_low_split = 25 # split between levels 1 and 2
        fault_tolerance = 5
        self.full_lower = full_middle_split - fault_tolerance # lower limit for going from 3 to 2
        self.middle_upper = full_middle_split + fault_tolerance # upper limit for going from 2 to 3
        self.middle_lower = middle_low_split - fault_tolerance # lower limit for going from 2 to 1
        self.low_upper = middle_low_split + fault_tolerance # upper limit for going from 1 to 2

    def update(self):
        battery_level = State.battery # get current battery level

        # Logger.log("Battery Level: %s" % (battery,))

        if self.level == 3:
            if battery_level < self.full_lower:
                self.set_new_level(2)
        elif self.level == 2:
            if battery_level > self.middle_upper:
                self.set_new_level(3)
            elif battery_level < self.middle_lower:
                self.set_new_level(1)
        elif self.level == 1:
            if battery_level > self.low_upper:
                self.set_new_level(2)

    def set_new_level(self, new_level):
        self.level = new_level
        self.flag = 1

    def make_texture(self):
        with self.text_buffer:
            gloo.clear(color=(1, 1, 1))
            self.program['texture'] = self.level_texture[self.level]
            # self.program.draw('triangles', self.indices)

    def draw(self):
        if self.flag:
            self.make_texture()
            self.flag = False

        set_state(depth_test=False)
        self.program.draw('triangles', self.indices)
        set_state(depth_test=True)
