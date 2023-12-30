"""
File used to run the game
Mostly just initializes things and passes them to game.py
"""

# import pygame
import pygame
import configs

# set up pygame screen first (helps with initialization
screen = pygame.display.set_mode(configs.resolution)

# import custom modules
from game import Game
from objects import actors
from objects import patrol
from objects.waypoint import waypoints
from objects import controller
from objects.interface import interface
from objects.uni_graph import game_map
from objects.schedule import schedule
import Mapping.map as map
from objects import recorders
from actor_tree.dummy_actor import Actor
import tools

configs.background = pygame.image.load('Storage/NavMesh2.png').convert_alpha()
pygame.display.set_caption(tools.translator("BU"))

# initialize objects
num_actors = [0, 3, 5, 7, 9, 10, 15, 20]
# num_actors = [1]
# all_actors = [actors.Actor(level=_) for _ in num_actors]
all_actors = [Actor(level=_) for _ in num_actors]

player = controller.Controller()

n_patrols = 1
patrols = [patrol.Patrol() for i in range(n_patrols)]

game_objects = [player] + patrols + all_actors + [game_map, map.game_map] + [interface]

game = Game(screen, game_objects)

game.run()

