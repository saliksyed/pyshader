import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import * 
from OpenGL.GLUT.freeglut import *
from renderer import Renderer
import math
import random
import json


"""

The camera motion implementations here are somewhat buggy and hacky (e.g Gimbal lock)

These need to be re-written using Quaternions. Some of the camera control choices need 
to be changed to the following:

orbit (left, right) (target remains fixed)
zoom (in, out) (moves just eye )
tilt (up, down) (eye remains fixed)
move (fwd, back, up, down) (moves eye and target)
strafe (left, right) (moves eye and target)
pan (eye remains fixed, target changes)
set_eye_pos
get_eye_pos
set_target_pos
get_target_pos
"""

class InterpolatedCamera:
    def __init__(self, cameras, on_finish_callback=None):
        self.set_cameras(cameras)
        self.total_t = 0
        self.on_finish_callback = on_finish_callback

    def is_ready(self):
        return len(filter(lambda x : x != None, self.cameras)) > 0

    def set_cameras(self, cameras):
        cameras = filter(lambda x : x != None, cameras)
        self.cameras = cameras
        self.default_camera = Camera()
        self.init()
    def set_projection(self, params):
        for camera in self.cameras:
            camera.set_projection(params)

    def to_json(self):
        ret = []
        for camera in self.cameras:
            ret.append(camera.to_json())
        return {"cameras" : ret}

    def from_json(self, json):
        json = json["cameras"]
        self.set_cameras(map(lambda x : Camera().from_json(x), json))

    def save(self, fname):
        open(fname, "w").write(json.dumps(self.to_json()))

    def load(self, fname):
        self.from_json(json.loads(open(fname, "r").read()))

    def current_camera(self):
        if not len(self.cameras):
            return self.default_camera
        return self.cameras[self.current_camera_idx]

    def target_camera(self):
        return self.cameras[self.target_camera_idx]

    def init(self):
        self.t = 0.0
        self.current_camera_idx =0
        self.next_camera_idxs = []
        if len(self.cameras) > 0:
            self.current_camera_idx = 0
            self.target_camera_idx = 0
        else:
            self.eye_pos = self.current_camera().eye_pos
            self.angle = self.current_camera().angle
            self.target_dist = self.current_camera().target_dist
            self.tilt_angle = self.current_camera().tilt_angle
            self.target_pos = self.get_target_pos()
            return
        if len(self.cameras) > 1:
            self.target_camera_idx = 1

        if len(self.cameras) > 2:
            self.next_camera_idxs = [x + 2 for x in range(len(self.cameras[2:]))]
        alpha = 0
        x = self.blend(alpha, self.current_camera().eye_pos[0], self.target_camera().eye_pos[0])
        y = self.blend(alpha, self.current_camera().eye_pos[1], self.target_camera().eye_pos[1])
        z = self.blend(alpha, self.current_camera().eye_pos[2], self.target_camera().eye_pos[2])
        self.eye_pos = [x, y, z]
        self.angle = self.blend(alpha, self.current_camera().angle, self.target_camera().angle)
        self.target_dist = self.blend(alpha, self.current_camera().target_dist, self.target_camera().target_dist)
        self.tilt_angle = self.blend(alpha, self.current_camera().tilt_angle, self.target_camera().tilt_angle)

    def get_target_pos(self):
        target_pos = [self.eye_pos[0] + self.target_dist * math.cos(self.angle)*math.sin(self.tilt_angle), self.eye_pos[1], self.eye_pos[2] + self.target_dist * math.sin(self.angle)*math.sin(self.tilt_angle)]
        target_pos[1] += self.target_dist * math.cos(self.tilt_angle)
        return target_pos

    def blend(self, alpha, v1, v2):
        return v1 * (1.0 - alpha) + v2 * alpha

    def blend_angle(self, alpha, v1, v2):
        cs = (1-alpha) * math.cos(v1) + alpha * math.cos(v2)
        sn = (1-alpha) * math.sin(v1) + alpha * math.sin(v2)
        return math.atan2(sn, cs)

    def tick(self, dt):
        self.total_t += dt
        if len(self.cameras) < 2:
            return
        alpha = self.t - int(self.t)
        dt *= self.current_camera().speed_mult
        if (alpha + dt) >= 1.0 and len(self.next_camera_idxs):
            self.current_camera_idx = self.target_camera_idx
            self.target_camera_idx = self.next_camera_idxs.pop(0)
            alpha = 0.0
        elif (alpha + dt) >= 1.0:
            if self.on_finish_callback:
                self.on_finish_callback()
            self.init()
        self.t += dt
        x = self.blend(alpha, self.current_camera().eye_pos[0], self.target_camera().eye_pos[0])
        y = self.blend(alpha, self.current_camera().eye_pos[1], self.target_camera().eye_pos[1])
        z = self.blend(alpha, self.current_camera().eye_pos[2], self.target_camera().eye_pos[2])
        self.eye_pos = [x, y, z]
        self.angle = self.blend(alpha, self.current_camera().angle, self.target_camera().angle)
        self.target_dist = self.blend(alpha, self.current_camera().target_dist, self.target_camera().target_dist)
        self.tilt_angle = self.blend(alpha, self.current_camera().tilt_angle, self.target_camera().tilt_angle)

    def apply_matrix(self):
        target_pos = self.get_target_pos()
        gluLookAt(self.eye_pos[0], self.eye_pos[1], self.eye_pos[2], target_pos[0], target_pos[1], target_pos[2], 0, 1., 0)

    def apply_projection_matrix(self):
        self.current_camera().apply_projection_matrix()

    def draw(self):
        if not self.target_pos or not self.eye_pos:
            return
        self.target_pos = self.get_target_pos()
        glPushMatrix()
        glColor3f(1.0, 0.0, 1.0)
        glTranslatef(self.target_pos[0], self.target_pos[1], self.target_pos[2])
        glutSolidSphere(0.1, 20, 20)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(self.eye_pos[0], self.eye_pos[1], self.eye_pos[2])
        glutSolidSphere(0.1, 20, 20)
        glPopMatrix()
        glBegin(GL_LINES)
        glVertex3f(self.target_pos[0], self.target_pos[1], self.target_pos[2])
        glVertex3f(self.eye_pos[0], self.eye_pos[1], self.eye_pos[2])
        glEnd()


