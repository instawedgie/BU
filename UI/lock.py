"""
Hmmmm
"""

from dataclasses import dataclass
import numpy as np

from UI.bat import Bat

# debug variables
debug = False


@dataclass
class Lock(Bat):
    state: str = 'task'
    speed_decrease: float = .8  # speed decrease while locked
    removal_time: int = 1000  # time to remove
    dropoff_val: int = 75  # place to reduce x^8 exponential decay
    dropoff_rate: float = .05  # ratio after dropoff
    visible: bool = False

    def update(self, actor, dt):
        """
        Used to manage per frame interaction with the actor
        :param actor: actor holding the lock
        :param dt: time between frames
        :return: None
        """

        # current lame method
        if actor.health > self.dropoff_val:
            # point slope formula for linear damage dropoff w/ respect to health
            mult = 1
        else:
            mult = ((actor.health / self.dropoff_val) ** 8)
        actor.afm_damage(self.intensity * mult, dt, self.afm)

class BRC(Lock):
    def __init__(self):
        # set up basic Lock values
        super(BRC, self).__init__(
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
            reduce_val=75,
        )

        # unique characteristics
        self.reduce_val = 75  # value to start reducing rates

    def update(self, actor, dt):
        if actor.health > 75:
            actor.damage(self.intensity, dt, self.afm)
        else:
            value = self.intensity * (((actor.health / 100)+self.reduce_val)**8)
            actor.damage(value, dt, self.afm)


# --- end of class

