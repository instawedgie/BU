"""
Used to create an armor object that can handle it's own durability, damage, and breaking
"""

from dataclasses import dataclass
import copy

debug = True

@dataclass
class Armor:
    durability: float = 1  # rate of wear while taking damage
    strength: float = 1  # damage multiplier
    name: str = 'REG'
    health: int = 100  # starting health
    break_strength: float = 1.75  # absolute break strength
    threshold: float = .9  # min value to take damage
    break_damage: float = 20

    # default args
    broken = False

    def __post_init__(self):
        self.current_bs = self.break_strength

    def damage(self, value, dt):
        """
        Apply damage to the armor based on frame time and intensity
        :param value: intensity of attack (0 - 1)
        :param dt: time between frames
        :return: boolean for if damage is blocked
        """
        # non-broken armor
        if not self.broken:
            # account for health in max break strength
            self.current_bs = self.break_strength - ((self.break_strength - 1) * (1-((self.health / 100)**.5)))
            if value > self.current_bs:
                if debug: print("Break strength reached")
                self.ruin()
            elif value > self.threshold:
                # damage armor
                self.health -= (value - self.threshold) * (1 + (50*((1-(self.health / 100))**8))) * dt * (1 - self.durability) * 50
                # manage break condition
                if self.health < 0:
                    self.ruin()
            return True
            # return False if armor is broken
        else:
            return False

    def ruin(self):
        """
        Function call for breaking the armor (self.break wouldn't work)
        :return: None
        """
        self.broken = True
        self.health = 0
        self.name = "broken_" + self.name

armor_list = [
    Armor(
        name='GRN',
        health=100,  # full health
        durability=.95,  # nearly unbreaking
        strength=.8,  # slight protection
        break_damage=50,
        break_strength=2,
        threshold=1.2,
    ),
    Armor(
        name='REG',
        durability=.8,  # decently strong
        health=100,  # full health
        break_damage=40,
        threshold=.95,
    ),
    Armor(
        name='THN',
        health=100,  # fairly weak
        durability=.2,  # fairly light
        strength=2,  # double damage
        break_damage=20,
        break_strength=1.5,
        threshold=.85,
    )
]

armors = {_.name: _ for _ in armor_list}

def get_armor(name):
    """
    Used to return new armor objects (based on the versions defined ^)
    Useful to ease creation of new armor types dynamically without changing initial classes
    :param name: Name of the armor type
    :return: a new Armor object
    """
    return copy.deepcopy(armors[name])