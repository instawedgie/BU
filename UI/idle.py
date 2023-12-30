"""
Idle state of the interface
Goal is to display actor stats when clicked (can be to the console for now)
"""

import pygame
import tools
from tools import vector

from UI.base_state import BaseState
from Menu.base_menu import MenuButton
import configs

# get singletons
from event_manager import mouse, event_manager

debug = False
debug_afm = True

# define some stats
bar_width = configs.power_bar_width
bar_left = configs.width + ((configs.menu_width - bar_width) / 2)

# manage stats that contribute to level
stat_names = ['strength', 'finesse', 'endurance', 'toughness']


class Idle(BaseState):
    """
    State for when player is not engaged in any activity.
        - Shows player stats w/ ability to change them when no actor is selected
        - Select an actor by holding space and clicking on them
        - When actor is selected, shows more detailed information along w/ stats change section
    """

    def __init__(self):
        super(Idle, self).__init__()

        # manage settings
        self.font = configs.graph_font
        self.font_size = configs.graph_font_size

        # init variables
        self.actor = None
        self.stats = {
            'Pos': None,
            'Ctl': None,
            'Sus': None,
            'Lck': None,
            'Afm': None,
            'Tnk': None,
            'Fel': None,
            'Tou': None,
            'End': None,
            'Fin': None,
            'Str': None,
            'Lvl': None,
            'Arm': None,
            'Tsk': None,
            'Nme': None,
        }
        self.bars = {
            'strength': StatBar('strength', (configs.width + 10, 10)),
            'finesse': StatBar('finesse', (configs.width + 10, 30)),
            'endurance': StatBar('endurance', (configs.width + 10, 50)),
            'toughness': StatBar('toughness', (configs.width + 10, 70)),
        }
        # self.bars = {}
        self.rect_locs = {key: (configs.width + 10, configs.height - (self.font_size + 2) - (n * (self.font_size + 3)))
                          for n, key in enumerate(self.stats.keys())}

        # manage stats objects
        self.stat_text = {key: None for key in self.stats.keys()}  # init dict with all "None" items
        self.text_rects = {key: None for key in self.stats.keys()}  # init dict with all "None" items

        # manage bar displays
        self.armor_rect = pygame.Rect((bar_left, 0), (bar_width, 0))  # initialize w/ 0 height
        self.health_rect = pygame.Rect((bar_left, 0), (bar_width, 0))  # initialize w/ 0 height

        # Behaviour Tree display button
        self.bt_display = None

        # Calc values for text display
        self.k_len = max([len(tools.translator(_)) for _ in self.stats.keys()])

    def update(self, dt):
        super().update(dt)

        # manage getting the player stats
        if self.actor:  # if we have an actor to view
            if self.actor.event:
                task = self.actor.event.name
            else:
                task = None
            # update the dictionaries
            # TODO: ADD ANY NEW KEY TO THE INIT METHOD!!!!!!!!!!
            self.stats = {
                'Pos': self.actor.position,
                'Ctl': try_name(self.actor.control),
                'Sus': try_name(self.actor.suspension),
                'Lck': try_name(self.actor.lock),
                'Afm': [_.name for _ in self.actor.c_afm],
                # 'Afm': [_.name for _ in self.actor.afm],
                'Tnk': '%.3f' % (self.actor.tank / self.actor.tank_size),
                'Fel': ' %.3f' % self.actor.fuel,
                'Tou': self.actor.toughness,
                'End': self.actor.endurance,
                'Fin': self.actor.finesse,
                'Str': self.actor.strength,
                'Lvl': self.actor.level,
                'Arm': self.actor.armor.name,
                'Tsk': task,
                'Nme': self.actor.name,
            }
            for key, value in self.stats.items():  # loop through dict items to create the text objects
                self.stat_text[key] = self.font.render(  # make text object
                    # tools.translator(key) + ':    ' + tools.translator(str(value)),  # create the string
                    f'{tools.translator(key).ljust(self.k_len)} : {tools.translator(str(value))}',
                    True,  # anti alias (???)
                    configs.text_color,  # set the color
                )
            # create a DICT of key: text.rectangle
            self.text_rects = {value: value.get_rect(topleft=self.rect_locs[key])
                               for key, value in self.stat_text.items()}

            # update bars
            # manage actor health display
            health_height = self.actor.calc_health / 100 * configs.height
            health_top = configs.height - health_height
            self.health_rect = pygame.Rect((configs.width + (configs.menu_width * .75), health_top),
                                           (bar_width, health_height))

            # manage actor armor display
            armor_height = self.actor.armor.health / 100 * configs.height
            armor_top = configs.height - armor_height
            self.armor_rect = pygame.Rect((configs.width + (configs.menu_width * .5), armor_top),
                                          (bar_width, armor_height))

            # update stat bars
            for key, value in self.bars.items():
                r = value.update(self.actor.__dict__[key])  # figure out if we need to change it
                if -1 <= r + self.actor.__dict__[key] + r <= 6:
                    self.actor.__dict__[key] += r
                    self.actor.__dict__['level'] = sum(
                        [self.actor.__dict__[_] for _ in stat_names]
                    )

            # manage bt display button
            if mouse.buttons_down[1]:
                if self.bt_display.text_rect.collidepoint(mouse.position.x,
                                                          mouse.position.y):  # if mouse is colliding with rectangle
                    self.bt_display()  # call the button's function

        else:  # no actor, show own stats
            # update stat bars
            for key, value in self.bars.items():
                r = value.update(event_manager.player.__dict__[key])  # figure out if we need to change it
                if -1 <= r + event_manager.player.__dict__[key] + r <= 6:
                    event_manager.player.__dict__[key] += r
                    event_manager.player.__dict__['level'] = sum(
                        [event_manager.player.__dict__[_] for _ in stat_names]
                    )

    def draw(self, screen):
        super().draw(screen)  # default draw for game objects
        # draw the stats
        if self.actor:  # if we are viewing an actor
            # draw health line
            pygame.draw.rect(screen, configs.health_color, self.health_rect)
            # draw armor line
            pygame.draw.rect(screen, configs.armor_color, self.armor_rect)
            # render the bt button
            self.bt_display.draw(screen)
            # render the text
            for text, rect in self.text_rects.items():
                screen.blit(text, rect)

        # render the bars (either player or actor, should always be on)
        for name, button in self.bars.items():
            button.draw(screen)

    # debug function used to print actor stats to the console, unnecessary w/ the updated display
    def show_actor_stats(self, actor):
        print(actor.position)
        print(actor.destination.wp_name)
        print("Att: " + str(actor.att))
        print("Sus: " + str(actor.suspension))
        print("Lck: " + str(actor.lock))
        print("Afm: " + str(actor.afm))

    def set_actor(self, actor):
        """
        Used to set idle + recorders to watch a specific actor
        :param actor: actor to watch
        :return: None
        """
        self.actor = actor

        # setup display tree button (if we have an actor)
        if self.actor:
            # Set up new behaviour tree button to point to the correct actor
            self.bt_display = MenuButton('Show BT', (420, 90), self.actor.print_tree)
            # change color of the stat bar to the actor's color
            for i in self.bars.values():
                i.show_color = self.actor.color
        else:  # manage resetting display to self stats
            # change stat bar color to white
            for i in self.bars.values():
                i.show_color = (255, 255, 255)


        if 'actor' in list(event_manager.recorders.keys()):
            event_manager.recorders['actor'].set_actor(actor)


