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
        assert isinstance(worldpos, tuple), "World position specified invalid, should be tuple"
        assert len(worldpos) == 3, "World position invalid (should be length 3)"

        self.mesh = self.make_mesh()
        self.vert_shader, self.frag_shader = self.make_shaders()
        self.program = Program(self.vert_shader, self.frag_shader)
        self.program.bind(VertexBuffer(self.mesh))
        if hasattr(self, make_tex):
            self.texture = self.make_tex()
            assert isinstance(self.texture, Texture2D), "Texture passed is not a texture!"

        self.program['texture'] = self.texture
        cube["texture"].interpolation = 'linear'

    def __setitem__(self, key, value):
        self.rebind(key, value)

    def bind(self, key, value):
        '''Rebind a single program item to a value'''
        self.program[key] = value

    def bind_multiple(self, **kwargs):
        '''rebind multiple things!'''
        for key, item in kwargs:
            self.program[key] = item

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

        if self.mesh is None:
            vertices, indices, _ = create_cube()
            self.mesh = 
            
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

    def make_tex(self):
        '''Make a texture
        THIS IS A DEFAULT TEXTURE
        '''
        texture = utils.checkerboard()
        return texture

    @property
    def draw(self):
        self.program.draw()

class Drawable_List():
    def __init__(self, view, *args):
        self.drawables = args
        self.view = view

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

