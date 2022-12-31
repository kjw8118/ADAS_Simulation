from ursina import *

import math

class Vehicle(Entity):

    steering_angle = 0

    def __init__(self, **kwargs):
        super().__init__(model='cube', scale_x=1.5, scale_y=1, scale_z=2.5, origin_y=-.5, color=color.orange, collider='box', **kwargs)


    def update(self):
        angle = self.steering_angle + held_keys['q'] - held_keys['e']
        if angle > 30:
            angle = 30
        if angle < -30:
            angle = -30

        self.steering_angle = angle

    def drive(self):
        self.forward