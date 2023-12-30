"""
Used for the water event
"""

import pygame

import configs
from tools import vector
from Mapping.objects.map_object import MapObject

debug = True


class WF(MapObject):

    def __init__(self, rect, waypoint, queue_positions=None):
        self.rect = rect
        self.waypoint = waypoint  # position used for the action
        self.position = self.waypoint.position

        # item action attributes
        self.user = None  # current actor
        self.queue = []  # actors waiting to use
        self.register_radius = 20  # distance until actor should register in the queue
        if not queue_positions:
            self.queue_positions = [vector((self.waypoint.position.x - ((1+_)*15), self.waypoint.position.y))
                                    for _ in range(10)]  # starting with 5 positions (idk)
        else:
            self.queue_positions = queue_positions


    def draw(self, screen):
        super().draw(screen)

        pygame.draw.rect(screen, configs.water_color, self.rect)

    def register(self, actor):
        """
        Used to allow an actor to use object or add them to the queue
        :param actor: actor wanting to use the object
        :return: None
        """
        # check for first user
        if not self.user and actor is not self.user:  # allow them to use object
            if debug: print("Assigning WF User " + actor.name)
            self.user = actor
        # otherwise add them to the queue
        else:
            if debug: print("Adding WF Queue " + actor.name)
            self.enqueue(actor)

    def deregister(self, actor):
        """
        Used to remove an actor from trying to use the object
        :param actor: actor leaving the object
        :return: None
        """
        # if debug: print("WF deregistering " + actor.name)
        # remove actor if they are current user
        if self.user is actor:
            if debug: print("WF removed user: " + actor.name)
            self.dequeue()

        # remove actor if they are in the queue
        else:
            if actor in self.queue:
                if debug: print("WF removed from queue " + actor.name)
                self.queue.remove(actor)

    def is_registered(self, actor):
        return (actor in self.queue or actor is self.user)

    def enqueue(self, actor):
        """
        Add an actor to the queue
         - WILL ADD DUPLICATES, BE CAREFUL
        :param actor: actor to add
        :return: None
        """
        self.queue += [actor]

    def dequeue(self):
        """
        Move up actors in the queue, push first in line to current user (if they exist)
        Remove current user if no actors left in the queue
        :return: None
        """
        # if we have users in the queue
        if self.queue:
            self.user = self.queue.pop(0)
        # if nobody is waiting
        else:
            self.user = None

    # get the position (as a vector) the actor is supposed to be at
    def get_position(self, actor):
        # figure out assigned position
        if not (actor is self.user or actor in self.queue):
            self.register(actor)  # add them to the queue

        # figure out assigned position
        if actor is self.user:
            return self.waypoint.position
        else:
            if actor in self.queue:
                n = self.queue.index(actor)
                if n > len(self.queue_positions):
                    n = len(self.queue_positions) - 1

                return self.queue_positions[n]

    # custom action function
    def update(self, actor):
        """
        Allow actor to use the fountain, including waiting in the queue
        Should be called once every frame by both the user and every actor in the queue
        :param actor: Actor to add
        :return: boolean for if they are good to use the fountain
        """
        if self.user is actor:
            # ensure user's destination is the waterfountain's position
            # actor.destination = self.waypoint.position
            # actor.waypoint = self.waypoint
            return True
        else:
            if actor not in self.queue:
                self.enqueue(actor)
            else:
                # prune the queue (just in case)
                for a in self.queue:
                    if not self.user and len(self.queue):
                        self.dequeue()
                        print("Warning: Actor got stuck in the queue!")
                    if a.event:  # ensure actor has an event
                        if a.event.name != 'water':
                            print("Warning: WF deregistered actor w/ a different event")
                            self.deregister(a)  # remove actor w/ different event 
                    else:
                        print("Warning: WF deregistered actor w/o an event ")
                        self.deregister(a)  # remove actor w/o an event
            return False
        pass

    def display(self):
        print("Queue: " + str([_.name for _ in self.queue]))
        if self.user:
            print("User:  " + str(self.user.name))
        else:
            print("User:  " + str(None))






