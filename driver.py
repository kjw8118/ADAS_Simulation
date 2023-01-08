from ursina import *

import math

from vehicle import Vehicle
import numpy as np

class VehicleModel:

    def __init__(self, position=np.array([[0],[0]]), rotation=0, wheelbase=4, track=1.8):
        self.position = position
        self.rotation = rotation/180*math.pi
        self.wheelbase = wheelbase
        self.track = track
        self.outline = {}
        self.update_outline()

        self.is_first = True
        self.last_value = 0
        self.num_phi = rotation/180*math.pi

    def update_position(self, movement, steering):
        if steering == 0:
            self.position += self.rotation_transformation(self.rotation, [0, movement])
            current_value = 0
        else:
            corner_radius = self.wheelbase / steering
            corner_angle = movement / corner_radius
            self.rotation += corner_angle
            local_increament = self.rotation_transformation(corner_angle, [-corner_radius, 0]) + np.array([[corner_radius], [0]])
            self.position += self.rotation_transformation(self.rotation,local_increament.reshape(1,2).tolist()[0])
            current_value = steering*movement/(2*self.wheelbase)
        if self.is_first:
            self.last_value = current_value
            self.is_first = False
        self.num_phi += current_value + self.last_value
        self.last_value = current_value
        print(self.num_phi, self.rotation,";")
        self.update_outline()

    def update_outline(self):
        self.outline['RL'] = self.rotation_transformation(self.rotation, [-self.track / 2, -self.wheelbase/2]) + self.position
        self.outline['RR'] = self.rotation_transformation(self.rotation, [self.track / 2, -self.wheelbase/2]) + self.position
        self.outline['FL'] = self.rotation_transformation(self.rotation, [-self.track / 2, self.wheelbase/2]) + self.position
        self.outline['FR'] = self.rotation_transformation(self.rotation, [self.track / 2, self.wheelbase/2]) + self.position

    def get_position(self):
        return self.position

    def get_rotation(self):
        return self.rotation*180/math.pi

    def rotation_transformation(self, angle, vec1):
        vec_np = np.array([[vec1[0]], [vec1[1]]])
        return np.array([[math.cos(-angle), -math.sin(-angle)],[math.sin(-angle), math.cos(-angle)]])@vec_np

class Wheel:

    def __init__(self, driver):
        self.left_wheel = Entity(model=Cylinder(resolution=16, radius=0.5, start=0.05, height=0.2, color_gradient=[color.black, color.gray]), y=0.5, rotation_x=-90, rotation_y=90)
        self.right_wheel = Entity(model=Cylinder(resolution=16, radius=0.5, start=0.05, height=0.2, color_gradient=[color.black, color.gray]), y=0.5, rotation_x=-90, rotation_y=-90)
        self.rear_left_wheel = Entity(model=Cylinder(resolution=16, radius=0.5, start=0.05, height=0.2, color_gradient=[color.black, color.gray]), y=0.5, rotation_x=-90, rotation_y=90)
        self.rear_right_wheel = Entity(model=Cylinder(resolution=16, radius=0.5, start=0.05, height=0.2, color_gradient=[color.black, color.gray]), y=0.5, rotation_x=-90, rotation_y=-90)
        self.parent = driver

    def update(self):
        self.left_wheel.world_position = Vec3(self.parent.vehicle_model.outline['FL'][0], self.left_wheel.world_position.y, self.parent.vehicle_model.outline['FL'][1])
        self.left_wheel.rotation_y = 90 + self.parent.rotation_y + self.parent.steering * 180 / math.pi
        self.right_wheel.world_position = Vec3(self.parent.vehicle_model.outline['FR'][0], self.left_wheel.world_position.y,
                                                self.parent.vehicle_model.outline['FR'][1])
        self.right_wheel.rotation_y = -90 + self.parent.rotation_y + self.parent.steering * 180 / math.pi

        self.rear_left_wheel.world_position = Vec3(self.parent.vehicle_model.outline['RL'][0],
                                              self.left_wheel.world_position.y,
                                              self.parent.vehicle_model.outline['RL'][1])
        self.rear_left_wheel.rotation_y = 90 + self.parent.rotation_y
        self.rear_right_wheel.world_position = Vec3(self.parent.vehicle_model.outline['RR'][0],
                                               self.left_wheel.world_position.y,
                                               self.parent.vehicle_model.outline['RR'][1])
        self.rear_right_wheel.rotation_y = -90 + self.parent.rotation_y


class Driver(Entity):
    import pygame

    def __init__(self, **kwargs):
        super().__init__(model='cube', collider='box', scale_x=1.8, scale_y=0.8, scale_z=4, origin_y=-1, **kwargs)
        self.vehicle_model = VehicleModel(position=np.array([[self.world_position.x], [self.world_position.z]]), rotation=self.rotation_y)
        self.wheel = Wheel(self)

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
        #print(self.world_position)
        self.get_driver_input()
        self.vehicle_model.update_position(self.aps, self.steering)
        position = self.vehicle_model.get_position()
        rotation = self.vehicle_model.get_rotation()
        #print(position, rotation)
        self.world_position = Vec3(position[0], self.world_position.y, position[1])
        self.rotation_y = rotation
        self.camera_following()
        self.wheel.update()
        #pass

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