import pygame

import configs
from tools import vector
from Mapping.objects.map_object import MapObject

debug = True


class Hng(MapObject):
    """
    Used for HGN and FNG UI events
    """
    color = (0, 0, 0)
    out_size = 3
    in_size = 1

    def draw(self, screen):
        super().draw(screen)

        pygame.draw.circle(screen, self.color, self.position.as_tuple(), self.out_size)
        pygame.draw.circle(screen, configs.background_color, self.position.as_tuple(), self.in_size)