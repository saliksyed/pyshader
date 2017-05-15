from pyshader import Renderer, VBO
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import * 
import math

class PointCloudExample(Renderer):
    def __init__(self, resolution):
        Renderer.__init__(self, resolution)
        self.tick = 0
        self.vbo = VBO(GL_POINTS)
        self.vbo.load_ply('data/manhattan_1mm_points.ply')
        self.shader('points','shaders/render_point.frag', 'shaders/project_point.vert', self.vbo)
        glutKeyboardFunc(self.move)
        self.eye_pos = [-4.95, 13.65, -10.43]
        self.target_dist = 10.
        self.angle = 0.0
        self.tilt_angle = 0.0

    def move(self, key, x, y):
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

    def draw(self):
        # Extend the draw method with your rendering logic!
        self.tick += 1.0 / 30.0
        
        # enable alpha blending and point sprites
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); 
        glEnable(GL_POINT_SPRITE);
        glClearColor(0.,0.,0.,1.)
        glClear(GL_COLOR_BUFFER_BIT);
        
        # We first render the light using horizontal_light.frag into a texture
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.5, 10., 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        target_pos = [self.eye_pos[0] + self.target_dist * math.cos(self.angle), self.eye_pos[1], self.eye_pos[2] + self.target_dist * math.sin(self.angle)]
        target_pos[1] += self.target_dist * math.sin(self.tilt_angle)
        gluLookAt(self.eye_pos[0], self.eye_pos[1], self.eye_pos[2], target_pos[0], target_pos[1], target_pos[2], 0, 1., 0)
        (self.shader('points')
                .tick(self.tick)
                .draw())


# Renders the example visualization in a GLUT window
if __name__ == '__main__':
    viz = PointCloudExample(Renderer.RES720P)
    viz.run()