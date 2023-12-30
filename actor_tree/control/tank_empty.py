"""
Used to remove control while emptying tank
Removes control by blocking the rest of the trees past the control tree on the root node (a sequence node)
"""

# package imports
from py_trees.common import Status

# custom module imports
from actor_tree.base_leaf import BaseLeaf
import configs

debug = True

class TankEmpty(BaseLeaf):
    """
    Blocking leaf that empties the tank
    """
    def __init__(self, name):
        super(TankEmpty, self).__init__(name)
        self.empty = False  # flag for when to activate the leaf

    def update(self):

        if self.actor.tank/self.actor.tank_size > 1:
            self.empty = True
            self.actor.get_afm('MSY')  # add msy afm
            if debug:
                print("%s is emptying tank" % self.actor.name)

        if self.empty:
            if self.actor.tank > 0:
                self.actor.tank -= configs.actor_tank_drain_rate * (self.actor.dt / 1000)
                return Status.RUNNING
            else:
                self.actor.tank = 0
                self.empty = False  # stop emptying tank
                return Status.SUCCESS

        return Status.SUCCESS  # return success if the running clause isn't caught


