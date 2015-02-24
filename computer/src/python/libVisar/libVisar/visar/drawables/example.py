from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer)
import numpy as np
from . import Drawable
from ...OpenGL import utils


class Example(Drawable):
    '''Draw a cube'''    
    cube_vertex = """
        #version 120
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        attribute vec3 position;
        attribute vec2 texcoord;
        varying vec2 v_texcoord;
        void main()
        {
            gl_Position = projection * view * model * vec4(position, 1.0);
            v_texcoord = texcoord;
        }
    """
    
    cube_fragment = """
        #version 120
        uniform sampler2D texture;
        varying vec2 v_texcoord;
        void main()
        {
            float r = texture2D(texture, v_texcoord).r;
            gl_FragColor = vec4(0, r, r, 1);
        }
    """

    def __init__(self):
        vertices, indices, _ = create_cube()
        vertices = VertexBuffer(vertices)
        self.indices = IndexBuffer(indices)
        self.program = Program(self.cube_vertex, self.cube_fragment)

        self.model = np.eye(4)
        self.view = np.eye(4)

        self.program.bind(vertices)
        self.program['texture'] = utils.checkerboard()
        self.program['texture'].interpolation = 'linear'
        self.program['model'] = self.model
        self.program['view'] = self.view

    def draw(self):
        self.program.draw('triangles', self.indices)