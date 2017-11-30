from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGL.GL.ARB.color_buffer_float import * 
from OpenGL.raw.GL.ARB.color_buffer_float import * 

class RenderTarget:
    def __init__(self, resolution):
        self.width = resolution[0]
        self.height = resolution[1]
        self.framebuffer = glGenFramebuffers(1)
        self.renderbuffer = glGenRenderbuffers(1)
        self.attached_texture = None
        glBindRenderbuffer(GL_RENDERBUFFER, self.renderbuffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, int(self.width), int(self.height))
        glBindRenderbuffer(GL_RENDERBUFFER, 0)

    def is_floating_point(self):
        if not self.attached_texture:
            return False
        return self.attached_texture.dtype() == 'float32'

    def attach(self, texture, clear=False):
        self.attached_texture = texture
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture.texture, 0)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.renderbuffer);
        # if clear != False:
        #     if self.is_floating_point():
        #         glClearNamedFramebufferfv(self.framebuffer, GL_COLOR, 0, [0.0, 0.0, 0.0, 0.0])
        #     else:
        #         glClearNamedFramebufferuiv(self.framebuffer, GL_COLOR, 0, [0,0,0,0])
