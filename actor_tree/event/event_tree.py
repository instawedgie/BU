"""
Handle Actor events (mostly locomotion + interaction)
"""

import py_trees
from py_trees.common import Status

import random
import time

import configs
from tools import vector
from Mapping.map import locations, idle_locations
import Mapping

from actor_tree.base_leaf import BaseLeaf

# import event classes
from actor_tree.event.event_classes.idle import Idle
from actor_tree.event.event_classes.wander import Wander
from actor_tree.event.event_classes.water import Water
from actor_tree.event.event_classes.tank import Tank

# debug variables
debug_completion = True
debug_assignment = True  # print message when assigning events to actors
debug_locomotion = False


def get_tree():
    root = py_trees.composites.Sequence(name='EventSelector', memory=False)

    # check if busy
    check_loc = Locomotion(name='Locomotion')

    # event completion composite
    event_loop = py_trees.composites.Sequence(name='EventLoop', memory=False)

    # event completion leaves
    needs_assign = AssignNeed('needs')  # assign needs before completing current event
    event_update = CompleteEvent('updater')  # complete an assigned event
    event_assign = AssignEvent('assigner')  # get a new, non-need based event

    event_loop.add_children([needs_assign, event_update, event_assign])

    # add children
    root.add_children([check_loc, event_loop])

    return root


# check if actor has arrived at destination
# if not, move to the location
# TODO: GRACEFULLY HANDLE ERRORS. This leaf will break easily if challenged with bad or empty paths
class Locomotion(BaseLeaf):
    def __init__(self, name):
        super(Locomotion, self).__init__(name)
        self.debug_cooldown = 10  # how often (s) we can say we are at the destination
        self.debug_timer = 0  # start the timer

    def update(self):

        # manage waypoint locomotion for types of Mapping.waypoint.Waypoint
        if self.actor.waypoint and type(self.actor.waypoint) is Mapping.waypoint.Waypoint:
            # manage reaching destination
            if (self.actor.destination and
                    vector.distance(self.actor.position, self.actor.destination.position) < self.actor.waypoint_radius):
                self.actor.waypoint = self.actor.destination
                if debug_locomotion:
                    # manage not spamming the console while we idle at our destination
                    if self.debug_timer <= 0:
                        print("%s has reached destination %s" % (self.actor.name, self.actor.destination.name))
                    self.debug_timer += self.actor.dt / 1000
                    if self.debug_timer >= self.debug_cooldown:
                        self.debug_timer = 0

                # return success when actor has reached their destination
                return Status.SUCCESS

            # manage reaching next waypoint
            elif vector.distance(self.actor.position, self.actor.waypoint.position) < self.actor.waypoint_radius:
                self.actor.waypoint = self.actor.path.pop()  # pop next waypoint from the path
                if debug_locomotion:
                    # ensure the debug message cool down is reset once we start moving
                    self.debug_timer = 0
                return Status.RUNNING  # still haven't arrived at destination

            # keep going towards current waypoint
            else:
                self.actor.go_to_waypoint()
                return Status.RUNNING

        # locomotion for when type(self.actor.waypoint) is a vector
        elif self.actor.waypoint and type(self.actor.waypoint) is vector:
            # manage arriving at waypoint
            if vector.distance(self.actor.position, self.actor.waypoint) < configs.waypoint_radius:
                return Status.SUCCESS
            # continue moving to waypoint
            else:
                self.actor.go_to_vector()
                return Status.RUNNING

        # return failure if nothing else caught the issue
        print("Locomotion failure, waypoint type = " + str(type(self.actor.waypoint)))
        return Status.FAILURE




class AssignNeed(BaseLeaf):
    """
    Used to check if actor needs to complete an event
    Will interrupt current assigned event if deemed important enough
    Called every single tick of the tree if actor has control
    """

    def __init__(self, name):
        super(AssignNeed, self).__init__(name)

        self.delay = 5  # period between checks (in seconds)
        self.start = time.time()

        self.events = {
            'water': Water,
            'tank': Tank,
        }

    def update(self):
        # init an empty event
        (eve, val) = (None, 0)  # no event, 0 importance

        # check each event (order is unimportant)
        if self.actor.event and self.actor.event.interruptable:
            for key, value in self.events.items():
                current_val = value.check_importance(self.actor)
                if val < current_val:
                    eve = value
                    val = current_val

            # check if we need to assign a new event
            if eve and self.actor.event:  # check if we found an important event and that the actor has an event
                if eve.name != self.actor.event.name:  # don't assign the same event we are already completing
                    if self.actor.event.check_importance(self.actor) < val:
                        print("%s needs %s" % (self.actor.name, eve.name))
                        self.actor.assign_event(eve)

        return Status.SUCCESS  # always return success (don't block the tree here)


