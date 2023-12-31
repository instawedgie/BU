# generic imports
import random

# specific imports
from py_trees.common import Status

# custom imports
import configs
from tools import vector
import tools
from actor_tree.event.event_classes.base_event import BaseEvent
from Mapping.map import event_regions

# get all event regions for this event
locations = [_ for _ in event_regions if _.key == 'water']

debug = False
debug_unregister = False

class Water(BaseEvent):
    name = 'water'

    def __init__(self, actor):
        super(Water, self).__init__(actor)

        # calculate distances to each region
        ds = [vector.distance(self.actor.position, vector(_.rect.center)) for _ in locations]

        # pick the closest region
        self.location = random.choice(locations).object  # TODO: actually pick the closes spot

        # assign actor the location
        self.actor.assign_destination(self.location.waypoint)

        # keep a registered boolean for simplicity
        self.registered = False



    def update(self):

        # check if fuel is full
        if self.actor.fuel >= 1:
            self.location.deregister(self.actor)  # de-register with the object
            self.actor.reset_event()  # remove the event from the actor
            return Status.SUCCESS  # continue through the tree
        else:
            self.interruptable = True

        # behaviour for unregistered actor
        if not self.location.is_registered(self.actor):
            # check if we are close enough to register
            if vector.distance(self.actor.position, self.location.waypoint.position) < self.location.register_radius:
                # register the actor
                self.location.register(self.actor)
                self.registered = True
            else:
                self.location.deregister(self.actor)  # ensure that we aren't still registered to the object
                # ensure we have the proper waypoint
                if not self.actor.destination == self.location.waypoint:
                    self.actor.assign_destination(self.location.waypoint)
                    return Status.RUNNING
            return Status.RUNNING

        # behaviour for registered actor
        else:
            # assign the correct position
            p = self.location.get_position(self.actor)
            # see if we need to assign the new waypoint and break out of leaf
            if self.actor.waypoint != p:
                self.actor.waypoint = p
                return Status.RUNNING
            # manage checking if we can use the fountain
            else:
                b = self.location.update(self.actor)  # check if we are current user
                if b:  # if we are the current user
                    # fill up actor's fuel
                    self.interruptable = False
                    self.actor.fuel += configs.water_fill_rate * (self.actor.dt / 1000)
                    return Status.RUNNING

        # one of the above conditions should be caught every time this leaf is ticked
        # leaving this as a failure to ensure we catch it for debugging
        return Status.FAILURE

    def control_update(self):
        if self.registered and not self.actor.control:
            d_obj = vector.distance(self.actor.position, self.location.waypoint.position)
            if not type(self.actor.waypoint) == vector:
                d_pos = vector.distance(self.actor.position, self.actor.waypoint.position)
            else:
                d_pos = vector.distance(self.actor.position, self.actor.waypoint)
            if (d_obj > self.location.register_radius and
                d_pos > self.location.register_radius):
                if debug_unregister:
                    tools.log("Control Update deregistered " + self.actor.name)
                self.location.deregister(self.actor)
                self.registered = False
        else:
            ...
            # if d < self.location.register_radius:
            #     self.location.register(self.actor)
            #     self.registered = True

        # always return success (don't block the control tree)
        return Status.SUCCESS


    @staticmethod
    def check_importance(actor):
        if actor.fuel < .5:
            return (.5 - actor.fuel) * 2
        else:
            return 0