"""
Store all interface data
"""

import numpy as np  # numpy module used to manage raster drawing arrays
from dataclasses import dataclass, field  # dataclass used to manage attack classes, field is part of dataclass
import copy  # used for the armor factory function


# define classes
import configs
from UI.bat import Bat
from UI.lock import Lock
from UI.armor import Armor, armors, get_armor
from UI.spells import Spell, spells
from UI.afm import Afm, afms, get_afm

# debugging variables
debug = False


@dataclass
class Control(Bat):
    diff: int = 1  # ???
    state: str = 'control'


# @dataclass
# class Lock(Bat):
#     state: str = 'task'
#     speed_decrease: float = .8  # speed decrease while locked
#     removal_time: int = 1000  # time to remove


@dataclass
class Suspension(Bat):
    state: str = 'task'
    time: int = 3000  # suspension duration (0 means permanent)

# Define the attacks in a list
control_list = [
    Control(
        name='REG',
        afm='REG',
        raster=np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ]
        ),
    ),
    Control(
        name='FRO',
        afm='FRO',
        raster=np.array(
            [
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
            ]
        ),
    ),
    Control(
        name='SQU',
        afm=['REG', 'FRO'],
        raster=np.array(
            [
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [1, 1, 1, 1, 1],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
            ]
        ),
        state='squ',
    ),
    Control(
        name='MSY',
        afm=['REG', 'MSY'],
        raster=np.array(
            [
                [1, 0, 0, 0, 1],
                [1, 1, 0, 1, 1],
                [1, 0, 1, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1],
            ]
        ),
        check_loc=True,
        state='msy',
        use_armor=False,
    ),
    Control(
        name='SRL',
        afm=['WTR'],
        raster=np.array(
            [
                [0, 1, 1, 1, 1],
                [0, 1, 0, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 1, 0],
                [1, 1, 1, 1, 0],
            ]
        ),
        check_loc=True,
        state='srl',
        use_armor=False,
    ),
    # TODO: Remove, never really worked, needs a much better system
    # Control(
    #     name='SPK',
    #     afm=[],
    #     raster=np.array(
    #         [
    #             [1, 1, 1, 1, 1],
    #             [1, 0, 0, 0, 0],
    #             [1, 1, 1, 1, 1],
    #             [0, 0, 0, 0, 1],
    #             [1, 1, 1, 1, 1],
    #         ]
    #     ),
    #     check_loc=False,
    #     use_armor=False,
    #     state='spk',
    # )
]
controls = {_.name: _ for _ in control_list}  # create dict of controls by name

lock_list = [
    Lock(
        name='SHO',
        afm=['REG', 'FRO'],
        raster=np.array(
            [
                [1, 1, 0, 1, 1],
                [0, 1, 0, 1, 0],
                [0, 1, 0, 1, 0],
                [0, 1, 0, 1, 0],
                [0, 1, 1, 1, 0],
            ]
        ),
        speed_decrease=.7,
        intensity=.3,
        dropoff_val=90,
        dropoff_rate=.03,
        armor_types=['THN'],
    ),
    Lock(
        name='BRC',
        afm='REG',
        raster=np.array(
            [
                [1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0],
                [1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0],
                [0, 1, 0, 1, 0],
            ]
        ),
        speed_decrease=.8,
        intensity=.3,
        dropoff_val=100,
        dropoff_rate=.05,
    ),
    Lock(
        name='ATL',
        raster=np.array(
            [
                [0, 1, 1, 1, 0],
                [0, 1, 0, 1, 0],
                [0, 1, 1, 1, 0],
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
            ]
        ),
        speed_decrease=.4,
        intensity=.2,
        dropoff_val=70,
        dropoff_rate=.05,
        armor_types=['GRN'],
        visible=True, 
    )
]

locks = {_.name: _ for _ in lock_list}  # create dict of locks by name

suspension_list = [
    Suspension(
        name='ATO',
        afm='REG',
        raster=np.array(
            [
                [0, 1, 1, 1, 0],
                [0, 1, 0, 1, 0],
                [0, 1, 1, 1, 0],
                [0, 1, 1, 1, 0],
                [0, 1, 1, 1, 0],
            ]
        ),
        time=5000,
        intensity=.7,
        armor_types=['GRN']
    ),
    Suspension(
        name='JKL',
        afm='REG',
        raster=np.array(
            [
                [0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [0, 0, 1, 0, 0],
            ]
        ),
        time=0,  # time=0 means indefinite suspension
        intensity=.5,
    ),
    Suspension(
        name='HNG',
        afm='REG',
        raster=np.array(
            [
                [1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1]
            ]
        ),
        time=0,  # indefinite suspension
        check_loc=True,  # only allow at certain waypoints
        intensity=1,
    ),
    Suspension(
        name='FNG',
        afm='FRO',
        raster=np.array(
            [
                [1, 0, 1, 0, 1],
                [1, 0, 1, 0, 1],
                [1, 1, 1, 1, 1],
                [1, 0, 1, 0, 1],
                [1, 0, 1, 0, 1]
            ]
        ),
        time=0,  # indefinite suspension
        check_loc=True,  # only allow at certain waypoints
        intensity=1,
    ),
]

suspensions = {_.name: _ for _ in suspension_list}  # create dict of suspensions by name

# create a dict of all rasters to look through:
attacks = {}
for d in [controls, locks, suspensions]:  # loop through all attacks
    attacks.update(d)  # add all attacks to the dictionary (still in format {name: attack_obj}

# ensure all attacks have afm objects instead of strings of the afm name
for a in attacks.values():  # loop through attacks
    a.afm = [afms[_] for _ in a.afm]  # list comprehension to change out the string to an afm obj
    if a.armor_types and type(a.armor_types) is not list:  # ensure that armor_type fields are a list
        a.armor_types = [a.armor_types]

attacks.update(spells)  # add spells to list of attacks

# create a dict of structure {name: raster}
raster_np = {key: value.raster for key, value in attacks.items()}  # dict comprehension ftw

#  --- Debug section ---
if debug:
    for k, v in attacks.items():
        print(k + ': ' + str([_.name for _ in v.afm]))

# --- Helper functions

# check a given input to the raster UI state and return the att obj (if there is a match)
def check_input(nt):
    # TODO: return attack obj instead of name and state strings
    """
    Used to check input from the raster state in the interface
    :param nt: Numpy array
    :return: Attack name and State name, or None if there is no match
    """
    for k, v in attacks.items():  # loop through attacks dict
        acc = np.sum(nt == v.raster) / nt.size  # get accuracy of input vs stored array
        if acc == 1:  # if we got it right
            if debug: print(k)
            return v  # return the att obj
    return None  # return None if a matching att is not found