"""
Base class used to create a menu
"""

import pygame

import configs
from event_manager import mouse

# debug variables
debug = False
draw_shadow = False

class BaseMenu:
    """
    Class for creating UI menus (generally a sequence of buttons)
    """
    # initialize the object
    def __init__(self, game_manager):

        # keep ref to the game
        self.game = game_manager

        # create a background surface
        self.background = pygame.Surface(configs.resolution)
        self.background.set_alpha(128)
        self.bg_rect = pygame.Rect((0, 0), configs.resolution)  # rectangle covering entire game window
        self.bg_color = pygame.Color(configs.menu_color)  # color for background rectangle
        pygame.draw.rect(self.background, self.bg_color, self.bg_rect)

        # init menu buttons
        self.buttons = {}  # dict to hold all buttons for the menu

    def add_button(self, name, button):
        self.buttons.update({
            name: button
        })

    # called once per frame
    def update(self, *args):  # added *args in case we need dt eventually (shouldn't)
        if mouse.buttons_down[1]:  # if mouse is left clicked
            for button in self.buttons.values():  # loop through all the buttons
                if button.text_rect.collidepoint(mouse.position.x, mouse.position.y):  # if mouse is colliding with rectangle
                    button()  # call the button's function
        pass

    # used to render the UI to the screen
    def draw(self, screen):
        # draw the background
        screen.blit(self.background, (0, 0))  # draw the background color for the menu

        # draw the buttons
        for button in self.buttons.values():  # loop through the buttons dict
            button.draw(screen)  # draw the button


class MenuButton:
    """
    Basic class used to easily create some clickable text
    """
    def __init__(self, text, location, function, font=None):
        """
        Create the button's text and rect
        :param text: text to display on the button
        :param location: location of the button's rect center
        :param function: action to complete upon clicking
        """

        if not font:
            self.font = configs.graph_font
        else:
            self.font = font

        self.idle_color = (0, 0, 255)  # blue on idle
        self.hover_color = (255, 255, 0)  # yellow for selection

        self.writing = text  # keep track of text for debugging
        self.text = self.font.render(text, True, self.idle_color)
        self.text_rect = self.text.get_rect(center=location)

        self.func = function  # use the given function when called (may need to handle button as an arg)

    def __call__(self, *args):
        if debug: print(self.writing)
        return self.func(*args)  # call and given function and return the output



    def draw(self, screen):
        """
        Used to draw the button to the screen each frame
        :param screen: Screen to draw the button on
        :return: None
        """
        if draw_shadow:
            pygame.draw.rect(screen, (210, 210, 210), self.text_rect)
        screen.blit(self.text, self.text_rect)

class Check:
    """
    Used to toggle True/False values in a menu
    """
    def __init__(self, location, function, initial_value=None):
        """
        Toggle a boolean value w/ the button
        :param location: position of toggle button
        :param function: function for setting toggle value
        :param value: initial value (otherwise checked during update)
        """
        # initial values
        self.value = initial_value
        self.location = location
        self.function = function

        # button background configs
        self.background = pygame.Rect((0, 0), (configs.tick_width, configs.tick_height))
        self.background.center = location

        # define things to get rid of the yellow lines
        self.text = None
        self.text_rect = None



    def draw(self, screen):
        # draw the background box
        pygame.draw.rect(screen, configs.background_color, self.background)
        # get current value
        if self.value:
            self.t = 'O'
            self.color = configs.true_color
        else:
            self.t = 'X'
            self.color = configs.false_color

        # draw the text
        self.text = configs.graph_font.render(self.t, True, self.color)
        self.text_rect = self.text.get_rect(center=self.location)





