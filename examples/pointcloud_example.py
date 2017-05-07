from pyshader import Renderer, VBO
import numpy
from OpenGL.GL import *

"""
    This example shows rendering a camera to display a point cloud map of Manhattan
"""
class PointCloudExample(Renderer):
    def __init__(self, resolution):
        Renderer.__init__(self, resolution)
        self.tick = 0
        self.vbo = VBO(GL_POINTS)
        self.vbo.load_ply('data/manhattan_1mm_points.ply')
        self.shader('points','shaders/render_point.frag', 'shaders/project_point.vert', self.vbo)

    def draw(self):
        # Extend the draw method with your rendering logic!
        self.tick += 1.0 / 30.0
        # step to the next frame of the video
        
        # We first render the light using horizontal_light.frag into a texture
        mat = numpy.array([0.3, 0, 0, 0, 0, 0.3, 0, 0, 0, 0, 0.3, 0, 0, 0, 0, 1], numpy.float32)
        (self.shader('points')
                .uniform('projection', mat)
                .uniform('view', mat)
                .uniform('model', mat)
                .tick(self.tick)
                .draw())


# Renders the example visualization in a GLUT window
if __name__ == '__main__':
    viz = PointCloudExample(Renderer.RES720P)
    viz.run()