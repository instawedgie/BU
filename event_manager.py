"""
Manage game events here (Mainly player inputs)
Needs to be updated to adapt to the different states of objects.interface
"""

import pygame
from pygame.locals import *

from tools import vector
from objects import recorders

import sys
import configs

debug = True  # used to control printing to the console
debug_mouse = False  # used to control printing out mouse buttons to console
debug_keys = False  # used to print out key displays for anger management
debug_force_quit = False  # allow force quit from key combo in event_manager's update loop

# control variables
movement_keys = {
    'up': K_w,
    'down': K_s,
    'right': K_d,
    'left': K_a,
    'sprint': K_LSHIFT,
    'lctl': K_LCTRL,
}


class KeyTracker:
    """
    Used to keep track of when keys are pressed, held, and released
    """

    def __init__(self):
        # list of tracked keys
        self.tracked_keys = []  # list of keys to track

        # dicts for storing key states
        self.keys_down = {}  # dict of if key is pushed down in format {key: bool}
        self.keys_pressed = {}  # dict of if key is held down in format {key: bool}
        self.keys_released = {}  # dict of if key is released in format {key: bool}

        # list containing the above dicts for easily adding new keys
        self.dict_list = [self.keys_down, self.keys_pressed, self.keys_released]

    def add_key(self, key):
        """
        Used to add a key for tracking (instead of tracking every key every frame)
        :param key: the key you want to track (ex: pygame.locals.K_UP, K_LSHIFT, etc...)
        :return: None
        """
        if key not in self.tracked_keys:
            self.tracked_keys += [key]
            for i in self.dict_list:
                i.update({key: False})

    def key_press(self, key):
        if debug_keys:
            print(key)
        self.keys_down[key] = True
        self.keys_pressed[key] = True

    def key_lift(self, key):
        self.keys_released[key] = True
        self.keys_pressed[key] = False

    def reset(self):
        """
        Used to reset the values of keys_down and keys_released between frames
        """
        for i in self.tracked_keys:
            self.keys_down[i] = False
            self.keys_released[i] = False


class MouseTracker:
    """
    Used to keep track of the mouse positions and buttons
    """

    def __init__(self):
        self.mouse_pos = vector(pygame.mouse.get_pos())

        self.position = vector(0, 0)
        self.num_buttons = 10  # making it slightly larger just in case

        self.buttons_down = self.list_maker()
        self.buttons_up = self.list_maker()
        self.buttons = self.list_maker()

    def button_press(self, button):
        if debug_mouse:
            print("Mouse button %i pressed" % button)
        self.buttons_down[button] = True
        self.buttons[button] = True

    def button_lift(self, button):
        if debug_mouse:
            print("Mouse button %i released" % button)
        self.buttons_up[button] = True
        self.buttons[button] = False

    def reset(self):
        self.buttons_down = self.list_maker()
        self.buttons_up = self.list_maker()

    def update_pos(self):
        self.position = vector(pygame.mouse.get_pos())

    def list_maker(self):
        return [False for _ in range(self.num_buttons)]


# create the objects for tracking
mouse = MouseTracker()
keys = KeyTracker()


class EventManager:

    def __init__(self):
        # init refs for player and other game objects
        self.player = None
        self.objects = None
        self.map_objects=[]

        # init control values
        self.pause = False  # used to pause the game

        # add recorders (for debugging)
        self.recorders = {
            'actor': recorders.ActorRecorder(mouse),
        }

        # ensure built-in keys are tracked
        if debug_force_quit:
            # add the necessary keys
            [keys.add_key(_) for _ in [K_LCTRL, K_LSHIFT, K_j]]

    def load_world(self, game_objects):
        """
        Called after initializing all other game objects. Greatly simplifies code.
        :param game_objects: A list of all fully initialized game objects
        :return: None
        """
        # grab controller
        self.player = game_objects[0]
        # keep a list of all game objects
        self.game_objects = game_objects
        # # grab a ref to the scheduler
        # self.schedule = next((x for x in game_objects if x.name == 'schedule'))
        # add our own recorders to the game objects
        self.game_objects += list(self.recorders.values())

        # manage recorders
        self.recorders['actor'].player = self.player  # set a ref to the player in the recorder

    def __call__(self, event):
        # default events
        if event.type == QUIT:  # player closes game window
            self.quit()
        if event.type == pygame.KEYDOWN and event.key == K_ESCAPE:  # player presses escape (pause)
            print("Pausing the game")
            self.pause = True  # set pause to True (should be picked up by the Game class)

        # update mouse tracker
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse.button_press(event.button)
        if event.type == pygame.MOUSEBUTTONUP:
            mouse.button_lift(event.button)

        # update key tracker
        if event.type == pygame.KEYDOWN and event.key in keys.tracked_keys:
            keys.key_press(event.key)
        if event.type == pygame.KEYUP and event.key in keys.tracked_keys:
            keys.key_lift(event.key)

        # built-in force quit with ctrl + shift + j (should be easy to avoid during testing)
        # TODO: Disable when not testing
        if keys.keys_pressed[K_LCTRL] and keys.keys_pressed[K_LSHIFT] and keys.keys_pressed[K_j]:
            self.quit()

    # called once per frame before looping through events
    def pre_loop(self):
        self.pause = False  # ensure that we don't carry over the pause boolean
        mouse.reset()
        keys.reset()
        mouse.update_pos()

    @staticmethod  # static method can be called from anywhere
    def quit():
        pygame.quit()
        sys.exit()

event_manager = EventManager()