from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL.ARB.color_buffer_float import * 
from OpenGL.raw.GL.ARB.color_buffer_float import * 
from helpers import read_points_from_ply
import numpy as np

class VertexAttr:
    def __init__(self, name, vertices=None):
        self.name = name
        if vertices != None:
            self.set_data(vertices)

    def set_data(self, vertices):
        self.vertices = vertices
        self.vbo = vbo.VBO(np.array(vertices,'float32'))

    def load_ply(self, fname):
        self.set_data(read_points_from_ply(fname))

    def bind(self, program=None):
        loc = glGetAttribLocation(program, self.name)
        glEnableVertexAttribArray(loc)
        self.vbo.bind()
        glVertexAttribPointer(loc, 3, GL_FLOAT, GL_FALSE, 0, self.vbo)
        self.vbo.unbind()
