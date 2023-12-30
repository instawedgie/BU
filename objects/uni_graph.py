"""
Current graph that we are using
Uses single directional edges to control the flow of traffic better
Should be updated to contain points inside of the rooms + doors
"""

import pygame

# import specific tools
import configs
from tools import vector
from objects.base_object import BaseObject

# debug variables
draw_rooms = False
debug_collisions = False

wp_name = 0


# this one should keep track of naming the waypoint manually
class Waypoint:
    wp_name = 0

    def __init__(self, position, paths=[]):
        self.position = position
        self.name = self.wp_name
        self.paths = paths
        Waypoint.wp_name += 1


waypoints = [
    # 0
    Waypoint(
        position=vector(
            x=120,
            y=40
        )
    ),
    Waypoint(
        position=vector(
            x=155,
            y=40
        )
    ),
    # 2
    Waypoint(
        position=vector(
            x=50,
            y=150
        )
    ),
    Waypoint(
        position=vector(
            x=125,
            y=145
        )
    ),
    Waypoint(
        position=vector(
            x=145,
            y=145
        )
    ),
    # 5
    Waypoint(
        position=vector(
            x=255,
            y=145
        )
    ),
    Waypoint(
        position=vector(
            x=280,
            y=145
        )
    ),
    Waypoint(
        position=vector(
            x=355,
            y=160
        )
    ),
    # 8
    Waypoint(
        position=vector(
            x=125,
            y=175
        )
    ),
    Waypoint(
        position=vector(
            x=140,
            y=170
        )
    ),
    # 10
    Waypoint(
        position=vector(
            x=260,
            y=175
        )
    ),
    Waypoint(
        position=vector(
            x=285,
            y=175
        )
    ),
    # 12
    Waypoint(
        position=vector(
            x=25,
            y=275
        )
    ),
    Waypoint(
        position=vector(
            x=120,
            y=265
        )
    ),
    Waypoint(
        position=vector(
            x=145,
            y=260
        )
    ),
    # 15
    Waypoint(
        position=vector(
            x=260,
            y=260
        )
    ),
    Waypoint(
        position=vector(
            x=280,
            y=260
        )
    ),
    # 17
    Waypoint(
        position=vector(
            x=120,
            y=280
        )
    ),
    Waypoint(
        position=vector(
            x=140,
            y=280
        )
    ),
    Waypoint(
        position=vector(
            x=255,
            y=285
        )
    ),
    Waypoint(
        position=vector(
            x=285,
            y=285
        )
    ),
    # 21
    Waypoint(
        position=vector(
            x=130,
            y=335
        )
    ),
    Waypoint(
        position=vector(
            x=270,
            y=315
        )
    ),
    # 23 (lock removal entry)
    Waypoint(
        position=vector(
            x=360,
            y=190
        )
    ),
    # (lock removal room)
    Waypoint(
        position=vector(
            x=360,
            y=215
        )
    ),
    # RM entry (25)
    Waypoint(
        position=vector(
            x=150,
            y=230
        )
    ),
    # RM Hallway (26)
    Waypoint(
        position=vector(
            x=140,
            y=230
        )
    )

]

# create links
waypoints[0].paths = [
    waypoints[3]
]
waypoints[1].paths = [
    waypoints[0],
]
waypoints[2].paths = [
    waypoints[8]
]
waypoints[3].paths = [
    waypoints[2],
    waypoints[8],
    waypoints[9]
]
waypoints[4].paths = [
    waypoints[1],
    waypoints[3],
    waypoints[8],
]
waypoints[5].paths = [
    waypoints[4],
]
waypoints[6].paths = [
    waypoints[5],
    waypoints[10]
]
waypoints[7].paths = [
    waypoints[6],
    waypoints[23]
]
waypoints[8].paths = [
    waypoints[4],
    waypoints[9],
    waypoints[13]
]
waypoints[9].paths = [
    waypoints[3],
    waypoints[4],
    waypoints[10]
]
waypoints[10].paths = [
    waypoints[6],
    waypoints[11],
    waypoints[15]
]
waypoints[11].paths = [
    waypoints[5],
    waypoints[6],
    waypoints[7]
]
waypoints[12].paths = [
    waypoints[17]
]
waypoints[13].paths = [
    waypoints[12],
    waypoints[17],
    waypoints[18],
]
waypoints[14].paths = [
    waypoints[26],
    waypoints[13],
    waypoints[17]
]
waypoints[15].paths = [
    waypoints[14],
    waypoints[19],
]
waypoints[16].paths = [
    waypoints[11],
    waypoints[15]
]
waypoints[17].paths = [
    waypoints[14],
    waypoints[18],
    waypoints[21]
]
waypoints[18].paths = [
    waypoints[13],
    waypoints[14],
    waypoints[19]
]
waypoints[19].paths = [
    waypoints[16],
    waypoints[22]
]
waypoints[20].paths = [
    waypoints[15],
    waypoints[16],
]
waypoints[21].paths = [
    waypoints[18]
]
waypoints[22].paths = [
    waypoints[20]
]
waypoints[23].paths = [
    waypoints[7],
    waypoints[24]
]
waypoints[24].paths = [
    waypoints[23]
]
waypoints[25].paths = [
    waypoints[26],
]
waypoints[26].paths = [
    waypoints[9],
    waypoints[13]
]

