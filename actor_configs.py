"""
Used to store information for the creation of Actors
More for specific actor stats, not general behavior
  - To change generic behaviour, use configs.py
"""

class NameGenerator:

    def __init__(self):
        # names already used
        self.used = []

        # default names
        self.names = [
            'Inesea',  # 0
            'Whitney',
            'Caitlyn',
            'Caroline',
            'Monica',
            'Emma',  # 5
            'Mary',
            'Beth',
            'Valerie',
            'Amanda',
            'Sabrina',  # 10
            'Charli',
            'London',
            'Maddie',
            'Katrina',
            'Juliana',  # 15
            'Livvy',
            'Kody',
            'Sam',
            'Maggie',
            'Jax',  # 20
        ]

    def __call__(self, level):
        n = self.names[level]
        self.used += [n]
        if self.used.count(n) > 1:
            v = self.used.count(n)
            n += '_%i' % v
        return n

name_generator = NameGenerator()

armor_percentages = {
    # 'Name': (GRN, REG, THN')
    'Inesea': (100, 0, 0),  # 0
    'Whitney': (20, 80, 0),
    'Caitlyn': (100, 0, 0),
    'Caroline': (50, 50, 0),
    'Monica': (20, 70, 10),
    'Emma': (20, 80, 0),  # 5
    'Mary': (0, 0, 100),
    'Beth': (80, 0, 20),
    'Valerie': (20, 60, 20),
    'Amanda': (0, 100, 0),
    'Sabrina': (20, 80, 0),  # 10
    'Charli': (0, 0, 100),
    'London': (10, 50, 40),
    'Maddie': (0, 20, 80),
    'Katrina': (0, 50, 50),
    'Juliana': (100, 0, 0),  # 15
    'Livvy': (0, 0, 100),
    'Kody': (0, 80, 20),
    'Sam': (0, 20, 80),
    'Maggie': (0, 30, 70),
    'Jax': (100, 0, 0),  # 20
}

actor_stats = {
    'Inesea': (0, 0, 0, 0, 0),  # 0
    'Whitney': (0, 0, 0, 0, 1),
    'Caitlyn': (0, 0, 2, 0, 0),
    'Caroline': (0, 0, 0, 2, 0),
    'Monica': (0, 0, 2, 2, 0),
    'Emma': (0, 0, 3, 1, 1),  # 5
    'Mary': (0, 3, 2, 1, 0),
    'Beth': (1, 1, 4, 1, 0),
    'Valerie': (2, 2, 2, 2, 0),
    'Amanda': (3, 3, 0, 3, 0),
    'Sabrina': (1, 1, 5, 3, 0),  # 10
    'Charli': (2, 5, 2, 1, 1),
    'London': (2, 3, 3, 1, 2),
    'Maddie': (2, 5, 2, 3, 1),
    'Katrina': (2, 3, 4, 4, 1),
    'Juliana': (5, 5, 0, 4, 1),  # 15
    'Livvy': (3, 5, 2, 1, 5),
    'Kody': (2, 5, 3, 4, 3),
    'Sam': (5, 5, 2, 2, 4),
    'Maggie': (5, 5, 3, 1, 5),
    'Jax': (5, 5, 5, 5, 0),  # 20
}