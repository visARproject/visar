from __future__ import division
import numpy as np
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer)
from vispy.util.transforms import perspective, translate, rotate
from vispy.geometry import create_sphere
from ...OpenGL.drawing import Drawable
from ...OpenGL import utils


class Targets(Drawable):
    # super(Targets, self).__init__()
    pass


class Target(Drawable):
    '''

    Bibliography:

    [1] Billboard drawing;
        http://stackoverflow.com/questions/5467007/inverting-rotation-in-3d-to-make-an-object-always-face-the-camera/5487981#5487981

    '''
    vertex_shader = """
        #version 120
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        attribute vec3 position;

        mat4 make_billboard(mat4 T) {
            float d = length(T[0]); // Length of 0th column of the transformation
            mat4 T_billboard;
            T_billboard[0] = vec4(d,  0., 0., 0.);
            T_billboard[1] = vec4(0., d,  0., 0.);
            T_billboard[2] = vec4(0., 0., d,  0.);
            T_billboard[3] = T[3]; // Maintain original translation
            return T_billboard;
        }

        void main()
        {
            // Prevent rotation of the object relative to camera view
            mat4 T = projection * view * model;

            mat4 T_billboard = make_billboard(T);
            gl_Position = T_billboard * vec4(position, 1.0);
        }
    """
    
    frag_shader = """
        #version 120
        uniform vec3 color;
        void main()
        {
            gl_FragColor = vec4(color, 1);
        }
    """

    def __init__(self, world_pos, color=(1.0, 0.0, 0.5)):
        '''Target(world_pos, color) -> Target
        Arguments:
            world_pos - absolute (GPS long-lat) position of marker
            color - specified as 3-tuple of floats with each element 
                in range [0, 1]. It is the color of the marker
        '''
        # Assertions
        assert isinstance(world_pos, tuple), "World position specified invalid, should be tuple"
        assert len(world_pos) == 3, "World position invalid (should be length 3)"
        assert max(color) <= 1.0, "Color should be in range [0.0, 1.0]"
        assert min(color) >= 0.0, "Color should be in range [0.0, 1.0]"
        assert len(color) == 3, "Color must be 3 channels (Ask Jacob if you want to do weird Alpha stuff)"

        self.projection = np.eye(4)
        self.view = np.eye(4)
        self.model = translate(np.eye(4), *world_pos)

        height = 5.0  # Meters

        # This is a triangle of height $height
        self.vertices = np.array([
            [0,           -height, 0],
            [-height / 2,          0, 0],
            [height / 2,           0, 0],
        ], dtype=np.float32)

        self.program = Program(self.vertex_shader, self.frag_shader)
        self.program['position'] = self.vertices
        self.program['view'] = self.view
        self.program['model'] = self.model
        self.program['projection'] = self.projection
        self.program['color'] = np.array(color)

    def draw(self):
        self.program.draw('triangle_strip')
        # utils.Logger.log("Drawing my stuff")