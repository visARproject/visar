from ...OpenGL.utils.transformations import quaternion_matrix

class State(object):
    '''Track the global state of the VisAR unit'''
    targets = [
        (10, 10, 10),
    ]

    # ex_quat = {"x": 0.50155109,  "y": 0.03353513,  "z": 0.05767266, "w": 0.86255189}
    orientation_quaternion = (0.50155109, 0.03353513, 0.05767266, 0.86255189)
    orientation_matrix =  quaternion_matrix(orientation_quaternion)

    @classmethod
    def set_orientation(self, quaternion):
        self.orientation_quaternion = quaternion
        self.orientation_quaternion = quaternion_matrix(quaternion)

    