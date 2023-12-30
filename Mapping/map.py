"""
Use this file to initiate and gain access to the map (namely: graphs and rooms)
"""

import pygame
import numpy as np
import matplotlib.pyplot as plt

import configs
import tools
from tools import vector
from objects.base_object import BaseObject

from Mapping.room import Room
from Mapping.waypoint import Waypoint, Edge, IdleLocation
from Mapping.event_region import EventRegion
import Mapping.event_region as er_classes

# import map object classes
from Mapping.objects.WF import WF
from Mapping.objects.hng import Hng
from Mapping.objects.tank import Tank

# load event manager LAST
from event_manager import event_manager

# debug variables
debug = False
debug_graph = False
debug_collisions = False
debug_navmesh = False
debug_plot_navmesh = False  # plot the navmesh during startup
debug_save_navmesh = False

# draw variables (draw various elements of the map)
draw_rooms = False
draw_waypoints = False
draw_edges = False

# ensure that we track edges if needed
if draw_edges:
    Edge.track = True  # track all created edges

# --- room definitions
rooms = {
    # blank room template for quicker boilerplate creation
    # '': Room(
    #     xlim=[, ],
    #     ylim=[, ],
    #     entrance=[, ],
    #     depth=2
    # ),
    'building': Room(
        xlim=[10, 390],
        ylim=[10, 390],
        entrance=[-10, -10],  # entrance is impossible to reach (need to ensure this doesn't cause issues)
        depth=1,  # lowest depth
    ),  # TODO: allow player to walk out this exit to close the game
    'Office': Room(
        xlim=[10, 60],
        ylim=[10, 110],
        entrance=[60, 55],
        depth=3
    ),
    'Reception': Room(
        xlim=[60, 110],
        ylim=[10, 70],
        entrance=[110, 30],
        depth=2
    ),
    'Main Closet': Room(
        xlim=[60, 110],
        ylim=[70, 110],
        entrance=[110, 90],
        depth=2
    ),
    'Library': Room(
        xlim=[160, 260],
        ylim=[10, 110],
        entrance=[160, 90],
        depth=2
    ),
    'Lib Office': Room(
        xlim=[160, 200],
        ylim=[10, 50],
        entrance=[200, 30],
        depth=3
    ),
    'Lib Closet': Room(
        xlim=[160, 200],
        ylim=[50, 70],
        entrance=[200, 60],
        depth=3
    ),
    'Cafe': Room(
        xlim=[260, 340],
        ylim=[10, 110],
        entrance=[285, 110],
        depth=2
    ),
    'Kitchen': Room(
        xlim=[340, 390],
        ylim=[10, 80],
        entrance=[340, 25],
        depth=3
    ),
    'Fridge': Room(
        xlim=[340, 390],
        ylim=[80, 110],
        entrance=[375, 80],
        depth=4
    ),
    'Closet North': Room(
        xlim=[10, 40],
        ylim=[110, 160],
        entrance=[40, 145],
        depth=2
    ),
    'Room 1': Room(
        xlim=[10, 110],
        ylim=[160, 220],
        entrance=[110, 200],
        depth=2
    ),
    'Room 2': Room(
        xlim=[10, 110],
        ylim=[220, 280],
        entrance=[110, 235],
        depth=2
    ),
    'Room 3': Room(
        xlim=[160, 260],
        ylim=[160, 230],
        entrance=[160, 200],
        depth=2
    ),
    'Room 4': Room(
        xlim=[160, 260],
        ylim=[280, 340],
        entrance=[180, 280],
        depth=2
    ),
    'MR': Room(
        xlim=[310, 350],
        ylim=[160, 205],
        entrance=[335, 160],
        depth=2
    ),
    'WR': Room(
        xlim=[350, 390],
        ylim=[160, 205],
        entrance=[365, 160],
        depth=2
    ),

    'SR': Room(
        xlim=[310, 390],
        ylim=[205, 340],
        entrance=[370, 340],
        depth=2
    ),
    'SR Closet': Room(
        xlim=[310, 350],
        ylim=[300, 340],
        entrance=[350, 320],
        depth=3
    ),
    'Gym': Room(
        xlim=[80, 160],
        ylim=[280, 390],
        entrance=[135, 280],
        depth=2
    ),
    'ML': Room(
        xlim=[10, 80],
        ylim=[280, 335],
        entrance=[80, 320],
        depth=3
    ),
    'WL': Room(
        xlim=[10, 80],
        ylim=[335, 390],
        entrance=[80, 350],
        depth=3
    ),
    'Gym Office': Room(
        xlim=[160, 210],
        ylim=[340, 390],
        entrance=[160, 375],
        depth=3
    ),
    'Gym Closet': Room(
        xlim=[210, 230],
        ylim=[340, 390],
        entrance=[210, 350],
        depth=4
    ),
    'Closet South': Room(
        xlim=[230, 260],
        ylim=[340, 390],
        entrance=[260, 375],
        depth=2
    ),
}

