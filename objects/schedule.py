"""
Singleton used for sheduling events, currently just a clock
"""

import pygame
import math

# import custom modules
import configs
from tools import vector

# import custom classes
from objects.base_object import BaseObject

# debug variables
debug = True

class Clock(BaseObject):

    def __init__(self):
        super(Clock, self).__init__()
        # name for finding in list of game objects
        self.name = "schedule"

        # time controls
        self.length = configs.period_length * 60  # length of each round (in seconds)
        self.time = self.length  # current time
        self.run = False  # if the clock needs to run

        # other controls
        self.period = 1  # current period

        # display attributes
        self.position = vector(35, 20)

    def update(self, dt):
        super().update(dt)

        if self.time <= 0:
            return

        # update the current time
        self.time -= dt / 1000

        if self.time <= 0:
            if debug: print("Schedule Expired!")
            self.reset()

    def draw(self, screen):
        super().draw(screen)

        # write the time as a string (p mm:ss)
        txt = configs.graph_font.render(self.get_string(), True, configs.text_color)
        txtb = txt.get_rect(center=(self.position.x, self.position.y))
        screen.blit(txt, txtb)

    def get_string(self):
        (m, s) = divmod(self.time, 60)
        s = math.ceil(s)
        return "%i - %02i:%02.0f" % (self.period, m, s)

    def reset(self):
        self.time = self.length
        if self.period >= configs.period_total:
            self.period = 1
        else:
            self.period += 1

# create a schedule singleton
schedule = Clock()






