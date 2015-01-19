import rendering
import numpy as np
import cv2
from vispy import app

im1 = cv2.cvtColor(np.flipud(cv2.imread('Red_Apple.jpg')), cv2.COLOR_BGR2RGB)

renderer = rendering.Renderer() # init the renderer

# create two modules (using a test image)
d1 = rendering.Drawable() 
d1.setTexture(im1)
d1.setVerticies([[-1,-1],[0,-1],[-1,0],[0,0]]) # no depth (automatically set at 1)
renderer.addModule(d1) # this interface might change later

d2 = rendering.Drawable()
d2.setTexture(im1)
d2.setVerticies([[-.2,-.2,0],[1,-.2,0],[-.2,1,0],[1,1,0]]) # has depth=0
renderer.addModule(d2)

# start the renderer (will be packaged elsewhere later)
renderer.show()
app.run()