# assign a name to each room
for key, value in rooms.items():
    value.name = key

# --- hallway waypoint definitions
hallway_nodes = [
    # boiler plate for easier creation
    # Waypoint(
    #     position=(, )
    # ),
    # --- office hallway left
    Waypoint(  # reception door
        position=(120, 30),
    ),
    Waypoint(  # mid point left
        position=(120, 60)
    ),
    Waypoint(  # office closet door
        position=(120, 90)
    ),
    Waypoint(
        position=(120, 120)
    ),
    # --- Office hallway right (starts: indx 4)
    Waypoint(
        position=(150, 30)
    ),
    Waypoint(
        position=(150, 60)
    ),

    Waypoint(
        position=(150, 90)
    ),
    Waypoint(
        position=(150, 120)
    ),
    # --- closet north hallway top (starts: indx 8)
    Waypoint(
        position=(100, 130)
    ),
    Waypoint(
        position=(70, 130)
    ),
    Waypoint(
        position=(50, 130)
    ),
    # --- North Closet hallway bottom (starts: indx 11)
    Waypoint(
        position=(100, 150)
    ),
    Waypoint(
        position=(70, 150)
    ),
    Waypoint(
        position=(50, 145)
    ),
    Waypoint(
        position=(120, 150)
    ),
    # --- Lib/Room3 hallway top (starts: indx 15)
    Waypoint(
        position=(170, 120)
    ),
    Waypoint(
        position=(200, 120)
    ),
    Waypoint(
        position=(240, 120)
    ),
    Waypoint(  # cafe door
        position=(285, 120)
    ),
    # --- Lib/Room3 hallway bottom (starts: indx 19)
    Waypoint(
        position=(170, 150)
    ),
    Waypoint(
        position=(200, 150)
    ),
    Waypoint(
        position=(240, 150)
    ),
    Waypoint(  # cafe door
        position=(270, 150)
    ),
    Waypoint(
        position=(150, 150)
    ),
    # MR and WR hallway top/bottom (start: indx 24)
    Waypoint(
        position=(310, 120)
    ),
    Waypoint(
        position=(340, 120)
    ),
    Waypoint(
        position=(370, 120)
    ),
    Waypoint(
        position=(365, 150)
    ),
    Waypoint(
        position=(335, 150)
    ),
    Waypoint(
        position=(300, 150)
    ),
    # --- Rooms 1/2/3 left (starts: indx 30)
    Waypoint(
        position=(120, 170)
    ),
    Waypoint(
        position=(120, 200)
    ),
    Waypoint(
        position=(120, 235)
    ),
    Waypoint(
        position=(125, 260)
    ),
    Waypoint(
        position=(135, 270)
    ),
    # Rooms 1/2/3 hallway left (starts: indx 35)
    Waypoint(
        position=(150, 240)
    ),
    Waypoint(
        position=(150, 200)
    ),
    Waypoint(
        position=(150, 170)
    ),
    # --- Rooms 3/4 hallway bottom (starts: indx 38)
    Waypoint(
        position=(160, 270)
    ),
    Waypoint(  # room 4 door
        position=(180, 270)
    ),
    Waypoint(
        position=(220, 270)
    ),
    Waypoint(
        position=(270, 270)
    ),
    # --- Rooms 3/4 hallway top (starts: indx 42)
    Waypoint(
        position=(180, 250)
    ),
    Waypoint(
        position=(220, 250)
    ),
    Waypoint(
        position=(270, 250)
    ),
    # --- Right hallway North (starts: indx 45)
    Waypoint(
        position=(270, 170)
    ),
    Waypoint(
        position=(270, 195)
    ),
    Waypoint(
        position=(270, 220)
    ),
    Waypoint(
        position=(300, 170)
    ),
    Waypoint(
        position=(300, 195)
    ),
    Waypoint(
        position=(300, 220)
    ),
    Waypoint(
        position=(300, 240)
    ),
    Waypoint(
        position=(300, 270)
    ),
    # --- Right hallway South bottom (starts: 53)
    Waypoint(
        position=(270, 290)
    ),
    Waypoint(
        position=(270, 320)
    ),
    Waypoint(
        position=(275, 355)
    ),
    Waypoint(
        position=(270, 375)
    ),
    Waypoint(  # 57
        position=(300, 290)
    ),
    Waypoint(
        position=(300, 320)
    ),
    Waypoint(  # ISSUE: missing the path, covered by another wp
        position=(300, 320)
    ),
    Waypoint(
        position=(300, 360)
    ),
    # --- South hallway (starts: indx 61)
    Waypoint(
        position=(290, 380)
    ),
    Waypoint(
        position=(320, 380)
    ),
    Waypoint(
        position=(370, 380)
    ),
    Waypoint(
        position=(370, 360)
    ),
    Waypoint(
        position=(320, 360)
    ),
]