class Camera:
    def __init__(self, eye_pos = [0, 0, 0], angle = 0, target_dist = 10, tilt_angle=0, speed_mult=1.0, projection_params=None):
        self.eye_pos = eye_pos
        self.angle = angle
        self.target_dist = target_dist
        self.tilt_angle = tilt_angle
        self.selected = False
        self.speed_mult = speed_mult
        self.set_projection(projection_params)


    def to_json(self):
        return {
            "eye_pos" : self.eye_pos,
            "angle" : self.angle,
            "target_dist": self.target_dist,
            "tilt_angle": self.tilt_angle,
            "speed_mult": self.speed_mult
        }

    def from_json(self, json):
        self.eye_pos = json["eye_pos"]
        self.angle = json["angle"]
        self.target_dist = json["target_dist"]
        self.tilt_angle = json["tilt_angle"]
        self.speed_mult = json["speed_mult"]
        return self

    def orbit(self, delta):
        # compute the new eye position:
        target = self.get_target_pos()
        self.angle -= delta
        self.eye_pos[0] = target[0] -  self.target_dist * math.cos(self.angle)*math.sin(self.tilt_angle)
        self.eye_pos[2] = target[2] -  self.target_dist * math.sin(self.angle)*math.sin(self.tilt_angle)

    def create_from_camera(self, other_camera):
        self.eye_pos = other_camera.eye_pos[:]
        self.angle = other_camera.angle
        self.target_dist = other_camera.target_dist
        self.tilt_angle = other_camera.tilt_angle
        self.speed_mult = other_camera.speed_mult

    def speed(self, delta):
        self.speed_mult += delta

    def set_selected(self, state=True):
        self.selected = state

    def tick(self, dt):
        self.target_pos = self.get_target_pos()

    def get_target_pos(self):
        target_pos = [self.eye_pos[0] + self.target_dist * math.cos(self.angle)*math.sin(self.tilt_angle), self.eye_pos[1], self.eye_pos[2] + self.target_dist * math.sin(self.angle)*math.sin(self.tilt_angle)]
        target_pos[1] += self.target_dist * math.cos(self.tilt_angle)
        return target_pos

    def move(self, delta):
        self.eye_pos[0] += delta * math.cos(self.angle)
        self.eye_pos[2] += delta * math.sin(self.angle)

    def move_vertical(self, delta):
        self.eye_pos[1] += delta

    def pan(self, theta):
        self.angle += theta
        if self.angle >= 2 * math.pi:
            self.angle -= 2*math.pi

    def tilt(self, phi):
        self.tilt_angle += phi
        if self.tilt_angle >= 2 * math.pi:
            self.tilt_angle -= 2*math.pi

    def zoom(self, amount):
        self.target_dist += amount

    def apply_matrix(self):
        target_pos = self.get_target_pos()
        gluLookAt(self.eye_pos[0], self.eye_pos[1], self.eye_pos[2], target_pos[0], target_pos[1], target_pos[2], 0, 1., 0)

    def set_projection(self, curr_params):
        if curr_params == None:
            self.projection_params = {
                "projection": "perspective",
                "fov": 45,
                "aspect_ratio": 1.5,
                "near": 0.1,
                "far": 1000.
            }
        else:
            self.projection_params = curr_params

    def apply_projection_matrix(self):
        curr_params = self.projection_params
        if curr_params["projection"] is "perspective":
            gluPerspective(curr_params["fov"], curr_params["aspect_ratio"], curr_params["near"], curr_params["far"])
        elif curr_params["projection"] is "ortho":
            glOrtho(curr_params["left"], curr_params["right"], curr_params["bottom"], curr_params["top"], curr_params["near"], curr_params["far"])


    def draw(self):
        if not self.target_pos:
            return
        glPushMatrix()
        if self.selected:
            glColor3f(1.0, 0.0, 0.0)
        else:
            glColor3f(0.5, 0.0, 0.0)
        glTranslatef(self.target_pos[0], self.target_pos[1], self.target_pos[2])
        glutSolidSphere(0.1, 20, 20)
        glPopMatrix()
        glPushMatrix()
        if self.selected:
            glColor3f(1.0, 1.0, 0.0)
        glTranslatef(self.eye_pos[0], self.eye_pos[1], self.eye_pos[2])
        glutSolidSphere(0.1, 20, 20)
        glPopMatrix()
        glBegin(GL_LINES)
        if self.selected:
            glColor3f(1.0, 0.0, 0.0)
        glVertex3f(self.target_pos[0], self.target_pos[1], self.target_pos[2])
        if self.selected:
            glColor3f(1.0, 1.0, 0.0)
        glVertex3f(self.eye_pos[0], self.eye_pos[1], self.eye_pos[2])
        glEnd()
