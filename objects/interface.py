"""
Game Object for the user interface on the left side of the screen
Controls combat directly though the states
    - bad implementation, should ideally separate the combat and GUI FSMs
"""
import pygame
from pygame.locals import *

# import custom modules
from tools import *
from objects.base_object import BaseObject
import configs
import UI
from objects.actors import Actor

# debug variables
debug = False


class Interface(BaseObject):
    """
    Use Interface.change_state to change the state, instead of setting interface.state directly
    """
    def __init__(self):
        super(Interface, self).__init__()

        # set the name
        self.name = 'interface'

        # set background displays
        self.background_rect = pygame.Rect((configs.width, 0), (configs.menu_width, configs.height))

        # set up the states
        self.states = {
            'idle': UI.idle.Idle(),
            'grab': UI.grab.Grab(),
            'raster': UI.raster.Raster(),
            'task': UI.task.Task(),
            'control': UI.control.Control(),
            'squ': UI.squ.Squ(),
            'srl': UI.srl.Srl(),
            'msy': UI.msy.Msy(),
            'spk': UI.spk.Spk(),
        }
        self.state_names = list(self.states.keys())
        self.state = 'idle'  # set initial state

    def update(self, dt):
        # default object update
        super().update(dt)

        # update the state
        self.states[self.state].update(dt)

    def draw(self, screen):
        super().draw(screen)

        # draw background
        pygame.draw.rect(screen, configs.menu_color, self.background_rect)

        # draw state
        self.states[self.state].draw(screen)

    # --- Helper functions ---

    # Change the state of the FSM (used to avoid rewriting code for complications with changing the state)
    def set_state(self, state):
        if debug: print("Changing state to: " + state)
        self.state = state  # change the state
        self.get_state().reset()  # reset the new state
        return self.get_state()  # return the new state to simplify external code


    # getter function to help with access to states (not really needed)
    def get_state(self):
        return self.states[self.state]  # get the current state


# define an interface to use as a singleton (can be accessed anywhere through
interface = Interface()

