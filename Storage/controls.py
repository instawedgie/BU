"""
Use to store the valid controls for raster.py

Set in here to insulate from change in the FSM
"""

import numpy as np
from dataclasses import dataclass

# debug booleans (for printing to the console)
debug = True


@dataclass
class Bat:
    """
    Base att class
    """
    afm: str = 'REG'
    name: str = 'att'
    # raster: np.array = np.zeros((5, 5))

    def __post_init__(self):
        # ensure that afms are left as a list (even if there is just one)
        if not type(self.afm) == list:
            self.afm = [self.afm]
        elif not self.afm:
            self.afm = []  # set to an empty list


@dataclass
class Control(Bat):
    diff: int = 1  # ???


@dataclass
class Lock(Bat):
    speed_decrease: float = .8  # speed decrease while locked
    afm: str = 'REG'  # residual effect
    removal_time: int = 1000  # time to remove


@dataclass
class Suspension(Bat):
    time: int = 3000  # suspension duration (0 means permanent)


@dataclass
class Afm:
    speed_decrease: float = .9  # speed decrease while present
    removal_time: int = 500  # time to wait while removing
    name: str = 'afm'
    permanent: bool = False  # if it can be removed


# Dict of structure {'Att_Name': Raster_Array}
raster_np = {
    'NAN': np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
    ),
    'ATO': np.array(
        [
            [0, 1, 1, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
        ]
    ),
    'REG': np.array(
        [
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
        ]
    ),
    'RAM': np.array(
        [
            [0, 0, 2, 0, 0],
            [0, 0, 2, 0, 0],
            [0, 0, 2, 0, 0],
            [0, 0, 2, 0, 0],
            [0, 0, 2, 0, 0],
        ]
    ),
    'FRO': np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
    ),
    'FAM': np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [2, 2, 2, 2, 2],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
    ),
    'BRC': np.array(
        [
            [1, 1, 1, 1, 1],
            [0, 1, 0, 1, 0],
            [1, 1, 1, 1, 1],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
        ]
    ),
    'SHO': np.array(
        [
            [1, 1, 0, 1, 1],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0],
        ]
    ),
    'SQU': np.array(
        [
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [1, 1, 1, 1, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
        ]
    ),
    'JKL': np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1],
            [0, 0, 1, 0, 0],
        ]
    ),
}

# raster states to use for each att
raster_states = {
    'NAN': 'idle',
    'ATO': 'task',
    'REG': 'control',
    'FRO': 'control',
    'BRC': 'task',
    'SHO': 'task',
    'SQU': 'control',
    'JKL': 'task',
}

# dict of control atts
controls = {
    'REG': Control(
        afm='REG'
    ),
    'FRO': Control(
        afm='FRO'
    ),
    'SQU': Control(
        afm=['REG', 'FRO']
    )
}
# dict of lock atts
locks = {
    'SHO': Lock(
        speed_decrease=.7
    ),
    'BRC': Lock(
        speed_decrease=.8
    )
}
# dict of suspension atts
suspensions = {
    'ATO': Suspension(
        time=5000
    ),
    'JKL': Suspension(
        time=0
    )
}
# dict of residuals
ams = {
    'REG': Afm(
        speed_decrease=.95
    ),
    'FRO': Afm(
        speed_decrease=.9
    ),
    'MSY': Afm(
        speed_decrease=1,
        permanent=True
    )
}

# assign name to each attack
for d in [controls, suspensions, locks]:
    for key, value in d.items():
        value.name = key

# assign name to each ams
for key, value in ams.items():
    value.name = key

print("HHHHHHH")
if debug:
    print("Debugging")
    for key, value in ams.items():
        print(key + ': ' + str(value.permanet))


def check_input(nt):
    """
    Used to check input from the raster state in the interface
    :param nt: Numpy array
    :return: Attack and State, or None if there is no match
    """
    for k, v in zip(raster_np.keys(), raster_np.values()):
        acc = np.sum(nt == v) / nt.size
        if acc == 1:
            return k, raster_states[k]
    return None
