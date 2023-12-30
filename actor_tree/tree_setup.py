"""
Used to set up a new tree
"""
import time
import typing

import py_trees
import py_trees.console as console

# import custom trees
from actor_tree.health import health_tree as health_tree_module
from actor_tree.control import control_tree as control_tree_module
from actor_tree.event import event_tree as event_tree_module


def create_root() -> py_trees.behaviour.Behaviour:
    """
    Create the root behaviour and it's subtree.

    NOTE: Actor will need to call the setup function w/ the proper **kwargs {'actor': Actor}

    Returns:
        the root behaviour
    """
    # create the top of the node
    root = py_trees.composites.Sequence(name="Sequence", memory=False)

    health_tree = health_tree_module.get_tree()
    control_tree = control_tree_module.get_tree()
    event_tree = event_tree_module.get_tree()

    # finish the root tree
    root.add_children([health_tree, control_tree, event_tree])

    # return the root tree
    # return root
    return py_trees.trees.BehaviourTree(root)