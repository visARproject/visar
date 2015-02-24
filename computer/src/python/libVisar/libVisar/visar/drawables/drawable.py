import numpy as np
from ...OpenGL import utils

from vispy.geometry import create_cube
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer)


class Drawable(object):
    def __init__(self, *args, **kwargs):
        '''Drawable(*args, **kwargs) -> Drawable
        Everything is tracked internally, different drawables will handle things differently
        Inherit from this for all drawables.

        Inheriting:
            You must define a make_mesh, make_shaders, and draw method. 
            If you do not make shaders, you will get a default
            If you do not make a mesh, you'll get a square that takes up the screen

        '''
        self.model = np.eye(4)
        self.view = np.eye(4)
        self.projection = np.eye(4)

        self.mesh = self.make_mesh()
        self.vert_shader, self.frag_shader = self.make_shaders()
        self.program = Program(self.vert_shader, self.frag_shader)
        self.program.bind(VertexBuffer(self.mesh))
        if hasattr(self, make_texture):
            self.texture = self.make_texture()
            assert isinstance(self.texture, Texture2D), "Texture passed is not a texture!"

        self.program['texture'] = self.texture
        cube["texture"].interpolation = 'linear'

    def __setitem__(self, key, value):
        self.bind(key, value)

    def translate(self, *args):
        translate(self.model, *args)
        self.program['model'] = self.model

    def rotate(self, *args):
        rotate(self.model, *args)
        self.program['model'] = self.model

    def bind(self, key, value):
        '''Rebind a single program item to a value'''
        self.program[key] = value

    def bind_multiple(self, **kwargs):
        '''rebind multiple things!'''
        for key, value in kwargs:
            self.bind(key, value)

    def make_mesh(self):
        '''mesh()
        Generates a default mesh (a cube)
        treat it as though it is a property (i.e. not a function)
        ex:
        >>> x = Target((100, 100, 100))
        >>> mesh = Target.mesh
        '''
        cube = Program(cube_vertex, cube_fragment)
        cube.bind(vertices)
        self.program['model'] = model
        self.program['view'] = view
        self.program['projection'] = projection

        if self.mesh is None:
            vertices, indices, _ = create_cube()
            # self.mesh = 
            
        else:
            return self.mesh

    def make_shaders(self):
        '''shader -> (vertex, fragment) 
        Returns vertex and fragment shaders as 2-tuple of strings

        THIS IS A DEFAULT SHADER
        '''
        fragment = ''
        vertex = ''
        return vertex, fragment

    def make_texture(self):
        '''Make a texture
        THIS IS A DEFAULT TEXTURE
        '''
        texture = utils.checkerboard()
        return texture

    def draw(self):
        self.program.draw()

class Context(object):
    '''Note contexts are nestable (you can treat a context as a drawable)
    '''
    def __init__(self, *args):
        self.drawables = args
        self.view = np.eye(4)
        self.projection = np.eye(4)

    def __getitem__(self, key):
        return(self.drawables[key])

    def __setitem__(self, key, value):
        raise(Exception("You should not be attempting to set a drawable during operation...pop it instead"))

    def append(self, *args):
        for arg in args:
            self.drawables.append(arg)

    def pop(self, index):
        return self.drawables.pop(index)

    def translate(self, *args):
        translate(self.view, *args)
        for drawable in self.drawables:
            drawable['view'] = self.view

    def rotate(self, *args):
        rotate(self.view, *args)
        for drawable in self.drawables:
            drawable['view'] = self.view

    def set_projection(self, projection):
        self.projection = projection
        for drawable in self.drawables:
            drawable['projection'] = self.projection

    def set_view(self, view):
        self.view = view
        for drawable in self.drawables:
            drawable['view'] = self.view

    def on_resize(self):
        for drawable in self.drawables:
            drawable['projection'] = self.projection

    def draw(self):
        for drawable in self.drawables:
            drawable.draw()