# rooms['building'].waypoints = hallway_nodes  # give the building access to all of the entry nodes
rooms['building'].add_waypoint(hallway_nodes)

# --- room waypoint definitions (specifically: entrances)
entryways = {}
for key, value in rooms.items():
    value.init_entrance()  # create entrance waypoint and keep ref in list of room's waypoints

# --- Edge definitions
# boiler plate for arthritis aversion
# Edge(hallway_nodes[], hallway_nodes[])
# --- office/library hallway
Edge(hallway_nodes[0], hallway_nodes[1])
Edge(hallway_nodes[1], hallway_nodes[2])
Edge(hallway_nodes[2], hallway_nodes[3])
Edge(hallway_nodes[4], hallway_nodes[0])
Edge(hallway_nodes[5], hallway_nodes[4])
Edge(hallway_nodes[6], hallway_nodes[5])
Edge(hallway_nodes[7], hallway_nodes[6])
Edge(hallway_nodes[7], hallway_nodes[3])
Edge(hallway_nodes[3], hallway_nodes[14])
Edge(hallway_nodes[3], hallway_nodes[23])
# --- North Closet hallway
Edge(hallway_nodes[3], hallway_nodes[8])
Edge(hallway_nodes[8], hallway_nodes[9])
Edge(hallway_nodes[9], hallway_nodes[10])
Edge(hallway_nodes[10], hallway_nodes[13], bi=True)  # add bi-directional just in case
Edge(hallway_nodes[13], hallway_nodes[12])
Edge(hallway_nodes[12], hallway_nodes[11])
Edge(hallway_nodes[11], hallway_nodes[14])
Edge(hallway_nodes[14], hallway_nodes[7])
Edge(hallway_nodes[14], hallway_nodes[23])
Edge(hallway_nodes[14], hallway_nodes[30])
# --- Lib/Room3 hallway
Edge(hallway_nodes[15], hallway_nodes[7])  # top run
Edge(hallway_nodes[16], hallway_nodes[15])
Edge(hallway_nodes[17], hallway_nodes[16])
Edge(hallway_nodes[18], hallway_nodes[17])
Edge(hallway_nodes[19], hallway_nodes[20])
Edge(hallway_nodes[20], hallway_nodes[21])
Edge(hallway_nodes[21], hallway_nodes[22])
Edge(hallway_nodes[18], hallway_nodes[22])
Edge(hallway_nodes[23], hallway_nodes[19])
Edge(hallway_nodes[23], hallway_nodes[7])
Edge(hallway_nodes[22], hallway_nodes[45])
# --- MR/WR hallway
Edge(hallway_nodes[22], hallway_nodes[29])
Edge(hallway_nodes[29], hallway_nodes[28])
Edge(hallway_nodes[28], hallway_nodes[27])
Edge(hallway_nodes[27], hallway_nodes[26])
Edge(hallway_nodes[26], hallway_nodes[25])
Edge(hallway_nodes[25], hallway_nodes[24])
Edge(hallway_nodes[29], hallway_nodes[18])
Edge(hallway_nodes[24], hallway_nodes[18])
# --- Rooms 1/2/3 hallway
Edge(hallway_nodes[30], hallway_nodes[31])
Edge(hallway_nodes[31], hallway_nodes[32])
Edge(hallway_nodes[32], hallway_nodes[33])
Edge(hallway_nodes[33], hallway_nodes[34])
Edge(hallway_nodes[34], hallway_nodes[35])
Edge(hallway_nodes[35], hallway_nodes[36])
Edge(hallway_nodes[36], hallway_nodes[37])
Edge(hallway_nodes[37], hallway_nodes[23])
Edge(hallway_nodes[34], hallway_nodes[38])
# --- Rooms 3/4 hallway
Edge(hallway_nodes[44], hallway_nodes[43])
Edge(hallway_nodes[43], hallway_nodes[42])
Edge(hallway_nodes[42], hallway_nodes[35])
Edge(hallway_nodes[42], hallway_nodes[34])
Edge(hallway_nodes[38], hallway_nodes[39])
Edge(hallway_nodes[39], hallway_nodes[34])
Edge(hallway_nodes[39], hallway_nodes[40])
Edge(hallway_nodes[40], hallway_nodes[41])
Edge(hallway_nodes[41], hallway_nodes[44])
Edge(hallway_nodes[39], hallway_nodes[42], bi=True)
Edge(hallway_nodes[41], hallway_nodes[51])
Edge(hallway_nodes[41], hallway_nodes[53])
# --- Right hallway North
Edge(hallway_nodes[52], hallway_nodes[51])
Edge(hallway_nodes[51], hallway_nodes[50])
Edge(hallway_nodes[50], hallway_nodes[49])
Edge(hallway_nodes[49], hallway_nodes[48])
Edge(hallway_nodes[48], hallway_nodes[29])
Edge(hallway_nodes[45], hallway_nodes[46])
Edge(hallway_nodes[46], hallway_nodes[47])
Edge(hallway_nodes[47], hallway_nodes[44])
Edge(hallway_nodes[52], hallway_nodes[44])
# --- Right hallway South
Edge(hallway_nodes[53], hallway_nodes[54])
Edge(hallway_nodes[54], hallway_nodes[55])
Edge(hallway_nodes[55], hallway_nodes[55])
Edge(hallway_nodes[55], hallway_nodes[56])
Edge(hallway_nodes[58], hallway_nodes[57])
Edge(hallway_nodes[59], hallway_nodes[57])
Edge(hallway_nodes[57], hallway_nodes[52])
Edge(hallway_nodes[55], hallway_nodes[58])
Edge(hallway_nodes[60], hallway_nodes[58])
Edge(hallway_nodes[60], hallway_nodes[59])
Edge(hallway_nodes[60], hallway_nodes[56], bi=True)
Edge(hallway_nodes[56], hallway_nodes[61])
Edge(hallway_nodes[55], hallway_nodes[61])
# --- Hallway South
Edge(hallway_nodes[61], hallway_nodes[62])
Edge(hallway_nodes[62], hallway_nodes[63])
Edge(hallway_nodes[63], hallway_nodes[64])
Edge(hallway_nodes[64], hallway_nodes[65])
Edge(hallway_nodes[65], hallway_nodes[60])

