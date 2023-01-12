from ursina import *
from ursina.duplicate import duplicate
from ursina.ursinamath import sample_gradient
import numpy as np

class PathGenerator:

    def __init__(self, initial_position=Vec3(0, 0.1, 0), initial_direction=Vec3(0, 0, 1), resolution=36, initial_slope=0):
        self.resolution = resolution
        self.unit_length = math.pi/self.resolution
        self.current_position = initial_position
        self.current_direction = initial_direction
        self.current_slope = 0
        self.target_slope = initial_slope
        self.path = []
        self.path.append(self.current_position*1)
        self.path_length_list = []
        self.path_curvature_list = []

    def push_straight_path(self, path_length):
        for path_current in np.arange(0, path_length, self.unit_length):
            self.current_position += self.unit_length * self.current_direction
            self.path.append(self.current_position*1)
            self.current_direction.y = ursinamath.distance_xz(Vec3(0,0,0), self.current_direction)*math.tan(self.current_slope*math.pi/180)
            self.current_direction = self.current_direction/ursinamath.distance(Vec3(0,0,0), self.current_direction)
            self.current_slope += (self.target_slope - self.current_slope)*0.1


    def push_curve_path(self, path_length, path_curvature):
        for path_current in np.arange(0, path_length, self.unit_length):
            self.current_position += self.unit_length * self.current_direction
            self.path.append(self.current_position*1)
            current_direction_2d_xz = ursinamath.rotate_point_2d(self.current_direction.xz, Vec3(0, 0, 0), self.unit_length * path_curvature*180/math.pi)
            current_direction_2d_y = ursinamath.distance_xz(Vec3(0, 0, 0), Vec3(current_direction_2d_xz[0], 0, current_direction_2d_xz[1])) * math.tan(
                self.current_slope * math.pi / 180)
            self.current_direction = Vec3(current_direction_2d_xz[0], current_direction_2d_y, current_direction_2d_xz[1])
            self.current_direction = self.current_direction/ursinamath.distance(Vec3(0,0,0), self.current_direction)
            self.current_slope += (self.target_slope - self.current_slope) * 0.1


    def push_angle_path(self, path_length, path_angle):
        step_angle = self.unit_length * path_angle / path_length * 180 / math.pi
        for path_current in np.arange(0, path_length, self.unit_length):
            self.current_position += self.unit_length * self.current_direction
            self.path.append(self.current_position*1)
            current_direction_2d_xz = ursinamath.rotate_point_2d(self.current_direction.xz, Vec3(0, 0, 0), step_angle)
            current_direction_2d_y = ursinamath.distance_xz(Vec3(0, 0, 0), Vec3(current_direction_2d_xz[0], 0,
                                                                                current_direction_2d_xz[1])) * math.tan(
                self.current_slope * math.pi / 180)
            self.current_direction = Vec3(current_direction_2d_xz[0], current_direction_2d_y,
                                          current_direction_2d_xz[1])
            self.current_direction = self.current_direction / ursinamath.distance(Vec3(0, 0, 0), self.current_direction)
            self.current_slope += (self.target_slope - self.current_slope) * 0.1

    def set_slope(self, slope):
        self.target_slope = slope

    def export_path(self):
        return self.path.copy()

    #def check_current_path(self):
    #    print([[self.path_length[i], self.path_curvature[i]] for i in range(len(self.path_length))])





class LaneModel(Mesh):
    def __init__(self, lane_position, lane_width, origin=(0,0), path=((0,0,0),(0,1,0)), is_center=False, **kwargs):
        self.lane_position = lane_position
        self.lane_width = lane_width
        self.base_shape = Plane()
        self.origin = origin
        self.path = path
        self.path_resolution = 36
        self.is_center = is_center
        self.thicknesses = ((1,0.01),)
        self.look_at = True
        self.cap_ends = False
        self.mode = 'ngon'
        if self.is_center:
            self.color_gradient = [color.yellow]
        else:
            self.color_gradient = [color.white]
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
            if not self.is_center and itr%(self.path_resolution) in [n for n in range(int(self.path_resolution/2))]:
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

            try:
                e.scale = self.thicknesses[i]
                b.scale = self.thicknesses[i - 1]
            except:
                pass

            # add sides
            if True:
                j = 0
                n = 1
            #for j in range(len(e.children)):
            #    n = j+1
            #    if j == len(e.children)-1:
            #        n = 0
                verts.append(b.children[j].world_position)
                verts.append(b.children[n].world_position)
                verts.append(e.children[j].world_position)

                verts.append(e.children[n].world_position)
                verts.append(e.children[j].world_position)
                verts.append(b.children[n].world_position)

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
    def __init__(self, road_width=3.5, origin=(0,0), path=((0,0,0),(0,1,0)), **kwargs):

        self.road_width = road_width
        self.base_shape = Plane()
        self.origin = origin
        self.path = path
        self.thicknesses = ((1, 0.01),)
        self.look_at = True
        self.cap_ends = False
        #self.mode = 'triangle'
        self.color_gradient = [color.gray]
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
            if True:
                j = 0
                n = 1
            #for j in range(len(e.children)):
            #    n = j+1
            #    if j == len(e.children)-1:
            #        n = 0

                verts.append(b.children[j].world_position)
                verts.append(b.children[n].world_position)
                verts.append(e.children[j].world_position)

                verts.append(e.children[n].world_position)
                verts.append(e.children[j].world_position)
                verts.append(b.children[n].world_position)

                #print(i, j, n, b.children[j].world_position, e.children[j].world_position, b.children[n].world_position,
                #      e.children[n].world_position, b.children[n].world_position, e.children[j].world_position)

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
        #self.uvs = [(v[0], v[1]) for v in verts]
        super().generate()
        destroy(b)
        destroy(e)

