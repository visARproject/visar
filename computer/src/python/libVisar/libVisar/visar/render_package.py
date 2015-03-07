from __future__ import division
import numpy as np
from vispy.util.transforms import perspective, translate, rotate
from vispy.gloo import (Program, VertexBuffer, IndexBuffer, Texture2D, clear,
                        FrameBuffer)
from vispy.util.transforms import perspective, translate, xrotate, yrotate
from vispy.util.transforms import zrotate

from vispy import gloo
from vispy import app

from ..OpenGL.utils import Logger
from ..OpenGL.shaders import Distorter
from .drawables import Context, Example, Target
from .environments import Terrain

# Presets
HUD_DEPTH = 5 # Minimum depth (Specified by Oculus docs)
FPS = 60 # Maximum FPS (how often needs_update is checked)

class Renderer(app.Canvas): # Canvas is a GUI object
    def __init__(self, size=(1980, 1020)):    
        # Create a rendering context (A render list)
        Logger.set_verbosity('log')
        ex = Example()
        terrain = Terrain()
        target = Target((1, 1, 1))

        self.default_view = np.array(
            [[0.8, 0.2, -0.48, 0],
             [-0.5, 0.3, -0.78, 0],
             [-0.01, 0.9, -0.3, 0],
             [-4.5, -21.5, -7.4, 1]],
             dtype=np.float32
        )

        self.view = np.eye(4)
        self.Render_List = Context(ex, terrain, target)
        self.Render_List.translate(0, 0, -7)
        projection = perspective(30.0, 1920 / float(1080), 2.0, 10.0)
        self.Render_List.set_projection(projection)
        self.Render_List.set_view(self.view)
        # Initialize gloo context
        app.Canvas.__init__(self, keys='interactive')
        self.size = size 

        # Create the distorter
        self.Distorter = Distorter(self.size)

        # Set an update timer to run every FPS
        self.interval = 1 / FPS
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
  
    def on_timer(self, event):
        self.Render_List.set_view(self.view)
        self.update()

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)
        self.Render_List.on_resize()
    
    def on_draw(self, event):
        # Draw each drawable using the distorter
        gloo.set_viewport(0, 0, *self.size)
        gloo.clear(color=True)
        gloo.set_clear_color('white')

        gloo.set_state(depth_test=True)
        self.Distorter.draw(self.Render_List)

    def on_key_press(self, event):
        """Controls -
        a(A) - move left
        d(D) - move right
        w(W) - move up
        s(S) - move down
        x/X - rotate about x-axis cw/anti-cw
        y/Y - rotate about y-axis cw/anti-cw
        z/Z - rotate about z-axis cw/anti-cw
        space - reset view
        p(P) - print current view
        i(I) - zoom in
        o(O) - zoom out
        """
        self.translate = [0, 0, 0]
        self.rotate = [0, 0, 0]

        if(event.text == 'p' or event.text == 'P'):
            print(self.view)
        elif(event.text == 'd' or event.text == 'D'):
            self.translate[0] = 0.3
        elif(event.text == 'a' or event.text == 'A'):
            self.translate[0] = -0.3
        elif(event.text == 'w' or event.text == 'W'):
            self.translate[1] = 0.3
        elif(event.text == 's' or event.text == 'S'):
            self.translate[1] = -0.3
        elif(event.text == 'o' or event.text == 'O'):
            self.translate[2] = 0.3
        elif(event.text == 'i' or event.text == 'I'):
            self.translate[2] = -0.3
        elif(event.text == 'x'):
            self.rotate = [1, 0, 0]
        elif(event.text == 'X'):
            self.rotate = [-1, 0, 0]
        elif(event.text == 'y'):
            self.rotate = [0, 1, 0]
        elif(event.text == 'Y'):
            self.rotate = [0, -1, 0]
        elif(event.text == 'z'):
            self.rotate = [0, 0, 1]
        elif(event.text == 'Z'):
            self.rotate = [0, 0, -1]
        elif(event.text == ' '):
            self.view = self.default_view

        translate(self.view, -self.translate[0], -self.translate[1],
                  -self.translate[2])
        xrotate(self.view, self.rotate[0])
        yrotate(self.view, self.rotate[1])
        zrotate(self.view, self.rotate[2])

    
def main():
    c = Renderer()
    c.show()
    c.app.run()


if __name__ == '__main__':
    main()