# Define door Edges for rooms w/ depth=2 (keep a ref so that it can be locked)
rooms['Reception'].add_edge(hallway_nodes[0])
rooms['Main Closet'].add_edge(hallway_nodes[2])
rooms['Closet North'].add_edge(hallway_nodes[13])
rooms['Library'].add_edge(hallway_nodes[6])
rooms['Cafe'].add_edge(hallway_nodes[18])
rooms['MR'].add_edge(hallway_nodes[28])
rooms['WR'].add_edge(hallway_nodes[27])
rooms['Room 1'].add_edge(hallway_nodes[31])
rooms['Room 2'].add_edge(hallway_nodes[32])
rooms['Room 3'].add_edge(hallway_nodes[36])
rooms['Room 4'].add_edge(hallway_nodes[39])
rooms['Gym'].add_edge(hallway_nodes[34])
rooms['Closet South'].add_edge(hallway_nodes[56])
rooms['SR'].add_edge(hallway_nodes[64])

# --- Create map objects

# create waypoints for map objects
wf1 = Waypoint(
    position=(380, 130)
)
Edge(wf1, hallway_nodes[26], bi=True)
Edge(wf1, hallway_nodes[27], bi=True)

mt1 = Waypoint(
    position=(315, 195)
)
Edge(mt1, rooms['MR'].entrance, bi=True)

