from ursina import *

import math

class Vehicle(Entity):
    def __init__(self, **kwargs):
        try:
            super().__init__(model='assets/Car.obj', texture=None, collider='mesh', origin_y=0, color=color.orange, **kwargs)
        except:
            super().__init__(model='Box', texture=None, collider='mesh', origin_y=0, color=color.orange,
                             **kwargs)

    def update(self):
        pass
