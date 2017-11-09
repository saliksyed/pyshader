from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import glutLeaveMainLoop
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGL.GL.ARB.color_buffer_float import * 
from OpenGL.raw.GL.ARB.color_buffer_float import * 
import numpy as np
import sys
import subprocess as sp
import OpenEXR, array
from PIL import Image
from helpers import FLIPPED_TEXTURE_FRAG_SHADER
from render_target import RenderTarget
from texture import Texture
from shader import Shader
from video import Video
from audio import Audio
from renderer import Renderer
from vertex_attr import VertexAttr
import threading
import traceback

class ComputeEngine:
    def __init__(self, size, renderer):
        self.renderer = renderer
        self.texture('buf0').blank(int(size[0]), int(size[1]))
        self.texture('buf1').blank(int(size[0]), int(size[1]))

    def data(self, data)
        self._data = data
        return self

    def dataWindow(self, width, height):
        # generate input data texture

    def computeWindow(self, width, height):
        # set target viewpoint size


    def run_iteration(self):
        # run the iteration
        glViewPort()



    def output_buffer(self):
        # return the texture storing the latest data
        return 'buf0'