# create actual map objects
map_objects = {
    'WF1': WF(
        rect=pygame.Rect((380, 125), (10, 10)),
        waypoint=wf1,
    ),
    'MT3': Tank(
        rect=pygame.Rect((334, 185), (16, 20))
    ),
    'MT2': Tank(
        rect=pygame.Rect((322, 185), (12, 20))
    ),
    'MT1': Tank(
        rect=pygame.Rect((310, 185), (12, 20))
    ),
    'HNG1': Hng(
        position=(385, 165)
    )
}

# send map objets to the event manager (to pass on to the game loop)
event_manager.map_objects = list(map_objects.values())

# define graphs for nested rooms (depth > 2)
# --- Library
temp_list = [
    Waypoint(
        position=(205, 30)
    ),
    Waypoint(
        position=(205, 60)
    ),
    Waypoint(
        position=(205, 90)
    )
]
rooms['Library'].add_waypoint(temp_list)
Edge(temp_list[0], temp_list[1], bi=True)
Edge(temp_list[1], temp_list[2], bi=True)
Edge(temp_list[2], rooms['Library'].entrance, bi=True)
rooms['Lib Office'].add_edge(temp_list[0])
rooms['Lib Closet'].add_edge(temp_list[1])
# --- Cafe
temp_list = [
    Waypoint(
        position=(350, 25)
    ),
    Waypoint(
        position=(330, 25)
    ),
]
rooms['Kitchen'].add_waypoint(temp_list[0])
rooms['Cafe'].add_waypoint(temp_list[1])
rooms['Fridge'].add_edge(temp_list[0])
Edge(temp_list[0], rooms['Kitchen'].entrance, bi=True)
rooms['Kitchen'].add_edge(temp_list[1])
Edge(temp_list[1], rooms['Cafe'].entrance, bi=True)
# --- Gym
temp_list = [
    Waypoint(  # office door
        position=(150, 375)
    ),
    Waypoint(  # ML door
        position=(90, 320)
    ),
    Waypoint(  # WL door
        position=(90, 350)
    ),
]
rooms['Gym'].add_waypoint(temp_list)
rooms['Gym Office'].add_edge(temp_list[0])
Edge(temp_list[0], rooms['Gym'].entrance, bi=True)
rooms['ML'].add_edge(temp_list[1])
Edge(temp_list[1], rooms['Gym'].entrance, bi=True)
rooms['WL'].add_edge(temp_list[2])
Edge(temp_list[2], rooms['Gym'].entrance, bi=True)

# define door edges for nested rooms (depth > 2)
rooms['Office'].add_edge(rooms['Reception'].entrance)
# rooms['ML'].add_edge(rooms['Gym'].entrance)
# rooms['WL'].add_edge(rooms['Gym'].entrance)
# rooms['Gym Office'].add_edge(rooms['Gym'].entrance)
rooms['Gym Closet'].add_edge(rooms['Gym Office'].entrance)
rooms['SR Closet'].add_edge(rooms['SR'].entrance)

