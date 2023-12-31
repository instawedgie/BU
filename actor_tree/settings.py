"""
Used to configure behavior throughout the tree
"""

groups = [
    [2, 3, 4, 5],
    [0, 6, 7, 8],
    [11, 13, 14, 16],
    [9, 10, 15, 19],
    [12, 17, 18],
    [1, 20]
]

pairs = {
    17: 2,
    18: 3,
    19: 5,
    20: 4
}

leader = {
    16: [6, 7, 8],
    17: [2, 9, 11],
    18: [3, 14],
    19: [5, 13],
    20: [4, 10]
}

shield = {
    16: [11, 13, 14],
    17: [12],
    18: [12],
    19: [15],
    20: [1]
}

