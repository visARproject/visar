# -*- coding: utf-8 -*-
# vispy: gallery 30
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# Author:   Nicolas P .Rougier
# Date:     04/03/2014
# Abstract: Show post-processing technique using framebuffer
# Keywords: framebuffer, gloo, cube, post-processing
# -----------------------------------------------------------------------------

import numpy as np
import sys
from vispy import app

from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer, RenderBuffer, set_viewport, set_state)
from vispy import gloo
from .shaders import make_distortion
from .rift_parameters import parameters


cube_vertex = """
#version 120
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
attribute vec3 position;
attribute vec2 texcoord;
attribute vec3 normal;  // not used in this example
attribute vec4 color;  // not used in this example
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
    gl_FragColor = vec4(r, r, r, 1);
}
"""

quad_vertex = """
#version 120
attribute vec2 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
    v_texcoord = texcoord;
}
"""

quad_fragment = """
#version 120
uniform sampler2D texture;
varying vec2 v_texcoord;
void main()
{
    vec2 d = 5.0 * vec2(sin(v_texcoord.y * 50.0), 0) / 512.0;

    // Inverse video

    //if( v_texcoord.x > 0.5 ) {
    //    gl_FragColor.rgb = 1.0 - texture2D(texture, v_texcoord + d).rgb;
    //} else {
    //    gl_FragColor = texture2D(texture, v_texcoord);
    //}

    if (v_texcoord.x > 0.5) {
        gl_FragColor.rgb = vec3(texture2D(texture, v_texcoord)) / 4.0;
    } else {
        gl_FragColor = texture2D(texture, v_texcoord);
    }
}
"""


def checkerboard(grid_num=8, grid_size=32):
    row_even = grid_num // 2 * [0, 1]
    row_odd = grid_num // 2 * [1, 0]
    Z = np.row_stack(grid_num // 2 * (row_even, row_odd)).astype(np.uint8)
    return 255 * Z.repeat(grid_size, axis=0).repeat(grid_size, axis=1)


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, title='Framebuffer post-processing',
                            keys='interactive', size=(1920, 1080))

    def on_initialize(self, event):
        # Build cube data
        # --------------------------------------
        vertices, indices, _ = create_cube()
        vertices = VertexBuffer(vertices)
        self.indices = IndexBuffer(indices)

        # Build program
        # --------------------------------------
        self.view = np.eye(4, dtype=np.float32)
        model = np.eye(4, dtype=np.float32)
        translate(self.view, 0, 0, -7)
        self.phi, self.theta = 60, 20
        rotate(model, self.theta, 0, 0, 1)
        rotate(model, self.phi, 0, 1, 0)

        self.cube = Program(cube_vertex, cube_fragment)
        self.cube.bind(vertices)
        self.cube["texture"] = checkerboard()
        self.cube["texture"].interpolation = 'linear'
        self.cube['model'] = model
        self.cube['view'] = self.view

        l_eye = Texture2D((4096, 4096, 3), interpolation='linear')
        r_eye = Texture2D((4096, 4096, 3), interpolation='linear')

        self.left_eye_buffer = FrameBuffer(l_eye, RenderBuffer((4096, 4096)))
        self.right_eye_buffer = FrameBuffer(r_eye, RenderBuffer((4096, 4096)))

        # Not 100% Sure I understand what 'count' does
        self.quad = Program(quad_vertex, quad_fragment, count=4)
        self.quad['texcoord'] = [(0, 0), (0, 1), (1, 0), (1, 1)]
        self.quad['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        self.quad['texture'] = l_eye

        self.left_distortion, self.left_indices = make_distortion.Mesh.make_eye(l_eye, 'left')
        self.right_distortion, self.right_indices = make_distortion.Mesh.make_eye(r_eye, 'right')

        # OpenGL and Timer initalization
        # --------------------------------------
        set_state(clear_color=(.3, .3, .35, 1), depth_test=True)
        self.timer = app.Timer('auto', connect=self.on_timer, start=True)
        self._set_projection(self.size)

    def on_draw(self, event):
        with self.left_eye_buffer:
            set_viewport(0, 0, 4096, 4096)
            clear(color=True, depth=True)
            set_state(depth_test=True)
            self.cube.draw('triangles', self.indices)
        with self.right_eye_buffer:
            set_viewport(0, 0, 4096, 4096)
            translate(self.view, 0, 4, 0)
            self.cube['view'] = self.view

            clear(color=True, depth=True)
            set_state(depth_test=True)
            self.cube.draw('triangles', self.indices)

        set_viewport(0, 0, *self.size)

        clear(color=True)
        # gloo.set_clear_color('white')

        set_state(depth_test=False)
        self.quad.draw('triangle_strip')
        # self.left_distortion.draw('triangles', indices=self.left_indices)
        # self.right_distortion.draw('triangles', indices=self.right_indices)

    def on_resize(self, event):
        self._set_projection(event.size)

    def on_mouse_move(self, event):
        pos = np.array(event.pos)
        if event.is_dragging and (1 in event.buttons):  # Mouse-Left click-drag
            delta = pos - np.array(event.last_event.pos)
            self.phi += delta[0]/5
            self.theta -= delta[1]/5

    def on_key_press(self, event):
        if event.text == 'q':
            sys.exit()

    def _set_projection(self, size):
        width, height = size
        set_viewport(0, 0, width, height)
        # projection = perspective(30.0, width / float(height), 2.0, 10.0)
        projection = parameters.projection_left
        self.cube['projection'] = projection
        # view = parameters.ortho_left # Added
        # self.cube['view'] = view  # Added

    def on_timer(self, event):
        self.theta += .5
        self.phi += .5
        model = np.eye(4, dtype=np.float32)
        rotate(model, self.theta, 0, 0, 1)
        rotate(model, self.phi, 0, 1, 0)
        self.cube['model'] = model
        self.update()

if __name__ == '__main__':
    c = Canvas()
    c.show()
    c.app.run()