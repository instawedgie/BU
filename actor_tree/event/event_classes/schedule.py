import configs
import random

from actor_tree.event.event_classes.base_event import BaseEvent

class Schedule(BaseEvent):
    """
    Used to follow actor's schedule
    """
    def __init__(self, actor):
        super(Schedule, self).__init__(actor)
        self.name = 'schedule'