class Road:
    def __init__(self, main_path=[Vec3(2*math.cos(theta), 0.1, theta * 8) for theta in np.arange(0, 2*math.pi, math.pi / 64)], number_of_lane=1, is_oneway=True):
        self.main_path = main_path
        #asphalt = load_texture("asphalt", "./assets/asphalt_texture.jpg")
        road_width = 3.5
        lane_width = 0.15
        self.road = {}
        self.road_mesh_control = {}
        self.llane = {}
        self.rlane = {}

        for i in range(number_of_lane):

            path_road = [(self.main_path[j+1]-self.main_path[j]).cross(Vec3(0,-1,0)).normalized()*road_width*(0.5+i)+self.main_path[j] for j in range(len(self.main_path)-1)]
            self.road[str(i+1)] = Entity(model=RoadModel(road_width=road_width, path=path_road), collider='mesh')

            if i == 0:
                self.llane[str(i+1)] = Entity(model=LaneModel(lane_position=-road_width / 2 + lane_width / 2, is_center=True, lane_width=lane_width, path=path_road))
            else:
                self.llane[str(i+1)] = Entity(model=LaneModel(lane_position=-road_width / 2 + lane_width / 2, lane_width=lane_width, path=path_road))
            self.rlane[str(i+1)] = Entity(model=LaneModel(lane_position=road_width / 2 - lane_width / 2, lane_width=lane_width, path=path_road))

            if not is_oneway:
                path_road = [(self.main_path[j + 1] - self.main_path[j]).cross(Vec3(0, 1, 0)).normalized() * road_width * (0.5 + i) + self.main_path[j] for j
                             in range(len(self.main_path) - 1)]
                self.road[str(-(i+1))] = Entity(model=RoadModel(road_width=road_width, path=path_road), collider='mesh')

                if i == 0:
                    self.rlane[str(-(i+1))] = Entity(
                        model=LaneModel(lane_position=road_width / 2 - lane_width / 2,  is_center=True, lane_width=lane_width,
                                        path=path_road))
                else:
                    self.rlane[str(-(i+1))] = Entity(
                        model=LaneModel(lane_position=road_width / 2 - lane_width / 2, lane_width=lane_width,
                                        path=path_road))
                self.llane[str(-(i+1))] = Entity(
                    model=LaneModel(lane_position=-road_width / 2 + lane_width / 2, lane_width=lane_width,
                                    path=path_road))



if __name__=="__main__":
    from ursina.shaders import lit_with_shadows_shader
    from ursina.prefabs.first_person_controller import FirstPersonController

    app = Ursina()
    #window.size = (1024, 768)

    random.seed(0)
    Entity.default_shader = lit_with_shadows_shader

    ground = Entity(model='plane', collider='box', scale=1024, texture='grass', texture_scale=(64, 64), name='ground')



    player = FirstPersonController()


    path_generator = PathGenerator(resolution=32)
    path_generator.push_straight_path(5)
    path_generator.set_slope(10)
    path_generator.push_straight_path(10)
    path_generator.set_slope(0)
    path_generator.push_angle_path(30, math.pi/6)
    path_generator.set_slope(-10)
    path_generator.push_straight_path(5)
    path_generator.set_slope(0)
    path_generator.push_curve_path(30, -1/50)
    path_generator.push_angle_path(20, math.pi / 3)
    path = path_generator.export_path()


    road = Road(main_path=path, number_of_lane=3, is_oneway=False)

    #p = Entity(model='plane',scale_z=5, origin_y=-1.5)#, texture="assets/asphalt_texture3.jpg")
    #p.texture_scale = (5,5)

    sun = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))
    Sky()

    app.run()