# --- Define points of interest
rls = ['Reception', 'Main Closet', 'Closet North', 'Library', 'Cafe', 'MR', 'WR', 'Room 1', 'Room 2', 'Gym', 'Room 4',
       'Closet South', 'SR', 'Lib Office', 'Lib Closet', 'Kitchen', 'Fridge', 'Gym Office', 'ML', 'WL']
locations = [rooms[_].entrance for _ in rls]  # waypoints to all the finished rooms
# locations = [_ for _ in rooms.values() if _.entrance]

unlock_locations = [
    rooms['WR'].entrance
]

# map holding locations for ilding (in no particular order)
idle_locations = [
    IdleLocation(hallway_nodes[25]),
    IdleLocation(hallway_nodes[20]),
    IdleLocation(hallway_nodes[63]),

]

# Queue positions for tank events
mr_tank_queue = [
    vector(340, 180),
    vector(340, 175),
    vector(340, 170),
    vector(340, 165)
]
# # reverse the list since I put it in the wrong order
# mr_tank_queue.reverse()

# --- Create event regions
event_regions = [
    # --- UI Event Regions
    # MSY
    EventRegion(
        'MSY',
        rect=rooms['Kitchen'].rect,
    ),
    # SRL
    EventRegion(
        'SRL',
        rect=rooms['MR'].rect,
        obj=[map_objects['HNG1']]
    ),
    EventRegion(
        'SRL',
        rect=rooms['WR'].rect,
    ),
    # HNG
    EventRegion(
        'HNG',
        rect=rooms['MR'].rect,
    ),
    EventRegion(
        'HNG',
        rect=rooms['WR'].rect,
    ),
    EventRegion(
        'HNG',
        rect=rooms['SR Closet'].rect,
    ),
    EventRegion(
        'HNG',
        rect=rooms['Closet North'].rect,
    ),
    EventRegion(
        'HNG',
        rect=rooms['Closet South'].rect,
    ),
    EventRegion(
        'HNG',
        rect=rooms['Main Closet'].rect,
    ),
    EventRegion(
        'HNG',
        rect=rooms['ML'].rect,
    ),
    EventRegion(
        'HNG',
        rect=rooms['WL'].rect,
        obj=[map_objects['HNG1']],
    ),
    EventRegion(
        'HNG',
        rect=rooms['Gym Closet'].rect,
    ),
    EventRegion(
        'HNG',
        rect=rooms['Fridge'].rect,
    ),
    EventRegion(
        'HNG',
        rect=rooms['Lib Closet'].rect,
    ),
    # FNG
    EventRegion(
        'FNG',
        rect=rooms['MR'].rect,
    ),
    EventRegion(
        'FNG',
        rect=rooms['WR'].rect,
    ),
    EventRegion(
        'FNG',
        rect=rooms['SR Closet'].rect,
    ),
    EventRegion(
        'FNG',
        rect=rooms['Closet North'].rect,
    ),
    EventRegion(
        'FNG',
        rect=rooms['Closet South'].rect,
    ),
    EventRegion(
        'FNG',
        rect=rooms['Main Closet'].rect,
    ),
    EventRegion(
        'FNG',
        rect=rooms['ML'].rect,
    ),
    EventRegion(
        'FNG',
        rect=rooms['WL'].rect,
    ),
    EventRegion(
        'FNG',
        rect=rooms['Gym Closet'].rect,
    ),
    EventRegion(
        'FNG',
        rect=rooms['Fridge'].rect,
    ),
    EventRegion(
        'FNG',
        rect=rooms['Lib Closet'].rect,
    ),
    # --- Needs Event Regions
    EventRegion(
        'water',
        rect=pygame.Rect((380, 125), (10, 10)),
        obj=map_objects['WF1'],
    ),
    er_classes.TankEventRegion(
        'tank',
        room=rooms['MR'],
        items=[map_objects[_] for _ in ['MT1', 'MT2', 'MT3']],
        queue_positions=mr_tank_queue,
    )
]

if debug_graph:
    print(rooms['Gym'].waypoints)

# ----- deal with navmesh

# get location of vector on the navmesh
def get_navmesh_coordinate(v):
    dv = v / configs.navmesh_ratio
    out = tools.floor_vector(dv)
    return out

