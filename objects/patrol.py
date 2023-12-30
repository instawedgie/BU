"""
Wrapper for an Actor object to change behavior (?)
"""

import random
import pygame
from pygame.locals import *
import numpy as np

from objects.base_object import BaseObject
import configs

# get the graph and the destinations
from Mapping.map import hallway_nodes, locations, unlock_locations, game_map
from tools import *
from objects.interface import interface
from event_manager import event_manager, keys, mouse
from Mapping.map import game_map as room_map
import Mapping.map as map

# rename hallway nodes for compatability
waypoints = hallway_nodes

# debug behaviors
show_vision = False  # show area of vision for patrol
show_forward = True

# debug_vars
debug = False
debug_pathfinding = False

class Patrol(BaseObject):
    def __init__(self, position=None):
        super(Patrol, self).__init__()

        # movement and positioning
        self.speed = configs.actor_speed
        self.waypoint_radius = configs.waypoint_radius  # distance to consider actor has arrived at waypoint
        self.radius = configs.actor_size
        self.waypoint_names = list(range(len(waypoints)))
        self.waypoint = waypoints[random.choice(self.waypoint_names)]
        self.destination = self.waypoint
        self.path = [self.destination]
        self.forward = vector(1, 0).unit()
        self.color = (255, 100, 100)
        self.chase_color= (255, 0, 0)

        # other variables
        self.vision_radius = configs.patrol_vision_radius
        self.vision_angle = configs.patrol_vision_angle
        # get starting position
        if not position:  # if we aren't given a starting position
            self.position = self.waypoint.position
        else:
            self.position = position

        # manage the guide
        self.guide = vector(self.position)  # create a new vector for our guide's position
        self.guide_speed = self.speed * configs.patrol_guide_speed_mult
        self.guide_min_distance = configs.patrol_move_distance
        self.guide_max_distance = configs.patrol_wait_distance

        # behavior variables
        self.reset_path = False  # choose new waypoint + calculate path
        self.stationary = False  # disable movement
        self.idle_time = 0
        self.chase = None  # actor/controller to chase
        self.holding = None  # held actor/controller
        self.chase_update_time = 0
        self.chase_update_period = 200  # how often to grab chase position (in ms)

    def update(self, dt):
        super().update(dt)

        # update forward vector
        try:  # using a try statement to avoid issues when self.position == self.guide
            self.forward = (self.guide - self.position).unit()
        except:
            pass

        # manage waiting
        if self.idle_time > 0:
            self.idle_time -= (dt / 1000)
        else:
            self.idle_time = 0

        # reset the path
        if self.reset_path:
            if debug_pathfinding:
                print("Patrol reset path")
            if type(self.waypoint) is not type(waypoints[0]):
                if debug_pathfinding: print("Getting nearest waypoint")
                self.waypoint = game_map.get_nearest_waypoint(self.position)
            if self.destination == self.waypoint or type(self.destination) == vector:
                if debug_pathfinding: print("Getting random destination")
                self.destination = random.choice(waypoints)
            self.path = a_star(waypoints, self.waypoint, self.destination)
            self.reset_path = False


        # map traversal
        if not self.chase:  # simple patrol
            if not self.idle_time:
                # ensure destination type is a vector
                if type(self.waypoint) == vector:
                    wp = self.waypoint
                else:
                    wp = self.waypoint.position

                # manage basic traversal to waypoint
                if self.waypoint and vector.distance(wp, self.guide) > self.waypoint_radius:
                    self.go_to_waypoint(dt)
                # manage arriving at destination/current waypoint
                else:
                    if self.waypoint == self.destination:  # arrival at waypoint
                        self.reset_path = True

                        # Manage a held actor
                        if self.holding:
                            self.holding.unfreeze()
                            self.holding = None
                    else:
                        try:
                            self.waypoint = self.path.pop()
                        except Exception as e:
                            print("-----  ERROR WITH PATROL PATH -----")
                            print("Current waypoint    : " + self.waypoint.name)
                            print("Current destination : " + self.destination.name)
                            print("Resetting path in an attempt to avoid a crash")
                            self.reset_path = True
        else:  # chase controller
            if room_map.can_see(self.position, self.chase.position):
                self.waypoint = self.chase.position
                self.idle_time = 0

            # manage catching actor
            if vector.distance(self.position, event_manager.player.position) < configs.controller_grab_radius:
                # freeze and manage the actor
                self.chase.freeze()
                try:  # statements for catching a controller
                    self.chase.release_actor()  # try and release actor (doesn't work for actors, only controller)
                except:
                    pass

                # manage where to take actor
                self.destination = map.rooms['Office'].entrance
                self.reset_path = True

                # start holding the actor
                self.holding = self.chase
                self.chase = None

            # move to current waypoint
            if self.waypoint and vector.distance(self.waypoint, self.guide) > self.waypoint_radius:
                self.go_to_waypoint(dt)
            # get next waypoint
            else:
                if self.idle_time > 0:  # currently paused at location
                    pass
                elif self.idle_time < 0:  # frame at end of wait time
                    self.chase = None
                    self.reset_path = True
                    if debug:
                        print("Giving up search...")
                else:  # pause at last known location
                    if debug:
                        print("Patrol out of waypoints")
                    r = room_map.get_doorframe(self.position)
                    if r:
                        if debug: print("Moving to doorway")
                        dv = (r.entrance_loc - self.position).unit() * self.waypoint_radius
                        self.waypoint = r.entrance + dv
                    # if we are still at the correct waypoint
                    if self.waypoint and vector.distance(self.waypoint, self.guide) < self.waypoint_radius:
                        if debug: print("Pausing at last location...")
                        self.pause(5)

        # event detection
        if not self.chase and not interface.state == 'idle':
            # if debug: print("Patrol is Looking...")
            # check if player is in range
            if vector.distance(self.position, event_manager.player.position) < self.vision_radius:
                # check if player is in same room
                if room_map.get_room(self.position) == room_map.get_room(event_manager.player.position):
                    # check if we can actually see player
                    can_see = (room_map.can_see(self.position, event_manager.player.position) and
                                vector.angle(self.forward, event_manager.player.position - self.position) < self.vision_angle)
                    if can_see:
                        if debug: print("Detected an event!")
                        self.chase = event_manager.player
                        self.chase_frames = 0
                        self.waypoint = self.chase.position
                        self.destination = self.waypoint
                        self.path = []


    def draw(self, screen):
        super().draw(screen)

        if show_vision:
            pygame.draw.circle(screen, (255, 230, 230, .1), self.position.as_tuple(), self.vision_radius)

        # manage color
        if self.chase:
            color = self.chase_color
        else:
            color = self.color

        # draw the circles
        pygame.draw.circle(screen, (0, 0, 0), self.position.as_tuple(), self.radius + 1)
        pygame.draw.circle(screen, color, self.position.as_tuple(), self.radius - 1)

        if show_forward:
            pygame.draw.circle(screen, (0, 0, 0), (self.position + (self.forward * (self.radius + 1))).as_tuple(), 1)

    # simple waypoint function, no look ahead or turning involved
    def go_to_waypoint(self, dt):
        # move the guide
        if type(self.waypoint) == vector:
            gp = self.waypoint
        else:
            gp = self.waypoint.position

        # move the guide
        if vector.distance(self.guide, self.position) < self.guide_max_distance:
            speed = self.guide_speed
            d = gp - self.guide
            dv = d.unit() * speed * (dt / 1000)
            self.guide += dv

        # manage held actor
        if self.holding:
            self.holding.position = self.guide

        # move to the patrol
        if vector.distance(self.guide, self.position) > self.guide_min_distance:
            # move the position
            speed = self.speed
            d = self.guide - self.position
            dv = d.unit() * speed * (dt / 1000)
            self.position += dv

    # pause the actor and then check for certain situations
    def pause(self, time=configs.destination_wait_time):
        """
        Make the actor stand still for a certain amount of time (actual actions handled in update)
        :param time: duration of pause (use standard destination wait time from configs)
        :return: None
        """
        self.idle_time = time

# --- End of class

