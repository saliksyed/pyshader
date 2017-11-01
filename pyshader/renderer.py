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
from vertex_attr import VertexAttr
import threading
import traceback

class Renderer:
    RES8K = [7680, 4320]
    RES4K = [3840, 2160]
    RES720P = [1280, 720]
    RES1440P = [2560, 1440]
    RES1080P = [1920, 1080]
    RES1024 = [1024, 768]
    RES2880 = [2880, 1800]
    RES1280 = [1280, 800]
    RES1440 = [1440, 900]
    RES1920 = [1920, 1200]
    def __init__(self, resolution, init_window=True):
        width = resolution[0]
        height = resolution[1]
        if init_window:
            self.init_window(width, height)
        self.textures = {}
        self.texture_units = {}
        self.shaders = {}
        self.videos = {}
        self.audio_tracks = {}
        self.attrs = {}
        self.width = float(width)
        self.height = float(height)
        self.isRunning = False
        self.isWriting = False
        self.render_target = RenderTarget(resolution)
        # The default texture shader is used by drawTexture()
        self.shaders['default_texture_shader'] = Shader(self)
        self.shaders['flipped_texture_shader'] = Shader(self, FLIPPED_TEXTURE_FRAG_SHADER)
        self.shader_args = {}
        self.render_lock = threading.Semaphore()

    def init_window(self, width, height):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
        glutInitWindowSize(width, height)
        self.window_id = glutCreateWindow('Visualization')
        glClearColor(0.,0.,0.,0.)
        glClampColor(GL_CLAMP_READ_COLOR, GL_FALSE)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable( GL_PROGRAM_POINT_SIZE )
        glMatrixMode(GL_MODELVIEW)
        glutIdleFunc(self.idle)
        glutDisplayFunc(self.display)

    def run(self):
        if self.isWriting:
            raise Exception('Can\'t display shader while writing to video file!')
        isRunning = True
        glutMainLoop()

    def idle(self):
        glutPostRedisplay()

    def video(self, name, video_file=None):
        if video_file:
            self.videos[name] = Video(name, video_file, self)
        return self._get_video(name)

    def attr(self, name, source_saved_file=None, source_ply_file=None, vertices=None):
        if source_saved_file:
            self.attrs[name] = VertexAttr(name)
            self.attrs[name].load(source_saved_file)
        elif source_ply_file:
            self.attrs[name] = VertexAttr(name)
            self.attrs[name].load_ply(source_ply_file)
        elif vertices:
            self.attrs[name] = VertexAttr(name)
            self.attrs[name].set_data(vertices)
        return self._get_attr(name)

    def texture(self, name, tformat=GL_RGBA, wrap=GL_CLAMP_TO_EDGE, tfilter=GL_NEAREST, ttype=GL_UNSIGNED_BYTE, tinternal_format=GL_RGBA):
        if name in self.textures:
            return self._get_texture(name)
        self.textures[name] = Texture(name, tformat, wrap, tfilter, ttype, tinternal_format)
        self.textures[name].blank(self.width, self.height)
        return self._get_texture(name)

    def get_texture_unit(self, name):
        if not name in self.texture_units:
            next_unit = len(self.texture_units) + 1
            self.texture_units[name] = next_unit
        return self.texture_units[name]

    def texture_from_image(self, name, image_path):
        # TODO: clean up to handle more texture formats
        # port this logic to Texture class
        img = Image.open(image_path).convert('RGB')
        img_data = np.array(list(img.getdata()), np.uint8)
        tex = self.texture(name, tformat=GL_RGB)
        tex.set(img_data, img.size[0], img.size[1])

    def shader(self, name, frag_shader=None, vertex_shader=None, vbo=None):
        if vertex_shader != None or frag_shader != None:
            self.shader_args[name] = [name, frag_shader, vertex_shader, vbo]
            self.shaders[name] = Shader(self, frag_shader, vertex_shader, vbo)
        return self._get_shader(name)

    def audio(self, name, filename=None, paused=False):
        if filename != None:
            self.audio_tracks[name] = Audio(filename, paused)
        return self._get_audio(name)

    def reload_shader(self, name):
        with self.render_lock:
            if name in self.shader_args:
                new_shader = self.shader(*self.shader_args[name])
                return new_shader
            else:
                raise 'Error tried to reload non-existant shader'

    def exit(self):
        glutLeaveMainLoop()
        glutDestroyWindow(self.window_id)

    def reload_all_shaders(self):
        for name in self.shader_args.keys():
            self.reload_shader(name)

    def draw(self):
        # sub class must implement!
        pass


    def drawTexture(self, textureName, flip=False):
        if flip:
            (self.shader('flipped_texture_shader').use()
                .input(textureName, withName='inputImage')
                .draw())        
        else:
            (self.shader('default_texture_shader').use()
                .input(textureName, withName='inputImage')
                .draw())

    def display(self):
        with self.render_lock:
            glViewport(0, 0, int(self.width), int(self.height))
            shaders.glUseProgram(0)
            try:
                self.draw()
            except:
                print "Render error!"
                traceback.print_exc()
            glutSwapBuffers()

    def output_file(self, fname):
        self.isWriting = True
        if self.isRunning:
            raise Exception('Can\'t write to video file and run live OpenGL context simultaneously!')
        # TODO: Mix all audio inputs in renderer and output them with video file
        command = [ 'ffmpeg',
        '-y', # (optional) overwrite output file if it exists
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-s', str(int(self.width)) + 'x' + str(int(self.height)), # size of one frame
        '-pix_fmt', 'rgb24',
        '-r', '24', # frames per second
        '-i', '-', # The input comes from a pipe
        '-an', # Tells FFMPEG not to expect any audio
        '-vcodec', 'libx264',
        '-crf',  '22',
        '-pix_fmt', 'yuv420p',
        fname ]
        self.pipe = sp.Popen(command, stdin=sp.PIPE)

    def get_pixels(self):
        # if the texture is floating point switch the data type
        if self.render_target.is_floating_point():
            buf = glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_FLOAT)
            return np.frombuffer(buf, dtype=np.float32)
        else:
            buf = glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE)
            return np.frombuffer(buf, dtype=np.uint8)

    def save_framebuffer_to_image(self, imname):
        if self.render_target.is_floating_point() and imname.split(".")[-1] != 'exr':
            raise 'Floating point framebuffer must be saved to .exr format'

        pixels = self.get_pixels()
        print pixels
        if self.render_target.is_floating_point():
            # TODO: Is there a better way to read pixels into individual channels
            # so we're not doing this slow copy operation?
            r = []
            g = []
            b = []
            for i in xrange(0, len(pixels)/4):
                r.append(pixels[i * 4])
                g.append(pixels[i * 4 + 1])
                b.append(pixels[i * 4 + 2])
            r = array.array('f', r).tostring()
            g = array.array('f', g).tostring()
            b = array.array('f', b).tostring()
            exr = OpenEXR.OutputFile(imname, OpenEXR.Header(int(self.width), int(self.height)))
            exr.writePixels({'R': r, 'G': g, 'B': b})
            exr.close()
        else:
            result = Image.frombuffer("RGBA", (int(self.width), int(self.height)),pixels)
            result.save(imname)

    def save_texture_to_image(self, texname, imname):
        self.set_target(texname)
        self.save_framebuffer_to_image(imname)
        self.set_target(None)

    def save_frame(self):
        # if the texture is floating point throw an exception
        # since it can't be written to video
        if self.render_target.is_floating_point():
            raise 'Cannot save floating point framebuffer output to video'
        pixel_buffer = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE)
        self.pipe.stdin.write(pixel_buffer)

    def set_target(self, texture_name=None, render_target=None):
        if texture_name == None:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glBindTexture(GL_TEXTURE_2D, 0)
        else:
            if not texture_name in self.textures:
                self.texture(texture_name)
            if not render_target:
                render_target = self.render_target
            render_target.attach(self.textures[texture_name])

    def render_frames(self, file_name, num_frames=60, finished_callback=None):
        # set the output file for the renderer:
        self.output_file(file_name)
        self.texture('output')
        if not finished_callback:
            for i in xrange(0, num_frames):
                print("Writing frame " + str(i))

                # Set the target for the rendering pass 
                # NOTE: If a target is not set, calling `shader.draw()` will render
                # to the GUI. This isn't desirable when writing video!
                self.set_target('output')

                # call draw
                self.draw()

                # save the frame
                self.save_frame()

        else:
            i = 0
            while not finished_callback():
                print("Writing frame " + str(i))

                # Set the target for the rendering pass 
                # NOTE: If a target is not set, calling `shader.draw()` will render
                # to the GUI. This isn't desirable when writing video!
                self.set_target('output')

                # call draw
                self.draw()

                # save the frame
                self.save_frame()
                i+=1

    def _get_audio(self, name):
        if name not in self.audio_tracks:
            raise Exception('Unknown audio: ' + str(name))
        return self.audio_tracks[name]


    def _get_shader(self, name):
        if name not in self.shaders:
            raise Exception('Unknown shader: ' + str(name))
        return self.shaders[name]

    def _get_texture(self, name):
        if name not in self.textures:
            raise Exception('Unknown texture: ' + str(name))
        return self.textures[name]

    def _get_video(self, name):
        if name not in self.videos:
            raise Exception('Unknown video: ' + str(name))
        return self.videos[name]

    def _get_attr(self, name):
        if name not in self.attrs:
            raise Exception('Unknown attrs: ' + str(name))
        return self.attrs[name]