# try and get the name of an attack, return attack if it can't be found
def try_name(item):
    """
    Used to check if an object has a name, if not we just display the object
        - Useful to avoid errors in the display if game code is changed
        - The problem will be obvious in the display code if something goes wrong
    :param item: object to check for a name
    :return: Either object's name or the given argument
    """
    try:  # try and grab the name
        return item.name
    except:  # return the item if item.name fails
        return item


class StatBar:
    """
    Object Used to change a stat and display the current value
        - Displays at the top of the screen for the 4 attributes
    """

    def __init__(self, name, pos):
        """
        :param name: name of the stat
        :param pos: top left position of the stat bar
        """

        # TODO: Display the name above the stat bar
        # TODO: Add ability to change the show color of the bars

        # visual vars (just wanted to avoid hard coding)
        y_offset = 7
        x_space = 13
        x_offset = 2

        # set up initial variables
        self.name = name
        if not type(pos) == vector:
            self.pv = vector(pos)
            self.pos = pos
        else:
            self.pv = pos
            self.pos = self.pv.as_tuple()
        self.font = configs.graph_font
        self.font_size = configs.graph_font_size + 30

        self.show_color = (255, 255, 255)  # blue when showing
        self.hide_color = configs.menu_color  # menu color when hiding

        self.sub_button = MenuButton(' - ', (self.pv.x, self.pv.y + y_offset), lambda: 6, font=self.font)
        self.pos_button = MenuButton(' + ', (self.pv.x + x_space * 6, self.pv.y + y_offset), lambda: 6, font=self.font)

        self.buttons = [self.sub_button]
        self.colors = [False for i in range(5)]

        # set up bar display
        self.bars = [pygame.Rect(((self.pv.x + 10) + (x_space * _), self.pv.y),
                                 (x_space - x_offset, x_space - x_offset)) for _ in range(5)]

    def update(self, value):  # added *args in case we need dt eventually (shouldn't)

        # update the color scheme
        self.colors = [self.show_color if (lvl < value) else self.hide_color for lvl in range(5)]

        if mouse.buttons_down[1]:  # if mouse is left clicked
            for button in self.buttons:  # loop through all the buttons
                if button.text_rect.collidepoint(mouse.position.x,
                                                 mouse.position.y):  # if mouse is colliding with rectangle
                    button()  # call the button's function
        # check if up/down is clicked
        if mouse.buttons_down[1]:
            if self.sub_button.text_rect.collidepoint(mouse.position.x,
                                                      mouse.position.y):  # if mouse is colliding with rectangle
                if debug: print("Decrease " + self.name)
                return -1
            elif self.pos_button.text_rect.collidepoint(mouse.position.x,
                                                        mouse.position.y):  # if mouse is colliding with rectangle
                if debug: print("Increase " + self.name)
                return 1
            else:
                return 0
        else:
            return 0

    def draw(self, screen):

        # TODO: Draw text for name of the stat

        # draw +/- buttons
        self.sub_button.draw(screen)
        self.pos_button.draw(screen)

        # draw display boxes
        for color, box in zip(self.colors, self.bars):
            pygame.draw.rect(screen, color, box)
