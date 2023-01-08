from ursina import *

import math

from vehicle import Vehicle, VehicleDynamics, Wheel
from roads import Road
import numpy as np


class Driver(Vehicle):
    import pygame

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        self.is_ortho = False
        self.is_first = False

        camera.rotation_x = 12
        self.set_camera_ortho(False)

        self.pygame.init()
        self.pad = self.pygame.joystick.Joystick(0)
        self.pad.init()
        self.pygame.event.get()

        self.aps = 0
        self.bps = 0
        self.steering = 0
        self.power = 0

    def update(self):

        self.get_driver_input()
        self.update_dynamics(self.aps, self.steering*180/math.pi)

        self.camera_following()


    def get_driver_input(self):
        self.pygame.event.get()
        self.aps = (self.pad.get_axis(5) + 1)/2/3
        self.bps = (self.pad.get_axis(4) + 1)/2
        self.steering = self.pad.get_axis(0)/12

    def set_camera_ortho(self, bool):
        self.is_ortho = bool
        camera.orthographic = bool
        if bool:
            self.visible = True
            self.wheel.set_visible(True)
            camera.rotation_x = 90
        else:
            if self.is_first:
                self.visible = False
                self.wheel.set_visible(False)
                camera.rotation_x = 4
            else:
                self.visible = True
                self.wheel.set_visible(True)
                camera.rotation_x = 12


    def camera_following(self):
        if self.is_ortho:
            follow = ursinamath.rotate_point_2d(Vec2(0, 10), Vec2(0, 0), self.rotation_y + self.steering * 180 / math.pi / 3)
            camera.world_position += (self.world_position + Vec3(follow[0], 7.5, follow[1]) - camera.world_position) * 0.035
            camera.rotation_y += (self.rotation_y + self.steering * 180 / math.pi / 3 - camera.rotation_y) * 0.02
        else:
            if self.is_first:
                follow = ursinamath.rotate_point_2d(Vec2(0, 2), Vec2(0, 0), self.rotation_y + self.steering * 180 / math.pi / 3)
                camera.world_position += (self.world_position + Vec3(follow[0], 1.5, follow[1]) - camera.world_position) * 0.05
                camera.rotation_y += (self.rotation_y + self.steering * 2.5 * 180 / math.pi - camera.rotation_y) * 0.04
            else:
                follow = ursinamath.rotate_point_2d(Vec2(0, -20), Vec2(0, 0), self.rotation_y + self.steering * 180 / math.pi / 3)
                camera.world_position += (self.world_position + Vec3(follow[0], 7.5, follow[1]) - camera.world_position) * 0.035
                camera.rotation_y += (self.rotation_y + self.steering*180/math.pi/3 - camera.rotation_y) * 0.035



if __name__=="__main__":
    from ursina.shaders import lit_with_shadows_shader
    from ursina.prefabs.first_person_controller import FirstPersonController

    app = Ursina()



    random.seed(0)
    Entity.default_shader = lit_with_shadows_shader

    ground = Entity(model='plane', collider='box', scale=1024, texture='grass', texture_scale=(64, 64), name='ground')
    road = Road(number_of_lane=3, is_oneway=False)

    target = Vehicle(z=-40, x=10)

    player = Driver(z=-20)
    ortho_bool = False

    def update():
        global ortho_bool
        if held_keys['p']:
            exit()

        if held_keys['o']:
            ortho_bool = not ortho_bool
            player.set_camera_ortho(ortho_bool)


    sun = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))
    Sky()

    app.run()