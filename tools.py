"""
Tools that are useful in most places
"""
import pygame.math

import configs

import math
import random

import queue

# debug_variables
debug = False
debug_navmesh = True


class vector:
    def __init__(self, x, y=None):
        if y is None:
            if type(x) == vector:  # given another vector to copy
                self.x = x.x
                self.y = x.y
            else:  # hopefully given a tuple/list
                self.x = x[0]
                self.y = x[1]
        else:  # passed two arguments
            self.x = x
            self.y = y

    def __repr__(self):
        return ("x: %i,y: %i" % (self.x, self.y))

    def __eq__(self, other):  # overwrite use of == operator
        if isinstance(other, vector):
            return self.x == other.x and self.y == other.y
        else:
            return False

    def __ne__(self, other):  # overwrite use of != operator
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.x, self.y))

    def __sub__(self, v):
        return vector(self.x - v.x, self.y - v.y)

    def __add__(self, v):
        return vector(self.x + v.x, self.y + v.y)

    def __mul__(self, v):
        return vector(self.x * v, self.y * v)

    def __truediv__(self, v):
        return self * (1 / v)

    def unit(self):
        return self / vector.magnitude(self)

    # return vector as a tuple of (x, y)
    def as_tuple(self):
        return self.x, self.y

    # return custom vector object as a pygame vector object (easier for built in methods)
    def as_pygame(self):
        return pygame.math.Vector2(self.x, self.y)

    # ------ Static Methods -------
    # call with tools.vector.function
    @staticmethod
    def magnitude(v):
        return math.sqrt((v.x ** 2) + v.y ** 2)

    @staticmethod
    def distance(a, b):
        d = a - b
        return (math.sqrt((d.x ** 2) + (d.y ** 2)))

    @staticmethod
    def angle(a, b):
        au = a.unit()
        bu = b.unit()
        d = (au.x * bu.x) + (au.y * bu.y)
        return math.degrees(math.acos(d))


# create a vector from a tuple (helps with coding the mouse position)
def vector_from_tuple(t):
    return vector(t[0], t[1])


# start_node and end_node are the actual waypoint objects, not the names
def a_star(graph, start_node, end_node):
    """
    Used to find the best path through a graph
    :param graph: graph object (?), could be removed since it is not actually used
    :param start_node: staring node on the graph
    :param end_node: ending node of the graph
    :return: a list containing the path (empty if no path is found)
    """
    # init open and closed lists
    open = start_node
    open_list = set([start_node])
    closed_list = set([])

    # init dict of g values
    g = {start_node: 0}

    # start parents list (for reverse traversal)
    parents = {start_node: start_node}

    # while there are still things in the open list
    while len(open_list) > 0:
        # initial next path is an empty list
        n = None

        # go through the open paths to find approximate quickest
        for v in open_list:
            if not n or g[v] + astar_h(open, v) < g[n] + astar_h(open, n):  # calculate next g value
                n = v

        if n == None:  # no more paths to check
            print("Path does not exist")
            return []

        # TODO: Finsh reconstructing the path
        if n == end_node:
            # reconstruct the path
            fp = []
            while True:
                fp += [n]
                n = parents[n]
                if n == start_node:
                    break
            # fp.reverse()  # reverse in place
            return fp  # return list of nodes in order to traverse them

        # loop through next paths
        for m in n.paths:
            # try and add list to open paths (if not already viewed)
            if m not in open_list and m not in closed_list:
                open_list.add(m)  # add to open list
                parents[m] = n  # add parent node of n
                g[m] = g[n] + astar_h(open, n)  # add g score for current node
            # # check if this is a quicker way to get to the previous node
            # else:
            #     if g[m] > g[n]:
            #         g[m] = g[n]
            #         parents[m] = parents[n]
            #
            #         if m in closed_list:
            #             closed_list.remove(m)
            #             open_list.add(m)
        open_list.remove(n)
        closed_list.add(n)


# calculate h value for the A* algorithm
def astar_h_navmesh(a, b):
    return vector.distance(vector(a), vector(b))


