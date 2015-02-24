'''This is from vispy.org, excepting rift stuff'''
from vispy import gloo
from vispy import app
import numpy as np
from scipy.spatial import Delaunay
from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer, RenderBuffer, set_viewport, set_state)

from ..drawables import Drawable
from ...OpenGL.utils import Logger


# Arrays for storing generated points and triangles
points = []
triangles = []
height = 0.0


def generate_terrain(r_min, r_max, c_min, c_max, disp):
    """Recursively generates terrain using diamond-square algorithm
    and stores the vertices in points
    """
    a = points[r_min][c_min][2]
    b = points[r_min][c_max][2]
    c = points[r_max][c_min][2]
    d = points[r_max][c_max][2]

    r_mid = (r_min + r_max)/2
    c_mid = (c_min + c_max)/2

    # e = (a+b+c+d)/4 + np.random.uniform(0, disp)
    e = (a+b+c+d)/4 + np.random.uniform(-disp/2, disp/2)

    points[r_mid][c_mid][2] = e

    # points[r_min][c_mid][2] = (a + b + e)/3 + np.random.uniform(0, disp)
    # points[r_max][c_mid][2] = (c + d + e)/3 + np.random.uniform(0, disp)
    # points[r_mid][c_min][2] = (a + c + e)/3 + np.random.uniform(0, disp)
    # points[r_mid][c_max][2] = (b + d + e)/3 + np.random.uniform(0, disp)

    points[r_min][c_mid][2] = (a + b + e)/3 + np.random.uniform(-disp/2, disp/2)
    points[r_max][c_mid][2] = (c + d + e)/3 + np.random.uniform(-disp/2, disp/2)
    points[r_mid][c_min][2] = (a + c + e)/3 + np.random.uniform(-disp/2, disp/2)
    points[r_mid][c_max][2] = (b + d + e)/3 + np.random.uniform(-disp/2, disp/2)

    new_disp = disp * (2 ** (-0.5))

    if (r_mid - r_min > 1 or c_mid - c_min > 1):
        generate_terrain(r_min, r_mid, c_min, c_mid, new_disp)
    if (r_max - r_mid > 1 or c_mid - c_min > 1):
        generate_terrain(r_mid, r_max, c_min, c_mid, new_disp)
    if (r_mid - r_min > 1 or c_max - c_mid > 1):
        generate_terrain(r_min, r_mid, c_mid, c_max, new_disp)
    if (r_max - r_mid > 1 or c_max - c_mid > 1):
        generate_terrain(r_mid, r_max, c_mid, c_max, new_disp)


def generate_points(length=3):
    """Generates points via recursive function and generate triangles using
    Scipy Delaunay triangulation

    Parameters
    ----------
    length : int
        (2 ** length + 1 by 2 ** length + 1) number of points is generated

    """
    Logger.log("Points are being generated...")
    global points, triangles, height
    size = 2**(length) + 1
    points = np.indices((size, size, 1)).T[0].transpose((1, 0, 2))
    points = points.astype(np.float32)
    generate_terrain(0, size-1, 0, size-1, length)
    height = length
    points = np.resize(points, (size*size, 3))
    points2 = np.delete(points, 2, 1)

    points3 = points2 - np.mean(points2, 0)

    tri = Delaunay(points3)
    triangles = points[tri.simplices]
    triangles = np.vstack(triangles)
    Logger.log("Points successfully generated.")


VERT_SHADER = """
uniform   float u_height;
uniform   mat4 model;
uniform   mat4 view;
uniform   mat4 projection;
attribute vec3  a_position;
varying vec4 v_color;

void main (void) {
    gl_Position = projection * view * model * vec4(a_position.xy, a_position.z * 2, 1.0);
    float r = a_position[2] * a_position[2] / (u_height * u_height * u_height);
    v_color = vec4(r / 1.4, r, 0.1, 1.0);
}
"""

FRAG_SHADER = """
varying vec4 v_color;

void main()
{
    gl_FragColor = v_color;
}
"""


class Terrain(Drawable):
    def __init__(self):
        generate_points(8)
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        #Sets the view to an appropriate position over the terrain
        self.default_view = np.array([[0.8, 0.2, -0.48, 0],
                                     [-0.5, 0.3, -0.78, 0],
                                     [-0.01, 0.9, -0.3, 0],
                                     [-4.5, -21.5, -7.4, 1]],
                                     dtype=np.float32)

        self.view = self.default_view
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        self.translate = [0, 0, 0]
        self.rotate = [0, 0, 0]

        self.program['u_height'] = height
        self.program['model'] = self.model
        self.program['view'] = self.view
        self.program['a_position'] = gloo.VertexBuffer(triangles)
        self.program['projection'] = self.projection


    def draw(self):
        self.program.draw('triangles')
