"""
Used to manage NPC behavior from one coherent source
Helps minimize need for inter-character controls
"""

from base_object import BaseObject

class ActorManager(BaseObject):
    """
    Init once in main.py as a singleton that holds refs to all the actors
    """
    def __init__(self, actors):
        super(ActorManager, self).__init__()
        self.actors = actors





