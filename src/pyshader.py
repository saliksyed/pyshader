from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
import numpy as np
import subprocess as sp
import sys
import math
from PIL import Image


QUAD_VERTEX_SHADER = """
attribute vec2 points;
varying vec2 coord;
varying vec2 index;

void main() {
    index = (points + 1.0) / 2.0;
    coord = (points * vec2(1, -1) + 1.0) / 2.0;
    gl_Position = vec4(points, 0.0, 1.0);
}
"""

def nearest_pow2(aSize):
    return math.pow(2, round(math.log(aSize) / math.log(2))) 

class Texture:
    def __init__(self, name, tformat=GL_RGBA, wrap=GL_CLAMP_TO_EDGE, tfilter=GL_NEAREST, ttype=GL_UNSIGNED_BYTE):
        self.name = name
        self.wrap =  wrap
        self.filter = tfilter
        self.format = tformat
        self.type = ttype
        self.texture = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self.wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self.wrap)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self.filter)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self.filter)

    def blank(self, width, height):
        glBindTexture(GL_TEXTURE_2D, self.texture);
        glTexImage2D(GL_TEXTURE_2D, 0, self.format, width, height, 0, self.format, self.type, None)

    def set(self, source, width, height):
        source_copy = np.array(source, copy=True)
        glBindTexture(GL_TEXTURE_2D, self.texture);
        glTexImage2D(GL_TEXTURE_2D, 0, self.format, width, height, 0, self.format, self.type, source_copy)

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

        results = sp.check_output(info_command)
        dimensions =  map(lambda x : int(x.split("=")[1]), results.split("\n")[:2])
        self.width = dimensions[0]
        self.height = dimensions[1]

        command = ['ffmpeg',
            '-i', self.video_file,
            '-f', 'image2pipe',
            '-pix_fmt', 'rgb24',
            '-vcodec','rawvideo', '-']
        self.pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)


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
    def __init__(self, resolution):
        width = resolution[0]
        height = resolution[1]
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
        glutInitWindowSize(width, height)
        glutCreateWindow('Visualization')
        glClearColor(0.,0.,0.,1.)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glutDisplayFunc(self.display)
        glMatrixMode(GL_MODELVIEW)
        self.textures = {}
        self.shaders = {}
        self.videos = {}
        self.width = float(width)
        self.height = float(height)
        self.framebuffer = glGenFramebuffers(1)
        self.renderBuffer = glGenRenderbuffers(1)
        self.isRunning = False
        self.isWriting = False
        glBindRenderbuffer(GL_RENDERBUFFER, self.renderBuffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, int(self.width), int(self.height))
        glBindRenderbuffer(GL_RENDERBUFFER, 0)
        glutIdleFunc(self.idle)

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

    def texture(self, name, tformat=GL_RGBA, wrap=GL_CLAMP_TO_EDGE, tfilter=GL_NEAREST, ttype=GL_UNSIGNED_BYTE):
        self.textures[name] = Texture(name, tformat, wrap, tfilter, ttype)
        self.textures[name].blank(self.width, self.height)
        return self._get_texture(name)

    def texture_from_image(self, name, image_path):
        img = Image.open(image_path)
        img_data = np.array(list(img.getdata()), np.uint8)
        tex = self.texture(name, tformat=GL_RGB)
        tex.set(img_data, img.size[0], img.size[1])

    def shader(self, name, frag_shader=None, vertex_shader=None):
        if vertex_shader != None or frag_shader != None:
            self.shaders[name] = Shader(self, frag_shader, vertex_shader)
        return self._get_shader(name)

    def draw(self):
        # sub class must implement!
        pass

    def display(self):
        glViewport(0, 0, int(self.width), int(self.height))
        self.draw()
        glutSwapBuffers()

    def output_file(self, fname):
        self.isWriting = True
        if self.isRunning:
            raise Exception('Can\'t write to video file while running shader!')
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

    def save_frame(self):
        pixel_buffer = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE)
        self.pipe.stdin.write(pixel_buffer)

    def set_target(self, texture_name=None):
        if texture_name == None:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
        else:
            if not texture_name in self.textures:
                raise Exception('Target texture not found: ' + texture_name)
            glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.textures[texture_name].texture, 0)
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.renderBuffer);

    def render_frames(self, file_name, num_frames=60):
        # set the output file for the renderer:
        self.output_file(file_name)
        self.texture('output')
        for i in xrange(0, num_frames):
            print "Writing frame " + str(i)

            # Set the target for the rendering pass 
            # NOTE: If a target is not set, calling `shader.draw()` will render
            # to the GUI. This isn't desirable when writing video!
            self.set_target('output')

            # call draw
            self.draw()

            # save the frame
            self.save_frame()

    def _get_shader(self, name):
        if name not in self.shaders:
            raise Exception('Unknown shader: ' + str(name))
        return self.shaders[name].use()

    def _get_texture(self, name):
        if name not in self.textures:
            raise Exception('Unknown texture: ' + str(name))
        return self.textures[name]

    def _get_video(self, name):
        if name not in self.textures:
            raise Exception('Unknown video: ' + str(name))
        return self.videos[name]

class Shader:
    def __init__(self, ctx, frag_shader, vertex_shader=None):
        if vertex_shader:
            vertex_shader_str = open(vertex_shader).read()
        else:
            vertex_shader_str = QUAD_VERTEX_SHADER
        vp = shaders.compileShader(vertex_shader_str, GL_VERTEX_SHADER)
        fp = shaders.compileShader(open(frag_shader).read(), GL_FRAGMENT_SHADER)
        self.shader = shaders.compileProgram(vp, fp)
        self.uniforms = {}
        self.ctx  = ctx
        self.vbo = vbo.VBO(
                        np.array( [
                            [ -1, 1, 0 ],
                            [ -1,-1, 0 ],
                            [  1,-1, 0 ],
                            [ -1, 1, 0 ],
                            [  1,-1, 0 ],
                            [  1, 1, 0 ]
                        ],'f')
                      )

    def uniform(self, name, value=None):
        if value is None:
            self.uniforms[name] = glGetUniformLocation(self.shader, name)
        else:
            if not name in self.uniforms:
                self.uniform(name)
            uniform_loc = self.uniforms[name]
            if isinstance(value, (list, tuple, np.ndarray)):
                integer = isinstance(value[0], int)
                method = 'glUniform' + str(len(value)) + ('i' if integer else 'f') + 'v'
                globals()[method](uniform_loc, 1, np.array([[self.ctx.width, self.ctx.height]], 'f'))
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
        self.uniform(withName, self.next_available_unit)
        glActiveTexture(GL_TEXTURE0 + self.next_available_unit);
        glBindTexture(GL_TEXTURE_2D, self.ctx.textures[name].texture);
        self.next_available_unit += 1
        return self

    def use(self):
        self.next_available_unit = 0
        shaders.glUseProgram(self.shader)
        self.vbo.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointerf(self.vbo)
        self.uniform('iResolution', [self.ctx.width, self.ctx.height])
        return self

    def tick(self, tick):
        self.uniform('iGlobalTime', tick)
        return self

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        self.vbo.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        shaders.glUseProgram(0)
        return self

    def drawTo(self, target):
        if target != None:
            # bind to the framebuffer
            self.ctx.set_target(target)
        self.draw()
        self.ctx.set_target(None)
        return self
