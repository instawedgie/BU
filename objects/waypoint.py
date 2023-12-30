"""
Initial code for testing the waypoints
Absolutely not necessary anymore
"""

import configs
import tools

# import specific tools
from tools import vector

class Waypoint:

    def __init__(self, position, name='waypoint', paths = []):
        self.position = position
        self.name = name
        self.paths = paths


waypoint_offset = 10
waypoints = {
    'tl':Waypoint(
        name='tl',
        position=vector(
            x=waypoint_offset,
            y=waypoint_offset,
        )
    ),
    'tr':Waypoint(
        name='tr',
        position=vector(
            x=configs.width - waypoint_offset,
            y=waypoint_offset,
        )
    ),
    'bl':Waypoint(
        name='bl',
        position=vector(
            x=waypoint_offset,
            y=configs.height - waypoint_offset
        )
    ),
    'br':Waypoint(
        name='br',
        position=vector(
            x=configs.width - waypoint_offset,
            y=configs.height - waypoint_offset
        )
    )
}

# link the waypoints
waypoints['tl'].paths = [
    waypoints['tr'],
    waypoints['br']
]
waypoints['tr'].paths = [
    waypoints['tl'],
    waypoints['bl']
]
waypoints['bl'].paths = [
    waypoints['tr'],
    waypoints['br']
]
waypoints['br'].paths = [
    waypoints['bl'],
    waypoints['tl']
]