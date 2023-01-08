from ursina import *
from ursina.duplicate import duplicate
from ursina.ursinamath import sample_gradient
import numpy as np

class RoadModel(Mesh):
    def __init__(self, base_shape=Plane, origin=(0,0), path=((0,0,0),(0,1,0)), thicknesses=((1,0.01),), color_gradient=None, look_at=True, cap_ends=True, mode='triangle', **kwargs):
        if callable(base_shape):
            base_shape = base_shape()

        self.base_shape = base_shape
        self.origin = origin
        self.path = path
        self.thicknesses = thicknesses
        self.look_at = look_at
        self.cap_ends = cap_ends
        self.mode = mode
        self.color_gradient = color_gradient
        super().__init__(**kwargs)


    def generate(self):
        shape = [Vec3(-1.75, 0, 0), Vec3(1.75, 0, 0)]

        # make the base shape and rotate it
        b = Entity(position=self.path[0], color=color.lime, scale=self.thicknesses[0], origin=self.origin)
        for p in shape:
            Entity(parent=b, position=Vec3(p), model='cube', scale=(.05, .05, .05), color=color.yellow)

        dirc_vec = self.path[1] - self.path[0]
        dirc = math.atan2(dirc_vec[2], dirc_vec[0])
        b.rotation_y = 90 - dirc * 180 / math.pi # b.look_at(self.path[1])

        e = duplicate(b)

        verts = []
        self.colors = []

        # cap start
        if self.cap_ends:
            for i in range(len(b.children)):
                verts.append(self.path[0])
                verts.append(b.children[i].world_position)
                if i >= len(b.children)-1:
                    verts.append(b.children[0].world_position)
                else:
                    verts.append(b.children[i+1].world_position)

                if self.color_gradient:
                    self.colors.extend([self.color_gradient[0], ]*3)

        for i in range(1, len(self.path)):
            b.position = self.path[i-1]
            if self.look_at:
                dirc_vec = self.path[i] - self.path[i-1]
                dirc = math.atan2(dirc_vec[2], dirc_vec[0])
                b.rotation_y = 90 - dirc * 180 / math.pi # b.look_at(self.path[i])
            e.position = self.path[i]
            if i+1 < len(self.path) and self.look_at:
                dirc_vec = self.path[i+1] - self.path[i]
                dirc = math.atan2(dirc_vec[2], dirc_vec[0])
                e.rotation_y = 90 - dirc * 180 / math.pi # e.look_at(self.path[i+1])

            # for debugging sections
            # clone = duplicate(e)
            # clone.color=color.brown
            # clone.scale *= 1.1

            try:
                e.scale = self.thicknesses[i]
                b.scale = self.thicknesses[i-1]
            except:
                pass

            # add sides
            for j in range(len(e.children)):
                n = j+1
                if j == len(e.children)-1:
                    n = 0
                verts.append(e.children[j].world_position)
                verts.append(b.children[n].world_position)
                verts.append(b.children[j].world_position)

                verts.append(e.children[n].world_position)
                verts.append(b.children[n].world_position)
                verts.append(e.children[j].world_position)

                if self.color_gradient:
                    from_color = sample_gradient(self.color_gradient, (i-1)/(len(self.path)-1))
                    to_color = sample_gradient(self.color_gradient, (i-0)/(len(self.path)-1))
                    self.colors.append(to_color)
                    self.colors.append(from_color)
                    self.colors.append(from_color)
                    self.colors.append(to_color)
                    self.colors.append(from_color)
                    self.colors.append(to_color)

        # cap end
        if self.cap_ends:
            for i in range(len(e.children)):
                if i >= len(e.children)-1:
                    verts.append(e.children[0].world_position)
                else:
                    verts.append(e.children[i+1].world_position)
                verts.append(e.children[i].world_position)
                verts.append(self.path[-1])

                if self.color_gradient:
                    self.colors.extend([self.color_gradient[-1], ]*3)

        self.vertices = verts
        super().generate()
        destroy(b)
        destroy(e)

class Road:
    def __init__(self):
        path = [Vec3(4*math.cos(theta/4), 0.01, theta * 10) for theta in np.arange(0, math.pi * 10, math.pi / 18)]
        self.model = Entity(model=RoadModel(path=path, cap_ends=False, color_gradient=[color.gray, color.gray]))


if __name__=="__main__":
    from ursina.shaders import lit_with_shadows_shader
    from ursina.prefabs.first_person_controller import FirstPersonController

    app = Ursina()
    window.size = (1024, 768)

    random.seed(0)
    Entity.default_shader = lit_with_shadows_shader

    ground = Entity(model='plane', collider='box', scale=1024, texture='grass', texture_scale=(24, 24), name='ground')

    player = FirstPersonController(y=2, origin_y=-.5)

    road = Road()

    sun = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))
    Sky()

    app.run()