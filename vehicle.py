from ursina import *

import math
import numpy as np


class Wheel:
    def __init__(self, dynamics):
        self.left_wheel = Entity(
            model=Cylinder(resolution=16, radius=0.5, start=0.05, height=0.2, color_gradient=[color.black, color.gray]),
            y=0.5, rotation_x=-90, rotation_y=90)
        self.right_wheel = Entity(
            model=Cylinder(resolution=16, radius=0.5, start=0.05, height=0.2, color_gradient=[color.black, color.gray]),
            y=0.5, rotation_x=-90, rotation_y=-90)
        self.rear_left_wheel = Entity(
            model=Cylinder(resolution=16, radius=0.5, start=0.05, height=0.2, color_gradient=[color.black, color.gray]),
            y=0.5, rotation_x=-90, rotation_y=90)
        self.rear_right_wheel = Entity(
            model=Cylinder(resolution=16, radius=0.5, start=0.05, height=0.2, color_gradient=[color.black, color.gray]),
            y=0.5, rotation_x=-90, rotation_y=-90)
        self.dynamics = dynamics

    def update(self):
        self.left_wheel.world_position = Vec3(self.dynamics.outline['FL'][0], self.left_wheel.world_position.y,
                                              self.dynamics.outline['FL'][1])
        self.left_wheel.rotation_y = 90 + self.dynamics.get_rotation() + self.dynamics.get_steering()

        self.right_wheel.world_position = Vec3(self.dynamics.outline['FR'][0], self.left_wheel.world_position.y,
                                               self.dynamics.outline['FR'][1])
        self.right_wheel.rotation_y = -90 + self.dynamics.get_rotation() + self.dynamics.get_steering()

        self.rear_left_wheel.world_position = Vec3(self.dynamics.outline['RL'][0], self.left_wheel.world_position.y,
                                                   self.dynamics.outline['RL'][1])
        self.rear_left_wheel.rotation_y = 90 + self.dynamics.get_rotation()

        self.rear_right_wheel.world_position = Vec3(self.dynamics.outline['RR'][0], self.left_wheel.world_position.y,
                                                    self.dynamics.outline['RR'][1])
        self.rear_right_wheel.rotation_y = -90 + self.dynamics.get_rotation()

    def set_visible(self, bool):
        self.left_wheel.visible = bool
        self.right_wheel.visible = bool
        self.rear_left_wheel.visible = bool
        self.rear_right_wheel.visible = bool

class VehicleDynamics:

    def __init__(self, position=np.array([[0],[0]]), rotation=0, wheelbase=4, track=1.8):
        self.position = position
        self.rotation = rotation/180*math.pi
        self.wheelbase = wheelbase
        self.track = track
        self.steering = 0

        self.outline = {}
        self.__update_outline()

        self.is_first = True
        self.last_value = 0
        self.num_phi = rotation/180*math.pi

    def update_position(self, movement, steering):
        self.steering = steering/180*math.pi
        if self.steering == 0:
            self.position += self.__rotation_transformation(self.rotation, [0, movement])
            current_value = 0
        else:
            corner_radius = self.wheelbase / self.steering
            corner_angle = movement / corner_radius
            self.rotation += corner_angle
            local_increament = self.__rotation_transformation(corner_angle, [-corner_radius, 0]) + np.array([[corner_radius], [0]])
            self.position += self.__rotation_transformation(self.rotation,local_increament.reshape(1,2).tolist()[0])
            current_value = self.steering*movement/(2*self.wheelbase)
        if self.is_first:
            self.last_value = current_value
            self.is_first = False
        self.num_phi += current_value + self.last_value
        self.last_value = current_value
        self.__update_outline()

    def __update_outline(self):
        self.outline['RL'] = self.__rotation_transformation(self.rotation, [-self.track / 2, -self.wheelbase/2]) + self.position
        self.outline['RR'] = self.__rotation_transformation(self.rotation, [self.track / 2, -self.wheelbase/2]) + self.position
        self.outline['FL'] = self.__rotation_transformation(self.rotation, [-self.track / 2, self.wheelbase/2]) + self.position
        self.outline['FR'] = self.__rotation_transformation(self.rotation, [self.track / 2, self.wheelbase/2]) + self.position

    def get_position(self):
        return self.position

    def get_rotation(self):
        return self.rotation*180/math.pi

    def get_steering(self):
        return self.steering*180/math.pi

    def __rotation_transformation(self, angle, vec1):
        vec_np = np.array([[vec1[0]], [vec1[1]]])
        return np.array([[math.cos(-angle), -math.sin(-angle)],[math.sin(-angle), math.cos(-angle)]])@vec_np


class Vehicle(Entity):
    def __init__(self, **kwargs):
        if False:
            super().__init__(model='assets/Car.obj', texture=None, collider='box', scale_x=1.8, scale_y=0.8, scale_z=4, origin_y=-1, color=color.orange, **kwargs)
        else:
            super().__init__(model='cube', texture=None, collider='box', scale_x=1.8, scale_y=0.8, scale_z=4, origin_y=-1, color=color.green,
                             **kwargs)
        self.dynamics = VehicleDynamics(position=np.array([[self.world_position.x], [self.world_position.z]]),
                                             rotation=self.rotation_y)
        self.wheel = Wheel(self.dynamics)
        self.t0 = time.time()
    def update(self):
        t = time.time() - self.t0
        self.update_dynamics(0.2, 15*math.sin(t*2))

    def update_dynamics(self, aps, steering):
        self.dynamics.update_position(aps, steering)
        position = self.dynamics.get_position()
        rotation = self.dynamics.get_rotation()
        self.world_position = Vec3(position[0], self.world_position.y, position[1])
        self.rotation_y = rotation

        self.wheel.update()
