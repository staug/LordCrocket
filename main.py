import sys
from os import path

import dill as pick
import pygame as pg

import constants as c
import random as rd
from entities import MonsterFactory, ItemFactory, EquipmentHelper, ItemHelper, DoorHelper, StairHelper, OpenableObjectHelper
from player import PlayerHelper
from settings import *
from tilemap import MapFactory, Camera, FieldOfView, Minimap
from utilities import Ticker, Publisher
from utilities_ui import TextBox, build_listing_dawnlike, build_listing_oryx, Button
from screen import CharacterScreen, PlayingScreen, InventoryScreen, MapScreen


class Game:

    def __init__(self):
        pg.display.init()
        pg.font.init()

        self.screen = pg.display.set_mode((GAME_WIDTH, GAME_HEIGHT), pg.RESIZABLE)
        pg.display.set_caption(GAME_TITLE + "-" + GAME_VER)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.playing = True

        self.load_data()

    def load_data(self):

        game_folder = path.dirname(__file__)
        image_folder = path.join(game_folder, IMG_FOLDER)
        assert IMG_STYLE in ("DAWNLIKE", "ORYX"), "Image style must be DAWNLIKE or ORYX"

        if IMG_STYLE == "DAWNLIKE":
            self.all_images = build_listing_dawnlike(image_folder)
        elif IMG_STYLE == "ORYX":
            self.all_images = build_listing_oryx(image_folder)

    def test(self, *args, **kwargs):
        print("Test {} {}".format(args, kwargs))
        for widget in self.widgets[:]:
            if widget.id == kwargs['widget']:
                self.widgets.remove(widget)

    def new(self):

        # Generic Game variables
        self.ticker = Ticker()
        self.bus = Publisher()
        self.game_state = c.GAME_STATE_PLAYING
        self.player_took_action = False
        self.minimap_enable = False
        self.objects = []
        self.level = 1

        # Loading fonts and initialize text system
        self.textbox = TextBox(self)
        self.textbox.text = "Welcome to the dungeon - {}".format(GAME_VER)

        self.widgets = []  # Any widget to be drawn on top...


        self.screens = {
            c.GAME_STATE_INVENTORY: InventoryScreen(self, c.GAME_STATE_PLAYING),
            c.GAME_STATE_MAP: MapScreen(self, c.GAME_STATE_PLAYING),
            c.GAME_STATE_CHARACTER: CharacterScreen(self, c.GAME_STATE_PLAYING),
            c.GAME_STATE_PLAYING: PlayingScreen(self, None)
        }

        # initializing map structure
        self.map = MapFactory("Map of the dead - Level {}".format(self.level), self.all_images).map
        self.minimap = Minimap(self)

        # Field of view
        self.fov = FieldOfView(self)

        # We have 5 sprites groups: two below the player, the player one and two above
        # They are drawn in the order below:
        self.player_min2_sprite_group = pg.sprite.Group()
        self.player_min1_sprite_group = pg.sprite.Group()
        self.player_sprite_group = pg.sprite.Group()  # the default group, also called level 0
        self.player_plus1_sprite_group = pg.sprite.Group()
        self.player_plus2_sprite_group = pg.sprite.Group()
        self.all_groups = [self.player_min2_sprite_group,
                           self.player_min1_sprite_group,
                           self.player_sprite_group,
                           self.player_plus1_sprite_group,
                           self.player_plus2_sprite_group]

        # Camera
        self.camera = Camera(self.map.tile_width * TILESIZE_SCREEN,
                             self.map.tile_height * TILESIZE_SCREEN)

        self.place_doors_stairs_traps(self.level)

        # Place player
        all_pos = self.map.get_all_available_tiles(c.T_FLOOR, self.objects, without_objects=True)
        self.player = PlayerHelper(self, all_pos.pop())
        self.visible_player_array = self.fov.get_vision_matrix_for(self.player, flag_explored=True)

        # place monsters and items
        ItemFactory(self).build_list(50)
        MonsterFactory(self).build_list(25)

        bt1 = Button((10, 10, 50, 20), None, font=pg.font.Font(None, 12), text="CLICK", id='A')
        bt1.command = lambda player=self.player, game=self: game.test(player=player, widget=bt1.id)
        bt2 = Button((10, 30, 50, 20), None, font=pg.font.Font(None, 12), text="CLICK2", id='B')
        bt2.command = lambda player=self.player, game=self: game.test(player=player, widget=bt2.id)
        self.widgets.append(bt1)
        self.widgets.append(bt2)

    def place_doors_stairs_traps(self, level):
        """
        This will place the basic objects: stairs, stairs and traps
        :param level: the current level
        :return: nothing
        """
        # place doors - except if we are in a pure maze
        pos_list = self.map.doors_pos[:]
        for pos in pos_list:
            DoorHelper(self, pos, ("DOOR_H_CLOSED", "DOOR_H_OPEN", "DOOR_V_CLOSED", "DOOR_V_OPEN"),
                       name="Door {}".format(pos),
                       open_function=DoorHelper.open_door)

        # Place stairs - Here we may have multiple.
        stair_pos = self.map.get_all_available_isolated_tiles(c.T_FLOOR, self.objects, without_objects=False)
        stairs_to_be_placed = 10 - level
        if len(stair_pos) > stairs_to_be_placed:
            for i in range(stairs_to_be_placed):
                StairHelper(self, stair_pos.pop(), "STAIRS", name="Stairs {}".format(i),
                            use_function=StairHelper.next_level)
        else:
            # Most probably we have far too many corridors - Maze like dungeon...
            print("Not found convenient way to place stairs - using second method")
            all_pos = self.map.get_all_available_tiles(c.T_FLOOR, self.objects, without_objects=True)
            for i in range(stairs_to_be_placed):
                StairHelper(self, all_pos.pop(), "STAIRS", name="Stairs {}".format(i),
                            use_function=StairHelper.next_level)

        # Traps: TODO

    def go_next_level(self):

        # First: cleanup!
        # Warning: we must act on a copy of the list!!!!!
        for entity in self.objects[:]:
            if entity != self.player:
                entity.remove_completely_object()
        print("Ticker now empty: {}".format(self.ticker.schedule))

        self.level += 1

        # initializing map structure
        self.map = MapFactory("Map of the dead - Level {}".format(self.level), self.all_images).map
        self.minimap = Minimap(self)

        # Field of view
        self.fov = FieldOfView(self)

        self.place_doors_stairs_traps(self.level)

        # Place player
        all_pos = self.map.get_all_available_tiles(c.T_FLOOR, self.objects, without_objects=True)
        new_player_pos = all_pos.pop()
        self.player.x = new_player_pos[0]
        self.player.y = new_player_pos[1]
        self.visible_player_array = self.fov.get_vision_matrix_for(self.player, flag_explored=True)
        self.player.invalidate_fog_of_war = True
        self.player_sprite_group.add(self.player)

        # Camera
        self.camera = Camera(self.map.tile_width * TILESIZE_SCREEN,
                             self.map.tile_height * TILESIZE_SCREEN)
        # place monsters
        ItemFactory(self).build_list(50)
        MonsterFactory(self).build_list(30)


    def load(self, filename="savegame"):
        with open(filename, "rb") as f:
            [self.objects, self.map, player_name, self.all_groups] = pick.load(f)
            self.map.game = self

            # Generic Game variables
            self.ticker = Ticker()
            self.game_state = c.GAME_STATE_PLAYING
            self.player_took_action = False
            self.minimap_enable = False

            self.inventory_screen = InventoryScreen(self, c.GAME_STATE_PLAYING)
            self.map_screen = MapScreen(self, c.GAME_STATE_PLAYING)
            self.playing_screen = PlayingScreen(self, None)
            self.character_screen = CharacterScreen(self, c.GAME_STATE_PLAYING)

            # initializing map structure
            self.minimap = Minimap(self)

            # Field of view
            self.fov = FieldOfView(self)

            # We have 5 sprites groups: two below the player, the player one and two above
            # They are drawn in the order below:
            [self.player_min2_sprite_group,
             self.player_min1_sprite_group,
             self.player_sprite_group,
             self.player_plus1_sprite_group,
             self.player_plus2_sprite_group] = self.all_groups

            # Camera
            self.camera = Camera(self.map.width, self.map.height)

            for entities in self.objects:
                entities.game = self
                entities.init_graphics()
                if entities.name == player_name:
                    self.player = entities
                    self.visible_player_array = self.fov.get_vision_matrix_for(self.player, flag_explored=True)
            for entities in self.player.inventory:
                entities.game = self
                entities.init_graphics(in_inventory=True)

    def run(self):
        # game loop - set self.playing = False to end the game
        while self.playing:
            self.screens[self.game_state].events()
            self.screens[self.game_state].update()
            self.screens[self.game_state].draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

if __name__ == '__main__':
    # create the game object
    g = Game()
    g.show_start_screen()
    while g.playing:
        g.new()
        # g.load()
        g.run()
    g.show_go_screen()
