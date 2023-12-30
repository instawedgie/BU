"""
Used to complete a task through the combat interface
"""
import pygame

import configs

from UI.base_state import BaseState

# get singletons
from event_manager import mouse, event_manager

debug = False


class Task(BaseState):
    def __init__(self):
        super(Task, self).__init__()

        # important values
        self.max_power = configs.task_max_power
        self.midline = (configs.menu_width / 2) + configs.width
        self.task_power = configs.task_power
        self.task_drain = configs.task_drain

        # display variables
        self.bar_left = self.midline - (configs.task_width / 2)
        self.side_box_width = configs.menu_width / 2
        self.success_box = pygame.Rect((configs.width, 0), (configs.menu_width, configs.height))
        self.ready_color = configs.success_green
        self.wait_color = configs.failure_red

        # init values in reset
        self.power = None  # power value
        self.side = None  # boolean for side of UI midline to click
        self.ready = None  # ready for the right click
        self.bar_rect = pygame.Rect((0, 0), (0, 0))  # holder for pygame.rect class
        self.side_rect = pygame.Rect((0, 0), (0, 0))  # holder for pygame.rect class
        self.color = None  # color to display the power bar

    def update(self, dt):
        super().update(dt)

        # handle clicks
        if mouse.buttons_down[1] and self.get_mouse_side(mouse.position):
            self.power += self.task_power
            self.side = not self.side

        # handle success
        self.ready = self.power > self.max_power
        if self.ready:
            self.color = self.ready_color
            if mouse.buttons_down[3]:  # if we right click
                if debug: print("Successful Task!")
                event_manager.player.successful_task()
        else:
            self.color = self.wait_color

        # handle power drain / failure case
        self.power -= self.task_drain * (dt / 1000)
        if self.power < 0:
            event_manager.player.failed_task()

        # handle power bar rectangle
        bar_height = (self.power / self.max_power) * configs.height
        bar_top = configs.height - bar_height
        self.bar_rect = pygame.Rect((self.bar_left, bar_top), (configs.task_width, bar_height))

        # handle correct side indicator
        if self.side:  # right side
            self.side_rect = pygame.Rect((self.midline, 0), (self.side_box_width, configs.height))
        else:  # left side
            self.side_rect = pygame.Rect((configs.width, 0), (self.side_box_width, configs.height))

    def draw(self, screen):
        super().draw(screen)

        # handle correct side bar
        pygame.draw.rect(screen, configs.task_side_color, self.side_rect)
        # handle power bar
        pygame.draw.rect(screen, self.color, self.bar_rect)

    # called when switched through interface FSM
    def reset(self):
        # get player and actor
        player = event_manager.player
        actor = player.holding

        # calc differences
        s_diff = player.strength - actor.strength
        f_diff = player.finesse - actor.finesse
        e_diff = player.endurance - actor.endurance

        # assign state variables
        self.max_power = configs.task_max_power * (1 - (s_diff * .1))  # 10% change per level
        self.task_power = configs.task_power * (1 + (f_diff * .1))  # 10% change per level
        self.task_drain = configs.task_drain * (1 - (e_diff * .1))  # 10% change per level
        self.power = configs.task_start  # start with some power (helps not get to 0)
        self.side = False  # start on left side
        self.ready = False
        self.color = self.wait_color

    # --- helper functions

    def get_mouse_side(self, pos):
        """
        Determine which side of the power bar the mouse is on
        :param pos: mouse position
        :return: Bool for if mouse is in a correct position
        """
        return (pos.x > self.midline) == self.side
