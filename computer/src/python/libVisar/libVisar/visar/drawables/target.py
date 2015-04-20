from __future__ import division
import numpy as np
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer, set_state)
from vispy.util.transforms import perspective, translate, rotate
from vispy.geometry import create_sphere
from ...OpenGL.drawing import Drawable
from ...OpenGL import utils
from ..globals import State, Paths


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
            d = 10;
            T_billboard[0] = vec4(d,  0., 0., 0.);
            T_billboard[1] = vec4(0., d,  0., 0.);
            T_billboard[2] = vec4(0., 0., d,  0.);
            T_billboard[3] = T[3]; // Maintain original translation
            return T_billboard;
        }

        void main()
        {
            // Prevent rotation of the object relative to camera view
            mat4 coord_fix;
            coord_fix[0] = vec4(0.0, 0.0, -1.0, 0.0);
            coord_fix[1] = vec4(-1.0, 0.0, 0.0, 0.0);
            coord_fix[2] = vec4(0.0, 1.0, 0.0, 0.0);
            coord_fix[3] = vec4(0.0, 0.0, 0.0, 1.0);

            mat4 T = projection * coord_fix * view * model;
            // mat4 T = projection * coord_fix;

            mat4 T_billboard = make_billboard(T);

            // vec4 ecef_position = projection * view * model * vec4(position, 1.0);

            //gl_Position = T_billboard * vec4(position + vec3(0.0, 10.0, 0.0), 1.0);
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

    targets = {} # list of targets

    @classmethod
    def do_update(self, target_dict, context, projection):
        '''method to create/delete/update targets within the world'''
        pending_updates = [x for x in self.targets] # get list of all updates to be done
        
        for key in target_dict:
            pos = target_dict[key]['position_ecef'] # get the position
            try: # assume target is in list
                self.targets[key].move((pos['x'], pos['y'], pos['z'])) # issue the update
                pending_updates.remove(key) # mark target as updated
            except: # target is not already in list, add it
                target = Target((pos['x'], pos['y'], pos['z'])) # create object
                
                # setup projection matrix
                target.projection = projection
                target.program['projection'] = projection    
                
                context.append(target) # add to list of renders
                self.targets[key] = target # add to dictionary

        # remove old targets
        for key in pending_updates:         
            context.remove(self.targets[key]) # remove from render list
            # Remove from dictionary
            self.targets.pop(key)

    def __init__(self, world_pos, color=(1.0, 0.0, 0.5)):
        '''Target(world_pos, color) -> Target
        Arguments:
            world_pos - ECEF position of target
            color - specified as 3-tuple of floats with each element 
                in range [0, 1]. It is the color of the marker
        '''
        # Assertions
        assert isinstance(world_pos, tuple), "World position specified invalid, should be tuple"
        assert len(world_pos) == 3, "World position invalid (should be length 3)"
        assert max(color) <= 1.0, "Color should be in range [0.0, 1.0]"
        assert min(color) >= 0.0, "Color should be in range [0.0, 1.0]"
        assert len(color) == 3, "Color must be 3 channels (Ask Jacob if you want to do weird Alpha stuff)"

        self.world_pos = world_pos
        self.projection = np.eye(4)
        self.view = np.eye(4)
        # self.model = translate(np.eye(4), *world_pos)
        local_position = State.position_ecef - self.world_pos
        self.model = translate(np.eye(4), *local_position)

        height = 1.0  # Meters

        # This is a triangle of height $height
        self.vertices = np.array([
            [0.,           0.,     0.],
            [-height / 2., height, 0.],
            [+height / 2., height, 0.],
        ], dtype=np.float32)

        self.program = Program(self.vertex_shader, self.frag_shader)
        self.program['position'] = self.vertices
        self.program['view'] = self.view
        self.program['model'] = self.model
        self.program['projection'] = self.projection
        self.program['color'] = np.array(color)

    def update(self):
        # local_position = self.world_pos - State.position_ecef
        x, y, z = self.world_pos
        local_position = self.world_pos
        # local_position = np.array([-y, z, -x])
        self.program['model'] = translate(np.eye(4), *local_position)
        print np.dot(State.orientation_matrix, np.hstack([local_position, 1.0]))
        print State.orientation_matrix
        # print 'local {}'.format(local_position)

    def move(self, world_pos):
        '''Move this target to a new position'''
        # self.model = translate(np.eye(4), *world_pos)
        # self.program['model'] = self.model
        self.world_pos = world_pos
    
    def draw(self):
        self.program.draw('triangle_strip')
