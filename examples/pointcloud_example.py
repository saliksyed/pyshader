from pyshader import Renderer, VBO
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import * 
import math

"""
    This example shows a multi-pass shader that renders a a point cloud 
    with depth of field.


"""

class PointCloudExample(Renderer):
    def __init__(self, resolution):
        Renderer.__init__(self, resolution)
        self.tick = 0
        self.vbo = VBO(GL_POINTS)
        self.vbo.load_ply('data/manhattan_1mm_points.ply')

        # This shader will render the points normally to a texture
        self.shader('points','shaders/render_point.frag', 'shaders/project_point.vert', self.vbo)
        
        # This shader will render just the depth to a texture
        self.shader('depth','shaders/render_depth.frag', 'shaders/project_point.vert', self.vbo)

        # the Depth-Of-Field shader will take the depth image, point image and blur using the distance
        self.shader('dof','shaders/render_dof.frag')

        glutKeyboardFunc(self.move)
        self.eye_pos = [-4.95, 13.65, -10.43]
        self.target_dist = 10.
        self.angle = 0.0
        self.tilt_angle = 0.0

    def move(self, key, x, y):
        """
            Handle keyboard controls
        """
        if key == 'w':
            self.eye_pos[0] += 0.5 * math.cos(self.angle)
            self.eye_pos[2] += 0.5 * math.sin(self.angle)
        elif key == 'a':
            self.angle -= 0.05
        elif key == 's':
            self.eye_pos[0] -= 0.5 * math.cos(self.angle)
            self.eye_pos[2] -= 0.5 * math.sin(self.angle)
        elif key == 'd':
            self.angle += 0.05
        elif key == 'q':
            self.eye_pos[1]+=0.1
        elif key == 'z':
            self.eye_pos[1]-=0.1
        elif key == 'e':
            self.tilt_angle+=0.1
        elif key == 'c':
            self.tilt_angle-=0.1

    def setup_scene(self):
        glEnable(GL_POINT_SPRITE);
        # setup the projection, modelview matrices
        glClearColor(0.,0.,0.,1.)
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.5, 0.1, 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # compute the eye position, target position of our camera
        target_pos = [self.eye_pos[0] + self.target_dist * math.cos(self.angle), self.eye_pos[1], self.eye_pos[2] + self.target_dist * math.sin(self.angle)]
        target_pos[1] += self.target_dist * math.sin(self.tilt_angle)
        gluLookAt(self.eye_pos[0], self.eye_pos[1], self.eye_pos[2], target_pos[0], target_pos[1], target_pos[2], 0, 1., 0)
        

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




# Renders the example visualization in a GLUT window
if __name__ == '__main__':
    viz = PointCloudExample(Renderer.RES1080P)
    viz.run()