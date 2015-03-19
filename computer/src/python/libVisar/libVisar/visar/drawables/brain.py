
from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer)
import numpy as np
from vispy import gloo
from vispy import app
from vispy.util.transforms import perspective, translate, rotate
from vispy.io import load_data_file
from ...OpenGL.drawing import Drawable
from ...OpenGL import utils

class Brain(Drawable):

    VERT_SHADER = """
    #version 120
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    uniform vec4 u_color;

    attribute vec3 a_position;
    attribute vec3 a_normal;
    attribute vec4 a_color;

    varying vec3 v_position;
    varying vec3 v_normal;
    varying vec4 v_color;

    void main()
    {
        v_normal = a_normal;
        v_position = a_position;
        v_color = a_color * u_color;
        gl_Position = projection * view * model * vec4(a_position,1.0);
    }
    """

    FRAG_SHADER = """
    #version 120
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 u_normal;

    uniform vec3 u_light_intensity;
    uniform vec3 u_light_position;

    varying vec3 v_position;
    varying vec3 v_normal;
    varying vec4 v_color;

    void main()
    {
        // Calculate normal in world coordinates
        vec3 normal = normalize(u_normal * vec4(v_normal,1.0)).xyz;

        // Calculate the location of this fragment (pixel) in world coordinates
        vec3 position = vec3(view*model * vec4(v_position, 1));

        // Calculate the vector from this pixels surface to the light source
        vec3 surfaceToLight = u_light_position - position;

        // Calculate the cosine of the angle of incidence (brightness)
        float brightness = dot(normal, surfaceToLight) /
                          (length(surfaceToLight) * length(normal));
        brightness = max(min(brightness,1.0),0.0);

        // Calculate final color of the pixel, based on:
        // 1. The angle of incidence: brightness
        // 2. The color/intensities of the light: light.intensities
        // 3. The texture and texture coord: texture(tex, fragTexCoord)

        // Specular lighting.
        vec3 surfaceToCamera = vec3(0.0, 0.0, 1.0) - position;
        vec3 K = normalize(normalize(surfaceToLight) + normalize(surfaceToCamera));
        float specular = clamp(pow(abs(dot(normal, K)), 40.), 0.0, 1.0);

        gl_FragColor = v_color * brightness * vec4(u_light_intensity, 1);
    }
    """

    def __init__(self):
        self.program = gloo.Program(self.VERT_SHADER, self.FRAG_SHADER)

        brain = np.load(load_data_file('brain/brain.npz', force_download='2014-09-04'))
        data = brain['vertex_buffer']
        faces = brain['index_buffer']

        self.theta, self.phi = -80, 180
        self.translate = 3

        self.faces = gloo.IndexBuffer(faces)
        self.program.bind(gloo.VertexBuffer(data))

        self.model = translate(np.eye(4), 0, 0, -5)
        self.program['model'] = self.model

        self.view = np.eye(4)
        self.program['view'] = self.view
        self.program['u_color'] = 1, 1, 1, 1
        self.program['u_light_position'] = (1., 1., 1.)
        self.program['u_light_intensity'] = (1., 1., 1.)


        self.projection = np.eye(4)
        self.program['projection'] = self.projection

    def update(self):
        # self.program['model'] = self.model
        # self.program['view'] = self.view
        self.program['u_normal'] = np.array(np.matrix(np.dot(self.view,
                                                             self.model)).I.T)
        pass

    def draw(self):
        self.program.draw('triangles', indices=self.faces)


