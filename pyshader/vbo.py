from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL.ARB.color_buffer_float import * 
from OpenGL.raw.GL.ARB.color_buffer_float import * 
import numpy as np
from helpers import read_points_from_ply, get_triangles_from_obj
import cPickle as pickle
import gzip

class VBO:
    def __init__(self, render_primitive=GL_TRIANGLES, arr=None):
        self.bounds = None
        self.tex_coords = None
        self.normals = None
        self.vertices = None
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

    def set_normals(self, normals):
        self.normals = normals

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

    def load_ply(self, fname, concat=False):
        if concat:
            self.vertices += read_points_from_ply(fname)
            self.set_vertices(self.vertices)
        else:
            vertices = read_points_from_ply(fname)
            self.set_vertices(vertices)

    def load_obj(self, fname, obj_name=None, scale=1.0, translate=[0, 0, 0], tex_coords=False, normals=False):
        vertices, tex_coords,  normals = get_triangles_from_obj(fname, obj_name, return_normals=normals, return_tex_coords=tex_coords, scale=scale, translate=translate)
        self.set_vertices(vertices)
        self.set_tex_coords(tex_coords)
        self.set_normals(normals)

    def save(self, fname):
        data = {}
        data['vertices'] = self.vertices
        if self.tex_coords != None:
            data['tex_coords'] = self.tex_coords
        if self.normals != None:
            data['normals'] = self.normals
        pickle.dump(data, open(fname, "wb"), 1)

    def load(self, fname):
        data = pickle.load(open(fname, "rb"))
        self.set_vertices(data['vertices'])
        if 'normals' in data:
            self.set_normals(data['normals'])
        if 'tex_coords' in data:
            self.set_tex_coords(data['tex_coords'])

    def size(self):
        return len(self.vertices)

    def write_to_texture(self, texture):
        pass

    def read_from_texture(self, texture):
        pass


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