navmesh = np.zeros((int(configs.width / configs.navmesh_ratio), int(configs.height / configs.navmesh_ratio)))+1

# bake in the walls
for r in rooms.values():
    lo = get_navmesh_coordinate(tools.vector(r.rect.left, r.rect.top))
    hi = get_navmesh_coordinate(tools.vector(r.rect.right, r.rect.bottom))
    # top wall
    navmesh[lo.x:hi.x+1, lo.y] = np.zeros(1 + hi.x - lo.x)
    # bottom wall
    navmesh[lo.x:hi.x+1, hi.y] = np.zeros(1 + hi.x - lo.x)
    # left wall
    navmesh[lo.x, lo.y:hi.y+1] = np.zeros(1 + hi.y - lo.y)
    # right wall
    navmesh[hi.x, lo.y:hi.y+1] = np.zeros(1 + hi.y - lo.y)

# un-bake the doors
for key, r in rooms.items():
    if key == 'building':  # make sure to leave out the exit to the building
        continue
    hi = get_navmesh_coordinate(vector(r.entry_rect.right, r.entry_rect.bottom))
    lo = get_navmesh_coordinate(vector(r.entry_rect.left, r.entry_rect.top))
    # navmesh[r.entry_rect.left:r.entry_rect.right, r.entry_rect.top:r.entry_rect.bottom] = 1
    navmesh[lo.x:hi.x+1, lo.y:hi.y+1] = 1
    if debug_navmesh:
        print(key)
        print((r.entry_rect.left, r.entry_rect.right))
        print((r.entry_rect.top, r.entry_rect.bottom))
        print("---")

if debug_plot_navmesh:
    plt.imshow(np.transpose(navmesh), cmap='gray')
    plt.title("Navmesh")
    plt.show()

if debug_save_navmesh:
    np.save('Storage/navmesh.npy', navmesh)


# TODO: BROKEN, UNUSED, remove when ready
# calculate a path through the navmesh
def navmesh_path(start, end):
    """
    Get a path using the navmesh
    :param start: starting vector
    :param end: ending vector
    :return: list of vectors to follow
    """
    path = tools.a_star_navmesh(navmesh, start.as_tuple(), end.as_tuple())
    return [vector(p) for p in path]


