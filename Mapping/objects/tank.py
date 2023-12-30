import pygame

import configs
from tools import vector
from Mapping.objects.map_object import MapObject

# debug variables
debug = True


class Tank(MapObject):
    width = 1

    def __init__(self, rect, door_rect=None):
        # display variables
        self.rect = rect
        self.position = vector(self.rect.center[0], self.rect.bottom - (int(configs.actor_size)))

        # manage door rect
        if not door_rect:
            self.door_rect = pygame.Rect((self.rect.left + (self.width), self.rect.top),
                                         (self.rect.width-(2*self.width), self.width))

        # behaviour variables
        self.user = None
        self.closed = False

    def draw(self, screen):
        # draw exterior
        pygame.draw.rect(screen, (0, 0, 0), self.rect, width=self.width)

        # draw door
        if not self.closed:
            pygame.draw.rect(screen, (255, 255, 255), self.door_rect)


