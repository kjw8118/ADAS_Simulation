from ursina import *

import math

from vehicle import Vehicle, VehicleDynamics, Wheel
import numpy as np


class Driver(Vehicle):
    import pygame

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        self.is_ortho = False
        camera.rotation_x = 12

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
        self.aps = (self.pad.get_axis(5) + 1)/2/4
        self.bps = (self.pad.get_axis(4) + 1)/2
        self.steering = self.pad.get_axis(0)/3

    def set_camera_ortho(self, bool):
        self.is_ortho = bool
        camera.orthographic = bool
        if bool:
            camera.rotation_x = 90
        else:
            camera.rotation_x = 12

    def camera_following(self):
        if self.is_ortho:
            follow = self.rotation_transformation(self.rotation_y * math.pi / 180 + self.steering / 3, [0, 10])
            camera.world_position += (self.world_position + Vec3(follow[0], 7.5, follow[1]) - camera.world_position) * 0.035
            camera.rotation_y += (self.rotation_y + self.steering * 180 / math.pi / 3 - camera.rotation_y) * 0.02
        else:
            follow = self.rotation_transformation(self.rotation_y * math.pi / 180 + self.steering / 3, [0, -20])
            camera.world_position += (self.world_position + Vec3(follow[0], 7.5, follow[1]) - camera.world_position) * 0.035
            camera.rotation_y += (self.rotation_y + self.steering*180/math.pi/3 - camera.rotation_y) * 0.035

    def rotation_transformation(self, angle, vec1):
        vec_np = np.array([[vec1[0]], [vec1[1]]])
        return np.array([[math.cos(-angle), -math.sin(-angle)],[math.sin(-angle), math.cos(-angle)]])@vec_np



if __name__=="__main__":
    from ursina.shaders import lit_with_shadows_shader
    from ursina.prefabs.first_person_controller import FirstPersonController

    app = Ursina()



    random.seed(0)
    Entity.default_shader = lit_with_shadows_shader

    ground = Entity(model='plane', collider='box', scale=512, texture='grass', texture_scale=(24, 24), name='ground')
    target = Vehicle(z=50)

    player = Driver(z=-50)
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