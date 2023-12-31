"""
Used to create new afm objects for storing residual affects
"""
import copy
from dataclasses import dataclass
import numpy as np

import configs
import tools

debug = False


@dataclass
class Afm:
    # properties
    intensity: float = 1.0  # damage multiplier
    speed_decrease: float = .9  # speed decrease while present
    removal_time: int = 500  # time to wait while removing
    name: str = 'afm'  # name
    trackers: int = 15  # number of frames to track
    decay: float = 0  # rate (%/s) of decay of afm value
    health: float = 1  # health of AFM
    base_imp: float = .2  # base importance to behaviour tree

    # flags
    damage: bool = True  # if afm applies damage
    armor: bool = True  # whether damage applies to armor
    permanent: bool = False  # if removable by actor
    track: bool = True  # if we should track power applied over time
    dt: bool = True  # if there is a dt component to affects

    # owner ref
    actor: str = None

    def __post_init__(self):
        self.frames = [0 for _ in range(self.trackers)]
        self.value = 1

    def reset(self):
        self.frames = [0 for _ in range(self.trackers)]
        self.value = 0

    def apply(self, actor):
        self.actor = actor

    def update(self, value, dt):
        """
        Extra basic update, should be overwritten for most cases
        :param value: input power
        :param dt: frame time
        :return: None
        """
        # manage value
        if not self.value:  # not given a value (decay)
            self.value -= dt * self.decay
        elif self.value < value:  # given a value (check max)
            self.value = min(1, value)


class ArmorAfm(Afm):

    def __post_init__(self):
        super().__post_init__()
        self.value = 0
        self.mixers = ['REG', 'FRO']

    def update(self, value, dt):

        dt *= (1 / 1000)  # convert from ms -> s

        # update current value
        if self.value < value:  # check if new val is higher than current
            self.value = min(1, value)  # use new val (without going over 1)

        # --- calculate affects
        # only work if we have armor
        if not self.actor.armor.broken:
            # update the armor
            if value > 0:
                self.actor.armor.damage(value, dt)

                # calc steady state value
                int_damage = value * dt * self.actor.armor.strength * self.intensity  # integral damage

                # track dt affects
                dt_damage = 0  # ensure we have a dt value to add at the end
                if self.track and self.dt:
                    # print(a.frames)
                    amn = np.argmin(self.frames)
                    amx = np.argmax(self.frames)
                    mn = np.amin(self.frames)
                    mx = np.amax(self.frames)
                    self.frames = self.frames[1:] + [value]  # cycle frames
                    if value > mx:  # positive slope
                        dt_damage = (  # calc dt damage to add to the int damage
                                (value - mn) * value * (10 * dt) * self.actor.armor.strength * self.intensity
                        )

                # manage afm interactions
                dm_mult = 1  # start with multiplier of 1
                if self.name in self.mixers:  # loop through mixers
                    for n in [_ for _ in self.mixers if _ != self.name]:  # loop through afms that aren't this one
                        a = self.actor.has_afm(n)  # check/get the afm
                        if a:  # if we have it
                            dm_mult += (a.value * .5) # add value to the multiplier

                # calc final values
                damage = (int_damage + dt_damage) * dm_mult
                self.actor.damage(damage)
                self.health -= damage * ((self.health / 100)) * (1 - (.2 * (self.actor.toughness - 3)))

                # manage breaking armor (only executes on frame that armor is broken)
                if self.actor.armor.broken:
                    self.actor.basic_damage(self.actor.armor.break_damage)
                    self.health -= damage * ((self.health / 100)) * (1 - (.2 * (self.actor.toughness - 3)))


@dataclass
class SpkAfm(Afm):
    def __post__init__(self):
        super(SpkAfm, self).__init__()
        self.values = [0, 0]
        self.value = 0

    def reset(self):
        self.values = [0, 0]
        self.value = 0

    def update(self, value, dt):
        self.value = sum(self.values) / 2


# end of class

afm_list = [
    ArmorAfm(
        name='REG',
        speed_decrease=.95,
        base_imp=.3,
    ),
    ArmorAfm(
        name='FRO',
        speed_decrease=.9,
        intensity=2,
        base_imp=.5, 
    ),
    Afm(
        name='MSY',
        speed_decrease=.98,
        permanent=True,
        track=False,
        armor=False,
    ),
    Afm(
        name='WTR',
        speed_decrease=1,
        permanent=True,
        track=False,
        armor=False,
        damage=False,
    ),
    # SpkAfm(
    #     name='SPK',
    #     speed_decrease=1,
    #     permanent=True,
    #     track=False,
    #     armor=False,
    #     damage=False,
    # )
]

afms = {_.name: _ for _ in afm_list}  # create a dict of afms by name

def get_afm(name):
    """
    Return a new copy of the afm to use for tracking affects
    :param name: name of afm in the Dict "afms"
    :return: clone of afm obj
    """
    if debug: tools.log("Making a new afm")
    if type(name) == Afm:  # given an afm object
        return copy.deepcopy(name)
    else:  # given an afm name
        return copy.deepcopy(afms[name])


