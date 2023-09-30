from vbo import VBO
from renderer import Renderer
from editor import Editor
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
                .use()
                .tick(self.tick)
                .drawTo('baseImage'))
        glClearColor(1.,1.,1.,1.)
        glClear(GL_COLOR_BUFFER_BIT)
        (self.shader('depth')
                .use()
                .tick(self.tick)
                .drawTo('depthImage'))
        glPopMatrix()

        (self.shader('dof')
                .use()
                .tick(self.tick)
                .input('baseImage', withName='iChannel0')
                .input('depthImage', withName='iChannel1')
                .uniform('minDistInFocus', 0.01)
                .uniform('maxDistInFocus', 0.15)
                .uniform('maxNearBlur', 6.0)
                .uniform('maxFarBlur', 1.0)
                .draw())




# Renders the example visualization in a GLUT window
if __name__ == '__main__':
    viz = PointCloudExample(Renderer.RES4K)
    viz.run()