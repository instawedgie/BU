"""
Used to simplify boiler plate
"""

import py_trees


class BaseLeaf(py_trees.behaviour.Behaviour):

    def __init__(self, name):
        super(BaseLeaf, self).__init__(name)
        self.actor = None

    def setup(self, **kwargs):
        self.actor = kwargs['actor']

    def update(self):
        return py_trees.common.Status.SUCCESS

