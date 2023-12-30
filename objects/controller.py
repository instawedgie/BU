"""
Class for the player
Handles controls and events
    - Actual event mechanics are handled by the interface class at objects.interface.Interface
"""

import pygame
from pygame.locals import *

# import custom modules
from tools import vector
import tools  # helps sometimes with the namespace
from objects.base_object import *
import configs
# from objects.actors import Actor
from actor_tree.dummy_actor import Actor
import UI.ui_controls as controls

# get the singletons :(
from objects.interface import interface
from event_manager import keys, mouse, event_manager
from objects.uni_graph import game_map
from Mapping.map import game_map as room_map
from Mapping.map import map_objects

# behavior variables
show_grab_radius = True  # grey circle around player to show grab radius
control_hold = True  # control held actor instead of player

# debug display variables
debug = False    # general debugging messages
debug_controls = False  # display messages regarding controls to the console
debug_attacks = True  # display messages regarding attacks to the console

# debug behavior variables
remove_collisions = not configs.debug_master_off and configs.debug_remove_collisions  # remove interactions with walls
check_armor = not configs.debug_remove_armor_checks

# class variables
# control variables
movement_keys = {
    'up': K_w,
    'down': K_s,
    'right': K_d,
    'left': K_a,
    'sprint': K_LSHIFT,
    'mod': K_SPACE,
    'negate': K_LCTRL,
}

movement_vectors = {
    movement_keys['up']: vector(0, -1),
    movement_keys['down']: vector(0, 1),
    movement_keys['right']: vector(1, 0),
    movement_keys['left']: vector(-1, 0),
}


