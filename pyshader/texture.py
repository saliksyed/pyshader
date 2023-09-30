from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGL.GL.ARB.color_buffer_float import * 
from OpenGL.raw.GL.ARB.color_buffer_float import * 
import numpy as np
import random
from PIL import Image
import random

class Texture:
    def __init__(self, name, tformat=GL_RGBA, wrap=GL_CLAMP_TO_EDGE, tfilter=GL_NEAREST, ttype=GL_UNSIGNED_BYTE, tinternal_format=GL_RGBA):
        self.name = name
        self.wrap =  wrap
        self.filter = tfilter
        self.format = tformat
        self.type = ttype
        self.texture = glGenTextures(1)
        self.internal_format = tinternal_format
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self.wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self.wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self.filter)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self.filter)

    def dtype(self):
        return 'float32' if self.type == GL_FLOAT else 'uint8'

    def read(self, width, height):
        dtype = self.dtype()
        num_items = width*height*4
        glBindTexture(GL_TEXTURE_2D, self.texture);
        if dtype == 'uint8':
            return np.frombuffer(glGetTexImage(GL_TEXTURE_2D, 0, self.format, self.type), np.uint8)
        else:
            return np.frombuffer(glGetTexImage(GL_TEXTURE_2D, 0, self.format, self.type), np.float32)

    def blank(self, width, height):
        source_copy = np.array([[0, 0, 0, 255] for i in range(0, int(width*height))], copy=True)
        glBindTexture(GL_TEXTURE_2D, self.texture);
        glTexImage2D(GL_TEXTURE_2D, 0, self.internal_format, width, height, 0, self.format, self.type, source_copy)

    def set(self, source, width, height):
        source_copy = np.array(source, dtype=self.dtype(), copy=True)
        glBindTexture(GL_TEXTURE_2D, self.texture);
        glTexImage2D(GL_TEXTURE_2D, 0, self.internal_format, width, height, 0, self.format, self.type, source_copy)

    def noise(self, width, height):
        source_copy = np.array([[int(255*random.random()), int(255*random.random()), int(255*random.random()), int(255*random.random())] for i in range(0, int(width*height))], copy=True)
        glBindTexture(GL_TEXTURE_2D, self.texture);
        glTexImage2D(GL_TEXTURE_2D, 0, self.internal_format, width, height, 0, self.format, self.type, source_copy)        
