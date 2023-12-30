"""
Used for misc actions through the raster interface
"""

import numpy as np
from dataclasses import dataclass, field

import configs

# imports for specific spells
from event_manager import event_manager

@dataclass
class Spell:
    name: str = 'spell'
    raster: np.ndarray = field(default_factory=lambda: np.zeros(configs.raster_resolution))  # raster drawing for UI
    function: type(lambda: 6) = lambda: 6
    state: str = 'idle'


def lock():
    """
    Turn on/off suspension attribute in an actor
    :return: None
    """
    event_manager.player.holding.stuck = not event_manager.player.holding.stuck

def undo():
    """
    Undo all locks/suspensions on the actor we are holding
    :return: None
    """
    event_manager.player.holding.remove_lock()
    event_manager.player.holding.suspension = None
    event_manager.player.release_actor(unstuck=True)

spells_list = [
    Spell(
        name='Lock',
        raster=np.array(
            [
                [1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1],
            ]
        ),
        function=lock
    ),
    Spell(
        name='Undo',
        raster=np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ]
        ),
        function=undo,
    )
]

spells = {_.name: _ for _ in spells_list}  # create a dict of afms by name