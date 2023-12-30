"""
Set up a tree for controlling Actor behaviour
Goal is to remove all logic from the Actor's Update and just tick the tree
 - Possibly leave in the control for locks + suspensions
"""


import time
import typing

import py_trees
import py_trees.console as console

# import custom scripts
from UI.afm import Afm, afms, get_afm
from actor_tree.dummy_actor import Actor

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
    root.add_children([control_tree, health_tree, event_tree])

    # return the root tree
    # return root
    return py_trees.trees.BehaviourTree(root)


##############################################################################
# Main
##############################################################################


if __name__ == '__main__':
    py_trees.logging.level = py_trees.logging.Level.WARN

    # create a new actor
    actor = Actor()

    # add an afm to the actor
    a = get_afm('REG')
    actor.add_afm(a)
    actor.afm[0].value = .5
    print("VIEW ACTOR AFM")
    print(actor.afm)

    ####################
    # Execute
    ####################
    for i in range(1, 4):
        try:
            print("\n--------- Tick {0} ---------\n".format(i))
            actor.bt.tick()
            print("\n")
            print(py_trees.display.unicode_tree(root=actor.bt.root, show_status=True))
            time.sleep(1.0)
        except KeyboardInterrupt:
            break
    print("\n")