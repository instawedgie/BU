"""
Used to show physical structures, especially ones that are used for events or actions
"""

from tools import vector

class MapObject:
    """
    Base class for map objects
    """

    def __init__(self, position):
        if not type(position) == vector:
            self.position = vector(position)
        else:
            self.position = position

    def draw(self, screen):
        pass

    def display(self):
        print("Displaying an object!")





