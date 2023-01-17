from ursina import *
from PIL import Image
import math

from vehicle import Vehicle, VehicleDynamics, Wheel
from roads import Road, PathGenerator
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

    def get_camera_position(self):
        follow = ursinamath.rotate_point_2d(Vec2(0, 2), Vec2(0, 0), self.rotation_y + self.steering * 180 / math.pi / 3)
        return self.world_position + Vec3(follow[0], 1.5, follow[1])

    def get_camera_rotation(self):
        return self.world_rotation

class Minimap(Entity):
    def __init__(self, position, **kwargs):
        self.map_size = 256
        self.boundary = 25
        super().__init__(
            parent=camera.ui,
            model="quad",
            scale=(0.4, 0.4),
            origin=(-0.5, 0.5),
            position=position,
            texture=Texture(Image.new(mode='RGBA', size=(self.map_size, self.map_size), color=(255, 255, 255, 255)))
        )

    def clear_minimap(self):
        self.texture = Texture(Image.new(mode='RGBA', size=(self.map_size, self.map_size), color=(255, 255, 255, 255)))

    def put_texture(self, texture):
        #self.texture._texture = texture
        self.texture = Texture(texture)
        #tex = Texture(texture)
        #tex.size = Vec2(512, 512)
        #print(texture)
        #self.setTexture(texture, 1)
        #self.reparent_to(texture)

    def draw_pcd(self, points):
        w = self.texture.width
        h = self.texture.height
        for point in points:
            x = point[0] / self.boundary * self.map_size
            y = point[1] / self.boundary * self.map_size
            if x <= w / 2 and x >= -w / 2 and y <= h / 2 and y >= -h / 2:
                self.texture.set_pixel(int(x + w / 2), int(y + h / 2), color.black)
        self.texture.apply()

if __name__=="__main__":
    from ursina.shaders import lit_with_shadows_shader
    from ursina.prefabs.first_person_controller import FirstPersonController

    app = Ursina()

    altBuffer = app.win.makeTextureBuffer("My Buffer", 512, 512)
    altRender = NodePath("new render")
    altCam = app.makeCamera(altBuffer)
    altCam.reparentTo(render)
    altCam.setPos(0, 10, 0)
    altCam.setHpr(15, 0, 0)
    mm = Minimap(position=window.top_left)

    random.seed(0)
    Entity.default_shader = lit_with_shadows_shader

    ground = Entity(model='plane', collider='box', scale=1024, texture='grass', texture_scale=(64, 64), name='ground')
    #road = Road(number_of_lane=3, is_oneway=False)

    target = Vehicle(z=-40, x=10)

    player = Driver(z=-20)
    ortho_bool = False

    path_generator = PathGenerator(resolution=32)
    path_generator.push_straight_path(20)
    path_generator.set_slope(10)
    path_generator.push_straight_path(20)
    path_generator.set_slope(0)
    path_generator.push_angle_path(30, math.pi / 6)
    path_generator.set_slope(-10)
    path_generator.push_straight_path(5)
    path_generator.set_slope(0)
    path_generator.push_curve_path(30, -1 / 50)
    path_generator.push_angle_path(20, math.pi / 3)
    path = path_generator.export_path()

    road = Road(main_path=path, number_of_lane=3, is_oneway=False)

    def update():
        global ortho_bool
        cam_pos = player.get_camera_position()
        cam_rot = player.get_camera_rotation()
        altCam.setPos(cam_pos)
        altCam.setHpr(cam_rot)
        mm.put_texture(altBuffer.getTexture())
        if held_keys['p']:
            exit()

        if held_keys['o']:
            ortho_bool = not ortho_bool
            player.set_camera_ortho(ortho_bool)


    sun = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))
    Sky()

    app.run()