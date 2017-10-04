from pyshader import VBO, Renderer, Editor
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import * 
import math

"""
    This example shows a multi-pass shader that renders a a point cloud 
    with depth of field.


"""

class PointCloudExample(Editor):
    def __init__(self, resolution):
        Editor.__init__(self, resolution)
        self.tick = 0
        self.vbo = VBO(GL_POINTS)
        self.vbo.load_ply('data/manhattan_1mm_points.ply')

        # This shader will render the points normally to a texture
        self.shader('points','shaders/render_point.frag', 'shaders/project_point.vert', self.vbo)
        
        # This shader will render just the depth to a texture
        self.shader('depth','shaders/render_depth.frag', 'shaders/project_point.vert', self.vbo)

        # the Depth-Of-Field shader will take the depth image, point image and blur using the distance
        self.shader('dof','shaders/render_dof.frag')        

    def draw(self):
        self.tick += 1.0 / 30.0
        
        glPushMatrix()
        self.setup_scene()
        (self.shader('points')
                .tick(self.tick)
                .drawTo('baseImage'))
        glClearColor(1.,1.,1.,1.)
        glClear(GL_COLOR_BUFFER_BIT)
        (self.shader('depth')
                .tick(self.tick)
                .drawTo('depthImage'))
        glPopMatrix()

        (self.shader('dof')
                .tick(self.tick)
                .input('baseImage', withName='iChannel0')
                .input('depthImage', withName='iChannel1')
                .uniform('minDistInFocus', 0.01)
                .uniform('maxDistInFocus', 0.15)
                .uniform('maxNearBlur', 6.0)
                .uniform('maxFarBlur', 1.0)
                .draw())




# # Renders the example visualization in a GLUT window


import tkinter as tk
from tkinter import Label, Button

import threading

class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        label = tk.Label(self.root, text="Hello World")
        label.pack()

        self.close_button = Button(self.root, text="Close", command=self.root.quit)
        self.close_button.pack()


        self.root.mainloop()


app = App()
print('Now we can continue running code while mainloop runs!')


viz = PointCloudExample(Renderer.RES4K)
# viz.run()