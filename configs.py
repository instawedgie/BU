"""
Define game configs and settings here
"""

import pygame
import random
import py_trees

# display options
import tools

# window tools
width = 400
height = 400
menu_width = 200
resolution = (width + menu_width, height)
background = None  # initialize background (is set during runtime by test.py or main.py)
main_font = None

# actor settings
actor_size = 5
actor_speed = 50
waypoint_radius = 2  # minimum acceptable distance to waypoint (in pixels)
suspend_offset = 2 * actor_size  # radius to suspension bar
suspend_width = actor_size * 3  # width of bar showing suspension
suspend_height = 3  # height of bar showing suspension
destination_wait_time = 250  # wait time in ms to pause at a destination
actor_power_trackers = 15  # frames to track accepted power
actor_max_idle_time = 10  # idle for 10 maximum of 10 seconds
actor_min_idle_time = 5  # idle for minimum of 5 seconds
actor_max_wander_time = 20  # wander for max of 60 seconds
actor_min_wander_time = 10  # wander for min of 30 seconds
actor_tank_min = .5  # min tank size
actor_tank_range = 1.5  # tank size range
actor_drain_min = 2  # minimum tank half life (min)
actor_drain_range = 2  # range of tank half life (min)
actor_tank_drain_rate = .1  # drop/second during tank empty

# controller settings
controller_size = 5
controller_speed = 50
controller_grab_radius = controller_size + actor_size + 5  # final number is pixels between actor and player borders

# patrol settings
patrol_vision_radius = 100
patrol_vision_angle = 60
patrol_guide_speed_mult = 1.2  # multiplier for patrol's guide speed
patrol_move_distance = 2  # min distance from guide to move patrol
patrol_wait_distance = 4  # max distance from guide to stop the guide

# map settings
entry_size = controller_size * 3
navmesh_width = 4  # extra pixels on either side of navmesh walls
navmesh_ratio = 1  # ratio of resolution:navmesh_resolution
can_see_multiplier = 2  # checks extra points on the navmesh for vision

# schedule settings
period_length = 5/60    # time for each round
period_total = 4  # num rounds per event

# ----- FSM settings -------
# idle settings
idle_info_radius = actor_size * 3

# grab settings
grab_time = 2  # time before failure
grab_size = 20  # size of circles
grab_num = 4  # number of circles to make
grab_alpha = 255  # opacity of circles
grab_bar_width = 50

# raster settings
raster_resolution = (5, 5)  # number of raster pixels
raster_offset = 1  # number of screen pixels to offset tiles by

# control settings
attack_power = 15  # attack per click
attack_drain = 50  # attack drain per second
attack_max = 120  # allow extra space for non-immediate draining from max power
num_tracers = 5  # number of frames of mouse position to store
num_averages = 30  # number of frames for moving average of power
max_mouse_power = 800  # reference for max width on mouse power
max_mouse_power_y = 500  # reference for max heigt on mouse power
power_bar_width = 50  # width of power bar on interface

# task settings
task_power = .15  # power put in for each click
task_drain = .30  # drain per second
task_start = .40  # starting power
task_max_power = 1  # max power for successful task
task_width = 20  # width of task bar

# msy settings
msy_resolution = (10, 10)  # size of drawing board
msy_offset = 0  # offset between tiles

# spk settings
spk_decay = .6
spk_max = 2.5
spk_rec_time = 1

# ---------------------------------
# === Event Settings
# water
water_fill_rate = .1  # fuel/second during water event

# tank
tank_threshold = .75  # start of when tank becomes a priority

# ---------------------------------

# manage fonts
pygame.font.init()
main_font_size = 30
main_font = pygame.font.SysFont('Comic Sans MS', main_font_size)
graph_font_size = 12
graph_font = pygame.font.SysFont('Courier', graph_font_size)
name_font_size = 10
name_font = pygame.font.SysFont('Times New Roman', name_font_size)
text_color = (255, 0, 0)

# ------ colors -------------
# general
background_color = (255, 255, 255)
menu_color = (200, 200, 200)
entry_color = (200, 200, 255)
edge_color = (255, 200, 200)
waypoint_color = (100, 255, 100)

# assign colors for rooms based on depth

room_colors = [
    (255, 255, 255),
    (255, 245, 245),
    (230, 230, 230),
    (200, 200, 200),
    (180, 180, 180),
]

# actors / players
actor_color = (0, 0, 255)
controller_color = (255, 0, 0)

# UI colors
attack_color = (150, 255, 150)
task_color = (200, 0, 0)
success_green = (50, 255, 50)
failure_red = (255, 20, 50)
task_side_color = (255, 255, 204)  # highlighter yellow
health_color = (255, 150, 150)
armor_color = (150, 150, 255)

# raster colors
raster_color = (0, 0, 0)
raster_background = (255, 255, 255)
msy_colors = [
    (255, 30, 0),
    (255, 200, 0)
]

# menu colors
true_color = (150, 255, 150)
false_color = (255, 100, 100)

# map colors
water_color = (200, 200, 255)


# name generator
class NameGenerator:
    names = [
        'actor_%02i' % x for x in range(50)
    ]
    rem_names = list(range(len(names)))

    def __call__(self):
        if not len(self.rem_names):
            self.rem_names = list(range(len(self.names)))

        i = self.rem_names.pop(random.randrange(len(self.rem_names)))
        return self.names[i]


name_generator = NameGenerator()  # create an object to use for getting random names

# ----- DEBUG VARIABLES -----
"""
Variables used to alter behavior for easier debugging. Read the comments. 
"""

# user display options
translate_strings = True  # whether to translate certain strings before displaying to user (ex: Str -> Strength)
show_actor_names = True  # show actor names to console

# main debug switch (True turns off all debug)
debug_master_off = True  # turn off all debug behaviors
debug_print_off = False  # TRY and turn off all debug printing

# misc pest control
debug_remove_collisions = False  # remove collisions for player movement
debug_remove_armor_checks = False  # do not check att armor_types

# power debugs
debug_control_power = False  # control interface simplified power
debug_squ_power = False  # squ interface simplified power
debug_srl_power = False  # swl interface simplified power
debug_spk_failure = False  # remove failure conditions for spk state

# py_tree logging
py_trees.logging.level = py_trees.logging.Level.WARN  # logging level for behavior trees