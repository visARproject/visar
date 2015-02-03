import numpy as np

# These matrices were manually extracted from the Rift SDK
# They correspond to the left and right eyes

projection_left = np.matrix([
    [0.929789, 0, 0.0156718, 0],
    [0, 0.752283, 0, 0],
    [0, 0, -1, -0.01],
    [0, 0, -1, 0],
])

projection_right = np.matrix([
    [0.929789, 0, 0.0156718, 0],
    [0, 0.752283, 0, 0],
    [0, 0, -1, -0.01],
    [0 ,0 ,-1 ,0],
])

ortho_left = np.matrix([
    [0.0016917, 0, 0, 0.0215198],
    [0, -0.00136874, 0, -0],
    [0, 0, 0, 0],
    [0, 0, 0, 1],
])
ortho_right = np.matrix([
    [0.0016917, 0, 0, -0.0215198],
    [0, -0.00136874, 0, -0],
    [0, 0, 0, 0],
    [0, 0, 0, 1 ],
])

surface_size = 4096
surface_depth = 64
