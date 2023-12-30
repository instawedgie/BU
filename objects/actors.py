"""
Made to randomly go to destinations in the graph
"""

import pygame
from pygame.locals import *

import math
import random
import numpy as np

# import custom modules
from tools import *
from objects.base_object import *
import configs
import UI.ui_controls as controls
import UI.armor
import UI.afm

# get the graph and the destinations
from Mapping.map import hallway_nodes, locations, unlock_locations, game_map

# rename hallway nodes for compatability
waypoints = hallway_nodes

# grab other singletons
from event_manager import mouse

# class variables
debug = False  # printing general debugs
debug_suspend = False  # printing suspension debugs
debug_pathfinding = False  # print pathfinding info to the console
debug_removal = False  # print info regarding removing afms


class Actor(BaseObject):
    # TODO: Use **kwargs instead of specifying the keyword arguments initially
    def __init__(self, *, actor_color=configs.actor_color, position=None, config=None, level=None):
        super(Actor, self).__init__()
        # actor stats
        if config:
            # load in config obj and assign NPC stats
            pass
        else:
            # UI stats
            self.name = configs.name_generator()  # generate random, ideally unused name (unless #actors > #names)
            self.color = [random.randint(1, 230) for i in range(3)]
            self.num_trackers = configs.actor_power_trackers

            # action stats
            if level:
                self.level = level
            else:
                self.level = random.randint(1, 20)

            # upgrade random stats based on level
            self.strength = 0
            self.finesse = 0
            self.toughness = 0
            self.endurance = 0

            stats = [self.strength, self.finesse, self.toughness, self.endurance]  # set up intial list
            for i in range(self.level):  # loop for each level
                out = random.choice([n for n, _ in enumerate(stats) if _ < 5])
                stats[out] += 1
            # self.stats = stats  # hold a list of stats
            self.__dict__.update({
                'strength': stats[0],
                'finesse': stats[1],
                'endurance': stats[2],
                'toughness': stats[3],
            })

        self.armor = UI.armor.get_armor(random.choice(list(UI.armor.armors.keys())))

        # movement and positioning
        self.speed = configs.actor_speed
        self.waypoint_radius = configs.waypoint_radius  # distance to consider actor has arrived at waypoint
        self.radius = configs.actor_size

        self.waypoint_names = list(range(len(waypoints)))
        self.waypoint = waypoints[random.choice(self.waypoint_names)]
        self.destination = self.waypoint
        self.path = [self.destination]

        # get starting position
        if not position:  # if we aren't given a starting position
            self.position = self.waypoint.position
        else:
            self.position = position

        # variables for actor navigation
        self.wait_time = 0  # initial value for how long to stay stationary voluntarily
        self.stationary = False  # bool for if we are waiting at our destination
        self.control = True  # bool for if we are able to move
        self.reset = False  # bool for if we need to reset our waypoints (due to losing control)

        # variables for general interface interaction
        self.att = None
        self.health = 100
        self.frame_damage = 0
        self.frame_powers = [0 for _ in range(self.num_trackers)]

        # behaviour tree variables
        self.event = None  # keep track of event (in string form :( )
        self.event_dict = {}  # use as a blackboard to keep track of necessary items for each event

        # afm variables
        self.afm = []  # list holding all Afm
        self.afm_pop = False  # bool for popping afm from list after waiting

        # variables for actor suspension
        self.suspension = None
        self.stuck = False  # if actor is stuck
        self.temp_stuck = False  # temporary freeze for control during a suspension
        self.suspend_duration = 0  # duration of suspension in ms
        self.suspend_time = 0  # time suspended in ms
        self.suspend_rect = pygame.Rect((0, 0), (0, 0))  # placeholder for suspension rectangle
        self.suspend_rect_background = Rect((0, 0), (0, 0))  # placeholder for background of suspension rectangle
        self.stuck_color = configs.failure_red  # color for if actor is stuck
        self.suspend_color = self.color  # color for if actor is suspended (and not stuck)
        self.sus_rect_color = self.suspend_color

        # variables for locking
        self.lock = None  # Name of Actor's lock (defaults to None), lock should be a string

    def update(self, dt):
        # handle default updates
        super().update(dt)

        # handle observation variables
        self.frame_damage = 0
        self.frame_powers = self.frame_powers[1:] + [0]  # cycle frame_power tracker and add 0 to right end
        for a in self.afm:
            a.frames = a.frames[1:] + [0]

        # deal with suspension
        if self.suspension:  # if we are suspended
            self.control = False  # ensure to disable movement
            # manage suspension background rectangle
            self.suspend_rect_background = pygame.Rect((self.position.x - (configs.suspend_width / 2) - 1,
                                                        self.position.y - (configs.suspend_offset + 1)),
                                                       (configs.suspend_width + 2, configs.suspend_height + 2))
            if not self.stuck and not self.temp_stuck:  # if we arent' stuck
                if self.suspend_time < self.suspend_duration:
                    self.suspend_time += dt
                    # update suspension wait bar
                    self.sus_rect_color = self.suspend_color
                    self.suspend_rect = pygame.Rect((self.position.x - (configs.suspend_width / 2),
                                                     self.position.y - configs.suspend_offset),
                                                    (configs.suspend_width * (
                                                                1 - self.suspend_time / self.suspend_duration),
                                                     configs.suspend_height))
                else:  # remove our own suspension
                    self.stuck = False
                    self.suspension = None
                    self.unfreeze()
            else:  # we are stuck
                # draw the suspension wait bar in red
                self.sus_rect_color = self.stuck_color
                self.suspend_rect = pygame.Rect((self.position.x - configs.suspend_width / 2,
                                                 self.position.y - configs.suspend_offset),
                                                (configs.suspend_width, configs.suspend_height))

            # manage armor and damage
            if self.suspension:  # ensure we are still suspended
                self.afm_damage(self.suspension.intensity, dt, self.suspension.afm)
                # free player if the actor is broken
                if self.armor.broken:
                    self.stuck = False
                    self.suspension = None
                    self.unfreeze()

        # deal with locks
        if self.lock:
            self.lock.update(self, dt)
            # check for broken armor
            if self.armor.broken:
                self.remove_lock()

        # update stationary values (generally used for waiting at a destination)
        if self.stationary:
            # update time of waiting
            try:
                if self.wait_time > 0:
                    self.wait_time -= dt
            except:
                print("ISSUE with " + self.name)
                print(self.wait_time)
            # begin steps to resume travel
            else:
                if debug_removal and (self.afm or self.lock): print('finished waiting')
                self.stationary = False
                self.reset = True
                # manage arrival at the waypoint
                if self.waypoint == self.destination:
                    # manage removing afm
                    rm_afm = [_ for _ in self.afm if not _.permanent]
                    if self.afm_pop:  # if we can remove an afm
                        if debug_removal: print("Removed an afm")
                        self.afm.pop()  # remove the last afm if we just finished waiting for it
                        self.afm_pop = False
                    if not self.lock and len(self.afm) > 0:  # if we don't have a lock and have an afm
                        self.remove_afm()
                    # manage removing locks
                    if self.lock and not self.stuck and self.destination in unlock_locations:  # if we have a lock and can remove it
                        self.remove_lock()
                    # assign a new destination (if we are all set)
                    if self.stuck or (not self.lock and not rm_afm):  # if we aren't stuck or are ready to move on
                        self.destination = random.choice(locations)

        # reset the character's path (for whatever reason)
        if self.reset:
            if debug_pathfinding:
                print("Resetting actor")
            # manage next waypoint
            current_room = game_map.get_room(self.position)  # figure out if player is in a room
            room_waypoints = list(current_room.waypoints.values())
            if not current_room:  # if player is not in a room
                raise Exception("Actor is not in a room")
            else:  # if not in a room
                try:
                    tmp_list = [vector.distance(self.position, _.position) for _ in room_waypoints]  # distance to waypoints
                    tmp_indx = np.argmin(np.array(tmp_list))  # index of the closest waypoint
                    add_closest = not self.waypoint == room_waypoints[tmp_indx]  # flag to add current closet waypoint to path
                    self.waypoint = room_waypoints[tmp_indx]  # set current waypoint to the closest waypoint (wrong)
                except Exception as e:
                    print(e)
                    print(current_room.name)
                    print(room_waypoints)
                    raise Exception("Things are breaking")

            # find a new path
            if debug_pathfinding:
                print("finding a new path")
                print('start: ' + str(self.waypoint.name))
                print('end  : ' + str(self.destination.name))
            self.path = a_star(waypoints, self.waypoint, self.destination)
            if debug_pathfinding: print([p.name for p in self.path])
            if vector.distance(self.waypoint.position, self.position) > self.waypoint_radius:  # waypoint out of range
                if debug_pathfinding:
                    print("Adding the closest waypoint")
                    print(self.path)
                    print([_.name for _ in self.path])
                    print(self.waypoint.name)
                self.path += [self.waypoint]  # add closest waypoint to the path
            # if debug_pathfinding:
                # print('start: ' + str(self.waypoint.name))
                # print('end  : ' + str(self.destination.name))
                # print([p.name for p in self.path])
            self.waypoint = self.path.pop()
            self.reset = False

        # manage traveling to waypoint
        if self.control and not self.stationary:  # if we have control and are not voluntarily stationary
            if self.waypoint and vector.distance(self.waypoint.position, self.position) > self.waypoint_radius:
                self.go_to_waypoint(dt)
            # manage arriving at waypoint
            else:
                if self.waypoint == self.destination:
                    self.pause(configs.destination_wait_time)
                else:
                    self.waypoint = self.path.pop()

    def draw(self, screen):
        super().draw(screen)

        if self.suspension:
            # suspension wait bar
            pygame.draw.rect(screen, configs.menu_color, self.suspend_rect_background)
            pygame.draw.rect(screen, self.sus_rect_color, self.suspend_rect)

        # drawing player during different states
        if self.lock:
            # draw black outline
            pygame.draw.circle(screen, (0, 0, 0), (self.position.x, self.position.y), self.radius)
            pygame.draw.circle(screen, self.color, (self.position.x, self.position.y), self.radius - 1)
        elif self.afm:
            # grey outline
            pygame.draw.circle(screen, configs.menu_color, (self.position.x, self.position.y), self.radius)
            pygame.draw.circle(screen, self.color, (self.position.x, self.position.y), self.radius - 1)
        else:
            # standard player
            pygame.draw.circle(screen, self.color, (self.position.x, self.position.y), self.radius)

    # --- Behaviour tree functions

    def reset_event(self):
        self.event = None
        self.event_dict = None

    # --- custom functions
    # simple waypoint function, no look ahead or turning involved
    def go_to_waypoint(self, dt):
        # manage lock's affect on travel
        speed = self.speed
        if self.lock:
            speed = speed * self.lock.speed_decrease
        # manage afms affect on travel
        for i in self.afm:
            speed = speed * i.speed_decrease
        d = self.waypoint.position - self.position
        dv = d.unit() * speed * (dt / 1000)
        self.position += dv

    # pause the actor and then check for certain situations
    def pause(self, time=configs.destination_wait_time):
        """
        Make the actor stand still for a certain amount of time (actual actions handled in update)
        :param time: duration of pause (use standard destination wait time from configs)
        :return: None
        """
        self.wait_time = time  # set time to wait
        self.stationary = True  # set stationary bool for a voluntary pause

    # prevent actor from moving (still updates in other ways)
    def freeze(self):
        """
        Disable actor's autonomous movement
            - Can still be moved by other forces
        :return: None
        """
        self.control = False  # disables movement
        if self.suspension:
            self.temp_stuck = True  # enact temporary stuck during external freeze
            self.suspend_time = 0  # reset suspension timer

    def unfreeze(self, pause=True):
        """
        Used to unfreeze the actor
        :param pause: Boolean for a short pause before resuming pathfinding
        :return: None
        """
        # manage attacks
        if self.att and not self.suspension:  # if we have an attack and are not suspended
            if debug:
                print(self.att)
                print(self.stuck)
                print("Removing attack")
            self.remove_att()
        self.stationary = pause  # short pause before resuming movement
        self.control = True  # enables movement
        self.reset = True  # forces player to recalculate path
        self.temp_stuck = False  # remove temporary stuck bool

    def afm_damage(self, value, dt, afm):
        # ensure we are dealing with a list
        if type(afm) != list:
            afms = [afm]
        else:
            afms = afm

        # loop through afms
        for afm in afms:
            # get the proper afm and update it
            if type(afm) is not str:
                base_a = afm.name  # try and use the name of the object given
            else:
                base_a = afm  # should be given a name
            a = self.get_afm(base_a)  # return the afm belonging to the actor (add it if missing)
            a.update(value, dt)  # update it


    def basic_damage(self, damage):
        """
        Used to just apply damage to an actor
        :param value: value to reduce from health
        :return: None
        """
        self.health -= damage * ((self.health / 100)) * (1 - (.2 * (self.toughness - 3)))


    def damage(self, value, dt=0, afm=None):
        """
        Apply damage to the player + their armor
        :param value: Max DPS (affected by armor + health levels)
        :param dt: time passed during frame
        :param afm: afm matching the damage
        :return: boolean for if actor still has armor
        """
        dt /= 1000
        # a time based attack
        if dt > 0:
            # if we have armor
            if self.armor and not self.armor.broken:
                if debug:
                    print('value: ' + str(value))
                    print('dt   : ' + str(dt))

                # # manage armor
                # if not afm or afm.armor:  # if we don't have an afm or afm has armor enabled
                #     self.armor.damage(value, dt)  # damage the armor

                # calculate actor damage
                int_damage = 0
                dt_damage = 0  # init dt damage at 0 (avoids a billion if statements)
                if afm:  # manage damage w/ afm
                    for base_a in afm:  # loop through given afms
                        # ensure proper afm format
                        if type(base_a) is not str:
                            base_a = base_a.name  # try and use the name of the object given
                        a = self.get_afm(base_a)
                        # manage armor
                        if a.armor:  # if we don't have an afm or afm has armor enabled
                            self.armor.damage(value, dt)  # damage the armor
                        if a.damage:
                            int_damage += value * dt * self.armor.strength * a.intensity  # integral damage
                        if a.name not in [_.name for _ in self.afm]:  # check if missing afm
                            self.add_afm(a)  # add it
                        if a.track and a.dt:
                            # print(a.frames)
                            amn = np.argmin(a.frames)
                            amx = np.argmax(a.frames)
                            mn = np.amin(a.frames)
                            mx = np.amax(a.frames)
                            a.frames[-1] += value  # add power to power tracker for d/dt damage
                            if value > mx:  # positive slope
                                if debug_suspend: print("UP!")
                                dt_damage += (
                                    (value - mn) * value * (10 * dt) * self.armor.strength * a.intensity
                                )
                else:
                    self.armor.damage(value, dt)  # damage the armor
                    int_damage = value * dt * self.armor.strength  # integral damage
                # take a way from health
                damage = int_damage + dt_damage
                self.health -= damage * ((self.health / 100)) * (1 - (.2 * (self.toughness - 3)))
                self.frame_damage += damage / dt  # add to damage during this frame

                # check for broken armor after attack
                if self.armor.broken:
                    self.damage(self.armor.break_damage)
                    return False
                return True
        # instantaneous attack
        else: # if dt = 0, just remove the health from the actor
            # damage val * health ratio * toughness ratio w/ a max value of 1 (too much damage when multiplied)
            damage = value * (self.health / 100) * min([(1 - (.2 * (self.toughness - 3))), 1])
            self.health -= damage
            # self.frame_damage += damage


    def suspend(self, att):
        self.freeze()  # freeze the actor
        self.remove_lock()  # remove any locks (if we have any) s

        self.att = att
        self.stuck = att.time <= 0  # figure out if stuck
        self.suspend_duration = att.time  # set suspension duration

        self.suspend_time = 0  # current time suspended
        self.suspension = att

    def control_actor(self, att=None):
        self.att = att
        self.freeze()

    def remove_att(self):
        if self.att:  # ensure there is an attack
            if self.att.afm:  # add residual lock (if necessary)
                self.add_afm(self.att.afm)
            self.att = None  # remove attack
        # if there is not an attack (Should not be called when we don't have one)
        else:
            if debug: print("Attempted to remove an Empty attack")

    # used to lock player, wrapped in function to control other mechanics during locking (potentially)
    def add_lock(self, lock):
        # remove suspension (if we have one)
        if self.suspension:
            self.suspension = None
            self.stuck = False
        # add the lock
        self.lock = lock  # add lock to player
        if not self.stuck:
            self.destination = random.choice(unlock_locations)  # set waypoint to a place to remove the lock

    # used to remove a lock, wrapped to potentially add useful features during unlocking
    def remove_lock(self):
        if self.lock is not None:
            if debug_removal: print("Removed a lock")
            self.pause(self.lock.removal_time)
            if self.lock.afm:
                self.add_afm(self.lock.afm)
        self.lock = None  # remove the lock

    # add residuals
    def add_afm(self, afm):
        """
        Add an AFM without duplications
        :param afm: afm object
        :return: None
        """
        if type(afm) is not list:
            afm = [afm]
        for a in afm:  # loop through given afm list
            if a.name not in [_.name for _ in self.afm]:  # if this afm not in our list of afms
                afm = UI.afm.get_afm(a.name)
                afm.apply(self)  # add the actor as the owner of the afm
                self.afm += [afm]  # add this afm to the list
                return afm

    def get_afm(self, name):
        """
        Used to ensure we are our actors afm
        :param name: either afm obj or str of afm
        :return: actor's afm object
        """
        if type(name) == UI.afm.Afm:
            name = name.name

        for a in self.afm:
            if a.name == name:
                return a

        # if we couldn't find it, add it
        if debug: print("Adding an Afm")
        afm = UI.afm.get_afm(name)  # ensure
        return self.add_afm(afm)  # add_afm returns the object it adds

    def has_afm(self, name):
        """
        Quick check for if an actor has a specific afm w/o adding it if missing
        :param name: AFM obj or string
        :return: Boolean for if it has the afm
        """
        if type(name) == UI.afm.Afm:
            name = name.name

        for a in self.afm:
            if a.name == name:
                return a
        return None


    # used to remove all afms
    def remove_afm(self, name=None):
        if not name:
            if debug_removal: print("Waiting for afm")
            # search for removable afm
            idx = -1
            while True:  # loop until released
                try:
                    afm = self.afm[idx]
                    if not afm.permanent:
                        del self.afm[idx]  # remove afm from the list
                        break  # get out of the loop
                    else:
                        idx -= 1
                except IndexError as e:
                    return  # exit if no more items to check in the list (and do not wait)
            self.pause(afm.removal_time)  # should only run an afm is found
            # self.afm_pop = True
        else:
            a = self.has_afm(name)
            if a:
                self.pause(a.removal_time)  # pause the actor's motion
                a.value = 0  # reset the value
                idx = self.afm.index(a)  # get the index
                del self.afm[idx]  # delete it from the afm list
