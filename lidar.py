from ursina import *
from PIL import Image
import numpy as np
# import cv2
# import open3d as o3d
import pcl

import math
import csv

from vehicle import Vehicle

class Cloud:
    points = []
    def __init__(self):
        pass

    def put_point(self, position, direction):
        self.points.append(Entity(model='sphere', scale=0.05, color=color.red, position=position))

    def clear_points(self):
        for point in self.points:
            destroy(point)
        self.points.clear()

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

    def draw_pcd(self, points):
        w = self.texture.width
        h = self.texture.height
        for point in points:
            x = point[0] / self.boundary * self.map_size
            y = point[1] / self.boundary * self.map_size
            if x <= w / 2 and x >= -w / 2 and y <= h / 2 and y >= -h / 2:
                self.texture.set_pixel(int(x + w / 2), int(y + h / 2), color.black)
        self.texture.apply()

class LiDAR(Entity):
    tof = {}
    img = None
    height = 800
    width = 800
    resolution = 2
    # pc = pcl.PointCloud()
    points = []
    cloud = Cloud()
    #cntr = Entity(model='sphere', scale=0.1, color=color.red)
    def __init__(self, **kwargs):
        super().__init__(model='cube', origin_y=-0.5, color=color.light_gray, **kwargs)

        #self.minimap = Minimap(position=window.top_left)
        #self.minimap2 = Minimap(position=window.top_right)

    def update(self):
        pcd_points = []

        world_rot_y = self.world_rotation_y
        for theta in np.arange(-6, 6, 2):
        #if True:
            #theta = 0
            for phi in np.arange(0, 360, 0.4):

                direction = Vec3(math.cos((phi + world_rot_y) / 180 * math.pi),
                                 math.sin(theta / 180 * math.pi),
                                 math.sin((phi + world_rot_y) / 180 * math.pi))
                hit = raycast(self.world_position + (0, 0.5, 0), direction, ignore=(self, self.parent), distance=50, debug=False)

                if hit.hit:
                    x = hit.distance * math.cos(phi / 180 * math.pi)
                    y = hit.distance * math.sin(phi / 180 * math.pi)
                    z = hit.distance * math.sin(theta / 180 * math.pi)
                    pcd_points.append([x, y, z])

        self.points = pcd_points
        pcd = pcl.PointCloud(pcd_points)
        vox = pcd.make_voxel_grid_filter()
        leaf_size = 1
        vox.set_leaf_size(leaf_size, leaf_size, leaf_size)
        vox_grid = vox.filter()
        self.cloud.clear_points()
        for pcd_point in vox_grid.to_array():
            x = self.world_x + pcd_point[0]*math.cos(world_rot_y / 180 * math.pi) - pcd_point[1]*math.sin(world_rot_y/ 180 * math.pi)
            y = self.world_y + 0.5 + pcd_point[2]
            z = self.world_z + pcd_point[0]*math.sin(world_rot_y / 180 * math.pi) + pcd_point[1]*math.cos(world_rot_y/ 180 * math.pi)
            self.cloud.put_point((x, y, z), [0, world_rot_y, 0])


        # Draw minimap
        #self.minimap2.clear_minimap()
        #self.minimap2.draw_pcd(cloud.to_array())
        #self.minimap.clear_minimap()
        #self.minimap.draw_pcd(self.points)



if __name__ == "__main__":
    from ursina.shaders import lit_with_shadows_shader
    from ursina.prefabs.first_person_controller import FirstPersonController

    #app = Ursina(position=(2000, 500))
    app = Ursina()

    window.size = (800, 600)

    random.seed(0)
    Entity.default_shader = lit_with_shadows_shader

    ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4, 4), name='ground')

    cars = [Vehicle(x=(x - 5) * 5, z=-(x - 5) * (x - 5)) for x in range(10)]

    player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=0, speed=8)
    player.collider = BoxCollider(player, center=Vec3(0, 0, 0), size=Vec3(1, .5, 2))

    lidar = LiDAR(parent=player, visible=False)


    def update():
        if held_keys['tab']:
            pass
        if held_keys['q']:
            exit()

    sun = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))
    Sky()

    app.run()
