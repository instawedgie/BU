"""
Used to create an area for location specific events
Created in the map script, each region has a list of keys that permit items
"""

import pygame
import tools

debug = True

class EventRegion:

    regions = []

    def __init__(self, key, rect=None, xlim=None, ylim=None, pos=None, waypoint=None, obj=None):
        # create region's boundary region
        if not rect:
            if xlim and ylim:
                self.rect = pygame.Rect((xlim[0], ylim[0]), (xlim[1] - xlim[0], ylim[1] - ylim[0]))
                self.pos = pos  # position used if event is in one location
            else:
                raise Exception("Must either pass a pygame.Rect or x and y limits for the region")
        else:
            self.rect = rect

        # key or keys used for unlocking certain events (can be multiple, ensure it's a list)
        self.key = key

        # keep ref to the waypoint (even if we aren't given one)
        self.waypoint = waypoint
        self.object = obj

        # keep track of all regions in the class
        EventRegion.regions += [self]


# --- End of class

class TankEventRegion:
    """
    Event region used to a queue for multiple action items
    """
    def __init__(self, key, room, items, queue_positions):
        # manage event attributes
        self.key = key

        # manage map attributes
        self.rect = room.rect
        self.room = room

        # manage object attributes
        self.items = items
        self.users = {
            obj: None for obj in self.items
        }

        # manage queue attributes
        self.queue_positions = queue_positions
        self.queue = tools.ActorQueue(queue_positions)

    def register_actor(self, actor):
        """
        Used to register an actor for the event
        :param actor: actor to register
        :return: None
        """
        # check for availability of items first
        for t in self.items:  # loop through objects
            if not t.user:  # if an object has no user
                if debug:
                    tools.log("%s is now a tank user" % actor.name)
                actor.waypoint = t.position
                t.user = actor
                actor.action_item = t
                return

        # if not using an object, add to the queue
        if debug:
            tools.log("%s is now queued for tank" % actor.name)
        self.queue.enqueue(actor)  # enqueue actor (no repeats)

    def deregister_actor(self, actor):
        """
        Used to de-register an actor
         - Should also update the queue
        :param actor: actor to de-register
        :return: None
        """
        if debug: tools.log("Deregistering actor " + actor.name)
        # check if they are a current user
        for t in self.items:
            if t.user == actor:
                t.user = self.queue.dequeue()  # pop an actor from the queue (or set to None if queue is empty)
                t.closed = False
                if t.user:
                    t.user.action_item = t  # give actor a reference to the item
                return

        # remove user from the queue (does nothing if actor is not in the queue)
        self.queue.remove(actor)

    def get_item(self, actor):
        for t in self.items:
            if t.user == actor:
                return t
        return None

    def is_user(self, actor):
        for t in self.items:
            if t.user == actor:
                return True

    def is_queued(self, actor):
        return self.queue.is_registered(actor)

    def is_registered(self, actor):
        # check if actor is a current user
        return self.is_user(actor) or self.is_queued(actor)

    def update(self, actor):
        """
        Called once per tick of the tree by a given actor
        :param actor: Actor calling the udpate function
        :return: boolean for if they can can begin the event
        """
        # check if actor is registered:
        if not self.is_registered(actor):
            self.register_actor(actor)
            return False

        # check if actor is a user
        t = self.get_item(actor)
        if t:
            actor.waypoint = t.position
            return True
        elif self.is_queued(actor):
            # update position in the queue
            actor.waypoint = self.queue.location(actor)
            return False
        else:
            if debug: tools.log("Updating unregistered actor")
            return False



