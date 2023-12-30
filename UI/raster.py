"""
Used to select an attack after a successful grab
"""

import pygame

import numpy as np
import math

# import my tools
import configs
import tools
from tools import vector

# import my modules
from UI.base_state import BaseState
from event_manager import mouse, event_manager

debug = False  # controls printing to the console

class Raster(BaseState):
    def __init__(self):
        super(Raster, self).__init__()

        # set up pixels
        self.resolution = configs.raster_resolution
        square_size = configs.menu_width
        self.window_size = (square_size, square_size)
        # nested tuple of ((left, top), (right, bottom))
        self.bounds = ((configs.width, (configs.height - self.window_size[1]) / 2),
                       (configs.resolution[0], configs.height - ((configs.height - self.window_size[1]) / 2)))

        # raster pixel sizing
        self.pixel_width = math.ceil(self.window_size[0] / self.resolution[0])
        self.pixel_height = math.ceil(self.window_size[1] / self.resolution[1])
        self.pixel_shape = (self.pixel_width, self.pixel_height)

        # raster pixel locations
        height_offset = (configs.height - self.window_size[1]) / 2
        self.xs = (np.array(range(self.resolution[0])) * self.pixel_width) + configs.width
        self.ys = (np.array(range(self.resolution[1])) * self.pixel_height) + height_offset

        # start inits by reset
        self.nt = None
        self.colors = None
        self.right_hold = True  # suspend input until right mouse is no longer held down
        self.reset()

        # define pixel array
        self.pixels = [
            [
                pygame.Rect(self.xs[xi], self.ys[yi], self.pixel_width, self.pixel_height)
                for yi in range(self.resolution[1])]
            for xi in range(self.resolution[0])]

        # set up other stats to display
        self.font = configs.graph_font
        self.armor = None
        self.armor_text = None
        self.armor_rect = None

    # Handles most of the init (since it will be happening again and again)
    def reset(self):
        self.nt = np.zeros(self.resolution)
        self.colors = [[configs.raster_background for x in range(self.resolution[1])] for y in range(self.resolution[0])]
        self.right_hold = True  # suspend all controls until right mouse button is released

        try:
            self.armor = event_manager.player.holding.armor
            self.armor_text = self.font.render(  # make text object
                # 'Armor: ' + self.armor.name,  # create the string
                f'{tools.translator("Armor")}: {tools.translator(self.armor.name)}',
                True,  # anti alias (???)
                configs.text_color,  # set the color
            )
            self.armor_rect = self.armor_text.get_rect(topleft=(configs.width + 10, 10))
        except:
            pass
        
    def update(self, dt):
        """
        Used to update and calculate values
        This state has a raster.right_hold bool to disable the update function until the right mouse is let go
           - Ensures that it is not automatically skipped if the right mouse is held during initiation of the state
           - State can be called using the right mouse button during certain instances
        :param dt: time in milliseconds sine last frame
        :return: None
        """
        super().update(dt)

        # manage control freeze
        if self.right_hold:
            if not mouse.buttons[3]:
                self.right_hold = False
            else:
                return  # break out of update until right mouse is let go

        # Draw on the canvas
        if mouse.buttons[1]:  # when left button is held
            if self.in_bounds(mouse.position):
                mouse_idx = self.relative_index(mouse.position)
                self.colors[mouse_idx[0]][mouse_idx[1]] = configs.raster_color
                self.nt[mouse_idx[1], mouse_idx[0]] = 1
                if debug:
                    print(mouse_idx)
                    print(self.nt)
        # check the canvas
        if mouse.buttons_down[3]:  # if right button is clicked
            event_manager.player.check_raster(self.nt)  # give the player the raster drawing


    def draw(self, screen):
        super().draw(screen)
        [
            [
                pygame.draw.rect(screen, self.colors[xi][yi], self.pixels[xi][yi])
                for xi in range(self.resolution[0])
            ]
            for yi in range(self.resolution[1])
        ]
        # write the armor type to the screen
        if self.armor_text:
            screen.blit(self.armor_text, self.armor_rect)

    # ---- Helper functions ----

    def in_bounds(self, pos):
        """
        Return if a position is within the boundaries of the raster window
        :param pos: tools.vector of the position of the mouse
        :return: a bool for if it's in the window
        """
        if self.bounds[0][0] < pos.x < self.bounds[1][0]:
            if debug: print('good in x')
            if self.bounds[0][1] < pos.y < self.bounds[1][1]:
                if debug: print("Good in y")
                return True  # return true if both work
        return False  # return false if either fail

    def relative_index(self, pos):
        """
        Get relative location with respect to the raster box
        :param pos: mouse position
        :return: coordinates in the box as (x, y)
        """
        # grab percentage of box
        x_decimal = (pos.x - self.bounds[0][0]) / self.window_size[0]
        y_decimal = (pos.y - self.bounds[0][1]) / self.window_size[1]

        # get raster pixel index
        x_index = math.floor(x_decimal * self.resolution[0])
        y_index = math.floor(y_decimal * self.resolution[1])

        # return the values
        return x_index, y_index