class AssignEvent(BaseLeaf):

    def __init__(self, name):
        super(AssignEvent, self).__init__(name)

        self.events = {
            'idle': Idle,
            'wander': Wander,
        }

    def update(self):
        k, e = random.choice(list(self.events.items()))  # pick a random key from the events dict
        if debug_assignment:
            print("%s assigned %s" % (self.actor.name, k))
        self.actor.assign_event(e)  # let the actor create a new event to use
        return Status.SUCCESS


class CompleteEvent(BaseLeaf):

    def update(self):
        if self.actor.event:
            try:  # wrapped in try clause in case we don't have an event assigned anymore (shouldn't happen)
                return self.actor.event.update()
            except Exception as e:
                if debug_completion:
                    print("WARNING: TRIED TO UPDATE EVENT, FAILED")
                    print(e)
                return Status.FAILURE  # could not update, probably due to actor.event == None
        else:
            return Status.SUCCESS  # succeed if there is no event to complete (should get assigned later in the tick)


# ========== UNUSED FUNCTIONS ========== # TODO: Delete


# check if the actor already has an event
class CheckEvent(BaseLeaf):
    def __init__(self, name):
        super(CheckEvent, self).__init__(name)

    def update(self):
        if self.actor.event:
            return Status.SUCCESS
        else:
            return Status.FAILURE


class old_AssignEvent(BaseLeaf):
    """
    Used to assign events when the actor doesn't have one
    """

    def __init__(self, name):
        super(old_AssignEvent, self).__init__(name)

        self.events = {
            'idle': self.assign_idle,
            'wander': self.assign_wander,
        }

    def update(self):
        # pick a random event and assign it to the actor
        k = random.choice(list(self.events.keys()))  # pick a random key from the events dict
        self.events[k]()  # complete the assignment function (odd syntax, function call from a dict)

        # return success on completion
        return Status.SUCCESS

    def assign_idle(self):
        if debug_assignment: print("Assigning idle to " + self.actor.name)
        self.actor.event = 'idle'
        t = configs.actor_min_idle_time + (
                    random.random() * (configs.actor_max_idle_time - configs.actor_min_idle_time))
        self.actor.event_dict.update({'time': t})  # add wait time to the event blackboard
        self.actor.assign_destination(random.choice(idle_locations).waypoint)

    def assign_wander(self):
        if debug_assignment: print("Assigning wander to " + self.actor.name)
        self.actor.event = 'wander'
        n = random.randint(configs.actor_min_wander_time, configs.actor_max_wander_time)  # number of waypoints to visit
        self.actor.event_dict.update({'locations': n})  # add location visits to the event blackboard
        self.actor.assign_destination(random.choice(locations))


# give actor a new destination
class RandomDestination(BaseLeaf):
    def __init__(self, name):
        super(RandomDestination, self).__init__(name)

    def update(self):
        # pick a new location
        self.actor.destination = random.choice(locations)
        # update the path
        self.actor.reset_path()
        return Status.SUCCESS


class old_CompleteEvent(BaseLeaf):
    def __init__(self, name):
        super(old_CompleteEvent, self).__init__(name)

    def update(self):
        """
        Run one frame of progress towards completing the assigned event
        Should only be called whenever the actor has reached their destination
        :return: a py_tree status correlating to the state of the event
        """
        if not self.actor.event:
            """
            We want to return success if the actor does not have an event assigned
             - Does not block the tree
             - Event is technically finished since there isn't one
             - Event is not running
             - Event is not failed since there is nothing to fail
            """
            return Status.SUCCESS

        elif self.actor.event == 'idle':
            # decrement the idle timer by dt
            self.actor.event_dict['time'] -= self.actor.dt * (1 / 1000)  # actor tracks dt for us

            if self.actor.event_dict['time'] < 0:
                self.actor.reset_event()  # reset the event if timer is complete
                return Status.SUCCESS

        elif self.actor.event == 'wander':
            # remove one location from the blackboard
            self.actor.event_dict['locations'] -= 1

            if self.actor.event_dict['locations'] <= 0:
                self.actor.reset_event()  # reset the event
                return Status.SUCCESS
            else:
                # assign a new location
                self.actor.assign_destination(random.choice(locations))

        # return running if nothing has broken us out of the loop yet
        return Status.RUNNING
