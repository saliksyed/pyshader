import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import * 
from OpenGL.GLUT.freeglut import *
from renderer import Renderer
import math
import random
import json
from renderer import Renderer
from cameras import *

class Editor(Renderer):
    def __init__(self, resolution, init_window=True):
        Renderer.__init__(self, resolution, init_window)
        self.tick = 0
        self.scale = 1.0
        glutKeyboardFunc(self.move)
        glutSpecialFunc(self.handle_special_keys)
        self.external_cameras = [None for i in xrange(0,10)]
        self.view_final_camera = False
        self.view_orbit_camera = False
        self.editor_camera = Camera([-4.95, 13.65, -10.43], 0.0, 10., 1.6)
        self.current_camera = self.editor_camera
        self.animated_camera = InterpolatedCamera(self.external_cameras, self.finished)
        self.key_handlers = {}
        self.anim_finished = False
        self.max_frames = None

    def finished(self):
        if self.view_orbit_camera:
            return False
        self.anim_finished= True

    def is_finished(self):
        return self.anim_finished or self.rendered_frames > self.max_frames

    def eye_position(self):
        if self.view_final_camera:
            return self.animated_camera.eye_pos
        else:
            return self.editor_camera.eye_pos

    def orbit_angle(self):
        if self.view_final_camera:
            return self.animated_camera.angle
        else:
            return self.editor_camera.angle

    def handle_special_keys(self, key, x, y):
        """
            Handle keyboard controls
        """
        if key == GLUT_KEY_UP:
            self.editor_camera.move(5.0)
        elif key == GLUT_KEY_LEFT:
            self.editor_camera.pan(-0.05)
        elif key == GLUT_KEY_DOWN:
            self.editor_camera.move(-5.0)
        elif key == GLUT_KEY_RIGHT:
            self.editor_camera.pan(0.05)

    def orbit_camera_on(self, idx=0):
        if self.view_orbit_camera:
            self.view_orbit_camera = False
            self.view_final_camera = False
        else:
            self.editor_camera.create_from_camera(self.external_cameras[idx])
            self.view_orbit_camera = True
            self.view_final_camera = False

    def load_camera(self, file_name):
        self.external_cameras = self.animated_camera.cameras
        self.animated_camera.load(file_name)
        self.animated_camera.set_on_finish(self.finished)
        self.external_cameras = self.animated_camera.cameras
        self.view_final_camera = True

    def move(self, key, x, y):
        """
            Handle keyboard controls
        """
        if key == ' ':
            if self.scale == 0.1:
                self.scale = 1.0
            else:
                self.scale = 0.1
        elif key == "_":
            self.external_cameras = [None for i in xrange(0, 10)]
            self.animated_camera = InterpolatedCamera(self.external_cameras)
            self.view_final_camera = False
            self.editor_camera = Camera([-4.95, 13.65, -10.43], 0.0, 10., 1.6)
        elif key == '+':
            self.orbit_camera_on()
        elif key =='R':
            self.reload_all_shaders()
        elif key =='r':
            self.current_camera.orbit(0.05)
        elif key =='t':
            self.current_camera.orbit(-0.05)
        elif key =='[':
            self.editor_camera.orbit(0.05)
        elif key ==']':
            self.editor_camera.orbit(-0.05)
        elif key == 'w':
            self.current_camera.move(5.0*self.scale)
        elif key == 'a':
            self.current_camera.pan(-0.05*self.scale)
        elif key == 's':
            self.current_camera.move(-5.0*self.scale)
        elif key == 'd':
            self.current_camera.pan(0.05*self.scale)
        elif key == 'q':
            self.current_camera.move_vertical(1.*self.scale)
        elif key == 'z':
            self.current_camera.move_vertical(-1.*self.scale)
        elif key == '\'':
            self.editor_camera.move_vertical(1.*self.scale)
        elif key == '/':
            self.editor_camera.move_vertical(-1.*self.scale)
        elif key == ';':
            self.editor_camera.tilt(-0.05*self.scale)
        elif key == '.':
            self.editor_camera.tilt(0.05*self.scale)
        elif key =='n':
            self.current_camera.speed(0.1)
        elif key =='m':
            self.current_camera.speed(-0.1)
        elif key == 'e':
            self.current_camera.tilt(-0.05*self.scale)
        elif key == 'c':
            self.current_camera.tilt(0.05*self.scale)
        elif key == 'f':
            self.current_camera.zoom(0.5*self.scale)
        elif key == '\\':
            self.editor_camera.create_from_camera(self.current_camera)
        elif key =='=':
            self.view_final_camera = not self.view_final_camera
        elif key == 'v':
            self.current_camera.zoom(-0.1*self.scale)
        elif key in ['1', '2', '3','4','5','6','7','8','9']:
            idx = int(key) - 1
            if not self.external_cameras[idx]:
                self.external_cameras[idx] = Camera()
                self.external_cameras[idx].create_from_camera(self.editor_camera)
            self.current_camera.set_selected(False)
            self.current_camera = self.external_cameras[idx]
            self.current_camera.set_selected(True)
            self.animated_camera.set_cameras(self.external_cameras)
        elif key in ['!', '@', '#','$','%','^','&','*','(']:
            idx = ['!', '@', '#','$','%','^','&','*','('].index(key)
            self.external_cameras[idx] = Camera()
            self.external_cameras[idx].create_from_camera(self.editor_camera)
        elif key == '`':
            file_name = raw_input("save current trajectory as ? ")
            self.animated_camera.save(file_name)
        elif key =='~':
            file_name = raw_input("load trajectory as ? ")
            self.load_camera(file_name.rstrip())
        else:
            for handled_key in self.key_handlers:
                if key == handled_key:
                    self.key_handlers[handled_key](self)
    
    def add_key_handler(self, key, func):
        self.key_handlers[key] = func

    def setup_scene(self, aperture=None, bokeh_theta=None):
        glEnable(GL_POINT_SPRITE);
        # setup the projection, modelview matrices
        glClearColor(0.,0.,0.,1.)
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # compute the eye position, target position of our camera
        if self.view_final_camera and self.animated_camera.is_ready():
            self.animated_camera.apply_projection_matrix()
        else:
            self.editor_camera.apply_projection_matrix()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # compute the eye position, target position of our camera
        if self.view_final_camera and self.animated_camera.is_ready():
            self.animated_camera.apply_matrix(aperture, bokeh_theta)
        else:
            self.editor_camera.apply_matrix(aperture, bokeh_theta)
    def tick_cameras(self, dt):
        for camera in self.external_cameras:
            if camera:
                camera.tick(dt)
        self.animated_camera.tick(dt)
        if self.view_orbit_camera:
            self.editor_camera.orbit(dt * self.editor_camera.speed_mult)


    def render_from_camera(self, camera, output_file, max_frames=None):
        self.load_camera(camera)
        self.view_final_camera = True
        self.anim_finished = False
        self.max_frames = max_frames
        self.rendered_frames = 0
        self.render_frames(output_file, finished_callback=self.is_finished)

    def draw_cameras(self):
        for camera in self.external_cameras:
            if camera:
                camera.draw()
        self.animated_camera.draw()


    def draw(self):
        glPushMatrix()
        self.setup_scene()
        self.draw_contents()
        self.draw_cameras()