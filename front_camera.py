from ursina import *
#from direct.showbase.ShowBase import ShowBase
from panda3d.core import Texture as PandaTexture
from roads import Road, PathGenerator
from driver import Driver
from PIL import Image
import numpy as np
import cv2
import copy

class Canvas(Entity):
    import cv2
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

    def clear_canvas(self):
        self.texture = Texture(Image.new(mode='RGBA', size=(self.map_size, self.map_size), color=(255, 255, 255, 255)))

    def put_texture(self, texture):
        self.texture = Texture(texture)


class FrontCamera(Entity):
    import cv2
    def __init__(self, app, **kwargs):
        #self.app = application
        super().__init__(**kwargs)
        self.base_texture = PandaTexture()
        self.base_buffer = app.win.makeTextureBuffer("Buffer", 512, 512, self.base_texture, True)
        self.base_cam = app.makeCamera(self.base_buffer)
        self.base_cam.reparentTo(render)
        self.base_cam.setPos(0, 10, 0)
        self.base_cam.setHpr(0, 15, 0)

        self.canvas = Canvas(position=window.top_left)
        self.is_canvas_enable = True

    def update(self):


        img_src = np.frombuffer(memoryview(self.base_texture.getRamImage()), dtype=np.uint8)






        if len(img_src):
            img = img_src.reshape((512, 512, int(len(img_src) / (512 * 512))))
            cv2.flip(img, 0, img)

            img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)


            img_res = img_gray

            if self.is_canvas_enable:
                img_pil = cv2.cvtColor(img_res, cv2.COLOR_GRAY2BGRA)
                self.canvas.put_texture(Image.fromarray(img_pil, 'RGBA'))#self.base_texture)
        #except:
            pass



    def set_canvas_enable(self, bool):
        self.is_canvas_enable = bool
        self.canvas.visible = bool

    def set_camera_position(self, position):
        self.base_cam.setPos(position)

    def set_camera_rotation(self, rotation):
        self.base_cam.setHpr((rotation[1], rotation[0], rotation[2]) )


if __name__=="__main__":
    from ursina.shaders import lit_with_shadows_shader
    from ursina.prefabs.first_person_controller import FirstPersonController

    app = Ursina()
    #window.size = (1024, 768)
    #tex = PandaTexture()
    #altBuffer = app.win.makeTextureBuffer("My Buffer", 512, 512, tex, True)
    #altBuffer.setSort(-100)
    #altRender = NodePath("new render")
    #altCam = app.makeCamera(altBuffer)
    #altCam.reparentTo(render)
    #altCam.setPos(0, 10, 0)
    #altCam.setHpr(15, 0, 0)
    #canvas = Canvas(position=window.top_left)

    fc = FrontCamera(app)

    random.seed(0)
    Entity.default_shader = lit_with_shadows_shader

    ground = Entity(model='plane', collider='box', scale=1024, texture='grass', texture_scale=(64, 64), name='ground')

    player = Driver(z=-20)

    path_generator = PathGenerator(initial_position=Vec3(-2, 0, 0), resolution=36)
    path_generator.push_straight_path(30)
    path_generator.push_angle_path(30, math.pi/18)
    path_generator.push_straight_path(5)
    path_generator.push_curve_path(30, -1/100)
    path_generator.push_angle_path(20, math.pi / 36)
    path = path_generator.export_path()


    road = Road(main_path=path, number_of_lane=3, is_oneway=False)
    canvas_trigger = True

    def update():
        fc.set_camera_position(player.get_camera_position())
        fc.set_camera_rotation(player.get_camera_rotation())
        #altCam.setPos(player.get_camera_position())
        #altCam.setHpr(player.get_camera_rotation())
        #canvas.put_texture(tex)

    def input(key):
        global canvas_trigger
        if key == 'tab up':
            canvas_trigger = not canvas_trigger
            fc.set_canvas_enable(canvas_trigger)


    sun = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))
    Sky()

    app.run()