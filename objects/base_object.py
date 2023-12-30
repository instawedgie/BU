"""
Base class for making game objects with standard update and draw functions
"""

class BaseObject:
    # define object from start
    def __init__(self):
        self.enabled = True  # allow for updates and rendering
        self.depth = 1000  # depth for order of rendering objects (unimplemented currently)

        self.name = None  # name used to help find it in a list of game objects

    # called each frame for computations
    def update(self, dt):
        pass

    # called each frame after object.update(dt)
    #   - intentionally left out dt to prevent heavy use, should mainly be used for observers / debug
    def late_update(self):
        pass

    # called each frame for rendering
    def draw(self, screen):
        pass