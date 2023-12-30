# import libraries
import pygame
import numpy as np

# import my modules
from UI.base_state import BaseState
from UI.afm import afms
from event_manager import event_manager, mouse
import configs
from tools import *

# debug behavior vars
remove_failure = configs.debug_spk_failure and not configs.debug_master_off

# debug vars
debug = True
debug_failure = True


class Spk(BaseState):

    def __init__(self):
        super(Spk, self).__init__()

        self.base = vector(0, 0)
        self.current = vector(0, 0)

        # behavior values
        self.grace_time = 1.5  # seconds before failure allowance
        self.power_drain = 100
        self.r_decay = configs.spk_decay  # ratio of r to decay per second
        self.max_power = configs.spk_max
        self.mid_height = configs.height / 2
        self.min_height = configs.height * .8
        self.max_height = configs.height * .2
        self.center_width = configs.width + (configs.menu_width / 2)
        self.recovery_time = configs.spk_rec_time

        # init boundary lines
        self.mid_line = pygame.Rect((configs.width, self.mid_height), (configs.menu_width, 2))
        self.min_line = pygame.Rect((configs.width, self.min_height), (configs.menu_width, 2))
        self.max_line = pygame.Rect((configs.width, self.max_height), (configs.menu_width, 2))
        self.center_line = pygame.Rect((configs.width + (configs.menu_width / 2), 0), (2, configs.height))

        # init power rects
        self.base_rects = [pygame.Rect((0, 0), (0, 0)) for _ in range(2)]
        self.current_rects = [pygame.Rect((0, 0), (0, 0)) for _ in range(2)]

        # init values
        self.crossed = False
        self.old_mouse = mouse.position
        self.wait_time = self.grace_time
        self.power = 0
        self.base_power = [0, 0]
        self.current_power = [0, 0]
        self.rest_time = [0, 0]  # time since last input

        # debugging tracers
        self.num_tracers = 5
        self.tracers = [mouse.position for _ in range(self.num_tracers)]
        self.tracer_frames = 0
        self.draw_tracers = False

    def update(self, dt):
        super().update(dt)

        # manage tracers
        if debug:
            if mouse.position.y > self.mid_height:
                self.tracer_frames = 0
                self.tracers = self.tracers[1:] + [mouse.position]  # cycle tracers
                self.draw_tracers = False
            else:
                if self.tracer_frames < .5 * self.num_tracers:
                    self.tracer_frames += 1
                    self.tracers = self.tracers[1:] + [mouse.position]
                else:
                    self.draw_tracers = True

        # get current power
        if mouse.position.x > configs.width:  # if mouse is on the menu
            if mouse.position.x > self.center_width:
                xp = 1
            else:
                xp = 0
            if self.old_mouse.y > self.mid_height > mouse.position.y:  # crossed mid-line this frame
                self.rest_time[xp] = 0  # reset rest time
                # input power based on position
                mouse_power = (dt / 1000) * (vector.distance(self.old_mouse, mouse.position) / configs.spk_max)
                # final power boosts higher inputs from [0 1] and decreases inputs > 1
                # for an example, plot x^2 and sqrt(x) on the sample graph. current power is the minimum at each point.
                self.power = min([mouse_power ** _ for _ in [2, .5]])
                # create diminishing returns based on power to current power
                increase = math.exp(-2 * (self.current_power[xp] / (self.power / 2))) * self.power
                self.current_power[xp] += increase
                self.crossed = True

                # manage base power
                if self.base_power[xp] < 100:
                    self.base_power[xp] += self.power * self.current_power[xp]

                if debug:
                    print("---spk---")
                    print("Power: " + str(self.power))
                    print("Cur P: " + str(self.current_power[xp]))
                    print("Inc  : " + str(increase))
                    print("Base : " + str(self.base_power[xp]))


        # manage crossing the top border (y=max_height)
        if self.crossed:
            if mouse.position.y < self.max_height:
                self.crossed = False

        # manage current power drain
        for xp in range(2):
            if self.rest_time[xp] > self.recovery_time:
                if self.current_power[xp] > 0:
                    self.current_power[xp] *= (1 - (dt / 1000) * self.r_decay)
                if self.current_power[xp] < 0:
                    self.current_power[xp] = 0
            else:
                self.rest_time[xp] += (dt / 1000)

        # update old mouse position
        self.old_mouse = mouse.position

        # manage power bars
        for i in range(2):
            # base power bars
            base_height = (self.base_power[i] / 100) * configs.height
            base_top = configs.height - base_height
            self.base_rects[i] = pygame.Rect(((configs.width + (150 * i)), base_top), (50, base_height))

            # current power bars
            curr_height = ((configs.height - base_height) * self.current_power[i] * .75) + base_height
            curr_top = configs.height - curr_height
            self.current_rects[i] = pygame.Rect((configs.width + (150 * i), curr_top), (50, curr_height))


            # # current power bars
            # height = self.current_power[i] * configs.height * .75
            # top = configs.height - height
            # self.current_rects[i] = pygame.Rect(((configs.width + (150) * i), top), (50, height))
            #
            # # base power bars
            # height = (self.base_power[i] / 100) * configs.height
            # top = configs.height - height
            # self.base_rects[i] = pygame.Rect(((configs.width + 50 + (50 * i)), top), (50, height))

            # if debug:
            #     print([('.2f' % _) for _ in self.current_power])

        # --- failure conditions
        if self.wait_time > 0:
            self.wait_time -= (dt / 1000)
        else:
            # left click released
            if not mouse.buttons[1]:
                self.quit()
            # ensure we want to manage failure conditions
            if not remove_failure:
                # mouse leaves x bounds
                if configs.width > mouse.position.x or configs.resolution[0] < mouse.position.x:
                    if debug_failure: print("Failed due to leaving x boundaries")
                    self.quit()
                # mouse leaves y bounds
                if self.min_height < mouse.position.y:
                    if debug_failure: print("Failed to to crossing the min line")
                    self.quit()
                # mouse crosses mid line before crossing y=0
                if self.crossed and mouse.position.y > self.mid_height:
                    if debug_failure: print("Failed to reset before crossing midline")
                    self.quit()

    def draw(self, screen):
        super().draw(screen)

        # draw boundary lines
        pygame.draw.rect(screen, (0, 0, 0), self.mid_line)
        pygame.draw.rect(screen, (0, 0, 0), self.center_line)
        pygame.draw.rect(screen, configs.armor_color, self.min_line)
        pygame.draw.rect(screen, configs.armor_color, self.max_line)

        # draw current power bars
        for i in range(2):
            pygame.draw.rect(screen, configs.health_color, self.current_rects[i])
            pygame.draw.rect(screen, configs.armor_color, self.base_rects[i])

        # manage debug stuff
        if debug:
            if self.draw_tracers:
                for p in self.tracers:
                    pygame.draw.circle(screen, (255, 0, 0), p.as_tuple(), 3)

    def reset(self):
        # init values
        self.old_mouse = mouse.position
        self.power = [0]
        self.base_power = [0, 0]
        self.current_power = [0, 0]
        self.wait_time = self.grace_time
        self.crossed = False

    def quit(self):
        if debug:
            print("SPK is quitting")
        self.power = 0
        event_manager.player.release_actor()
        event_manager.player.control = True
