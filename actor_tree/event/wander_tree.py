"""
Tree used to control random waypoint wander
"""

import py_trees
from py_trees.common import Status

import random

import configs
from tools import vector
from Mapping.map import locations

from actor_tree.base_leaf import BaseLeaf

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
