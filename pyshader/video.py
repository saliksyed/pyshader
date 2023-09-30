from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL.ARB.color_buffer_float import * 
from OpenGL.raw.GL.ARB.color_buffer_float import * 
import numpy as np
import subprocess as sp
import random

"""
    Class to handle reading in video from disk
    uses sub-process + ffmpeg to read data, writes out data to OpenGL texture
"""
class Video:
    def __init__(self, name, video_file, context):
        self.name = name
        self.video_file = video_file
        self.texture = context.texture(name, tformat=GL_RGB)
        self.start_reading()

    def next_frame(self):
        # TODO: Make the API support "tick" for time based updates
        raw_image = self.pipe.stdout.read(self.width*self.height*3) 
        raw_image = np.fromstring(raw_image, dtype='uint8')
        self.texture.set(raw_image, self.width, self.height)
        self.pipe.stdout.flush()

    def start_reading(self):
        info_command = ['ffprobe',
            '-v', 'error',
            '-show_entries', 'stream=width,height',
            '-of', 'default=noprint_wrappers=1', self.video_file]

        results = sp.check_output(info_command).decode(sys.stdout.encoding)
        
        dimensions =  [x for x in map(lambda x : int(x.split("=")[1]), results.split("\n")[:2])]
        self.width = dimensions[0]
        self.height = dimensions[1]

        command = ['ffmpeg',
            '-i', self.video_file,
            '-f', 'image2pipe',
            '-pix_fmt', 'rgb24',
            '-vcodec','rawvideo', '-']
        self.pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)