# create the map object (compartmentalize any map based code in this script)
class Map(BaseObject):
    """
    Holds and draws all game objects if we want to
    """

    def __init__(self):
        super(Map, self).__init__()
        self.rooms = rooms
        self.navmesh = navmesh  # ref to the navmesh array

    def draw(self, screen):
        super().draw(screen)

        # draw all rooms
        if draw_rooms:
            for name, r in rooms.items():
                if r.depth > 1:
                    pygame.draw.rect(screen, configs.room_colors[r.depth - 1], r.rect)
                    pygame.draw.rect(screen, configs.entry_color, r.entry_rect)

        # draw all edges
        if draw_edges:
            for e in Edge.edges:
                e.draw(screen)

        # draw all waypoints
        if draw_waypoints:
            for wp in Waypoint.waypoints:
                wp.draw(screen)

    def check_next(self, current, pos):
        """
        Used to check if the player is colliding with a wall
        :param player: the player or actor who is moving
        :param pos: the next position they would like to move to
        :return: a bool for their movement in the x and y directions
        """
        player_room = self.get_room(current)  # figure out what room the player is in
        next_room = self.get_room(pos)  # get the next room
        if player_room is not None:  # if player is already in a room (Player should always be in a room)
            next_entry = next_room and next_room.entry_rect.collidepoint(current.as_tuple())
            player_entry = player_room.entry_rect.collidepoint(current.as_tuple())
            if next_entry or player_entry:  # if player is in entryway
                # if debug_collisions: print("In an entryway")
                return (True, True)  # give player full freedom

            else:  # check if both x and y are in the room
                if player_room == next_room:  # player is moving within the same room
                    return (True, True)  # allow full freedom
                else:  # player is trying to move into a different room
                    # out case (moving out of a nested room)
                    # if we don't have a next room, or current room is nested in next
                    if not next_room or player_room.depth >= next_room.depth:
                        out = (player_room.rect.left < pos.x < player_room.rect.right,
                               player_room.rect.top < pos.y < player_room.rect.bottom)
                    # in case (moving into a nested room)
                    else:  # move out of a nested room
                        out = (current.y < next_room.rect.top or current.y > next_room.rect.bottom,
                               current.x < next_room.rect.left or current.x > next_room.rect.right)
                if debug_collisions:
                    if not all(out):
                        print("In a room")
                        print(out)
                # return tuple for which directions are inside of the room
            return out
        else:  # player is not in a room (Should be impossible, leaving for compatability)
            next_room = self.get_room(pos)
            if next_room is None:  # if next point is not in a room
                # if debug_collisions: ("Out of room, into hallway")
                return (True, True)
            else:
                if next_room.entry_rect.collidepoint(current.as_tuple()):  # if player in the entryway
                    # if debug_collisions: ("Out of room, in entryway")
                    return (True, True)  # give player full freedom
                else:  # next point is moving illegally into a room return which points break the code
                    # return tuple for which directions we are allowed to move in
                    out = (current.y < next_room.rect.top or current.y > next_room.rect.bottom,
                           current.x < next_room.rect.left or current.x > next_room.rect.right)
                    if debug_collisions:
                        if not all(out):
                            print("In hallway, into room")
                            print(out)
                    # needed to flip x and y, makes sense if you think about it hard enough (
                    return out

    def into_rect(self, pos, rect):
        # return (rect.left < pos.x < rect.rigt,
        #         rect.top < pos.y < rect.bottom)
        return rect.left > pos.x > rect.right, rect.top > pos.y > rect.bottom

    def get_room(self, position):
        """
        Return the room with the highest depth for a given position
        :param position: position as type tools.vector
        :return: room.Room obj
        """
        p = position.as_tuple()
        out = None  # start with no room
        for r in rooms.values():
            if r.collidepoint(p):  # if position is in a room
                # if we don't have an out room or out's depth is higher than out's depth
                if not out or out.depth < r.depth:
                    out = r  # set return variable to new room
        return out

    def get_doorframe(self, position):
        """
        Loop through all doorframes to check if player is in an entrance
        Used for when player is holding an actor
        :param position: player position > tools.vector
        :return: room of the current entryway (None if not in an entryway)
        """
        p = position.as_tuple()
        for r in rooms.values():
            if r.entry_rect.collidepoint(p):
                return r
        return None

    def check_event(self, position, key):
        pos = position.as_tuple()  # get tuple of location to check

        for r in EventRegion.regions:  # loop through event regions
            if r.rect.collidepoint(pos):  # if we are in this region
                if r.key == key:  # if the key matches
                    return True  # return True

        return False  # return false if no matching EventRegion found

    def get_nearest_waypoint(self, position, waypoints=None):
        """
        Return the closest waypoint to a given position (searches within the current room's waypoints)
        :param position: position to check
        :param waypoints: list of waypoints to check (default: all waypoints in the current room)
        :return: Waypoint object
        """
        # use all created waypoints if not given a list to search through
        if not waypoints:
            waypoints = list(self.get_room(position).waypoints.values())

        # loop through waypoints to find the minimum
        mp = Waypoint.waypoints[0]
        md = vector.distance(mp.position, position)
        for wp in waypoints:
            d = vector.distance(wp.position, position)
            if d < md:
                md = d
                mp = wp

        return mp

    def can_see(self, pi, po):
        """
        Use the navmesh to check if two positions can see eachother
        :param pi: first position
        :param po: second position
        :return: bool for if positions can see eachother
        """
        n = int(max([(abs(int(pi.x - po.x + 1))), abs(int(pi.y - po.y + 1))]) * configs.can_see_multiplier)
        xl = np.linspace(pi.x, po.x, n)
        yl = np.linspace(pi.y, po.y, n)
        ps = [get_navmesh_coordinate(vector(x, y)) for x, y in zip(xl, yl)]  # all positions on the line

        return all([navmesh[v.x, v.y] for v in ps])


# initialize the map
game_map = Map()

