"""
Script for success/failure of initial attack
Goal is to run the mouse through 3 different points in configs.grab_time seconds
"""
import pygame

# import libraries
from itertools import compress
import numpy as np

# import my modules
from UI.base_state import BaseState
import configs
from tools import *

# get singletons
from event_manager import mouse, event_manager

# variables for the things
indicator_colors = {
    True: configs.success_green + (configs.grab_alpha, ),
    False: configs.failure_red + (configs.grab_alpha, )
}

indicator_colors = {
    True: pygame.Color(configs.success_green, a=.1),
    False: pygame.Color(configs.failure_red, a=100)
}

debug = False


class Grab(BaseState):

    def __init__(self):
        super(Grab, self).__init__()
        self.num_circles = configs.grab_num
        self.positions = {random_position(): False for _ in range(self.num_circles)}  # dict of {position: hit_bool}
        self.grab_time = configs.grab_time
        self.time = self.grab_time
        self.colors = {p: indicator_colors[self.positions[p]] for p in self.positions.keys()}  # color for each circle
        self.grab_size = configs.grab_size

    def update(self, dt):
        super().update(dt)

        # ps = list(compress(self.positions.keys(), np.logical_not(self.positions.values())))
        ps = list(compress(self.positions.keys(), np.logical_not(list(self.positions.values()))))
        for p in ps:  # only loop through un-hit positions
            dist = vector.distance(p, mouse.position)
            if dist < self.grab_size:
                self.positions[p] = True

        # deal with success case
        if all(self.positions.values()):
            if debug: print(self.positions.values())
            # break out and change state
            event_manager.player.good_grab()

        # deal with failure case
        if self.time < 0:
            # break out back to idle
            event_manager.player.fail_grab()
        else:
            # subtract dt from current time left
            # print(self.time)
            self.time -= (dt / 1000)

        self.colors = {p: indicator_colors[self.positions[p]] for p in self.positions.keys()}  # color for each circle

        # create rect to display remaining time
        time_height = (self.time / self.grab_time) * configs.height
        self.time_rectangle = pygame.Rect((configs.width + (configs.menu_width/2) - (configs.grab_bar_width/2),
                                           configs.height - time_height),
                                          (configs.grab_bar_width, time_height))

    def draw(self, screen):
        super().draw(screen)
        for p in self.positions:
            pygame.draw.circle(screen, self.colors[p], p.as_tuple(), self.grab_size)
        pygame.draw.rect(screen, configs.attack_color, self.time_rectangle)



    def reset(self):
        # get actor and player
        player = event_manager.player
        actor = event_manager.player.holding

        # calculate relative stats
        s_diff = player.strength - actor.strength
        f_diff = player.finesse - actor.finesse
        e_diff = player.endurance - actor.endurance

        # Assign starting values
        self.grab_size = configs.grab_size * (1 + (s_diff * .1))  # 10% change per level
        self.grab_time = configs.grab_time * (1 + (e_diff * .05))  # 10% change per level
        self.num_circles = [round(_) for _ in np.linspace(configs.grab_num*2, 1, 11)][f_diff + 5]  # arbitrary function (plot it range [-4, 4])
        self.positions = {random_position(): False for _ in range(self.num_circles)}  # new random positions
        self.time = configs.grab_time


