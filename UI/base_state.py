"""
Base state for the FSM in objects/interface.py
Update and draw are called once per frame (in that order)
Reset is called everytime that the state is changed (useful for resetting the state w/o much overhead)
"""

from dataclasses import dataclass

debug = False

class BaseState:
    # define object from start
    def __init__(self):
        if debug: print("Init state: " + str(type(self)))
        pass

    # called each frame for computations
    def update(self, dt):
        pass

    # called each frame for rendering
    def draw(self, screen):
        pass

    # called after changing to this state (used to reset values if needed)
    def reset(self, **kwargs):
        pass

