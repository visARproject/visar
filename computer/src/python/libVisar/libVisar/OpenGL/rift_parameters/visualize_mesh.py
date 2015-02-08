'''
Experimenting with visualizing the appropriate distortion mesh

'''
from __future__ import division

import numpy as np
import sys
from vispy import app

from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer, RenderBuffer, set_viewport, set_state)

from .read_map import read_map
import os
fpath = os.path.dirname(os.path.realpath(__file__))

vertex = """
uniform mat4 rotation;
attribute vec2 screen_pos;
attribute vec2 red_xy;
attribute vec2 green_xy;
attribute vec2 blue_xy;

varying vec2 v_texcoord;

void main() {
    gl_Position = rotation * vec4(screen_pos, 0.0, 1.0); // Maybe elem 2 should be 1.0 for 1.0 zplane?
    v_texcoord = red_xy;
    gl_PointSize = 2;
}
"""

fragment = """
uniform sampler2D texture;
varying vec2 v_texcoord;

void main() {
    gl_FragColor = texture2D(texture, v_texcoord);
}

"""



cube_vertex = """
attribute vec2 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 1.0, 1.0);
    v_texcoord = texcoord;
}
"""

cube_fragment = """
uniform sampler2D texture;
varying vec2 v_texcoord;
void main()
{
    float r = texture2D(texture, v_texcoord).r;
    gl_FragColor = vec4(r, r, r, 1);
}
"""

def scale_between(value, v_min, v_max, _min, _max):
    v_ranged = (value - v_min) / (v_max - v_min)
    normalized = ((_max - _min) * v_ranged) + _min
    return normalized

def make_sheet((x_len, y_len)):
    '''Create the deformation mesh for a single eye
    This takes a pretty long time to generate

    '''
    vertices = np.zeros(x_len * y_len, dtype=[
        ('position', np.float32, 3),
        ('texcoord', np.float32, 2),
    ])
    for x in range(0, x_len):
        for y in range(0, y_len):
            index = (x * y_len) + y
            x_sc = scale_between(x, 0, x_len, -1, 1)
            y_sc = scale_between(y, 0, y_len, -1, 1)
            vertices['position'][index] = np.array([x_sc, y_sc, 0.0])
            vertices['texcoord'][index] = np.array([x / x_len, y / y_len])

    indices = None
    return vertices, indices

def make_distortion():
    # mapping = read_map()
    # mapping['screen_pos'] /= np.array([960, 1080])
    print "Starting screen pos remap"
    try:
        mapping = np.load(os.path.join(fpath, 'normalized_map.npy'))
    except IOError:
        mapping = read_map()
        mapping['screen_pos'] = np.apply_along_axis(lambda o: (
                        scale_between(o[0], 0, 960, -1, 1), 
                        scale_between(o[1], 0, 1080, -1, 1)
                    ),
                    1,
                    mapping['screen_pos']
            )
    np.save('normalized_map.npy', mapping)
    print "Ending screen pos remap"
    return mapping

def checkerboard(grid_num=8, grid_size=32):
    row_even = grid_num // 2 * [0, 1]
    row_odd = grid_num // 2 * [1, 0]
    Z = np.row_stack(grid_num // 2 * (row_even, row_odd)).astype(np.uint8)
    return 255 * Z.repeat(grid_size, axis=0).repeat(grid_size, axis=1)

class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, title='Visualize Mesh',
                            keys='interactive', size=(1920, 1080))

    def on_initialize(self, event):
        self.rho = 0.0
        # Build cube data
        # --------------------------------------
        self.checker = Program(cube_vertex, cube_fragment)
        self.checker['texture'] = checkerboard()
        self.checker['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        self.checker['texcoord'] = [(0, 0), (0, 1), (1, 0), (1, 1)]

        # sheet, indices = make_sheet((960, 1080))
        # sheet_buffer = VertexBuffer(sheet)

        left_eye = Texture2D((960, 1080, 3), interpolation='linear')
        self.left_eye_buffer = FrameBuffer(left_eye, RenderBuffer((960, 1080)))
        # Build program
        # --------------------------------------
        self.view = np.eye(4, dtype=np.float32)
        self.program = Program(vertex, fragment)
        distortion_buffer = VertexBuffer(make_distortion())
        self.program.bind(distortion_buffer)
        self.program['rotation'] = self.view
        self.program['texture'] = left_eye

        # OpenGL and Timer initalization
        # --------------------------------------
        set_state(clear_color=(.3, .3, .35, 1), depth_test=True)
        self.timer = app.Timer('auto', connect=self.on_timer, start=True)
        self._set_projection(self.size)

    def on_draw(self, event):
        with self.left_eye_buffer:
            set_viewport(0, 0, *self.size)
            clear(color=True)
            set_state(depth_test=False)
            self.checker.draw('triangle_strip')
        set_viewport(0, 0, *self.size)
        clear(color=True)
        set_state(depth_test=True)
        self.program.draw('points')

    def on_resize(self, event):
        self._set_projection(event.size)

    def on_mouse_move(self, event):
        pos = np.array(event.pos)

    def on_key_press(self, event):
        if event.text == 'q':
            sys.exit()

    def _set_projection(self, size):
        width, height = size
        set_viewport(0, 0, width, height)
        projection = perspective(30.0, width / float(height), 2.0, 10.0)
        # self.program['projection'] = projection

    def on_timer(self, event):
        self.rho = 0.1
        if self.rho >= 30:
            self.rho = 0

        self.update()

if __name__ == '__main__':
    c = Canvas()
    c.show()
    c.app.run()