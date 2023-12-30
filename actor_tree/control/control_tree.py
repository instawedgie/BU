"""
Used to check actor control before running
"""

import py_trees
from py_trees.common import Status
from actor_tree.base_leaf import BaseLeaf
from actor_tree.control.tank_empty import TankEmpty

debug_log = True

def get_tree():
    """
    Used to ensure an actor is free before ticking the rest of the tree
    :return: a tree composite containing control logic
    """

    # create the root node
    root = py_trees.composites.Parallel(name="Control", policy=py_trees.common.ParallelPolicy.SuccessOnAll())

    # create leaves
    # sus = LocksSuspensions(name="pre-damage")  # check on suspension
    ctrl = CheckControl(name="control")  # check on overall control
    timer = TickTimer(name="timer")
    tank = TankEmpty(name='tank_empty')
    event = EventControlUpdate(name='event_control')

    # add the children
    root.add_children([ctrl, timer, tank, event])

    return root

class CheckControl(BaseLeaf):
    """
    Check if the actor has overall control
    Return Success if actor has control
    """
    def __init__(self, name):
        super(CheckControl, self).__init__(name)

    def update(self):
        # check if we have control
        if self.actor.control:
            return Status.SUCCESS
        else:
            return Status.FAILURE


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
        return Status.SUCCESS

class TickTimer(BaseLeaf):

    def __init__(self, name):
        super(TickTimer, self).__init__(name)

    def update(self):
        if self.actor.wait_time > 0:
            self.actor.wait_time -= self.actor.dt
            return Status.RUNNING  # block the tree until timer is over (take away all control)
        elif self.actor.wait_time < 0:
            self.actor.wait_time = 0

        return Status.SUCCESS


class EventControlUpdate(BaseLeaf):
    """
    Used to update parts of the event before the actual event update
     - Mostly useful to manage what happens if actor does not have control
     - Also can be used to register/deregister for queues based on proximity to the object
        - Since event update is not called during locomotion
    """
    def update(self):
        if self.actor.event:
            return self.actor.event.control_update()
        else:
            return Status.SUCCESS  # return success if we don't have an event

