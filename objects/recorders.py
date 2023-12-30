"""
Used to record certain attributes frame by frame and plot / save them
May get more and more complex depending on what we desire to see
May have many different classes for viewing different behaviors
"""

import pygame
import numpy as np
import matplotlib.pyplot as plt

import configs
import tools
from objects.base_object import BaseObject

# graph behavior variables
limit_y_range = True
y_limit = 2.5

# debug variables
debug = True

class ActorRecorder(BaseObject):
    def __init__(self, mouse):
        super(ActorRecorder, self).__init__()

        # set refs to game objects
        #   - will be given them by other objects as-needed
        self.actor = None
        self.player = None
        self.interace = None

        # performance params
        self.concat_delay = 60  # only concat every 60 frames

        # visual parameters
        self.position = tools.vector(395, 5)  # position in top left of game window
        self.radius = 5

        # set up color dictionary
        # Command should be: self.color = self.color_dict[self.record]
        self.color_dict = {
            True: configs.false_color,  # red
            False: configs.true_color,  # green
        }

        # keep track of the mouse tracker from event manager
        self.mouse = mouse  # given mouse obj during construction

        # init important variables
        self.record = False  # boolean to start recording
        self.time = np.array([])
        self.health = np.array([])
        self.armor = np.array([])
        self.bs = np.array([])
        self.power = np.array([])
        self.damage = np.array([])
        self.idx = 0

    def late_update(self):

        # only do things if there is an actor to record
        if self.actor:
            # check for clicks on indicator light
            if self.mouse.buttons_down[1]:
                if tools.vector.distance(self.position, self.mouse.position) < self.radius:
                    # flip value of self.record
                    self.record = not self.record

                    # manage start of recording
                    if self.record:
                        self.start_recording()
                    # manage end of recording
                    else:
                        self.end_recording()

            # manage recording
            if self.record:
                if not self.actor:
                    if debug: print("No actor to record!")
                    return  # break out of function to avoid errors

                # concat NaNs to list if too short
                if self.idx <= len(self.health):
                    self.health = np.concatenate([self.health, np.array([np.NaN for _ in range(self.concat_delay)])])
                    self.armor = np.concatenate([self.armor, np.array([np.NaN for _ in range(self.concat_delay)])])
                    self.bs = np.concatenate([self.bs, np.array([np.NaN for _ in range(self.concat_delay)])])
                    self.power = np.concatenate([self.power, np.array([np.NaN for _ in range(self.concat_delay)])])
                    self.damage = np.concatenate([self.damage, np.array([np.NaN for _ in range(self.concat_delay)])])
                # record the values
                self.health[self.idx] = self.actor.health
                self.armor[self.idx] = self.actor.armor.health
                self.bs[self.idx] = self.actor.armor.current_bs
                self.power[self.idx] = getattr(self.interface.get_state(), 'power', 0)  # try and get interface power
                self.damage[self.idx] = self.actor.frame_damage
                self.idx += 1  # inc the index


    def draw(self, screen):
        super().draw(screen)

        # only draw indicator if we have an actor to record
        if self.actor:
            pygame.draw.circle(screen, self.color_dict[self.record], self.position.as_tuple(), self.radius)

    def set_actor(self, actor):
        """
        Used to set idle + recorders to watch a specific actor
            - Currently not handling much, used out of an abundance of caution
        :param actor: actor to watch
        :return: None
        """
        self.actor = actor  # set up ref to the actor
        self.interface = self.player.get_interface()  # grab a ref to the interface everytime we are given a new actor

    def end_recording(self):
        """
        Used to save/plot recorded files once off button is pressed
        :return: None
        """
        # create a time vector
        # self.time = np.linspace(len(self.health / 60))
        # plot the health / armor health
        fig = plt.figure()
        plt.plot(self.health)
        plt.plot(self.armor)
        plt.ylim([-5, 105])
        plt.legend(['health', 'armor'])
        plt.grid()
        fig.show()

        # plot all stats
        fig, ax = plt.subplots(layout='constrained')
        ax.plot(self.health / 100)
        ax.plot(self.armor / 100)
        ax.plot(self.bs)
        ax.plot(self.power)
        ax.plot(self.damage)
        ax.legend(['health', 'armor', 'bs', 'power', 'damage rate'])
        ax.grid()
        if limit_y_range:
            ytop = min((y_limit, np.amax(self.damage)))
            ax.set_ylim([0, ytop])
        fig.show()

        # # plot per-frame damage
        # fig, ax = plt.subplots(layout='constrained')
        # ax.plot(self.damage)
        # # ax.set_yscale('log')
        # plt.grid()
        # fig.show()


    def start_recording(self):
        """
        Set up variables for the start of a new recording
        :return: None
        """
        self.idx = 0
        self.time = np.array([])
        self.health = np.array([])
        self.armor = np.array([])
        self.bs = np.array([])
        self.power = np.array([])
        self.damage = np.array([])





