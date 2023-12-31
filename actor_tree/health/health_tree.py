"""
Top node for figuring out the health tree
"""

import py_trees

import math
import numpy as np

import tools

from actor_tree.base_leaf import BaseLeaf
from py_trees.common import Status

debug_log = False
debug_removal = False
debug_water = False

def get_tree():
    root = py_trees.composites.Sequence(name='Health', memory=False)

    # calculate health (based on AFMs)
    health_calc = HealthCalc(name='health_calc')

    # update water status
    water = WaterUpdate(name='water_update')

    # update locks/suspensions
    lock_suspension = LocksSuspensions(name='locks_suspensions')

    # update actor health
    # health_calc = HealthUpdate(name='health_update')

    # add children to the root
    root.add_children([water, lock_suspension, health_calc])

    return root

# TODO: Fix, not removing AFMs
class AFMCheck(BaseLeaf):

    def __init__(self, name):
        super(AFMCheck, self).__init__(name)
        self.afm = None

    def update(self):

        # check if we are currently removing an AFM
        if self.afm:
            if not self.actor.has_afm(self.afm.name).value:  # if afm has value of 0
                if debug_log:
                    self.logger.debug("Successfully removed " + self.afm.name)
                self.afm = None  # remove our ref to the afm and continue
            else:
                return Status.RUNNING  # continue removing current afm

        # check for afm removal
        p_afm = [_ for _ in self.actor.afm if (_.value > 0 and not _.permanent)]
        if len(p_afm):
            if (1 - (self.actor.level / 20)) > self.actor.health / 100:
                tools.log("AAAAAAAAA")
                if not self.afm:
                    if self.actor.afm:
                        p_afm = [_ for _ in self.actor.afm if (_.value > 0 and not _.permanent)]
                        # loop through actor's afms
                        for a in p_afm:
                            if not a.permanent and a.value > 0:
                                if debug_log:
                                    self.logger.debug("Removing " + a.name + "...")
                                self.afm = a
                                self.actor.remove_afm(a.name)
                                return py_trees.common.Status.RUNNING

        # return success if no issues with AFMs
        return Status.SUCCESS


class HealthCalc(BaseLeaf):
    """
    Calculate health based on all AFM values
    """
    def update(self):
        # check for all AFMs that do damage
        afm = [_ for _ in self.actor.afm if (_.damage and _.health < 1)]

        # calculate and set the new health
        health = np.prod([_.health for _ in afm])
        self.actor.calc_health = health * 100

        # return a status
        return Status.SUCCESS  # always return success in the health loop

class LocksSuspensions(BaseLeaf):
    """
    Handle actor suspensions
    Return SUCCESS
    """

    def __init__(self, name):
        super(LocksSuspensions, self).__init__(name)

    def update(self):
        # manage suspensions
        self.actor.update_suspension()
        self.actor.update_lock()
        return Status.SUCCESS  # don't block the health tree


class WaterUpdate(BaseLeaf):
    """
    Update water periodically (managed by self.delay)
    """
    def __init__(self, name):
        super(WaterUpdate, self).__init__(name)
        self.delay = 1  # time (seconds) between update ticks
        self.timer = self.delay

    def update(self):
        if self.timer > 0:  # update timer
            self.timer -= self.actor.dt * (1/1000)
        else:  # update water values
            # reset the timer
            self.timer = self.delay

            # calculate fuel drain
            df = self.actor.fuel * (1-math.exp(-(self.delay * (1/60)) * self.actor.drain_rate))  # change in fuel

            # update values
            self.actor.fuel -= df
            self.actor.tank += df

        # # manage tank overflow
        # if self.actor.tank/self.actor.tank_size > 1:
        #     self.actor.get_afm('MSY')  # add a msy afm (if we don't already have one)
        #     self.actor.tank = 0
        #     if debug_water:
        #         print("%s emptied tank" % self.actor.name)

        return Status.SUCCESS  # don't block the health tree



