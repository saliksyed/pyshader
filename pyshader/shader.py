from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGL.GL.ARB.color_buffer_float import * 
from OpenGL.raw.GL.ARB.color_buffer_float import * 

from helpers import QUAD_VERTEX_SHADER, TEXTURE_FRAG_SHADER
from vbo import VBO
import numpy as np

class Shader:
    def __init__(self, ctx, frag_shader=None, vertex_shader=None, vbo=None):
        if vertex_shader:
            try:
                vertex_shader_str = open(vertex_shader).read()
            except:
                vertex_shader_str = vertex_shader
        else:
            vertex_shader_str = QUAD_VERTEX_SHADER

        if frag_shader:
            try:
                frag_shader_str = open(frag_shader).read()
            except:
                frag_shader_str = frag_shader
        else:
            frag_shader_str = TEXTURE_FRAG_SHADER
        vp = shaders.compileShader(vertex_shader_str, GL_VERTEX_SHADER)
        fp = shaders.compileShader(frag_shader_str, GL_FRAGMENT_SHADER)
        self.shader = shaders.compileProgram(vp, fp)
        self.uniforms = {}
        self.ctx  = ctx
        self.set_vbo(vbo)

    def set_vbo(self, val):
        if not val:
            val = VBO()
        self.vbo = val

    def uniform(self, name, value=None):
        if value is None:
            self.uniforms[name] = glGetUniformLocation(self.shader, name)
        else:
            if not name in self.uniforms:
                self.uniform(name)
            uniform_loc = self.uniforms[name]
            if isinstance(value, (list, tuple, np.ndarray)):
                if len(value) > 4:
                    method = 'glUniformMatrix' + str(int(math.sqrt(len(value)))) + 'fv'
                    globals()[method](uniform_loc, 1, False, value)
                else:
                    integer = isinstance(value[0], int)
                    method = 'glUniform' + str(len(value)) + ('i' if integer else 'f') + 'v'
                    globals()[method](uniform_loc, 1, value)
            elif isinstance(value, (float, int, bool)):
                integer = isinstance(value, int)
                if (integer):
                    glUniform1i(uniform_loc, value)
                else:
                    glUniform1f(uniform_loc, value)
            else:
                raise Exception('Invalid uniform value: ' + str(value))
        return self

    def input(self, name, withName=None, fromShader=None):
        if not withName:
            withName = name
        self.uniform(withName, self.ctx.get_texture_unit(name))
        glActiveTexture(GL_TEXTURE0 + self.ctx.get_texture_unit(name));
        glBindTexture(GL_TEXTURE_2D, self.ctx.textures[name].texture);
        return self

    def attr(self, name):
        self.ctx.attr(name).bind(self.shader)
        return self

    def use(self, vbo=None):
        shaders.glUseProgram(self.shader)
        self.vbo.bind()
        self.uniform('iResolution', [self.ctx.width, self.ctx.height])
        return self

    def tick(self, tick):
        self.uniform('iGlobalTime', tick)
        return self

    def draw(self, clear=True):
        self.vbo.draw(clear)
        self.vbo.unbind()
        shaders.glUseProgram(0)
        return self

    def drawTo(self, target, clear=True):
        if target != None:
            # bind to the framebuffer
            self.ctx.set_target(target, clear=clear)
        self.draw(clear)
        self.ctx.set_target(None)
        return self
