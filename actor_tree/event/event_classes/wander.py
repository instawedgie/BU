# generic imports
import configs
import random

# specific imports
from py_trees.common import Status

# custom imports
from actor_tree.event.event_classes.base_event import BaseEvent
from Mapping.map import locations  # imports locations of interest (currently: doorways)

debug = False

class Wander(BaseEvent):
    """
    Used to wander between N random points
    New obj is created every time event is assigned
    """
    def __init__(self, actor):
        super(Wander, self).__init__(actor)
        self.name = 'wander'

        # init variables
        self.visits = random.randint(configs.actor_min_wander_time, configs.actor_max_wander_time)  # num places to go



    def update(self):
        # remove one location from the blackboard
        self.visits -= 1

        if self.visits <= 0:  # if we are done with the event
            self.actor.reset_event()  # reset the event
            return Status.SUCCESS
        else:
            # assign a new location
            self.actor.assign_destination(random.choice(locations))
            return Status.RUNNING  # block the tree (will be left hanging while locomotion runs)