# start_node and end_node are the actual waypoint objects, not the names
def a_star_navmesh(graph, start_node, end_node):
    """
    Used to find the best path through a graph
    :param graph: navmesh array filled with 1's and 0's
    :param start_node: staring position as a vector
    :param end_node: ending position as a vector
    :return: a list containing the path (empty if no path is found)
    """
    # init open and closed lists
    if True:
        open = start_node
        open_list = set([start_node])
        closed_list = set([])

        # init dict of g values
        g = {start_node: 0}

        # start parents list (for reverse traversal)
        parents = {start_node: start_node}

        # while there are still things in the open list
        while len(open_list) > 0:
            # initial next path is an empty list
            n = None

            # go through the open paths to find approximate quickest
            for v in open_list:
                if not n or g[v] + astar_h_navmesh(end_node, v) < g[n] + astar_h_navmesh(end_node, n):  # calculate next g value
                    n = v

            if n == None:  # no more paths to check
                print("Path does not exist")
                return []

            # TODO: Finsh reconstructing the path
            if n == end_node:
                # reconstruct the path
                print("Finished the path!")
                fp = []
                while True:
                    fp += [n]
                    n = parents[n]
                    if n == start_node:
                        break
                # fp.reverse()  # reverse in place
                return fp  # return list of nodes in order to traverse them

            # loop through next paths
            nv = vector(n)
            checklist = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(checklist)
            paths = [floor_vector(nv + vector(_)) for _ in checklist if inbounds(nv + vector(_))]
            paths = [_ for _ in paths if graph[_.x, _.y]]
            for m in paths:
                # try and add list to open paths (if not already viewed)
                if m.as_tuple() not in open_list and m.as_tuple() not in closed_list:
                    open_list.add(m.as_tuple())  # add to open list
                    parents[m.as_tuple()] = n  # add parent node of n
                    g[m.as_tuple()] = g[n] + astar_h_navmesh(open, n)  # add g score for current node
                # check if this is a quicker way to get to the previous node
                else:
                    if g[m.as_tuple()] > g[n]:
                        g[m.as_tuple()] = g[n]
                        parents[m.as_tuple()] = parents[n]

                        if m.as_tuple() in closed_list:
                            closed_list.remove(m.as_tuple())
                            open_list.add(m.as_tuple())
            open_list.remove(n)
            closed_list.add(n)

            # if debug_navmesh:
            #     print(len(open_list))
            #     print(len(closed_list))
            #     print("------")


# calculate h value for the A* algorithm
def astar_h(a, b):
    return vector.distance(a.position, b.position)


# calculate h value for the A* algorithm
def astar_h_navmesh(a, b):
    return vector.distance(vector(a), vector(b))


def inbounds(v):
    (mx, my) = (configs.width, configs.height)
    return 0 <= v.x < mx and 0 <= v.y < my


# ensure position tuples are ints
def floor_vector(v):
    return vector(math.floor(v.x), math.floor(v.y))

class random_color_generator:
    def __call__(self):
        out = [random.randint(1, 230) for i in range(3)]
        return out


def random_position(width_margins=0, height_margins=0):
    x = (random.random() * (configs.width - width_margins)) + width_margins
    y = (random.random() * (configs.height - height_margins)) + height_margins
    return vector(x, y)


# find nearest object in a given radius
def find_nearest_object(position, objects, radius, object_type=None):
    """
    :param position: position to search from
    :param objects: list of game objects
    :param radius: radius from player
    :param object_type: type of object to return
    :return: the nearest matching object to the player, None if no matching objects
    """
    if object_type:
        new_objects = [_ for _ in objects if type(_) == object_type]
    else:
        new_objects = objects
    if debug: print(new_objects)

    current_dist = radius
    out = None
    for obj in new_objects:
        dist = vector.distance(position, obj.position)
        if dist < current_dist:
            current_dist = dist
            out = obj
    if debug: print(out)
    return out


def error(s):
    n = 12
    ss = n * '='
    ns = ' ERROR '
    print(ss + ns + ss)
    print(s)
    print(ss + ((len(ns) * '=')) + ss)


