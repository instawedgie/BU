"""
Class definition of a waypoint
"""

import pygame

import configs
import tools

# behavior variables
maintain_edges = True  # keeps a list of all created edges (for drawing the graph)

# debug variables
debug_waypoint = False
debug_edge = False

class Waypoint:
    """
    Used as points of interest for NPC pathfinding.
     - Occasionally refer to it as a node when talking about it in comments
    """
    # automatically keep track of index of waypoint creation
    wp_index = 0  # track index of waypoints that are made
    waypoints = []  # keep list of waypoints (in case of emergency)  (should belong to the class, not the object)

    def __init__(self, position, paths=None, name=None):

        # handle different types of positions (turn all to tools.vector)
        if type(position) == list:
            position = tools.vector(position[0], position[1])
        if type(position) == tuple:
            position = tools.vector(position)

        # assign waypoint position (raise error if type is not a vector)
        assert type(position) == tools.vector, "Incorrect argument given for waypoint's position argument"
        self.position = position  # position of the waypoint

        self.index = self.wp_index  # index of waypoint in Waypoint.waypoints

        # ensures default argument is not mutable (avoids giving multiple waypoints the same path)
        if paths is None:  # if not given a path
            paths = []  # create a NEW empty list
        self.paths = paths  # create list of connected waypoints (usually start w/ empty list)

        if name is None:  # if we are not given a name
            self.name = 'wp_%02i' % self.wp_index  # name it after it's index
        else:  # if we are given a name
            self.name = name  # store the given name

        # generate we want to display when showing the graph
        t = "%03i" % self.index  # set the text to the waypoint zero-padded to 3 digits
        self.txt = configs.graph_font.render(str(t), True, configs.text_color)  # text object
        self.txtb = self.txt.get_rect(center=(self.position.x, self.position.y))  # rect of the text

        # manage class values
        Waypoint.wp_index += 1  # update index
        Waypoint.waypoints += [self]  # update list of all waypoints

    # write the index of the waypoint to the screen
    def draw(self, screen):
        screen.blit(self.txt, self.txtb)  # draw text to the screen


class Edge:
    """
    Used as a way to quickly add edges to our graph
    We can create the graph without using this class, however this is useful for creating certain types of connections
     - Namely, this allows us to lock doors for actors using the graph
     - Just making this to ensure that we have a way to keep track of all edges in the graph if deemed necessary
    """
    # keep track of the edges for drawing the list
    track = maintain_edges  # var to keep track of edges
    index = 0
    edges = []

    def __init__(self, node1, node2, bi=False):
        """
        Nodes to add to the list
        :param node1: Starting node
        :param node2: Ending node
        :param bi: Whether to make node bi-directional
        """
        node1.paths += [node2]  # append node 2 to the list of node 1's paths
        if bi:  # if node is bidirectional
            node2.paths += [node1]  # append node 1 to the list of node 2's paths

        # maintain references to the waypoints
        self.node1 = node1
        self.node2 = node2
        self.bi = bi
        self.enabled = True  # allow access to this edge

        # manage class values
        if Edge.track:
            Edge.index += 1  # update index
            Edge.edges += [self]  # update list of all edges

    # draw an arrow between waypoints
    def draw(self, screen):
        pygame.draw.line(screen, configs.edge_color, self.node1.position.as_pygame(), self.node2.position.as_pygame())

    # disable use of a node
    def disable_edge(self):
        if self.enabled:  # only if we currently have access
            if self.node2 in self.node1.paths:  # if the node we are looking for is in the list of paths
                self.node1.paths.remove(self.node2)  # remove node 2 from node 1's paths
            if self.bi and self.node1 in self.node2.paths:  # if bi edge and in eachother's paths
                self.node2.paths.remove(self.node1)  # remove node 1 from node 2's paths
        self.enabled = False

    # enable use of an edge
    def enable_edge(self):
        if self.node2 not in self.node1.paths:  # if node 2 is not already in the list of paths
            self.node1.paths += [self.node2]   # add node 2 to node 1's list of paths
        if self.bi and self.node1 not in self.node2.paths:  # if node 1 not already in list of paths
            self.node2.paths += [self.node1]  # add node 1 to node 2's list of paths


class IdleLocation:
    """
     - Used to manage locations for idling (groups possible)
     - Very important to have the NPCs manage adding/removing themselves to the waypoint upon enter/exit
     - Still need to add to the graph after creation
    """
    def __init__(self, waypoint, name=None):
        self.waypoint = waypoint
        self.position = waypoint.position
        self.paths = waypoint.paths

        # specific vars
        self.members = []

    def add_member(self, actor):
        """
        Add a member to this location IF they are not already in the list
        :param actor: member to add
        :return: None
        """
        if actor not in self.members:
            self.members += [actor]

    def remove_member(self, actor):
        """
        Remove a member to this location IF they are not already in the list
        :param actor: member to remove
        :return: None
        """
        if actor in self.members:
            self.members.remove(actor)




