from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL.ARB.color_buffer_float import * 
from OpenGL.raw.GL.ARB.color_buffer_float import * 
from vbo import VBO
import numpy as np

class VertexAttr(VBO):
    def __init__(self, name, vertices=None):
        VBO.__init__(self, GL_POINTS, vertices=vertices)
        self.name = name

    def bind(self, program=None):
        loc = glGetAttribLocation(program, self.name)
        glEnableVertexAttribArray(loc)
        self.vbo.bind()
        glVertexAttribPointer(loc, 3, GL_FLOAT, GL_FALSE, 0, self.vbo)
        self.vbo.unbind()

    def unbind(self):
        raise 'Cannot unbind vertex attribute'

    def draw(self, clear=True):
        raise 'Cannot draw vertex attribute'
