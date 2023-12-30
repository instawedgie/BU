"""
Used to carry and actor
"""

# import libraries
import pygame
import numpy as np

# import my modules
from UI.base_state import BaseState
from UI.afm import afms
from event_manager import event_manager, mouse
import configs
from tools import *

# define some stats
bar_width = configs.power_bar_width
bar_left = configs.width + ((configs.menu_width - bar_width) / 2)

debug = False  # control printing to the console
debug_power = not configs.debug_master_off and configs.debug_squ_power  # directly control power w/ mouse y position

class Squ(BaseState):

    def __init__(self):
        super(Squ, self).__init__()

        # initialize values
        self.power_x = 0
        self.power_y = 0
        self.power_list_x = [0 for _ in range(configs.num_averages)]
        self.power_list_y = [0 for _ in range(configs.num_averages)]
        self.max_mouse_power_x = configs.max_mouse_power
        self.max_mouse_power_y = configs.max_mouse_power
        # self.min_power = 0
        self.power_frames = 0
        self.started = False
        self.att = None

        # initialize mouse tracers
        mouse_pos = vector_from_tuple(pygame.mouse.get_pos())
        self.tracers = [vector(0, 0) for _ in range(configs.num_tracers)]

        # initialize displays
        self.bar_rect_x = pygame.Rect((bar_left, 0), (bar_width, 0))  # initialize w/ 0 height
        self.bar_rect_y = pygame.Rect((bar_left, 0), (bar_width, 0))  # initialize w/ 0 height
        self.gain_rect_x = pygame.Rect((bar_left, 0), (bar_width, 0))
        self.gain_rect_y = pygame.Rect((bar_left, 0), (bar_width, 0))
        self.min_rect = pygame.Rect((bar_left, 0), (bar_width, 0))  # initialize w/ 0 height
        self.armor_rect = pygame.Rect((bar_left, 0), (bar_width, 0))  # initialize w/ 0 height
        self.health_rect = pygame.Rect((bar_left, 0), (bar_width, 0))  # initialize w/ 0 height
        self.break_rect = pygame.Rect((bar_left, 0), (bar_width, 0))  # initialize w/ 0 height

    # update the height of the power bar
    def update(self, dt):
        super().update(dt)

        # TODO: Current code to exit the control state is managed by the player. Should be moved to the class instead.

        # track the mouse
        mouse_pos = vector_from_tuple(pygame.mouse.get_pos())  # vector of the mouse position
        self.tracers = self.tracers[1:] + [mouse_pos]  # remove first entry, add new mouse pos

        # calculate the power
        if not debug_power:
            xlist = [_.x for _ in self.tracers]
            max_dist = max(xlist) - min(xlist)
            current_power = max_dist / self.max_mouse_power
            self.power_list_x = self.power_list_x[1:] + [current_power]
            self.power_x = sum(self.power_list_x) / configs.num_averages

            ylist = [_.y for _ in self.tracers]
            max_dist = max(ylist) - min(ylist)
            current_power = max_dist / self.max_mouse_power_y
            self.power_list_y = self.power_list_y[1:] + [current_power]
            self.power_y = sum(self.power_list_y) / configs.num_averages

        else:
            self.power_x = max((mouse_pos.y / (configs.height / 2), 0))
            self.power_y = max((mouse_pos.x / (configs.width / 2), 0))

        event_manager.player.holding.afm_damage(self.power_x, dt, afm=[afms['REG']])
        event_manager.player.holding.afm_damage(self.power_y, dt, afm=[afms['FRO']])

        # power bar rectangle x
        bar_height = self.power_x * configs.height
        bar_top = configs.height - bar_height
        self.bar_rect_x = pygame.Rect((configs.width + (configs.menu_width * .25), bar_top),
                                    (bar_width, bar_height))

        # overflow rectangle x
        mx = max((0, self.power_x - 1))
        gain_height = mx * configs.height
        # gain_top = configs.height - gain_height
        self.gain_rect_x = pygame.Rect((configs.width + (configs.menu_width * .25), 0),
                                    (bar_width, gain_height))

        # power bar rectangle y
        bar_height = self.power_y * configs.height
        bar_top = configs.height - bar_height
        self.bar_rect_y = pygame.Rect((configs.width + (configs.menu_width * 0), bar_top),
                                      (bar_width, bar_height))

        # overflow rectangle y
        my = max((0, self.power_y - 1))
        gain_height = my * configs.height
        # gain_top = configs.height - gain_height
        self.gain_rect_y = pygame.Rect((configs.width + (configs.menu_width * 0), 0),
                                       (bar_width, gain_height))

        # manage actor health display
        health_height = event_manager.player.holding.health / 100 * configs.height
        health_top = configs.height - health_height
        self.health_rect = pygame.Rect((configs.width + (configs.menu_width * .75), health_top),
                                       (bar_width, health_height))

        # manage actor armor display
        armor_height = event_manager.player.holding.armor.health / 100 * configs.height
        armor_top = configs.height - armor_height
        self.armor_rect = pygame.Rect((configs.width + (configs.menu_width * .5), armor_top),
                                      (bar_width, armor_height))

        # manage armor break display
        bs = event_manager.player.holding.armor.current_bs
        break_height = (bs - 1) * configs.height
        # break_top = configs.height - armor_height
        self.break_rect = pygame.Rect((configs.width, break_height),
                                    (configs.menu_width, 2))  # draw line for min power

        # manage failure conditions
        if mouse.buttons_up[1]:  # if we release the mouse
            self.quit()
        # TODO: Check for broken armor

        # if self.power_frames < 30:
        #     if self.power > self.min_power:
        #         self.power_frames += 1
        # else:
        #     if debug: print(self.min_power)
        #     if self.power < self.min_power:
        #         self.quit()
        #         event_manager.player.release_actor()

    def draw(self, screen):
        super().draw(screen)
        # draw the power bar x
        pygame.draw.rect(screen, configs.attack_color, self.bar_rect_x)
        # draw the gain line x
        pygame.draw.rect(screen, configs.false_color, self.gain_rect_x)
        # draw the power bar y
        pygame.draw.rect(screen, configs.attack_color, self.bar_rect_y)
        # draw the gain line y
        pygame.draw.rect(screen, configs.false_color, self.gain_rect_y)
        # draw a line for min power
        pygame.draw.rect(screen, configs.false_color, self.min_rect)
        # draw armor break line
        pygame.draw.rect(screen, configs.armor_color, self.break_rect)
        # draw health line
        pygame.draw.rect(screen, configs.health_color, self.health_rect)
        # draw armor line
        pygame.draw.rect(screen, configs.armor_color, self.armor_rect)


    def reset(self):

        # use actor/player stats to control difficulty of the state
        player = event_manager.player
        actor = player.holding
        self.att = actor.att

        # set state difficulty
        p_diff = player.strength - actor.strength
        f_diff = player.finesse - actor.finesse
        self.max_mouse_power = configs.max_mouse_power * (1 - (p_diff * .15))  # 10% change per level diff
        self.max_mouse_power_y = configs.max_mouse_power_y * (1 - (p_diff * .05))  # 10% change per level diff
        if actor.stuck or actor.suspension:
            self.min_power = 0
        else:
            self.min_power = ((4 - f_diff) * .1)  # n% max power per level

        # set initial values
        self.min_rect = pygame.Rect((configs.width, configs.height * (1 - self.min_power)), (configs.menu_width, 2))  # draw line for min power
        self.power_list_x = [0 for _ in range(configs.num_averages)]  # reset power list to 0
        self.power_list_y = [0 for _ in range(configs.num_averages)]  # reset power list to 0
        mouse_pos = vector_from_tuple(pygame.mouse.get_pos())  # get current mouse position
        self.tracers = [mouse_pos for _ in range(configs.num_tracers)]  # reset tracers to current mouse position
        self.power_x = 0
        self.power_y = 0
        self.bar_rect_x = (0, 0, 0, 0)
        self.bar_rect_y = (0, 0, 0, 0)
        self.power_frames = 0  # count how many frames we are in the power for

    def quit(self):
        """
        Reset the mouse to the center of the screen when control is finished
            - Helps not need to recenter the mouse yourself
            - Helps player maintain control at the end of the attack
        :return: None
        """
        pygame.mouse.set_pos((configs.width / 2, configs.height / 2))
        event_manager.player.release_actor()
        event_manager.player.control = True


