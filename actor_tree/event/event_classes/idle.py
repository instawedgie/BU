# generic imports
import random

# specific imports
from py_trees.common import Status

# custom imports
import configs
from actor_tree.event.event_classes.base_event import BaseEvent
from Mapping.map import idle_locations


class Idle(BaseEvent):

    def __init__(self, actor):
        super(Idle, self).__init__(actor)
        self.name = 'idle'

        self.t = (  # time to idle at this location
                configs.actor_min_idle_time + (random.random() *
                                               (configs.actor_max_idle_time - configs.actor_min_idle_time))
        )

        # pick location and assign it to the actor
        self.destination = random.choice(idle_locations).waypoint
        self.actor.assign_destination(self.destination)

    def update(self):
        """
        SHOULD be called once the actor has arrived at their desired location
        :return: a py_tree status
        """

        if self.actor.waypoint != self.destination:
            self.actor.assign_destination(self.destination)
            return Status.FAILURE  # something interrupted process, could not complete idle
        else:
            self.t -= self.actor.dt * (1/1000)

            if self.t < 0:
                self.actor.reset_event()
                return Status.SUCCESS  # successfully completed the event

        # still running (waiting in place) if not caught by those two statements)
        return Status.RUNNING


