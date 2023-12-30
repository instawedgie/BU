"""
Base att class for extending to other types
"""

from dataclasses import dataclass, field
import numpy as np

# custom scripts
import configs


@dataclass
class Bat:
    """
    Base att class
    """
    # most important attributes
    name: str = 'att'  # name (-_-)
    afm: str = 'REG'  # residual effect (should be a list, will turn single strings into a list of len 1 w/ __post__init
    state: str = 'idle'  # next state to enter in UI when called
    raster: np.ndarray = field(default_factory=lambda: np.zeros(configs.raster_resolution))  # raster drawing for UI
    intensity: float = 1.0  # intensity of attack
    # ^ look up "How to declare numpy array of particular type as type in dataclass" on stack overflow for more info

    # enable/disable variables
    lvl = 0  # eventually used to determine unlock level
    use_armor: bool = True  # requires armor
    check_loc: bool = False  # control if this is only allowed in certain locations (unsure of handling currently)
    armor_types: list = None  # requires specific armor type/types


    def __post_init__(self):
        # ensure that afms are left as a list (even if there is just one)
        if not type(self.afm) == list:
            self.afm = [self.afm]
        elif not self.afm:
            self.afm = []  # set to an empty list

        # ensure that att has a raster drawing