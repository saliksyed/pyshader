from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGL.GL.ARB.color_buffer_float import * 
from OpenGL.raw.GL.ARB.color_buffer_float import * 
import numpy as np
import subprocess as sp
import random
import sys
import math
from PIL import Image
import random
import pickle

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

TEXTURE_FRAG_SHADER = """
uniform sampler2D inputImage;
varying vec2 index;

void main() {
    gl_FragColor = texture2D(inputImage, index);
}
"""

FLIPPED_TEXTURE_FRAG_SHADER = """
uniform sampler2D inputImage;
varying vec2 index;

void main() {
    gl_FragColor = texture2D(inputImage, vec2(index.x, 1.0 - index.y));
}
"""



def parse_triangle_vertex(line):
    vals = filter(lambda x : len(x) > 0, line.split("/"))
    return map(lambda x : abs(int(x)) - 1, vals)

def parse_obj_file(path):
    f = open(path, "r")
    ret = {}
    curr_obj = None
    count = 0
    while True:
        line = f.readline()
        if not line:
            break
        items = line.rstrip().split()
        if len(items) <= 1:
            continue
        current_mode = items[0]
        if current_mode == "#":
            if items[1] == "object":
                if curr_obj != None:
                    # reverse since vertices are indexed via negative indicies
                    ret[curr_obj]["vertices"].reverse()
                curr_obj = items[2]
                count += 1
                print "Parsing object: %s" % curr_obj
                ret[curr_obj] = {
                    "vertices": [],
                    "texture_coords": [],
                    "faces": [],
                    "normals": []
                }
        elif current_mode == "v":
            ret[curr_obj]["vertices"].append(map(lambda x : float(x), items[1:]))
        elif current_mode == "vn":
            ret[curr_obj]["normals"].append(map(lambda x : float(x), items[1:]))
        elif current_mode == "vt":
            ret[curr_obj]["texture_coords"].append(map(lambda x : float(x), items[1:]))
        elif current_mode == "f":
            ret[curr_obj]["faces"].append(map(parse_triangle_vertex, items[1:4]))

    return ret


def get_triangles(file, obj_name=None, return_tex_coords=False):
    obj_objects = parse_obj_file(file)
    if obj_name:
        tmp_obj_objects = {}
        tmp_obj_objects[obj_name] = obj_objects[obj_name]
        obj_objects = tmp_obj_objects
    vertices = []
    texture_coords = []
    for obj_name in obj_objects:
        obj = obj_objects[obj_name]
        for face in obj["faces"]:
            a = face[0][0]
            b = face[1][0]
            c = face[2][0]
            va = np.array(obj["vertices"][a])
            vb = np.array(obj["vertices"][b])
            vc = np.array(obj["vertices"][c])
            vertices.append(va)
            vertices.append(vb)
            vertices.append(vc)
            if return_tex_coords:
                if "texture_coords" in obj:
                    ta = obj["texture_coords"][a]
                    tb = obj["texture_coords"][b]
                    tc = obj["texture_coords"][c]
                else:
                    ta = [0.0,0.0, 0.0]
                    tb = [0.0,0.0, 0.0]
                    tc = [0.0,0.0, 0.0]
                
                if len(ta) < 3: #force 3D tex coords if 2D found
                    ta.append(0.0)
                if len(tb) < 3:
                    tb.append(0.0)
                if len(tc) < 3:
                    tc.append(0.0)
                texture_coords.append(ta)
                texture_coords.append(tb)
                texture_coords.append(tc)
    return vertices, texture_coords


def read_faces_and_vertices_from_obj(path, verbose=False):
    f = open(path, "r")
    ret = {}
    curr_obj = None
    while True:
        line = f.readline()
        if not line:
            break
        items = line.rstrip().split()
        if len(items) <= 1:
            continue
        current_mode = items[0]
        if current_mode == "#":
            if items[1] == "object":
                curr_obj = items[2]
                if verbose:
                    print "Parsing object: %s" % curr_obj
                ret[curr_obj] = {
                    "vertices": [],
                    "faces": []
                }
        elif current_mode == "v":
            ret[curr_obj]["vertices"].append(map(lambda x : float(x), items[1:]))
        elif current_mode == "f":
            ret[curr_obj]["faces"].append(map(lambda x : int(abs(x)), items[1:4]))
    return ret

def read_points_from_ply(fname):
    vertices = []
    header_ended = False
    with open(fname, "r") as f:
        for line in f.readlines():
            line = line.rstrip()
            if header_ended:
                vertices.append(map(float, line.split()))
            elif line == "end_header":
                header_ended = True
            else:
                continue
    return vertices

def nearest_pow2(aSize):
    return math.pow(2, round(math.log(aSize) / math.log(2))) 

class VertexAttr:
    def __init__(self, name):
        self.name = name

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
        return np.frombuffer(glGetTexImage(GL_TEXTURE_2D, 0, self.format, self.type), np.uint8)

    def blank(self, width, height):
        source_copy = np.array([[0, 0, 0, 255] for i in xrange(0, int(width*height))], copy=True)
        glBindTexture(GL_TEXTURE_2D, self.texture);
        glTexImage2D(GL_TEXTURE_2D, 0, self.internal_format, width, height, 0, self.format, self.type, source_copy)

    def set(self, source, width, height):
        source_copy = np.array(source, dtype=self.dtype(), copy=True)
        glBindTexture(GL_TEXTURE_2D, self.texture);
        glTexImage2D(GL_TEXTURE_2D, 0, self.internal_format, width, height, 0, self.format, self.type, source_copy)

    def noise(self, width, height):
        source_copy = np.array([[int(255*random.random()), int(255*random.random()), int(255*random.random()), int(255*random.random())] for i in xrange(0, int(width*height))], copy=True)
        glBindTexture(GL_TEXTURE_2D, self.texture);
        glTexImage2D(GL_TEXTURE_2D, 0, self.internal_format, width, height, 0, self.format, self.type, source_copy)        

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