class Controller(BaseObject):
    # TODO: Use **kwargs instead of specifying the keyword arguments initially
    def __init__(self, *, position=vector(270, 165)):
        super(Controller, self).__init__()

        # set the name
        self.name = 'controller'

        # STATS: Have to change them here for now
        self.strength = 3
        self.finesse = 3
        self.endurance = 3
        self.toughness = 3

        if debug:
            print("Initializing a controller...")
        # movement and positioning
        self.position = position
        self.speed = configs.controller_speed

        self.color = configs.controller_color
        self.radius = configs.controller_size

        self.control = True  # enable player movement

        # initialize attack values
        self.holding = None
        self.power = 0
        self.att = None

        # initialize event variables
        self.viewing = None  # actor that the player is viewing
        self.interface_state = None  # place holder for the state of the interface # TODO: Remove this (stale ref)

        # update event_manager to track our necessary keys
        [keys.add_key(key) for key in movement_keys.values()]

        self.current_room = None

    def update(self, dt):
        # handle default updates
        super().update(dt)

        # ----- DEBUGGING ------
        if debug:
            cr = room_map.get_room(self.position)
            # print out room display
            # if not cr == self.current_room:
            #     self.current_room = cr
            #     print('moved to: ' + cr.name)
            # do magic with the mouse
            if mouse.buttons_down[3] and keys.keys_pressed[movement_keys['mod']]:
                print("Trying to start debug_state")
                self.debug_state()  # debugging function used to initiate a state
            if mouse.buttons_down[4]:
                print(interface.state)
            if mouse.buttons_down[5]:
                print(str(mouse.position))
            if mouse.buttons_down[6]:
                print("Suspending Actor")
                self.debug_task()

        # manage idle controls
        if interface.state == 'idle' and self.control:
            if mouse.buttons_down[1]:  # left click
                if keys.keys_pressed[movement_keys['mod']]:  # if holding the modifier key (generally: space bar)
                    if debug_controls: print("Viewing")
                    self.view_actor(event_manager.game_objects)  # try and tag an actor for viewing
                elif not keys.keys_pressed[movement_keys['negate']]:  # generally: try and control an actor
                    if debug_controls: print("Trying to control!")
                    self.control_actor(event_manager.game_objects)
                elif keys.keys_pressed[movement_keys['negate']]:
                    print("Negated click!")
                    # check and see if we are looking for a map object
                    map_obj = tools.find_nearest_object(mouse.position, list(map_objects.values()), 30)
                    if map_obj:
                        map_obj.display()
            if mouse.buttons_down[3] and not keys.keys_pressed[movement_keys['mod']]:  # right click
                if debug: print("Trying to grab!")
                self.grab_actor(event_manager.game_objects)

        # handle holding another actor during control
        if self.holding and interface.state == 'control':
            self.power = interface.get_state().power
            if mouse.buttons_up[1]:
                interface.get_state().quit()  # manage control quit (put mouse back to center of screen)
                self.release_actor()  # empty grab should let go of player (if already holding one)

        # handle player movement through a function (too much going on to include in the update call)
        self.move_player(dt)

        # ---- END OF UPDATE ----

    def draw(self, screen):
        super().draw(screen)

        # draw grab radius (if desired)
        if show_grab_radius:
            pygame.draw.circle(screen, (220, 220, 220), self.position.as_tuple(),
                               configs.controller_grab_radius - configs.actor_size)

        # draw the player
        pygame.draw.circle(screen, self.color, (self.position.x, self.position.y), self.radius)

    # --- Event functions

    # update player position based on input
    def move_player(self, dt):
        """
        Used to get input and move player accordingly
        :param dt: time since last frame in ms
        :return: None
        """
        # skip the process if we do not have control
        if not self.control:
            return

        # create a general direction vector
        mv = vector(0, 0)  # start with no movement
        for k, v in movement_vectors.items():  # loop through pairs of pygame_key, pressed_boolean
            mv += (v * keys.keys_pressed[k])  # add up values of only the pressed keys (vector * False = vector(0, 0))

        if vector.magnitude(mv) > 0:  # if we need to move
            # calculate speed
            speed = self.speed  # initial speed to use
            sprint = keys.keys_pressed[movement_keys['sprint']]  # boolean for if we are sprinting
            if self.holding and self.power < 1:  # if we are holding an actor w/o full power
                speed *= .2  # use 20% speed
            elif sprint and not self.holding:  # if we are not holding an actor and pressing sprint key
                speed *= 1.5  # multiply speed by 1.5

            if not self.holding or not control_hold:  # move player and (possibly) held actor
                dp = mv.unit() * speed * (dt / 1000)  # change in position (as a vector)
                np = self.position + dp  # new desired position

                # adjust change in position by checking for collisions
                dp = self.collision_adjustment(self.position, dp)

                # move to the new position (w/ collision manager approved dp vector)
                self.position += dp

                if self.holding:  # also move actor we are holding (if we have one)
                    # move actor freely if player is in a door frame (avoids leaving actor stuck in a room)
                    if room_map.get_doorframe(self.position):
                        self.holding.position += dp
                    else:  # restrict actor movement w/ walls
                        self.holding.position += self.collision_adjustment(self.holding.position, dp)
            else:  # move holidng and have player follow
                # calc desired position
                dp = mv.unit() * speed * (dt / 1000)  # change in position (as a vector)
                np = self.holding.position + dp  # new desired position

                # adjust change in position by checking for collisions
                dp = self.collision_adjustment(self.holding.position, dp)

                # move holding to the new position (w/ collision manager approved dp vector)
                self.holding.position += dp

                # move self to follow the new position
                if vector.distance(self.position, self.holding.position) > (.5 * configs.controller_grab_radius):
                    # calc distance to move
                    dp = self.holding.position - self.position
                    mv = dp.unit() * speed * (dt / 1000)
                    self.position += mv

    def freeze(self):
        """
        Quick method to freeze the actor (used in case we want to do more than just set control to False)
        :return: None
        """
        self.control = False

    def unfreeze(self):
        """
        Quick method to return control (used in case there is more to adjust than simply the control variable
        :return: None
        """
        self.control = True



    @staticmethod
    def collision_adjustment(cp, dp):
        """
        Take a current position and goal position and have the map adjust goal position for collisions in the map
        :param cp: current position
        :param dp: change in position
        :return: Map-Approved change in position
        """

        # skip collision detection if we want to remove annoying walls during debug process
        if remove_collisions:
            return dp

        np = cp + dp  # calculate new position
        possible = room_map.check_next(cp, np)  # get bool tuple from the map

        # adjust x and y values
        dp.x *= possible[0]
        dp.y *= possible[1]

        # return the actual movement vector
        return dp

    # view an actor in the inspector
    @staticmethod  # doesn't need self reference, might as well make static
    def view_actor(game_objects):
        """
        Used by the idle UI state to display actor stats on side menu
        Sets the actor held by self.interface_state (will set to None if no actor is found)
        :param game_objects: List of game objects to search through
        :return: None
        """
        # find the nearest actor to the mouse click (can be None to remove any viewing)
        found_actor = tools.find_nearest_object(
            mouse.position,
            game_objects,
            configs.controller_grab_radius,
            object_type=Actor,
        )

        if interface.state == 'idle':  # ensure interface state is 'idle'
            interface.states[interface.state].set_actor(found_actor)

    # Function used to launch into a state for debugging purposes (constantly changing)
    def debug_state(self):
        print("Starting debug state")
        found_actor = tools.find_nearest_object(
            mouse.position,
            event_manager.game_objects,
            configs.controller_grab_radius,
            object_type=Actor
        )
        if found_actor:  # if we actually clicked somebody
            self.holding = found_actor  # keep ref to the found actor
            print("Freezing actor: " + self.holding.name + " for spk state")
            self.holding.freeze()  # freeze actor
            # found_actor.add_afm([controls.afms['MSY']])  # add msy afm to actor
            found_actor.position = self.position + vector(0, 5)  # move actor to 5 squares below player
            # self.att = controls.controls['MSY']
            self.dynamic_state('spk')

    # handle grab attempt
    def grab_actor(self, game_objects):
        """
        Used to initiate a grab
        SHOULD only initiate when the interface state is 'idle'
        :param game_objects: List of game objects to search through
        :return: None
        """
        # find actor in nearby area
        if not self.holding:  # only search if not already holding an actor
            self.holding = tools.find_nearest_object(self.position, game_objects,
                                                     radius=configs.controller_grab_radius,
                                                     object_type=Actor)
        if self.holding:
            if debug: print("Found Actor")
            # manage grabs during actor states
            if self.holding.suspension or self.holding.lock:  # manage a suspended actor
                if debug: print("Grabbed suspended Actor")
                self.control = False  # disable player movement
                # self.holding.suspension = None  # remove the suspension
                # self.holding.remove_lock()  # remove any locks
                # self.holding.unfreeze()  # ensure everything else is reset
                self.holding.freeze()  # refreeze player (fresh)
                self.good_grab()  # skip the grab controls, go straight into raster
            else:  # case for a free actor
                self.control = False  # disable player movement
                self.holding.control = False  # disable actor movement
                interface.set_state('grab')  # set combat interface to grab state

        else:
            if debug: print("No Actor Found")

    # fail a grab (called by the state)
    def fail_grab(self):
        interface.set_state('idle')
        self.control = True  # return control to player
        self.holding.control = True  # return control to actor
        self.holding = None  # remove hold on actor

    # succeed in a grab (called by the state)
    def good_grab(self):
        # TODO: Remove the old remove lock code (handled more gracefully by the actor)
        # self.holding.remove_lock()  # remove the lock if there is one (Decided this was bad)
        self.start_raster()  # begin raster state

    # starting the raster state on combat interface
    def start_raster(self):
        self.control = False  # ensure player doesn't have control
        interface.set_state('raster')

    def check_raster(self, nt):
        """
        Used to check if raster input is valid, and then starts actions for valid input
        :param nt: numpy array from UI.raster
        :return: None
        """
        self.att = controls.check_input(nt)
        failed = False
        if self.att:
            if type(self.att) == controls.Spell:
                self.att.function()
                failed = True  # set to failed to release us from raster
            else:
                if debug_attacks:
                    print("Successful raster input")
                    print("Att: " + self.att.name)
                    print("Ste: " + self.att.state)

                # check if location specific
                if self.att.check_loc:
                    if not room_map.check_event(self.position, self.att.name):
                        if debug_attacks: print("Invalid location for input.")
                        failed = True  # invalid attack, break out

                # check for required armor types
                if check_armor:  # if we are not removing armor checks for debugging
                    if self.att.use_armor and self.att.armor_types:  # if we have specified armor types
                        if self.holding.armor.name not in self.att.armor_types:
                            if debug_attacks: print("Invalid armor type")
                            failed = True

                # check if we use armor and if it is broken
                if self.att.use_armor and not self.holding.armor.health > 0:
                    failed = True

                # deal with different att values
                if self.att.state == 'control':
                    self.control_actor(att=self.att)  # begin control of the actor
                    self.control = True  # enable player movement
                if self.att.state == 'idle':
                    self.release_actor()  # drop the actor
                    self.control = True  # enable player movement
                if self.att.state == 'task':
                    self.start_task()
                else:
                    # deal with different interface states dynamically (should have done this to begin with)
                    self.dynamic_state(self.att.state)
        else:  # no attack found, break out
            failed = True

        if failed:  # raster input was invalid, break out to idle
            if debug: print("Raster not found")
            self.release_actor()
            self.control = True

    def dynamic_state(self, state):
        # just change the interface
        # ensure that all future states can handle what needs to happen with the player and actor
        #   - probably by grabbing them from event manager
        interface.set_state(state)

    def start_task(self):
        self.control = False  # ensure player is immobile
        interface.set_state('task')  # set interface FSM to 'task'

    # TODO: Remove old debug function 'debug_task' (Used to automatically apply a suspension, wouldn't work anymore)
    def debug_task(self):
        if not self.holding:  # if not holding, find something
            self.holding = tools.find_nearest_object(self.position, event_manager.game_objects,
                                                     radius=configs.controller_grab_radius,
                                                     object_type=Actor)
        if self.holding:
            self.holding.suspend()
            self.holding = None
            interface.set_state('idle')

    def successful_task(self):
        """
        Used to go to the next state after a successful task
        :return: None
        """
        if debug: print("Successful task")
        if self.holding:  # ensure we are still holding an actor
            if self.att.name in controls.locks.keys():  # if att is a lock
                if debug_attacks: print("Successful Lock")
                self.holding.add_lock(self.att)  # add a lock to the actor
            elif self.att.name in controls.suspensions.keys():  # if the att is a suspension
                if debug_attacks:
                    print("Successful Suspension")
                self.holding.suspend(self.att)  # add suspension to the actor
                if debug_attacks: print(self.holding.suspension)
            else:
                tools.error('Could not find task output in controls.py')
        self.release_actor()  # drop the actor
        self.control = True  # return control to the player

    def failed_task(self):
        if debug: print("Failed task")
        self.release_actor()  # drop the actor
        self.control = True

    # handle clicking an actor (finding a nearby player)
    def control_actor(self, game_objects=None, att=controls.controls['REG']):
        if debug_attacks: print("trying to control actor")
        if not self.holding:  # if not already holding an actor, search for one
            self.holding = tools.find_nearest_object(self.position, game_objects, radius=configs.controller_grab_radius,
                                                     object_type=Actor)

        # Handling the case of successful control
        if self.holding:  # if holding an actor after ^ block
            if debug_attacks: print("successful control")
            self.att = att
            self.holding.control_actor(att=att)  # freeze the actor's movement
            self.interface_state = interface.set_state('control')  # set combat interface to control
            self.control = True

    def release_actor(self, unstuck=False):
        """
        Used to release an actor
            - Safe to call if we are not currently holding one, has no affect
        :param unstuck: optional bool for if we should set stuck=False on the actor before letting go
        """
        if debug: print("Letting go of actor")
        if self.holding:  # only run if we are actually holding an actor
            # pause the actor depending on power level at release (if the state has a power attribute)
            if hasattr(interface.states[interface.state], 'power'):
                power = interface.states[interface.state].power  # all control states should have a power level
                pause_time = power * 250  # pause for up to 1 second for max power
                self.holding.pause(time=pause_time)  # use voluntary pause function from the actor
                self.holding.reset_path()

            self.holding.unfreeze()  # unfreeze the actor the player is holding
            if unstuck:
                self.holding.stuck = False  # removes stuck parameter from actor

            # manage the interface
            self.interface_state = interface.set_state('idle')

            # deal with the player
            self.holding = None  # remove reference to the held actor (still held by game_objects)
            self.att = None
            self.power = 0  # set the power bar level to 0

    # === Ugly ref grabbers ===  >:{
    def get_interface(self):
        """
        Used to grab a reference to the interface once it is initiated
            - Mostly used for recorders during debugging
            - Can't think of another use for it currently
        :return: the interface singleton
        """
        return interface