locations = [
    waypoints[0],
    waypoints[2],
    waypoints[6],
    waypoints[7],
    waypoints[12],
    waypoints[21],
    waypoints[22]
]

unlock_locations = [
    waypoints[24]
]


# manage rooms for NPC creation
class Room:
    """
    Used to manage leaving rooms if brought in by a player
    Can also be used to manage player->wall collisions
    """

    def __init__(self, rect, entrance, entry_width=configs.entry_size, entry_height=configs.entry_size):
        self.rect = rect  # boundaries of the room as a pygame.Rect
        self.waypoints = []  # contains no waypoints yet

        # manage the entrance waypoint
        self.entrance = entrance  # waypoint for the entryway

        # manage they entryway rect (for player)
        entry_size = (entry_width, entry_height)
        # top_corner = (self.entrance.position.x - (entry_width / 2), self.entrance.position.y + (entry_height / 2))
        self.entry_rect = pygame.Rect((0, 0), entry_size)  # init rectangle at 0, 0 for ease of use
        self.entry_rect.center = entrance.position.as_tuple()  # set center of rectangle to center of the waypoint


rooms = [
    Room(
        pygame.Rect((152, 192), ((243 - 150), (245 - 190))),
        waypoints[25],
    )
]


class Map(BaseObject):
    """
    Holds and draws all game objects if we want to
    """

    def __init__(self):
        super(Map, self).__init__()
        self.rooms = rooms

    def draw(self, screen):
        super().draw(screen)
        if draw_rooms:
            for r in rooms:
                pygame.draw.rect(screen, configs.room_color, r.rect)
                pygame.draw.rect(screen, configs.entry_color, r.entry_rect)

    def check_next(self, player, pos):
        """
        Used to check if the player is colliding with a wall
        :param player: the player or actor who is moving
        :param pos: the next position they would like to move to
        :return: a bool for their movement in the x and y directions
        """
        player_room = self.get_room(player.position)  # figure out what room the player is in
        if player_room is not None:  # if player is already in a room
            if player_room.entry_rect.collidepoint(player.position.as_tuple()):  # if player is in entryway
                # if debug_collisions: print("In an entryway")
                return (True, True)  # give player full freedom
            else:  # check if both x and y are in the room
                out = (player_room.rect.left < pos.x < player_room.rect.right,
                       player_room.rect.top < pos.y < player_room.rect.bottom)
                if debug_collisions:
                    if not all(out):
                        print("In a room")
                        print(out)
                # return tuple for which directions are inside of the room
                return out
        else:  # player is not in a room
            next_room = self.get_room(pos)
            if next_room is None:  # if next point is not in a room
                # if debug_collisions: ("Out of room, into hallway")
                return (True, True)
            else:
                if next_room.entry_rect.collidepoint(player.position.as_tuple()):  # if player in the entryway
                    # if debug_collisions: ("Out of room, in entryway")
                    return (True, True)  # give player full freedom
                else:  # next point is moving illegally into a room return which points break the code
                    # return tuple for which directions we are allowed to move in
                    out = (player.position.y < next_room.rect.top or player.position.y > next_room.rect.bottom,
                           player.position.x < next_room.rect.left or player.position.x > next_room.rect.right)
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
        p = position.as_tuple()
        for r in rooms:
            if r.rect.collidepoint(p):
                return r  # only return the first room that player collides with
        return None  # default to returning None if outside of a room


game_map = Map()
