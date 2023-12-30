"""
Test configuration to run things more quickly without affecting the main application
Very easy to get into a specific scenario to get better tests (setting certain states, etc)
"""

import pygame
import configs
from game import Game

# import custom modules
from objects import actors
from objects.waypoint import waypoints

# create screen
screen = pygame.display.set_mode(configs.resolution)
configs.background = pygame.image.load('Storage/NavMesh.png').convert_alpha()


# define actors
my_obj = actors.Actor()

num_actors = 20
all_actors = [actors.Actor() for _ in range(num_actors)]



game = Game(screen, all_actors)
game.run()

