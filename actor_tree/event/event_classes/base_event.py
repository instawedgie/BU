"""
Create a base class to simplify code in the behaviour tree
Will be updated if:
 - Actor has been assigned the event
 - Tree has not been blocked by other activities (Locomotion, control tree, etc)
"""

from py_trees.common import Status


class BaseEvent:

    name = 'task'  # ensure each class has a name

    def __init__(self, actor):
        self.actor = actor
        self.interruptable = True  # enable/disable ability to assign a needs event

    def update(self):
        """
        Called during some ticks of the event tree
         - Generally only blocked by the locomotion leaf
        :return: py_trees.common.Status
        """
        return Status.SUCCESS

    def control_update(self):
        """
        Called during each tick of the control tree
         - Should be kept as light as possible
         - Mostly to manage what happens during loss of control or proximity based events
        :return: py_trees.common.Status
        """
        return Status.SUCCESS

    def interrupt(self):
        """
        Called by the control loop if the actor loses control for any reason
        :return: None
        """
        pass

    @staticmethod
    def check_importance(actor):
        """
        Return a float value between 0-1 of how important this task is to a given actor
        :param actor: actor obj
        :return: float
        """
        return 0





