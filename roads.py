from ursina import *
from ursina.duplicate import duplicate
from ursina.ursinamath import sample_gradient
import numpy as np

class LaneModel(Mesh):
    def __init__(self, lane_position, lane_width, base_shape=Plane, origin=(0,0), path=((0,0,0),(0,1,0)), is_center=False, thicknesses=((1,0.01),), color_gradient=[color.white], look_at=True, cap_ends=False, mode='line', **kwargs):
        if callable(base_shape):
            base_shape = base_shape()
        self.lane_position = lane_position
        self.lane_width = lane_width
        self.base_shape = base_shape
        self.origin = origin
        self.path = path
        self.is_center = is_center
        self.thicknesses = thicknesses
        self.look_at = look_at
        self.cap_ends = cap_ends
        self.mode = mode
        if self.is_center:
            self.color_gradient = [color.yellow]
        else:
            self.color_gradient = color_gradient
        super().__init__(**kwargs)


    def generate(self):
        shape = [Vec3(self.lane_position - self.lane_width/2, 0.1, 0), Vec3(self.lane_position + self.lane_width/2, 0.1, 0)]


        # make the base shape and rotate it
        b = Entity(position=self.path[0], color=color.lime, scale=self.thicknesses[0], origin=self.origin)
        for p in shape:
            Entity(parent=b, position=Vec3(p), model='cube', scale=(.01, .01, .01), color=color.yellow)

        dirc_vec = self.path[1] - self.path[0]
        dirc = math.atan2(dirc_vec[2], dirc_vec[0])
        b.rotation_y = 90 - dirc * 180 / math.pi # b.look_at(self.path[1])

        e = duplicate(b)

        verts = []
        self.colors = []
        itr = 0
        for i in range(1, len(self.path)):
            itr += 1
            if not self.is_center and itr%8 in [n for n in range(int(8/2))]:
                continue
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
                b.scale = self.thicknesses[i - 1]
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




        self.vertices = verts
        self.uvs = [(v[0], v[1]) for v in verts]
        super().generate()
        destroy(b)
        destroy(e)
class RoadModel(Mesh):
    def __init__(self, road_width=3.5, base_shape=Plane, origin=(0,0), path=((0,0,0),(0,1,0)), thicknesses=((1,0.01),), color_gradient=None, look_at=True, cap_ends=False, mode='line', **kwargs):
        if callable(base_shape):
            base_shape = base_shape()

        self.road_width = road_width
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
        shape = [Vec3(-self.road_width/2, 0, 0), Vec3(self.road_width/2, 0, 0)]

        # make the base shape and rotate it
        b = Entity(position=self.path[0], color=color.lime, scale=self.thicknesses[0], origin=self.origin)
        for p in shape:
            Entity(parent=b, position=Vec3(p), model='cube', scale=(.01, .01, .01), color=color.yellow)

        dirc_vec = self.path[1] - self.path[0]
        dirc = math.atan2(dirc_vec[2], dirc_vec[0])
        b.rotation_y = 90 - dirc * 180 / math.pi # b.look_at(self.path[1])

        e = duplicate(b)

        verts = []
        self.colors = []

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

        self.vertices = verts
        self.uvs = [(v[0], v[1]) for v in verts]
        super().generate()
        destroy(b)
        destroy(e)

class Road:
    def __init__(self, number_of_lane=1, is_oneway=True):
        path = [Vec3(2*math.cos(theta/8), 0.1, theta * 2) for theta in np.arange(0, 32*math.pi, math.pi / 18)]
        #asphalt = load_texture("asphalt", "./assets/asphalt_texture.jpg")
        road_width = 3.5
        lane_width = 0.15
        self.model = []
        self.llane = []
        self.rlane = []
        for i in range(number_of_lane):

            path_road = [(path[j+1]-path[j]).cross(Vec3(0,-1,0)).normalized()*road_width*(0.5+i)+path[j] for j in range(len(path)-1)]
            self.model.append(Entity(model=RoadModel(road_width=road_width, path=path_road, color_gradient=[color.light_gray])))#, texture="assets/asphalt_texture3.jpg")

            if i == 0:
                self.llane.append(Entity(model=LaneModel(lane_position=-road_width / 2 + lane_width / 2, is_center=True, lane_width=lane_width, path=path_road)))
            else:
                self.llane.append(Entity(model=LaneModel(lane_position=-road_width / 2 + lane_width / 2, lane_width=lane_width, path=path_road)))
            self.rlane.append(Entity(model=LaneModel(lane_position=road_width / 2 - lane_width / 2, lane_width=lane_width, path=path_road)))

            if not is_oneway:
                path_road = [(path[j + 1] - path[j]).cross(Vec3(0, 1, 0)).normalized() * road_width * (0.5 + i) + path[j] for j
                             in range(len(path) - 1)]
                self.model.append(Entity(model=RoadModel(road_width=road_width, path=path_road, color_gradient=[
                    color.light_gray])))  # , texture="assets/asphalt_texture3.jpg")

                if i == 0:
                    self.rlane.append(Entity(
                        model=LaneModel(lane_position=road_width / 2 - lane_width / 2,  is_center=True, lane_width=lane_width,
                                        path=path_road)))
                else:
                    self.rlane.append(Entity(
                        model=LaneModel(lane_position=road_width / 2 - lane_width / 2, lane_width=lane_width,
                                        path=path_road)))
                self.llane.append(Entity(
                    model=LaneModel(lane_position=-road_width / 2 + lane_width / 2, lane_width=lane_width,
                                    path=path_road)))



            #self.model.texture_scale = (5, 5)

            #print(self.model.texture)


if __name__=="__main__":
    from ursina.shaders import lit_with_shadows_shader
    from ursina.prefabs.first_person_controller import FirstPersonController

    app = Ursina()
    #window.size = (1024, 768)

    random.seed(0)
    Entity.default_shader = lit_with_shadows_shader

    ground = Entity(model='plane', collider='box', scale=1024, texture='grass', texture_scale=(64, 64), name='ground')

    player = FirstPersonController(y=1.5, origin_y=0)

    road = Road(number_of_lane=3, is_oneway=False)

    #p = Entity(model='plane',scale_z=5, origin_y=-1.5)#, texture="assets/asphalt_texture3.jpg")
    #p.texture_scale = (5,5)

    sun = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))
    Sky()

    app.run()