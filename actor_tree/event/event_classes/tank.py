"""
Description Here
"""

# generic imports
import random

# specific imports
from py_trees.common import Status

# custom imports
import configs
from tools import vector
from actor_tree.event.event_classes.base_event import BaseEvent
from Mapping.map import event_regions

# get all event regions for this event
locations = [_ for _ in event_regions if _.key == 'tank']

debug = False
debug_tank = True


class Tank(BaseEvent):
    name = 'tank'

    def __init__(self, actor):
        super(Tank, self).__init__(actor)

        # calculate distances to each region
        ds = [vector.distance(self.actor.position, vector(_.rect.center)) for _ in locations]

        # pick the closest region
        self.location = random.choice(locations)  # TODO: actually pick the closes spot

        # move the actor to the room entrance
        self.actor.assign_destination(self.location.room.entrance)

    def update(self):
        """
        Called as the last part of the tree, usually when self.actor has control and is at the destination
        :return: py_trees.Status
        """

        # check if tank is empty
        if self.actor.tank <= 0:
            self.actor.tank = 0
            self.location.deregister_actor(self.actor)  # remove actor from the event region code/users
            self.actor.action_item = None  # remove ref to action item (if we were have one)
            return Status.SUCCESS
        else:
            self.interruptable = True

        # Unregistered Section
        if not self.location.is_registered(self.actor):
            # check if we need to register the actor
            if self.actor.waypoint == self.location.room.entrance:
                print("Registering from tank leaf")
                self.location.update(self.actor)
                return Status.RUNNING
            # ensure actor is moving towards the room
            else:
                self.actor.assign_destination(self.location.room.entrance)
                return Status.RUNNING  # event is still running (will be left hanging)
        # Registered section
        else:
            if debug_tank:
                # print("Attempt to get location of waiting actor")
                ...
            b = self.location.update(self.actor)  # update self.actor's location, return if they can start the event
            # b will return true when actor is at the correct place to begin the event
            if b:  # "if we can begin the event"
                self.actor.action_item.closed = True  # close the door
                self.interruptable = False
                self.actor.tank -= configs.actor_tank_drain_rate * (self.actor.dt / 1000)  # drain actor's tank
                return Status.RUNNING
            # Actor is waiting in the queue
            else:
                return Status.RUNNING

    def control_update(self):
        """
        Ensure freeing up resources, specifically when self.actor.control = False
        :return: py_trees.Status.SUCCESS
        """
        # check if character is registered
        if self.location.is_registered(self.actor):
            # check if they are not in the room
            if not (self.location.rect.collidepoint(self.actor.position.as_tuple()) or
                    self.location.room.entry_rect.collidepoint(self.actor.position.as_tuple())):
                # deregister them
                self.location.deregister_actor(self.actor)
        # check if they are a user
        # if self.location.is_user(self.actor):
        #     # check if they are not in the correct location
        #     ...
        #         # deregister them

        # always return success (don't block the control tree)
        return Status.SUCCESS

    @staticmethod
    def check_importance(actor):
        tr = actor.tank / actor.tank_size
        if tr > configs.tank_threshold:
            return (tr - configs.tank_threshold) * (1 / (1 - configs.tank_threshold))
        else:
            return 0
