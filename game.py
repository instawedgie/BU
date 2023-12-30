"""
Base class to run the game
Uses a game object system where each has two main functions: update and draw
There is a single event manager that deals with player input
Have a debug display function for displaying whatever needs fixing
"""

# pygame imports
import pygame
from pygame.locals import *

# generic imports
import os
import sys
import subprocess


# local imports
import configs
import event_manager

# grab the singletons from other modules
from objects.uni_graph import waypoints
from event_manager import event_manager, mouse, keys

# debug variables
debug = False
MOUSE_VIEW = False
GRAPH_VIEW = False

FPS_VIEW = False  # print fps values to the console
track_min = False  # either track min (True) or track drops below fps_floor
fps_floor = 58  # min value to show frame rate drops
min_fps = 10000  # set initial value for tracking min fps

class Game:
    def __init__(self, screen, game_objects):

        # init variables
        self.done = False  # exit the game
        self.screen = screen  # game window
        self.clock = pygame.time.Clock()  # pygame clock (manage fps + get dt between frames)
        self.fps = 60  # desired fps
        self.game_objects = game_objects  # list of game objects

        # deal with pause menu
        self.pause = False  # enables start menu, freezes game objects
        self.pause_menu = PauseMenu(self)  # init pause menu object (w/ a reference to this obj)

        # give event_manager access to game_objects
        self.game_objects = game_objects
        self.event_manager = event_manager  # keep a ref to event_manager (don't want to rewrite rn)
        event_manager.load_world(game_objects)
        self.map_objects = event_manager.map_objects

    # manage and track events (generally player inputs)
    def event_loop(self):
        self.event_manager.pre_loop()  # reset events + trackers
        for event in pygame.event.get():  # loop through events during this frame
            self.event_manager(event)  # deal with the event
        # check if game should be paused
        if self.event_manager.pause:  # check if event manager is paused
            self.pause = True  # pause our game

    # game loop (run once per frame)
    def run(self):
        while not self.done:  # while game is not over
            dt = self.clock.tick(self.fps)  # manage fps (given in ms)
            if FPS_VIEW:
                fps = (1/(dt / 1000))
                if track_min:
                    global min_fps
                    jfc = min_fps > fps
                    if jfc:
                        min_fps = fps
                        print("min fps: %.2f" % fps)
                else:
                    if fps < fps_floor:
                        print("fps drop: %.2f" % fps)

            self.event_loop()  # manage events

            if not self.pause:  # if the game is not paused
                for i in self.game_objects:  # loop through all game objects
                    i.update(dt)  # update the game object
                for i in self.game_objects:
                    i.late_update()
            else:  # game is paused
                self.pause_menu.update(dt)

            # fill in background
            self.screen.fill(configs.background_color)
            self.screen.blit(configs.background, (0, 0))

            # display the map objects
            for i in self.map_objects:
                i.draw(self.screen)

            # display the game objects (even when paused, they show up in the background)
            for i in self.game_objects:  # render each object
                i.draw(self.screen)

            # deal with drawing the pause menu
            if self.pause:  # if game is paused
                self.pause_menu.draw(self.screen)  # draw the pause menu

            # display the debug output
            debug_display(self.screen)  # custom function that shows things for the devs while debugging
            # update display
            pygame.display.update()  # pygame built-in, shows what was drawn to the screen this frame

    # used to resume the game
    def resume(self):
        self.pause = False

    # used to quit the game
    def quit(self):
        print("Quitting the game")
        self.event_manager.quit()

    # SHOULD reset the game for the player (iffy at best)
    def reset(self):
        """
        Nasty way of restarting the game.
        Close the game window, call the file again, wait for it to finish, sys.exit()
        :return: None
        """
        print(sys.argv)
        pygame.quit()  # close the current game window
        subprocess.run(['python.exe'] + sys.argv)# call another version of the game
        sys.exit()  # exit when the nested game is complete



def debug_display(screen):
    if MOUSE_VIEW:
        mouse_pos = pygame.mouse.get_pos()
        mx = configs.main_font.render("MX: %i"%mouse_pos[0], True, configs.text_color)
        mxr = mx.get_rect(center=(30, configs.height-40))
        my = configs.main_font.render("MY: %i"%mouse_pos[1], True, configs.text_color)
        myr = my.get_rect(center=(10, configs.height-20))

        # blit text
        screen.blit(my, (10, configs.height - 40))
        screen.blit(mx, (10, configs.height - 80))
    if GRAPH_VIEW:
        for wp in waypoints:
            t = wp.name
            txt = configs.graph_font.render(str(t), True, configs.text_color)
            txtb = txt.get_rect(center=(wp.position.x, wp.position.y))
            screen.blit(txt, txtb)


# class used to draw the pause menu
class PauseMenu:
    """
    Class def used to handle the UI during pauses
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
        self.buttons = {
            'cont': MenuButton(
                'Continue',  # text to display
                (configs.width / 2, configs.height / 2),  # location of the button
                self.game.resume  # resume the game
            ),
            'exit': MenuButton(
                'Exit', # text to display
                (configs.width / 2, configs.height / 2 + 30),  # location of the button
                self.game.quit  # quit the game
            ),
            'reset': MenuButton(
                'Restart',  # button text
                (configs.width / 2, configs.height / 2 + 15),  # button location
                self.game.reset  # reset the game
            )
        }

        # ensure we are tracking left control key for quick quit
        keys.add_key(K_LCTRL)

    # called once per frame
    def update(self, *args):  # added *args in case we need dt eventually (shouldn't)
        # manage quick quit in the menu by pressing the w key
        if keys.keys_pressed[K_w]:
            event_manager.quit()

        # manage button presses
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
    def __init__(self, text, location, function):
        """
        Create the button's text and rect
        :param text: text to display on the button
        :param location: location of the button's rect center
        :param function: action to complete upon clicking
        """
        self.font = configs.graph_font
        self.font_size = configs.graph_font_size

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
        screen.blit(self.text, self.text_rect)