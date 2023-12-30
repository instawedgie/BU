"""
Class used to manage individual rooms
"""

import pygame

import configs

from tools import vector, ActorQueue
from Mapping.waypoint import Edge, Waypoint

# debug variables
debug = False


class Room:
    """
    Used to manage leaving rooms if brought in by a player
    Can also be used to manage player->wall collisions
    """

    def __init__(self, xlim, ylim, entrance, entry_width=configs.entry_size, entry_height=configs.entry_size,
                 depth=2):
        """
        Used to create a room for both boundaries and managing game flow
        :param xlim: x limits of the room
        :param ylim: y limits of the room
        :param entrance: center of room's entrance
        :param entry_width: width (x) of entryway
        :param entry_height: height (y) of entryway
        :param depth: used to stack rooms inside one another (whole building = 1, most rooms = 2)
        """
        # turn given boundaries into a pygame rect (for easier collisions / drawing)
        self.rect = pygame.Rect((xlim[0], ylim[0]), (xlim[1]-xlim[0], ylim[1]-ylim[0]))

        self.waypoints = {}  # set waypoints to an empty list (add later)
        self.depth = depth  # order of importance (1 being least important)

        # manage the entrance waypoint
        self.entrance_loc = entrance  # waypoint for the entryway
        self.entrance = None  # waypoint for the entrance
        self.edge = None  # maintain edge (so we can lock out NPCs) (assign during graph creation)
        self.locked = False  # boolean for locking the door (currently unused)

        # manage they entryway rect (for player)
        entry_size = (entry_width, entry_height)
        self.entry_rect = pygame.Rect((0, 0), entry_size)  # init rectangle at 0, 0 for ease of use
        # self.entry_rect.center = entrance.position.as_tuple()  # set center of rectangle to center of the waypoint
        self.entry_rect.center = entrance

        # init empty name variable (assign after creation)
        self.name = None

    def init_entrance(self):
        self.entrance = Waypoint(
            position=self.entrance_loc,  # location of entrance
            name=self.name + '_entrance',
        )
        self.add_waypoint(self.entrance, 'entrance')

    def add_waypoint(self, waypoint, name=None):
        if type(waypoint) == list:  # if given a list of waypoints
            return self._add_waypoints(waypoint)
        if not name:
            n = len([_ for _ in self.waypoints.keys() if 'wp_' not in _])
            name = self.name + ('_%02i'%n)
        self.waypoints.update({name: waypoint})

    def _add_waypoints(self, waypoints):
        for wp in waypoints:
            self.add_waypoint(wp)


    def add_edge(self, waypoint):
        """
        Used to add and maintain reference to an edge so that we can lock the door for NPCs
        :param waypoint: waypoint object
        :return: None
        """
        self.edge = Edge(self.entrance, waypoint, bi=True)

    # check if a point is inside of the room
    def collidepoint(self, pos):
        if type(pos) == vector:
            pos = pos.as_tuple()
        return self.rect.collidepoint(pos)


# ========== Subclasses =========


class RoomR(Room):

    def assign_objects(self, tanks, tank_queue_positions = None):
        # manage params
        self.tanks = tanks
        if not tank_queue_positions:
            self.queue_positions = [

            ]
        else:
            self.tank_queue_positions = tank_queue_positions

        # init attributes
        self.tank_queue = Queue()


    def register_tank(self, actor):
        # check for free action item
        for t in self.tanks:
            if not t.user:
                t.user = actor
        # otherwise add them to the queue
        else:
            if debug: print("Adding RR Queue " + actor.name)
            self.tank_queue.enqueue(actor)

    def update_tank(self):
        """
        Called by actors in the queue each frame
        Should give them a location to stay while waiting
        :return: None
        """
        # update the queue
        for t in self.tanks:
            if not t.user:
                t.user = self.tank_queue.dequeue()