class RenderTarget:
    def __init__(self, resolution):
        self.width = resolution[0]
        self.height = resolution[1]
        self.framebuffer = glGenFramebuffers(1)
        self.renderbuffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.renderbuffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, int(self.width), int(self.height))
        glBindRenderbuffer(GL_RENDERBUFFER, 0)


    def attach(self, texture):
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.renderbuffer);


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
        glClearColor(0.,0.,0.,0.)
        glClampColor(GL_CLAMP_READ_COLOR, GL_FALSE)
        glClampColorARB(GL_CLAMP_READ_COLOR_ARB, GL_FALSE)
        glClampColorARB(GL_CLAMP_FRAGMENT_COLOR_ARB, GL_FALSE)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable( GL_PROGRAM_POINT_SIZE )
        glutDisplayFunc(self.display)
        glMatrixMode(GL_MODELVIEW)
        self.textures = {}
        self.texture_units = {}
        self.shaders = {}
        self.videos = {}
        self.attrs = {}
        self.width = float(width)
        self.height = float(height)
        self.isRunning = False
        self.isWriting = False
        self.render_target = RenderTarget(resolution)
        # The default texture shader is used by drawTexture()
        self.shaders['default_texture_shader'] = Shader(self)
        self.shaders['flipped_texture_shader'] = Shader(self, FLIPPED_TEXTURE_FRAG_SHADER)
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

    def attr(self, name, source_ply_file=None, vertices=None):
        if source_ply_file:
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
        img = Image.open(image_path).convert('RGB')
        img_data = np.array(list(img.getdata()), np.uint8)
        tex = self.texture(name, tformat=GL_RGB)
        tex.set(img_data, img.size[0], img.size[1])

    def shader(self, name, frag_shader=None, vertex_shader=None, vbo=None):
        if vertex_shader != None or frag_shader != None:
            self.shaders[name] = Shader(self, frag_shader, vertex_shader, vbo)
        return self._get_shader(name)

    def draw(self):
        # sub class must implement!
        pass


    def drawTexture(self, textureName, flip=False):
        if flip:
            (self.shader('flipped_texture_shader')
                .input(textureName, withName='inputImage')
                .draw())        
        else:
            (self.shader('default_texture_shader')
                .input(textureName, withName='inputImage')
                .draw())

    def display(self):
        glViewport(0, 0, int(self.width), int(self.height))
        shaders.glUseProgram(0)
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

    def get_pixels(self):
        buf = glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE)
        return np.frombuffer(buf, dtype=np.uint8)

    def save_frame(self):
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
            render_target.attach(self.textures[texture_name].texture)

    def render_frames(self, file_name, num_frames=60, finished_callback=None):
        # set the output file for the renderer:
        self.output_file(file_name)
        self.texture('output')
        if not finished_callback:
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

        else:
            i = 0
            while not finished_callback():
                print "Writing frame " + str(i)

                # Set the target for the rendering pass 
                # NOTE: If a target is not set, calling `shader.draw()` will render
                # to the GUI. This isn't desirable when writing video!
                self.set_target('output')

                # call draw
                self.draw()

                # save the frame
                self.save_frame()
                i+=1


    def _get_shader(self, name):
        if name not in self.shaders:
            raise Exception('Unknown shader: ' + str(name))
        return self.shaders[name].use()

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

class VBO:
    def __init__(self, render_primitive=GL_TRIANGLES, arr=None):
        self.bounds = None
        if not arr:
            arr = [
                [ -1, 1, 0 ],
                [ -1,-1, 0 ],
                [  1,-1, 0 ],
                [ -1, 1, 0 ],
                [  1,-1, 0 ],
                [  1, 1, 0 ]
            ]
        self.set_vertices(arr)
        self.render_primitive=render_primitive

    def set_vertices(self, arr):
        self.vertices = arr
        self.bounds = None
        self.vbo = vbo.VBO(np.array(self.vertices,'float32'))

    def set_tex_coords(self, coords):
        self.tex_coords = coords

    def bind(self):
        self.vbo.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointerf(self.vbo)

    def draw(self, clear=True):
        if clear:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDrawArrays(self.render_primitive, 0, self.size())

    def unbind(self):
        self.vbo.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)

    def load_ply(self, fname):
        vertices = read_points_from_ply(fname)
        self.set_vertices(vertices)

    def load_obj(self, fname, obj_name=None):
        vertices, tex_coords = get_triangles(fname, obj_name, True)
        self.set_vertices(vertices)
        self.set_tex_coords(tex_coords)

    def save(self, fname):
        pickle.dump(self.vertices, open(fname, "wb"))

    def load(self, fname):
        vertices = pickle.load(open(fname, "rb"))
        self.set_vertices(vertices)

    def size(self):
        return len(self.vertices)

    def write_to_texture(self, texture):
        print "foobar"

    def read_from_texture(self, texture):
        print "foobar"


    def get_bounds(self):
        if not self.bounds:
            mins = [None, None, None]
            maxes = [None, None, None]
            for pt in self.vertices:
                for i in xrange(0,3):
                    mins[i] = min(mins[i], pt[i]) or pt[i]
                    maxes[i] = max(maxes[i], pt[i])

            self.bounds = (mins, maxes)
        return self.bounds


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

    def use(self):
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
            self.ctx.set_target(target)
        self.draw(clear)
        self.ctx.set_target(None)
        return self
