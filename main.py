import sys
from os import path

import dill as pick
import pygame as pg

import constants as c
import random as rd
from entities import MonsterFactory, EquipmentHelper, ItemHelper, DoorHelper, StairHelper, OpenableObjectHelper
from player import PlayerHelper
from settings import *
from tilemap import MapFactory, Camera, FieldOfView, Minimap
from utilities import Ticker, Publisher
from utilities_ui import TextBox, build_listing_dawnlike, build_listing_oryx
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


        # loading graphics
        # item_image_src = pg.image.load(path.join(image_folder, 'Item.png')).convert_alpha()
        # level_image_src = pg.image.load(path.join(image_folder, 'Level.png')).convert_alpha()
        # wall_image_src = pg.image.load(path.join(image_folder, 'Wall.png')).convert_alpha()
        #
        # self.all_images = {
        #     "PLAYER": {
        #         "E": load_image_list(IMG_FOLDER, 'HeroEast.png'),
        #         "W": load_image_list(IMG_FOLDER, 'HeroWest.png'),
        #         "N": load_image_list(IMG_FOLDER, 'HeroNorth.png'),
        #         "S": load_image_list(IMG_FOLDER, 'HeroSouth.png')},
        #     # ENEMIES
        #     "BAT": load_image_list(IMG_FOLDER, 'BatA.png'),
        #     "BEARD": load_image_list(IMG_FOLDER, 'BeardA.png'),
        #     "MONKEY": load_image_list_dawnlike(IMG_FOLDER, "Misc0.png", "Misc1.png", 2, 3),
        #     # NPC
        #     "DOG": load_image_list(IMG_FOLDER, 'DogA.png'),
        #     # ITEMS
        #     "REMAINS": load_image(IMG_FOLDER, item_image_src, 44, 2),
        #     "POTION_R": load_image(IMG_FOLDER, item_image_src, 1, 1),
        #     # EQUIPMENT
        #     "SWORD": load_image(IMG_FOLDER, item_image_src, 1, 16),
        #     "HELMET": load_image(IMG_FOLDER, item_image_src, 13, 16),
        #     "CAPE": load_image(IMG_FOLDER, item_image_src, 27, 17),
        #     "ARMOR": load_image(IMG_FOLDER, item_image_src, 14, 16),
        #     "LEG": load_image(IMG_FOLDER, item_image_src, 15, 16),
        #     "GLOVE": load_image(IMG_FOLDER, item_image_src, 16, 16),
        #     "SHOES": load_image(IMG_FOLDER, item_image_src, 17, 16),
        #     "SHIELD": load_image(IMG_FOLDER, item_image_src, 11, 13),
        #     "BOW": load_image(IMG_FOLDER, item_image_src, 11, 17),
        #     "ARROW": load_image(IMG_FOLDER, item_image_src, 21, 17),
        #     "RING": load_image(IMG_FOLDER, item_image_src, 1, 4),
        #     "NECKLACE": load_image(IMG_FOLDER, item_image_src, 1, 5),
        #     #
        #     "WALLS": load_wall_structure_dawnlike(wall_image_src),
        #     "FLOOR": [[load_image(IMG_FOLDER, level_image_src, x, y) for x in range(4)] for y in range(15)],
        #     "FLOOR_EXT": [[load_image(IMG_FOLDER, level_image_src, x, y) for x in range(4, 6)] for y in range(15)],
        #     "DOOR_V_OPEN": load_image(IMG_FOLDER, level_image_src, 15, 2),
        #     "DOOR_H_OPEN": load_image(IMG_FOLDER, level_image_src, 16, 2),
        #     "DOOR_CLOSED": load_image(IMG_FOLDER, level_image_src, 14, 2),
        #     "STAIRS": load_image(IMG_FOLDER, level_image_src, 13, 0),
        #     "FIREBALL": load_image(IMG_FOLDER, level_image_src, 42, 27),
        #     "SPECIAL_EFFECT": [load_image(IMG_FOLDER, level_image_src, x, 21) for x in range(4)]
        # }

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

        self.questionbox = None  # The question box will capture input from the player

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



        # place monsters
        MonsterFactory(self).build_list(25)

        all_pos = self.map.get_all_available_tiles(c.T_FLOOR, self.objects, without_objects=True)
        for i in range(200):
            ItemHelper(self, "Healing Potion"+str(i), all_pos.pop(), "POTION_R",
                       use_function=lambda player=self.player: ItemHelper.cast_heal(player))

            EquipmentHelper(self, "Sword", all_pos.pop(), "SWORD", slot=c.SLOT_HAND_RIGHT, modifiers={c.BONUS_STR: 2})
            EquipmentHelper(self, "Helmet", all_pos.pop(), "HELMET", slot=c.SLOT_HEAD, modifiers={c.BONUS_STR: -1})
        for i in range(200):
            OpenableObjectHelper(self, all_pos.pop(), "CHEST_CLOSED", "CHEST_OPEN_GOLD", name="Gold {}".format(i),
                                 use_function=OpenableObjectHelper.manipulate_treasure)
            OpenableObjectHelper(self, all_pos.pop(), "CHEST_CLOSED", "CHEST_OPEN_TRAP", name="Trap {}".format(i),
                             use_function=OpenableObjectHelper.manipulate_trap)
            OpenableObjectHelper(self, all_pos.pop(), "CHEST_CLOSED", "CHEST_OPEN_EMPTY", name="Empty {}".format(i),
                             use_function=OpenableObjectHelper.manipulate_empty)
            OpenableObjectHelper(self, all_pos.pop(), "COFFIN_CLOSED", "COFFIN_OPEN", name="Vampire {}".format(i),
                             use_function=OpenableObjectHelper.manipulate_vampire)
            # EquipmentHelper(self, "Cape", all_pos.pop(), "CAPE", slot=c.SLOT_CAPE, modifiers={})
            # EquipmentHelper(self, "Leg", all_pos.pop(), "LEG", slot=c.SLOT_LEG, modifiers={})
            # EquipmentHelper(self, "Armor", all_pos.pop(), "ARMOR", slot=c.SLOT_TORSO, modifiers={})

            # pos = self.map.get_random_available_tile(c.T_FLOOR)
            # item_component = Item(use_function=lambda player=self.player: Item.cast_heal(player))
            # item = GameObject(self, "HEALING POTION", pos[0], pos[1], self.items_img['Potion_R'], blocks=False,
            #                       item=item_component)

            # (x, y) = all_pos.pop()
            # Entity(self, "Sword", x, y, 'SWORD', blocks=False,
            #       equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_HAND_RIGHT, hit_bonus=4))
            # (x, y) = all_pos.pop()
            # Entity(self, "Helmet of fire", x, y, 'HELMET', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_HEAD, protection_bonus=2))
            # (x, y) = all_pos.pop()
            # Entity(self, "Cape of Truth", x, y, 'CAPE', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_CAPE, protection_bonus=1))
            # (x, y) = all_pos.pop()
            # Entity(self, "Leg of fire", x, y, 'LEG', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_LEG))
            # (x, y) = all_pos.pop()
            # Entity(self, "Armor", x, y, 'ARMOR', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_TORSO))
            # (x, y) = all_pos.pop()
            # Entity(self, "Glove", x, y, 'GLOVE', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_GLOVE))
            # (x, y) = all_pos.pop()
            # Entity(self, "Shoes", x, y, 'SHOES', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_FOOT))
            # (x, y) = all_pos.pop()
            # Entity(self, "Shield", x, y, 'SHIELD', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_HAND_LEFT, protection_bonus=2))
            # (x, y) = all_pos.pop()
            # Entity(self, "Bow", x, y, 'BOW', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_BOW, hit_bonus=1))
            # (x, y) = all_pos.pop()
            # Entity(self, "Arrow", x, y, 'ARROW', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_QUIVER, hit_bonus=1))
            # (x, y) = all_pos.pop()
            # Entity(self, "Ring", x, y, 'RING', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_RING, vision_bonus=1))
            # (x, y) = all_pos.pop()
            # Entity(self, "Necklace", x, y, 'NECKLACE', blocks=False,
            #        equipment=EquipmentEntity(slot=EquipmentEntity.SLOT_NECKLACE, vision_bonus=2))

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

    def place_object(self, level):
        """
        Setup all objects (enemies and items so far)
        :param level: the desired level
        :return:
        """
        all_pos = self.map.get_all_available_tiles(c.T_FLOOR, self.objects, without_objects=True)
        number_enemies = int(len(all_pos) / 50)
        for i in range(number_enemies):
            roll = rd.randint(0,100)
            if level == 1:
                if 0 < roll < 5:
                    pass

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
        MonsterFactory(self).build_list(30)

        all_pos = self.map.get_all_available_tiles(c.T_FLOOR, self.objects, without_objects=True)
        for i in range(200):
            EquipmentHelper(self, "Cape", all_pos.pop(), "CAPE", slot=c.SLOT_CAPE, modifiers={c.BONUS_STR: 2})
            EquipmentHelper(self, "Ring", all_pos.pop(), "RING", slot=c.SLOT_RING, modifiers={c.BONUS_STR: -1})

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