# make a queue to recycle for different types of events that require a managed queue
class ActorQueue:

    def __init__(self, queue_positions):
        # manage args
        self.queue_positions = queue_positions

        # init the queue
        self.queue = []

    def enqueue(self, actor):
        """
        Enqueue items without duplicates
        :param actor: item to add
        :return: boolean for if actor was added
        """
        if actor in self.queue:
            return False
        else:
            self.queue += [actor]
            return True

    def dequeue(self):
        """
        Return first item in line and shift up the others
        Returns None if the queue is empty
        :return: item or None
        """
        if len(self.queue):
            return self.queue.pop(0)
        else:
            return None

    def remove(self, actor):
        """
        Used to remove an actor from the queue
        :param item: item to remove
        :return: boolean for if the item was removed
        """
        if actor in self.queue:
            i = self.queue.index(actor)
            self.queue.pop(i)
            return True
        else:
            return False

    def location(self, actor):
        """
        Called by the actor to get location in the queue
        :param actor: Actor looking for location
        :return: tools.vector or None
        """
        i = self.position(actor)
        if i is not None:
            if i >= len(self.queue_positions):  # check if out of queue positions
                return self.queue_positions[-1]  # return last queue position
            else:
                return self.queue_positions[i]  # return actor's queue position
        else:

            return None  # return none to signify actor is not in the queue

    def position(self, actor):
        """
        Return the position(index) of actor in the queue
        :param actor: actor to find
        :return: int
        """
        if actor in self.queue:
            return self.queue.index(actor)
        else:
            return None

    def is_registered(self, actor):
        """
        Return if an actor is in the queue
        :param actor: actor to check for
        :return: boolean
        """
        return actor in self.queue

def translator(s):
    """
    Translate commonly used strings to something the user will understand
    :param s: string to translate
    :return: string useful for a user
    """

    # create the dict
    out_d = {
        # General
        'BU': 'Bully University',
        # Attributes
        'Str': 'Strength',
        'Fin': 'Finesse',
        'End': 'Endurance',
        'Tou': 'Toughness',
        'Lvl': 'Level',
        # Armor
        'Arm': 'Panties',
        'Armor': 'Panties',
        'GRN': 'Granny',
        'THN': 'Thong',
        # Behaviour Tree
        'Tsk': 'Task',
        'Fel': 'Fuel',
        'Tnk': 'Tank',
        # Actions
        'Lck': 'Lock',
        'Sus': 'Supsension',
        'Ctl': 'Control',
        'Afm': 'Aftermath',
        # UI Controls
        'REG': 'Regular',
        'FRO': 'Frontal',
        'SQU': 'Squeaky Clean',
        'MSY': 'Messy',
        'SRL': 'Swirly',
        # UI Locks
        'SHO': 'Shoulder',
        'BRC': 'Bra Connection',
        'ATL': 'Atomic Lock',
        # UI Suspensions
        'ATO': 'Atomic',
        'JKL': 'Jock Lock',
        'HNG': 'Hanging',
        'FNG': 'Frontal Hanging',
        # AFMs
        'AFM': 'Aftermath',
        'WTR': 'Water',
    }

    # return the string
    if configs.translate_strings and s in list(out_d.keys()):
        return out_d[s]
    else:
        return s

def log(s):
    if not configs.debug_print_off:
        print(s)

# class NameGenerator:
#
#     def __init__(self):
#         # names already used
#         self.used = []
#
#         # default names
#         self.names = [
#             'Inesea',  # 0
#             'Whitney',
#             'Caitlyn',
#             'Caroline',
#             'Monica',
#             'Emma',  # 5
#             'Mary',
#             'Beth',
#             'Valerie',
#             'Amanda',
#             'Sabrina',  # 10
#             'Charli',
#             'London',
#             'Maddie',
#             'Katrina',
#             'Juliana', # 15
#             'Livvy',
#             'Kody',
#             'Sam',
#             'Maggie',
#             'Jax',  # 20
#         ]
#
#     def __call__(self, level):
#         n = self.names[level]
#         self.used += [n]
#         if self.used.count(n) > 1:
#             v = self.used.count(n)
#             n += '_%i' % v
#         return n
#
# name_generator = NameGenerator()


