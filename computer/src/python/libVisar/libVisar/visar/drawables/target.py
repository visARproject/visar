from .drawable import Drawable
import numpy as np


class Targets(drawable):
    super(Target, self).__init__()
    pass


class Target(object):
    def __init__(self, world_pos, color=(1.0, 0.0, 0.5)):
        '''Target(world_pos, color) -> Target
        Arguments:
            world_pos - absolute (GPS long-lat) position of marker
            color - specified as 3-tuple of floats with each element 
                in range [0, 1]. It is the color of the marker
        '''
        assert isinstance(worldpos, tuple), "World position specified invalid, should be tuple"
        assert len(worldpos) == 3, "World position invalid (should be length 3)"
        self.mesh = None

    def mesh(self):
        '''mesh(), virtual property
        Generates and/or returns a triangle mesh

        treat it as though it is a property (i.e. not a function)
        ex:
        >>> x = Target((100, 100, 100))
        >>> mesh = Target.mesh()
        '''
        if self.mesh is None:
            self.mesh = np.zeros(3, 
                dtype=[
                    ('a_pos', np.float32, 3),
                    ('a_color', np.float32, 3),
                ]
            )

        else:
            return self.mesh

    def shader(self):
        '''shader -> (vertex, fragment) 
        Returns vertex and fragment shaders as 2-tuple of strings
        '''
        fragment = ''
        vertex = ''
        return vertex, fragment

    @property
    def draw(self):
        pass