from ..OpenGL.utils.transformations import quaternion_matrix
from ..OpenGL.utils import Logger

def main():
    ex_quat = {"x": 0.50155109,  "y": 0.03353513,  "z": 0.05767266, "w": 0.86255189}
    orientation_quaternion = (0.50155109, 0.03353513, 0.05767266, 0.86255189)
    matrix =  quaternion_matrix(orientation_quaternion)
    Logger.set_verbosity('log')
    Logger.log( matrix )
    Logger.log( type(matrix) )
    Logger.warn( matrix.shape )


    ''' The plan here is to contruct a new view matrix for the targets each frame
    As for the map and other UI elements, they don't need a view matrix
    '''

    
