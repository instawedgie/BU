"""
Initial Bi-Directional Graph
Not in use anymore, currently use a more detailed graph that handles walking on different sides of the hall
"""

# import specific tools
from tools import vector

class Waypoint:

    def __init__(self, position, name='waypoint', paths=[]):
        self.position = position
        self.name = name
        self.paths = paths

waypoints = [
    Waypoint(
        name=0,
        position=vector(
            x=135,
            y=50
        )
    ),
    # mid-high
    Waypoint(
        name=1,
        position=vector(
            x=60,
            y=160
        )
    ),
    Waypoint(
        name=2,
        position=vector(
            x=135,
            y=160
        )
    ),
    Waypoint(
        name=3,
        position=vector(
            x=270,
            y=160
        )
    ),
    Waypoint(
        name=4,
        position=vector(
            x=360,
            y=160
        )
    ),
    # mid-low
    Waypoint(
        name=5,
        position=vector(
            x=40,
            y=270
        )
    ),
    Waypoint(
        name=6,
        position=vector(
            x=130,
            y=270
        )
    ),
    Waypoint(
        name=7,
        position=vector(
            x=265,
            y=270
        )
    ),
    # bottom
    Waypoint(
        name=8,
        position=vector(
            x=125,
            y=335
        )
    ),
    Waypoint(
        name=9,
        position=vector(
            x=270,
            y=310
        )
    ),
]

# link the waypoints
waypoints[0].paths = [
    waypoints[2]
]
waypoints[1].paths = [
    waypoints[2],
]
waypoints[2].paths = [
    waypoints[0],
    waypoints[1],
    waypoints[3],
    waypoints[6]
]
waypoints[3].paths = [
    waypoints[2],
    waypoints[4],
    waypoints[7]
]
waypoints[4].paths = [
    waypoints[3]
]
waypoints[5].paths = [
    waypoints[6]
]
waypoints[6].paths = [
    waypoints[2],
    waypoints[5],
    waypoints[7],
    waypoints[8]
]
waypoints[7].paths = [
    waypoints[3],
    waypoints[6],
    waypoints[9]
]
waypoints[8].paths = [
    waypoints[6]
]
waypoints[9].paths = [
    waypoints[7]
]

