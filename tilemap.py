import pygame as pg
from settings import *
import random
from os import path
import constants as c
import utilities as ut


class Tile:
    """
    A tile of the map and its properties
    """
    
    def __init__(self, tile_type=c.T_VOID, room=None):
        self.tile_type = tile_type
        self.explored = False
        self.room = room

    def block_for(self, entity):
        if entity.blocking_tile_list:
            if self.tile_type in entity.blocking_tile_list:
                return True
            else:
                return False
        elif self.tile_type in (c.T_VOID, c.T_WALL):
            return True
        return False

    def block_view_for(self, entity):
        if hasattr(entity, "blocking_view_tile_list"):
            if self.tile_type in entity.blocking_view_tile_list:
                return True
            else:
                return False
        elif self.tile_type in (c.T_VOID, c.T_WALL):
            return True
        return False


class Room:

    def __init__(self, size, position=None):
        """
        Initialize the room
        :param size: the size of the room (tuple)
        :param position: The upper left corner of the room (tuple)
        """
        self.size = size
        self.position = position
        self.name = Room._name_generator()
        self.doors = []
        self.connecting_room = []

    @staticmethod
    def _name_generator():
        room_name_part1 = ('Accursed', 'Ancient', 'Baneful', 'Batrachian', 'Black', 'Bloodstained', 'Cold', 'Dark',
                           'Devouring', 'Diabolical', 'Ebon', 'Eldritch', 'Forbidden', 'Forgotten', 'Haunted', 'Hidden',
                           'Lonely', 'Lost', 'Malevolent', 'Misplaced', 'Nameless', 'Ophidian', 'Scarlet', 'Secret',
                           'Shrouded', 'Squamous', 'Strange', 'Tenebrous', 'Uncanny', 'Unspeakable', 'Unvanquishable',
                           'Unwholesome', 'Vanishing', 'Weird')
        room_name_part2 = ('room', 'hall', 'place', 'pit', 'shamble',
                           'crossing', 'location', 'center', 'cavity', 'cell',
                           'hollow', 'alcove', 'antechamber', 'wherabouts')
        room_name_part3 = ('the Axolotl', 'Blood', 'Bones', 'Chaos', 'Curses', 'the Dead', 'Death', 'Demons', 'Despair',
                           'Deviltry', 'Doom', 'Evil', 'Fire', 'Frost', 'the 8 Geases', 'Gloom', 'Hells', 'Horrors',
                           'Ichor', 'Ice', 'Id Insinuation', 'the Idol', 'Iron', 'Madness', 'Mirrors', 'Mists',
                           'Monsters', 'Mystery', 'Necromancy', 'Oblivion', 'Peril', 'Phantasms', 'Random Harlots',
                           'Secrets', 'Shadows', 'Sigils', 'Skulls', 'Slaughter', 'Sorcery', 'Syzygy', 'Terror',
                           'Torment', 'Treasure', 'the Under City', 'the Underworld', 'the Unknown', 'Whispers')
        return "{} {} of {}".format(random.choice(room_name_part1),
                                    random.choice(room_name_part2),
                                    random.choice(room_name_part3))

    def get_tile_list(self):
        tiles = []
        (pos_x, pos_y) = self.position
        (size_x, size_y) = self.size
        for x in range(pos_x, pos_x + size_x):
            for y in range(pos_y, pos_y + size_y):
                tiles.append((x, y))
        return tiles


class MapFactory:
    """
    Used to generate one of the predefined map type
    """
    def __init__(self, name, graphical_resources,
                 seed=None, filename=None, dimension=(81, 121)):

        random.seed(seed)

        map_correctly_initialized = False
        self.map = None

        if filename is not None:
            self.map = FileMap(name, graphical_resources, filename)
        else:
            while not map_correctly_initialized:
                print(" *** GENERATING DUNGEON *** ")
                map_type = ut.roll(4)
                if map_type == 1:
                    self.map = CaveMap(name, graphical_resources, dimension)
                elif map_type == 2:
                    self.map = MazeMap(name, graphical_resources, dimension)
                elif map_type == 3:
                    self.map = RoomAndMazeMap(name, graphical_resources, dimension)
                else:
                    self.map = RoomMap(name, graphical_resources, dimension)
                all_size = int(dimension[0] * dimension[1])
                print("DUNGEON: Available Tile: {} Limit {}".format(
                    len(self.map.get_all_available_tiles(c.T_FLOOR, [], without_objects=True)),
                    all_size / 4
                ))
                map_correctly_initialized = \
                    len(self.map.get_all_available_tiles(c.T_FLOOR, [],
                                                         without_objects=True)) > all_size / 4
        # Make it a bit more beautiful
        self.map.remove_extra_walls()


class Map:
    """
    The Map, representing a level.
    Mainly holds a reference to a set of tiles, as well as dimensions.
    """
    def __init__(self, name, graphical_resources, dimension):

        self.graphical_resources = graphical_resources
        self.name = name
        self._background = None

        self.tile_width = dimension[0]  # width of map, expressed in tiles
        self.tile_height = dimension[1]  # height of map, expressed in tiles

        self.tiles = []
        self.rooms = []
        self._doors_pos = None

        self.wall_ref_number = random.randint(0, len(self.graphical_resources['WALLS']) - 1)  # we keep this as a ref for later
        # The following is a trick to adapt the graphics
        self._adapt_graphical_resources(graphical_resources)

    def _adapt_graphical_resources(self, graphical_resources):
        if IMG_STYLE == c.IM_STYLE_ORYX:
            graphical_resources["STAIRS"] = graphical_resources["STAIRS_LIST"][self.wall_ref_number]
            graphical_resources["DOOR_V_CLOSED"] = graphical_resources["DOOR_V_CLOSED_LIST"][self.wall_ref_number]
            graphical_resources["DOOR_H_CLOSED"] = graphical_resources["DOOR_H_CLOSED_LIST"][self.wall_ref_number]
            graphical_resources["DOOR_V_OPEN"] = graphical_resources["DOOR_V_OPEN_LIST"][self.wall_ref_number]
            graphical_resources["DOOR_H_OPEN"] = graphical_resources["DOOR_H_OPEN_LIST"][self.wall_ref_number]

    @property
    def background(self):
        if self._background is None:
            self._build_background()
        return self._background

    def clean_before_save(self):
        self._background = None
        self.graphical_resources = None

    def remove_extra_walls(self):
        """
        Generic method used by all to clean up after generation
        """
        for x in range(0, self.tile_width):
            for y in range(0, self.tile_height):
                if self.tiles[x][y].tile_type == c.T_WALL:
                    delta = [(0, -1), (0, 1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
                    count = 0
                    for (dx, dy) in delta:
                        if x + dx < 0 or x + dx >= self.tile_width or y + dy < 0 or y + dy >= self.tile_height:
                            count += 1
                        elif self.tiles[x + dx][y + dy].tile_type in (c.T_WALL, c.T_VOID):
                            count += 1
                    if count == 8:
                        self.tiles[x][y].tile_type = c.T_VOID

    def wall_weight(self, x, y, door_list, tile_type=c.T_WALL):
        """
        Taken from http://www.angryfishstudios.com/2011/04/adventures-in-bitmasking/
        :param x:
        :param y:
        :param door_list: current list of doors
        :param tile_type: the tyle type used as reference
        :return:
        """
        weight = 0
        if (y - 1 >= 0 and (self.tiles[x][y-1].tile_type == tile_type or (x, y-1) in door_list)) or y == 0:
            weight += 1
        if (x - 1 >= 0 and (self.tiles[x-1][y].tile_type == tile_type or (x - 1, y) in door_list)) or x == 0:
            weight += 8
        if (y+1 < self.tile_height and (self.tiles[x][y+1].tile_type == tile_type or (x, y+1) in door_list)) or\
                        y == self.tile_height - 1:
            weight += 4
        if (x+1 < self.tile_width and (self.tiles[x+1][y].tile_type == tile_type or (x + 1, y) in door_list)) or\
                        x == self.tile_width - 1:
            weight += 2
        return weight

    def get_random_available_tile(self, tile_type, game_objects, without_objects=True):
        """
        Return a tile matching the characteristics: given tile type
        Used to get a spawning position...
        By default, the tile should be without objects and out of any doors position
        :param tile_type: the type of tile that we look for
        :param without_objects: check if no objects is there, and that it is not a possible door position
        :param game_objects: the list of current objects in the game
        :return: a tile position (tuple)
        """
        entity_pos_listing = []

        if without_objects:
            for entity in game_objects:
                entity_pos_listing.append((entity.x, entity.y))

        while True:
            x = random.randint(0, self.tile_width - 1)
            y = random.randint(0, self.tile_height - 1)
            if self.tiles[x][y].tile_type == tile_type:
                if without_objects and ((x, y) not in entity_pos_listing and (x, y) not in self.doors_pos):
                    return x, y
                elif (x, y) not in self.doors_pos:
                    return x, y

    def get_close_available_tile(self, ref_pos, tile_type, game_objects, without_objects=True):
        """
        Return a tile matching the characteristics: given tile type near entity
        By default, the tile should be without objects and out of any doors position
        :param ref_pos: the ref position for the object
        :param tile_type: the type of tile that we look for
        :param without_objects: check if no objects is there, and that it is not a possible door position
        :param game_objects: the list of current objects in the game
        :return: a tile position (tuple) that matches free, the ref pos if none is found
        """
        entity_pos_listing = []

        if without_objects:
            for entity in game_objects:
                entity_pos_listing.append((entity.x, entity.y))

        delta = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        random.shuffle(delta)
        pos_x, pos_y = ref_pos

        for d in delta:
            x = pos_x + d[0]
            y = pos_y + d[1]
            if self.tiles[x][y].tile_type == tile_type:
                if without_objects and ((x, y) not in entity_pos_listing and (x, y) not in self.doors_pos):
                    return x, y
                elif (x, y) not in self.doors_pos:
                    return x, y
        return ref_pos


    @property
    def doors_pos(self):
        if self._doors_pos is None:
            self._doors_pos = []
            for room in self.rooms:
                for door in room.doors:
                    if door not in self._doors_pos:
                        self._doors_pos.append(door)
        return self._doors_pos

    def get_all_available_tiles(self, tile_type, game_objects, without_objects=False):
        """
        Return all tile matching the characteristics: given tile type
        Used to get a spawning position...
        :param tile_type: the type of tile that we look for
        :param without_objects: set to True to remove objects overlap
        :param game_objects: the list of current game objects
        :return: a list of tile positions (tuple)
        """
        listing = []
        entity_pos_listing = []

        if without_objects:
            for entity in game_objects:
                entity_pos_listing.append((entity.x, entity.y))

        for x in range(self.tile_width):
            for y in range(self.tile_height):
                if self.tiles[x][y].tile_type == tile_type:
                    if without_objects:
                        if (x, y) not in entity_pos_listing and (x, y) not in self.doors_pos:
                            listing.append((x, y))
                    else:
                        listing.append((x, y))
        random.shuffle(listing)
        return listing

    def get_all_available_isolated_tiles(self, tile_type, game_objects, without_objects=False, surrounded=7, max=None):
        """
        Return all tile matching the characteristics: given tile type, surrounded by 8 cells of same type
        Used to get a spawning position...
        :param tile_type: the type of tile that we look for
        :param without_objects: set to True to remove objects overlap
        :param game_objects: the list of current game objects
        :param surrounded: the number of tiles of same type that the tile should have around
        :return: a list of tile positions (tuple)
        """
        listing = self.get_all_available_tiles(tile_type, game_objects, without_objects=without_objects)
        result = []
        for pos in listing:
            x, y = pos
            v = 0
            for delta in [(-1, -1), (-1, 0), (-1, 1), (0, 1), (0, -1), (1, -1), (1, 0), (1, 1)]:
                dx, dy = delta
                if without_objects and (x + dx, y + dy) in listing:
                    v += 1
                elif 0 <= x + dx < self.tile_width and 0 <= y+dy < self.tile_height:
                    if self.tiles[x+dx][y+dy].tile_type == tile_type:
                        v += 1
                        if v >= surrounded:
                            break
            if v >= surrounded:
                result.append(pos)
                if max and len(result) >= max:
                    return result
        return result

    def get_room_at(self, x, y):
        if hasattr(self, "rooms"):
            for room in self.rooms:
                if (x, y) in room.get_tile_list():
                    return room
        return None

    def _build_background(self, name=None):
        """
        Build the image from the map.
        :param name: Optional filename to store the resulting file
        :return: Nothing
        """
        if self._background is None:
            self._background = pg.Surface((self.tile_width * TILESIZE_SCREEN,
                                           self.tile_height * TILESIZE_SCREEN))
            self._background.fill(BGCOLOR)
            if IMG_STYLE == c.IM_STYLE_DAWNLIKE:
                self._build_background_dawnlike()
            elif IMG_STYLE == c.IM_STYLE_ORYX:
                self._build_background_oryx()

            # complex_walls = type(self.graphical_resources['WALLS']) is list
            #
            # floor_serie = random.randint(0, len(self.graphical_resources['FLOOR']) - 1)
            #
            # wall_series = 0
            # if complex_walls:
            #     wall_series = random.randint(0, len(self.graphical_resources['WALLS']) - 1)
            #
            # for y in range(self.tile_height):
            #     for x in range(self.tile_width):
            #         if self.tiles[x][y].tile_type == c.T_FLOOR:
            #             if random.randint(0, 100) >= 85:
            #                 floor_image = random.randint(0, len(self.graphical_resources['FLOOR_EXT'][floor_serie]) - 1)
            #             else:
            #                 floor_image = random.randint(0, len(self.graphical_resources['FLOOR'][floor_serie]) - 1)
            #             self._background.blit(self.graphical_resources['FLOOR'][floor_serie][floor_image],
            #                                   (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
            #
            #         elif self.tiles[x][y].tile_type == c.T_WALL:
            #             if not complex_walls:
            #                 self._background.blit(self.graphical_resources['WALLS'],
            #                                       (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
            #             else:
            #                 # First, we copy an image of the floor to make it look better
            #                 floor_image = random.randint(0, len(self.graphical_resources['FLOOR'][floor_serie]) - 1)
            #                 self._background.blit(self.graphical_resources['FLOOR'][floor_serie][floor_image],
            #                                       (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
            #                 # Then the wall
            #                 door_list = []
            #                 # build door list - except if we are in a pure maze
            #                 if hasattr(self, "rooms") and self.rooms is not None:
            #                     for room in self.rooms:
            #                         for door_pos in room.doors:
            #                             door_list.append(door_pos)
            #                 weight = self.wall_weight(x, y, door_list)
            #                 self._background.blit(self.graphical_resources['WALLS'][wall_series][weight],
            #                                       (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))

        if name is not None:
            pg.image.save(self._background, path.dirname(__file__) + '/' + name)

    def _build_background_dawnlike(self):
        """
        Build background using dawnlike tileset
        :return: Nothing, just blitting things on _background property
        """
        # First, we choose our wall serie
        wall_series = random.randint(0, len(self.graphical_resources['WALLS']) - 1)
        floor_series = random.randint(0, len(self.graphical_resources['FLOOR']) - 1)

        for y in range(self.tile_height):
            for x in range(self.tile_width):

                door_list = []
                # build door list - except if we are in a pure maze
                if hasattr(self, "rooms") and self.rooms is not None:
                    for room in self.rooms:
                        for door_pos in room.doors:
                            door_list.append(door_pos)
                weight_wall = self.wall_weight(x, y, door_list)
                weight_floor = self.wall_weight(x, y, door_list, tile_type=c.T_FLOOR)

                if self.tiles[x][y].tile_type == c.T_WALL:
                    # We always blit a floor... but using the wall as reference for weight
                    self._background.blit(self.graphical_resources['FLOOR'][floor_series][weight_wall],
                                          (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                    self._background.blit(self.graphical_resources['WALLS'][wall_series][weight_wall],
                                          (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                elif self.tiles[x][y].tile_type == c.T_FLOOR:
                    self._background.blit(self.graphical_resources['FLOOR'][floor_series][weight_floor],
                                          (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))

    def _build_background_oryx(self):
        """
        Build background using oryx tileset
        :return: Nothing, just blitting things on _background property
        """
        # First, we choose our wall serie
        wall_series = floor_series = self.wall_ref_number
        type_floor = 0

        for y in range(self.tile_height):
            for x in range(self.tile_width):

                door_list = []
                # build door list - except if we are in a pure maze
                if hasattr(self, "rooms") and self.rooms is not None:
                    for room in self.rooms:
                        for door_pos in room.doors:
                            door_list.append(door_pos)
                weight_wall = self.wall_weight(x, y, door_list)
                weight_floor = self.wall_weight(x, y, door_list, tile_type=c.T_FLOOR)

                if self.tiles[x][y].tile_type == c.T_WALL:
                    # We always blit a floor... but using the wall as reference for weight
                    self._background.blit(self.graphical_resources['FLOOR'][floor_series][type_floor],
                                          (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                    self._background.blit(self.graphical_resources['WALLS'][wall_series][weight_wall],
                                          (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                elif self.tiles[x][y].tile_type == c.T_FLOOR:
                    other_floor = random.randint(0, 99)
                    _type_floor = type_floor
                    with_spider_web = False
                    if other_floor > 70:
                        _type_floor = other_floor % len(self.graphical_resources['FLOOR'][floor_series])
                    self._background.blit(self.graphical_resources['FLOOR'][floor_series][_type_floor],
                                          (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                    # Adding wall shadow on floor tile
                    if weight_floor in (0, 2, 4, 6, 8, 10, 12, 14):
                        self._background.blit(self.graphical_resources['WALLS_SHADOW'],
                                              (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                    if random.randint(0, 100) <= 20:
                        with_spider_web = True
                        # Adding spider web on floor tile if the wall is correct
                        if weight_floor == 6:
                            self._background.blit(self.graphical_resources['SPIDER_WEB_TOP_LEFT'],
                                                  (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                        elif weight_floor == 3:
                            self._background.blit(self.graphical_resources['SPIDER_WEB_BOTTOM_LEFT'],
                                                  (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                        elif weight_floor == 9:
                            self._background.blit(self.graphical_resources['SPIDER_WEB_BOTTOM_RIGHT'],
                                                  (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                        elif weight_floor == 12:
                            self._background.blit(self.graphical_resources['SPIDER_WEB_TOP_RIGHT'],
                                                  (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                    if not with_spider_web and random.randint(0, 100) <= 5:
                        self._background.blit(random.choice(self.graphical_resources['FLOOR_DECO_LIST']),
                                              (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))


class MazeMap(Map):
    """
    This represents a pure maze.
    Such a dungeon doesn't contain doors or rooms.
    """

    def __init__(self, name, graphical_resource, dimension, spareness=3):

        assert dimension[0] % 2 == 1 and dimension[1] % 2 == 1, "Maze dimensions must be odd"

        Map.__init__(self, name, graphical_resource, dimension)
        print(" MAZE: Initialization")

        # We use algorithm at http://www.brainycode.com/downloads/RandomDungeonGenerator.pdf
        # Starting with walls everywhere, and all not explored
        self.tiles = [[Tile(c.T_WALL)
                       for y in range(self.tile_height)]
                      for x in range(self.tile_width)]

        print(" MAZE: FLOOD")
        self._flood_maze(to_explore=(self.tile_width - 1) * (self.tile_height - 1) / 4)

        print(" MAZE: Remove dead End")
        # Now, we want to remove some dead end
        for i in range(spareness):
            for x in range(1, self.tile_width - 1):
                for y in range(1, self.tile_height - 1):
                    if self.tiles[x][y].tile_type == c.T_FLOOR:
                        delta = [(0, -1), (0, 1), (1, 0), (-1, 0)]
                        count = 0
                        for (dx, dy) in delta:
                            if self.tiles[x + dx][y + dy].tile_type == c.T_FLOOR:
                                count += 1
                        if count <= 1:
                            self.tiles[x][y].tile_type = c.T_WALL

    def _flood_maze(self, to_explore=0):
        # 2. We pick a random cell, and flag it explored. Demarrage sur un impair!
        found = False
        current_x = current_y = 0
        forbidden_tiles = []
        if hasattr(self, "rooms"):
            for room in self.rooms:
                forbidden_tiles = forbidden_tiles + room.get_tile_list()
        while not found:
            current_x = int(random.randint(0, self.tile_width) / 2)
            if current_x % 2 == 0:
                current_x += 1
            current_y = int(random.randint(0, self.tile_width) / 2)
            if current_y % 2 == 0:
                current_y += 1
            if not self.tiles[current_x][current_y].explored and not (current_x, current_y) in forbidden_tiles:
                self.tiles[current_x][current_y].explored = True
                found = True

        self.tiles[current_x][current_y].tile_type = c.T_FLOOR
        explored = [(current_x, current_y)]

        trials = 0
        while len(explored) < to_explore and trials < (self.tile_width * self.tile_height)/4:
            current_cell = self.tiles[current_x][current_y]
            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            # 3. We pick a random direction
            random.shuffle(directions)
            found = False
            (dir_x, dir_y) = (0, 0)

            while not found and len(directions) > 0:
                (dir_x, dir_y) = directions.pop()
                # 3A: we test if this new cell is valid and not explored
                if 0 < current_x + dir_x < self.tile_width and 0 < current_y + dir_y < self.tile_height:
                    if not self.tiles[current_x + dir_x][current_y + dir_y].explored:
                        if not (current_x + dir_x, current_y + dir_y) in forbidden_tiles:
                            found = True

            if found:
                # 4. we create a corridor
                self.tiles[current_x + int(dir_x / 2)][current_y + int(dir_y / 2)].tile_type = c.T_FLOOR
                current_x += dir_x
                current_y += dir_y
                self.tiles[current_x][current_y].tile_type = c.T_FLOOR
                self.tiles[current_x][current_y].explored = True
                explored.append((current_x, current_y))
            else:
                (current_x, current_y) = random.choice(explored)
            trials += 1

        for x in range(self.tile_width):
            for y in range(self.tile_height):
                self.tiles[x][y].explored = False


class _RoomExtension:

    def __init__(self):
        self.tiles = []
        self.tile_height = self.tile_width = 0
        assert 0, "Constructor should not be called"

    def _add_connected_room(self, room, list_connected, to_visit, already_visited):
        already_visited.append(room)

        for connection in room.connecting_room:
            if connection not in to_visit and connection not in already_visited:
                to_visit.append(connection)

        for room_to_visit in to_visit:
            if room_to_visit not in already_visited:
                self._add_connected_room(room_to_visit, list_connected, to_visit, already_visited)

        if room in to_visit:
            to_visit.remove(room)

    def _get_branching_position_direction(self, branching_room, except_dir=None):
        while True:
            # we consider pos = 0,0
            walls = {'N': [(x, 0) for x in range(1, branching_room.size[0] - 1)],
                     'S': [(x, branching_room.size[1] - 1) for x in range(1, branching_room.size[0] - 1)],
                     'W': [(0, y) for y in range(1, branching_room.size[1] - 1)],
                     'E': [(branching_room.size[0] - 1, y) for y in range(1, branching_room.size[1] - 1)]}
            valid_list = ['N', 'S', 'E', 'W']
            if except_dir is not None:
                for dir in except_dir:
                    if dir is not None:
                        valid_list.remove(dir)
            dir = random.choice(valid_list)
            target = random.choice(walls[dir])
            # We don't want doors next to doors...
            x = target[0] + branching_room.position[0]
            y = target[1] + branching_room.position[1]
            if dir in ('N', 'S'):
                if not (self.tiles[x - 1][y].tile_type == c.T_FLOOR or self.tiles[x + 1][y].tile_type == c.T_FLOOR):
                    return x, y, dir
            if dir in ('E', 'W'):
                if not (self.tiles[x][y-1].tile_type == c.T_FLOOR or self.tiles[x][y+1].tile_type == c.T_FLOOR):
                    return x, y, dir

    def _generate_room(self, min_size, max_size, modulo_rest=2):
        """
        Generate a room according to the criteria
        :param min_size: tuple with the minimum dimension
        :param max_size: tuple with the max dimension
        :param modulo_rest: put to 0 for even dimensions, 1 for odd
        :return:
        """
        size_x = random.randint(min_size[0], max_size[0])
        size_y = random.randint(min_size[1], max_size[1])
        if modulo_rest < 2:
            while size_x % 2 != modulo_rest:
                size_x = random.randint(min_size[0], max_size[0])
            while size_y % 2 != modulo_rest:
                size_y = random.randint(min_size[1], max_size[1])
        return Room((size_x, size_y))

    def _space_for_new_room(self, new_room_size, new_room_position, tiles_blocking=c.T_FLOOR):
        for y in range(new_room_position[1],
                       new_room_position[1] + new_room_size[1]):
            for x in range(new_room_position[0],
                           new_room_position[0] + new_room_size[0]):
                if x < 0 or x > self.tile_width - 1:
                    return False
                if y < 0 or y > self.tile_height - 1:
                    return False
                if self.tiles[x][y].tile_type in tiles_blocking:
                    return False
        return True

    def _place_room(self, room, grid_position):
        room.position = grid_position
        for y in range(grid_position[1], grid_position[1] + room.size[1]):
            for x in range(grid_position[0], grid_position[0] + room.size[0]):
                self.tiles[x][y].room = room
                if y in (grid_position[1], grid_position[1] + room.size[1] - 1) or \
                                x in (grid_position[0], grid_position[0] + room.size[0] - 1):
                    self.tiles[x][y].tile_type = c.T_WALL
                else:
                    self.tiles[x][y].tile_type = c.T_FLOOR


class RoomMap(Map, _RoomExtension):
    """
    A dungeon made of rooms, which are linked via straight corridors (or just rooms, depending on criteria)
    """
    def __init__(self, name, graphical_resource, dimension):

        assert dimension[0] % 2 == 1 and dimension[1] % 2 == 1, "Maze dimensions must be odd"

        Map.__init__(self, name, graphical_resource, dimension)
        print(" ROOM MAP: Initialization")
        room_size_range = ((6, 6), (9, 9))
        max_num_room = int(dimension[0]*dimension[1] / 81 * .9)

        self.tiles = [[Tile(c.T_VOID)
                       for y in range(self.tile_height)]
                      for x in range(self.tile_width)]

        # generate the dungeon
        self.rooms.append(self._generate_room(room_size_range[0], room_size_range[1]))
        self._place_room(self.rooms[-1],
                         (int(self.tile_width / 2 - (self.rooms[-1].size[0] / 2)),
                         int(self.tile_height / 2 - (self.rooms[-1].size[1] / 2))))

        for _ in range(self.tile_width * self.tile_height * 2):
            if len(self.rooms) == max_num_room:
                break
            branching_room = random.choice(self.rooms)
            choice_wall = self._get_branching_position_direction(branching_room)
            branching_pos = (choice_wall[0], choice_wall[1])
            branching_dir = choice_wall[2]
            new_room = self._generate_room(room_size_range[0], room_size_range[1])
            tunnel_length = random.choice((0, 2, 3, 5))

            if branching_dir == 'N':
                new_room_pos = (int(branching_pos[0] - (new_room.size[0] / 2)),
                                int(branching_pos[1] - new_room.size[1] + 1 - tunnel_length))
            elif branching_dir == 'E':
                new_room_pos = (int(branching_pos[0] + tunnel_length),
                                int(branching_pos[1] - (new_room.size[1] / 2)))
            elif branching_dir == 'S':
                new_room_pos = (int(branching_pos[0] - (new_room.size[0] / 2)),
                                int(branching_pos[1] + tunnel_length))
            elif branching_dir == 'W':
                new_room_pos = (int(branching_pos[0] - (new_room.size[0]) + 1 - tunnel_length),
                                int(branching_pos[1] - (new_room.size[1] / 2)))

            if self._space_for_new_room(new_room.size, new_room_pos):
                self._place_room(new_room, new_room_pos)
                self.rooms.append(new_room)
                # Now connecting room
                # No tunnel, easy case:
                new_room.doors.append(branching_pos)
                self.tiles[branching_pos[0]][branching_pos[1]].tile_type = c.T_FLOOR
                new_room.connecting_room.append(branching_room)
                branching_room.connecting_room.append(new_room)
                # We now place the tunnel
                if branching_dir == 'N':
                    for i in range(1, tunnel_length + 1):
                        self.tiles[branching_pos[0]][branching_pos[1] - i].tile_type = c.T_FLOOR
                        self.tiles[branching_pos[0] - 1][branching_pos[1] - i].tile_type = c.T_WALL
                        self.tiles[branching_pos[0] + 1][branching_pos[1] - i].tile_type = c.T_WALL
                    if tunnel_length >= 3:
                        branching_room.doors.append((branching_pos[0], branching_pos[1] - tunnel_length))
                elif branching_dir == 'E':
                    for i in range(1, tunnel_length + 1):
                        self.tiles[branching_pos[0] + i][branching_pos[1]].tile_type = c.T_FLOOR
                        self.tiles[branching_pos[0] + i][branching_pos[1] - 1].tile_type = c.T_WALL
                        self.tiles[branching_pos[0] + i][branching_pos[1] + 1].tile_type = c.T_WALL
                    if tunnel_length >= 3:
                        branching_room.doors.append((branching_pos[0] + tunnel_length, branching_pos[1]))
                elif branching_dir == 'S':
                    for i in range(1, tunnel_length + 1):
                        self.tiles[branching_pos[0]][branching_pos[1] + i].tile_type = c.T_FLOOR
                        self.tiles[branching_pos[0] - 1][branching_pos[1] + i].tile_type = c.T_WALL
                        self.tiles[branching_pos[0] + 1][branching_pos[1] + i].tile_type = c.T_WALL
                        if tunnel_length >= 3:
                            branching_room.doors.append((branching_pos[0], branching_pos[1] + tunnel_length))
                elif branching_dir == 'W':
                    for i in range(1, tunnel_length + 1):
                        self.tiles[branching_pos[0] - i][branching_pos[1]].tile_type = c.T_FLOOR
                        self.tiles[branching_pos[0] - i][branching_pos[1] - 1].tile_type = c.T_WALL
                        self.tiles[branching_pos[0] - i][branching_pos[1] + 1].tile_type = c.T_WALL
                    if tunnel_length >= 3:
                        branching_room.doors.append((branching_pos[0] - tunnel_length, branching_pos[1]))


class RoomAndMazeMap(Map, _RoomExtension):

    def __init__(self, name, graphical_resource, dimension):

        assert dimension[0] % 2 == 1 and dimension[1] % 2 == 1, "Maze dimensions must be odd"

        Map.__init__(self, name, graphical_resource, dimension)
        dungeon_ok = False

        while not dungeon_ok:
            print("DUNGEON MAZE: Initialization")
            dungeon_ok = True

            # We use algorithm at http://journal.stuffwithstuff.com/2014/12/21/rooms-and-mazes/
            self.tiles = [[Tile(c.T_WALL)
                           for y in range(self.tile_height)]
                          for x in range(self.tile_width)]

            # We place a bunch of room
            count_explored = 0
            for i in range(int(self.tile_width * self.tile_height / 2)):
                # We generate a room
                new_room = self._generate_room((5, 5), (17, 17), modulo_rest=1)
                pos = [random.randint(0, self.tile_width), random.randint(0, self.tile_height)]
                if pos[0] % 2 == 1:
                    pos[0] += 1
                if pos[1] % 2 == 1:
                    pos[1] += 1

                if self._space_for_new_room(new_room.size, pos):
                    self._place_room(new_room, pos)
                    self.rooms.append(new_room)
                    tile_list = new_room.get_tile_list()
                    for (x, y) in tile_list:
                        self.tiles[x][y].explored = True
                        count_explored += 1
            print("DUNGEON MAZE: Rooms placed")

            # Now we fill almost everything else with maze
            self._flood_maze(to_explore=(self.tile_width * self.tile_height - count_explored) / 4)
            print("DUNGEON MAZE: Maze in position")

            # We place at least one door per room
            for room in self.rooms:
                branching_dir_1 = self._place_door_in_dungeon_maze(room)
                # Add a 60% proba of second door
                if random.randint(0, 100) <= 60:
                    branching_dir_2 = self._place_door_in_dungeon_maze(room, except_dir=branching_dir_1)
                    # And a 25% more of a third door
                    if random.randint(0, 100) < 50:
                        self._place_door_in_dungeon_maze(room, except_dir=[branching_dir_1, branching_dir_2])

            print("DUNGEON MAZE: Doors in position")
            # Now we check if we have rooms that are not connected and we remove them:
            connected_external_list = []
            for room in self.rooms:
                room_tile_list = room.get_tile_list()
                for (x, y) in room.doors:
                    # which tile is external
                    delta = [(0, -1), (0, 1), (1, 0), (-1, 0)]
                    for (dx, dy) in delta:
                        if self.tiles[x + dx][y + dy].tile_type == c.T_FLOOR:
                            if self.tiles[x + dx][y + dy] not in room_tile_list:
                                if self.tiles[x + dx][y + dy].room is None:
                                    if room not in connected_external_list:
                                        connected_external_list.append(room)
                                else:
                                    other_room = self.tiles[x + dx][y + dy].room
                                    room.connecting_room.append(other_room)
                                    other_room.connecting_room.append(room)

            list_old_rooms = self.rooms[:]
            # Now let's recursively go from the connected group
            for room in connected_external_list:
                already_visited = []
                self._add_connected_room(room, connected_external_list, [], already_visited)
                for visited_room in already_visited:
                    if visited_room not in connected_external_list:
                        connected_external_list.append(visited_room)

            self.rooms = connected_external_list
            # At this point all the internal group that are connected via relays should be somewhere..

            print("DUNGEON MAZE: Non connected rooms flagged")
            for room in list_old_rooms:
                if room not in self.rooms:
                    # Erase the wall and floor
                    room_tile_list = room.get_tile_list()
                    for (x, y) in room_tile_list:
                        self.tiles[x][y].room = None
                        self.tiles[x][y].tile_type = c.T_WALL
            print("DUNGEON MAZE: Non connected rooms removed")

            # Now, we want to remove some dead end
            spareness = random.randint(1, 5)
            for i in range(spareness):
                for x in range(1, self.tile_width - 1):
                    for y in range(1, self.tile_height - 1):
                        if self.tiles[x][y].tile_type == c.T_FLOOR:
                            delta = [(0, -1), (0, 1), (1, 0), (-1, 0)]
                            count = 0
                            for (dx, dy) in delta:
                                if self.tiles[x + dx][y + dy].tile_type == c.T_FLOOR:
                                    count += 1
                            if count <= 1:
                                self.tiles[x][y].tile_type = c.T_WALL

            print("DUNGEON MAZE: Dead ends removed")

    def _flood_maze(self, to_explore=0):
        # 2. We pick a random cell, and flag it explored. Demarrage sur un impair!
        found = False
        current_x = current_y = 0
        forbidden_tiles = []
        if hasattr(self, "rooms"):
            for room in self.rooms:
                forbidden_tiles = forbidden_tiles + room.get_tile_list()
        while not found:
            current_x = int(random.randint(0, self.tile_width) / 2)
            if current_x % 2 == 0:
                current_x += 1
            current_y = int(random.randint(0, self.tile_width) / 2)
            if current_y % 2 == 0:
                current_y += 1
            if not self.tiles[current_x][current_y].explored and not (current_x, current_y) in forbidden_tiles:
                self.tiles[current_x][current_y].explored = True
                found = True

        self.tiles[current_x][current_y].tile_type = c.T_FLOOR
        explored = [(current_x, current_y)]

        trials = 0
        while len(explored) < to_explore and trials < (self.tile_width * self.tile_height)/4:

            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            # 3. We pick a random direction
            random.shuffle(directions)
            found = False
            (dir_x, dir_y) = (0, 0)

            while not found and len(directions) > 0:
                (dir_x, dir_y) = directions.pop()
                # 3A: we test if this new cell is valid and not explored
                if 0 < current_x + dir_x < self.tile_width and 0 < current_y + dir_y < self.tile_height:
                    if not self.tiles[current_x + dir_x][current_y + dir_y].explored:
                        if not (current_x + dir_x, current_y + dir_y) in forbidden_tiles:
                            found = True

            if found:
                # 4. we create a corridor
                self.tiles[current_x + int(dir_x / 2)][current_y + int(dir_y / 2)].tile_type = c.T_FLOOR
                current_x += dir_x
                current_y += dir_y
                self.tiles[current_x][current_y].tile_type = c.T_FLOOR
                self.tiles[current_x][current_y].explored = True
                explored.append((current_x, current_y))
            else:
                (current_x, current_y) = random.choice(explored)
            trials += 1

        for x in range(self.tile_width):
            for y in range(self.tile_height):
                self.tiles[x][y].explored = False

    def _place_door_in_dungeon_maze(self, room, except_dir=None):
        trials = 400
        while trials > 0:
            choice_wall = self._get_branching_position_direction(room, except_dir=except_dir)
            branching_pos = (choice_wall[0], choice_wall[1])
            branching_dir = choice_wall[2]  # 'N', 'S', 'E', 'W'
            # is this a valid door? Valid means it open in something that is in the grid
            delta = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
            after_door_pos_x = choice_wall[0] + delta[branching_dir][0]
            after_door_pos_y = choice_wall[1] + delta[branching_dir][1]
            if 0 <= after_door_pos_x < self.tile_width and 0 <= after_door_pos_y < self.tile_height:
                if self.tiles[after_door_pos_x][after_door_pos_y].tile_type == c.T_FLOOR:
                    room.doors.append(branching_pos)
                    self.tiles[branching_pos[0]][branching_pos[1]].tile_type = c.T_FLOOR
                    return branching_dir
            trials -= 1
        return None


class CaveMap(Map):
    """
    A cavelike dungeon
    """

    def __init__(self, name, graphical_resource, dimension):

        assert dimension[0] % 2 == 1 and dimension[1] % 2 == 1, "Maze dimensions must be odd"

        Map.__init__(self, name, graphical_resource, dimension)    # dimensions doivent être impair!

        self.tiles = [[Tile(c.T_FLOOR)
                       for y in range(self.tile_height)]
                      for x in range(self.tile_width)]

        # Initial Random Noise
        for y in range(self.tile_height):
            for x in range(self.tile_width):
                if x in [0, self.tile_width-1] or y in [0, self.tile_height-1] or random.randint(0, 100) <= 30:
                    self.tiles[x][y].tile_type = c.T_WALL

        for repeat in range(5):
            for y in range(1, self.tile_height - 1):
                for x in range(1, self.tile_width - 1):
                    count = self._count_wall_tile(x, y)
                    if count >= 5 or count <= 1:
                        self.tiles[x][y].tile_type = c.T_WALL
                    else:
                        self.tiles[x][y].tile_type = c.T_FLOOR

        for repeat in range(3):
            for y in range(1, self.tile_height - 1):
                for x in range(1, self.tile_width - 1):
                    count = self._count_wall_tile(x, y)
                    if count >= 5:
                        self.tiles[x][y].tile_type = c.T_WALL
                    else:
                        self.tiles[x][y].tile_type = c.T_FLOOR

    def _count_wall_tile(self, posx, posy):
        count = 0

        for x in [posx-1, posx, posx+1]:
            for y in [posy-1, posy, posy+1]:
                if self.tiles[x][y].tile_type == c.T_WALL:
                    count += 1

        return count


class FileMap(Map):
    """
    This is a hardoced dungeon, taken from a file definition.
    It should contain specific locations for NPC or monsters
    """

    def __init__(self, name, graphical_resource, filename):
        Map.__init__(self, name, graphical_resource, (1, 1))  # dimensions will be set after

        file_data = []
        with open(filename, 'rt') as f:
            for line in f:
                file_data.append(line.strip())

        self.tile_width = len(file_data[0])  # width of map, expressed in tiles
        self.tile_height = len(file_data)  # height of map, expressed in tiles

        self.tiles = [[Tile(c.T_FLOOR)
                       for y in range(self.tile_height)]
                      for x in range(self.tile_width)]

        # Parse the file
        for row, tiles in enumerate(file_data):
            for col, tile in enumerate(tiles):
                if tile == str(c.T_WALL):
                    self.tiles[col][row].tile_type = c.T_WALL
                elif tile == str(c.T_FLOOR):
                    self.tiles[col][row].tile_type = c.T_FLOOR
                else:
                    self.tiles[col][row].tile_type = c.T_VOID


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + int(PLAYABLE_WIDTH / 2)
        y = -target.rect.y + int(PLAYABLE_HEIGHT / 2)
        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # up
        x = max(-(self.width - PLAYABLE_WIDTH), x)
        y = max(-(self.height - PLAYABLE_HEIGHT), y)
        # and apply it to the camera rect
        self.camera = pg.Rect(x, y, self.width, self.height)

    def reverse(self, pos):
        """
        Return the pos in the original file from a position on the screen.
        Used for example to get the position following a mouse click
        """
        (screen_x, screen_y) = pos
        (cam_x, cam_y) = self.camera.topleft
        return screen_x - cam_x, screen_y - cam_y


class Minimap:

    def __init__(self, game):
        self.game = game
        self._background = None

    def build_background(self, zoom_factor=2):
        self._background = pg.Surface((self.game.map.tile_width * zoom_factor, self.game.map.tile_height * zoom_factor))
        backpixels = pg.PixelArray(self._background)
        for x in range(self.game.map.tile_width):
            for y in range(self.game.map.tile_height):
                if self.game.map.tiles[x][y].explored:
                    tile_type = self.game.map.tiles[x][y].tile_type
                    if tile_type == c.T_WALL:
                        backpixels[x*zoom_factor:x*zoom_factor+1, y*zoom_factor:y*zoom_factor+1] = RED
                    elif tile_type == c.T_FLOOR:
                        backpixels[x * zoom_factor:x * zoom_factor + 1, y * zoom_factor:y * zoom_factor + 1] = WHITE
        # Now we add a big cross at the player position
        if hasattr(self.game, "player"):
            pos_x = self.game.player.x
            pos_y = self.game.player.y
            backpixels[(pos_x - 1) * zoom_factor:(pos_x + 1) * zoom_factor + 1,
            pos_y * zoom_factor:pos_y * zoom_factor + 1] = GREEN
            backpixels[pos_x * zoom_factor:pos_x * zoom_factor + 1,
            (pos_y - 1) * zoom_factor:(pos_y + 1) * zoom_factor + 1] = GREEN

        self._background = backpixels.make_surface()
        return self._background

    @property
    def background(self):
        if self._background is None:
            return self.build_background()
        else:
            return self._background


class FieldOfView:
    RAYS = 360  # Should be 360!

    STEP = 3  # The step of for cycle. More = Faster, but large steps may
    # cause artifacts. Step 3 is great for radius 10.

    RAD = 5  # FOV radius.

    # Tables of precalculated values of sin(x / (180 / pi)) and cos(x / (180 / pi))

    SINTABLE = [
        0.00000, 0.01745, 0.03490, 0.05234, 0.06976, 0.08716, 0.10453,
        0.12187, 0.13917, 0.15643, 0.17365, 0.19081, 0.20791, 0.22495, 0.24192,
        0.25882, 0.27564, 0.29237, 0.30902, 0.32557, 0.34202, 0.35837, 0.37461,
        0.39073, 0.40674, 0.42262, 0.43837, 0.45399, 0.46947, 0.48481, 0.50000,
        0.51504, 0.52992, 0.54464, 0.55919, 0.57358, 0.58779, 0.60182, 0.61566,
        0.62932, 0.64279, 0.65606, 0.66913, 0.68200, 0.69466, 0.70711, 0.71934,
        0.73135, 0.74314, 0.75471, 0.76604, 0.77715, 0.78801, 0.79864, 0.80902,
        0.81915, 0.82904, 0.83867, 0.84805, 0.85717, 0.86603, 0.87462, 0.88295,
        0.89101, 0.89879, 0.90631, 0.91355, 0.92050, 0.92718, 0.93358, 0.93969,
        0.94552, 0.95106, 0.95630, 0.96126, 0.96593, 0.97030, 0.97437, 0.97815,
        0.98163, 0.98481, 0.98769, 0.99027, 0.99255, 0.99452, 0.99619, 0.99756,
        0.99863, 0.99939, 0.99985, 1.00000, 0.99985, 0.99939, 0.99863, 0.99756,
        0.99619, 0.99452, 0.99255, 0.99027, 0.98769, 0.98481, 0.98163, 0.97815,
        0.97437, 0.97030, 0.96593, 0.96126, 0.95630, 0.95106, 0.94552, 0.93969,
        0.93358, 0.92718, 0.92050, 0.91355, 0.90631, 0.89879, 0.89101, 0.88295,
        0.87462, 0.86603, 0.85717, 0.84805, 0.83867, 0.82904, 0.81915, 0.80902,
        0.79864, 0.78801, 0.77715, 0.76604, 0.75471, 0.74314, 0.73135, 0.71934,
        0.70711, 0.69466, 0.68200, 0.66913, 0.65606, 0.64279, 0.62932, 0.61566,
        0.60182, 0.58779, 0.57358, 0.55919, 0.54464, 0.52992, 0.51504, 0.50000,
        0.48481, 0.46947, 0.45399, 0.43837, 0.42262, 0.40674, 0.39073, 0.37461,
        0.35837, 0.34202, 0.32557, 0.30902, 0.29237, 0.27564, 0.25882, 0.24192,
        0.22495, 0.20791, 0.19081, 0.17365, 0.15643, 0.13917, 0.12187, 0.10453,
        0.08716, 0.06976, 0.05234, 0.03490, 0.01745, 0.00000, -0.01745, -0.03490,
        -0.05234, -0.06976, -0.08716, -0.10453, -0.12187, -0.13917, -0.15643,
        -0.17365, -0.19081, -0.20791, -0.22495, -0.24192, -0.25882, -0.27564,
        -0.29237, -0.30902, -0.32557, -0.34202, -0.35837, -0.37461, -0.39073,
        -0.40674, -0.42262, -0.43837, -0.45399, -0.46947, -0.48481, -0.50000,
        -0.51504, -0.52992, -0.54464, -0.55919, -0.57358, -0.58779, -0.60182,
        -0.61566, -0.62932, -0.64279, -0.65606, -0.66913, -0.68200, -0.69466,
        -0.70711, -0.71934, -0.73135, -0.74314, -0.75471, -0.76604, -0.77715,
        -0.78801, -0.79864, -0.80902, -0.81915, -0.82904, -0.83867, -0.84805,
        -0.85717, -0.86603, -0.87462, -0.88295, -0.89101, -0.89879, -0.90631,
        -0.91355, -0.92050, -0.92718, -0.93358, -0.93969, -0.94552, -0.95106,
        -0.95630, -0.96126, -0.96593, -0.97030, -0.97437, -0.97815, -0.98163,
        -0.98481, -0.98769, -0.99027, -0.99255, -0.99452, -0.99619, -0.99756,
        -0.99863, -0.99939, -0.99985, -1.00000, -0.99985, -0.99939, -0.99863,
        -0.99756, -0.99619, -0.99452, -0.99255, -0.99027, -0.98769, -0.98481,
        -0.98163, -0.97815, -0.97437, -0.97030, -0.96593, -0.96126, -0.95630,
        -0.95106, -0.94552, -0.93969, -0.93358, -0.92718, -0.92050, -0.91355,
        -0.90631, -0.89879, -0.89101, -0.88295, -0.87462, -0.86603, -0.85717,
        -0.84805, -0.83867, -0.82904, -0.81915, -0.80902, -0.79864, -0.78801,
        -0.77715, -0.76604, -0.75471, -0.74314, -0.73135, -0.71934, -0.70711,
        -0.69466, -0.68200, -0.66913, -0.65606, -0.64279, -0.62932, -0.61566,
        -0.60182, -0.58779, -0.57358, -0.55919, -0.54464, -0.52992, -0.51504,
        -0.50000, -0.48481, -0.46947, -0.45399, -0.43837, -0.42262, -0.40674,
        -0.39073, -0.37461, -0.35837, -0.34202, -0.32557, -0.30902, -0.29237,
        -0.27564, -0.25882, -0.24192, -0.22495, -0.20791, -0.19081, -0.17365,
        -0.15643, -0.13917, -0.12187, -0.10453, -0.08716, -0.06976, -0.05234,
        -0.03490, -0.01745, -0.00000
    ]

    COSTABLE = [
        1.00000, 0.99985, 0.99939, 0.99863, 0.99756, 0.99619, 0.99452,
        0.99255, 0.99027, 0.98769, 0.98481, 0.98163, 0.97815, 0.97437, 0.97030,
        0.96593, 0.96126, 0.95630, 0.95106, 0.94552, 0.93969, 0.93358, 0.92718,
        0.92050, 0.91355, 0.90631, 0.89879, 0.89101, 0.88295, 0.87462, 0.86603,
        0.85717, 0.84805, 0.83867, 0.82904, 0.81915, 0.80902, 0.79864, 0.78801,
        0.77715, 0.76604, 0.75471, 0.74314, 0.73135, 0.71934, 0.70711, 0.69466,
        0.68200, 0.66913, 0.65606, 0.64279, 0.62932, 0.61566, 0.60182, 0.58779,
        0.57358, 0.55919, 0.54464, 0.52992, 0.51504, 0.50000, 0.48481, 0.46947,
        0.45399, 0.43837, 0.42262, 0.40674, 0.39073, 0.37461, 0.35837, 0.34202,
        0.32557, 0.30902, 0.29237, 0.27564, 0.25882, 0.24192, 0.22495, 0.20791,
        0.19081, 0.17365, 0.15643, 0.13917, 0.12187, 0.10453, 0.08716, 0.06976,
        0.05234, 0.03490, 0.01745, 0.00000, -0.01745, -0.03490, -0.05234, -0.06976,
        -0.08716, -0.10453, -0.12187, -0.13917, -0.15643, -0.17365, -0.19081,
        -0.20791, -0.22495, -0.24192, -0.25882, -0.27564, -0.29237, -0.30902,
        -0.32557, -0.34202, -0.35837, -0.37461, -0.39073, -0.40674, -0.42262,
        -0.43837, -0.45399, -0.46947, -0.48481, -0.50000, -0.51504, -0.52992,
        -0.54464, -0.55919, -0.57358, -0.58779, -0.60182, -0.61566, -0.62932,
        -0.64279, -0.65606, -0.66913, -0.68200, -0.69466, -0.70711, -0.71934,
        -0.73135, -0.74314, -0.75471, -0.76604, -0.77715, -0.78801, -0.79864,
        -0.80902, -0.81915, -0.82904, -0.83867, -0.84805, -0.85717, -0.86603,
        -0.87462, -0.88295, -0.89101, -0.89879, -0.90631, -0.91355, -0.92050,
        -0.92718, -0.93358, -0.93969, -0.94552, -0.95106, -0.95630, -0.96126,
        -0.96593, -0.97030, -0.97437, -0.97815, -0.98163, -0.98481, -0.98769,
        -0.99027, -0.99255, -0.99452, -0.99619, -0.99756, -0.99863, -0.99939,
        -0.99985, -1.00000, -0.99985, -0.99939, -0.99863, -0.99756, -0.99619,
        -0.99452, -0.99255, -0.99027, -0.98769, -0.98481, -0.98163, -0.97815,
        -0.97437, -0.97030, -0.96593, -0.96126, -0.95630, -0.95106, -0.94552,
        -0.93969, -0.93358, -0.92718, -0.92050, -0.91355, -0.90631, -0.89879,
        -0.89101, -0.88295, -0.87462, -0.86603, -0.85717, -0.84805, -0.83867,
        -0.82904, -0.81915, -0.80902, -0.79864, -0.78801, -0.77715, -0.76604,
        -0.75471, -0.74314, -0.73135, -0.71934, -0.70711, -0.69466, -0.68200,
        -0.66913, -0.65606, -0.64279, -0.62932, -0.61566, -0.60182, -0.58779,
        -0.57358, -0.55919, -0.54464, -0.52992, -0.51504, -0.50000, -0.48481,
        -0.46947, -0.45399, -0.43837, -0.42262, -0.40674, -0.39073, -0.37461,
        -0.35837, -0.34202, -0.32557, -0.30902, -0.29237, -0.27564, -0.25882,
        -0.24192, -0.22495, -0.20791, -0.19081, -0.17365, -0.15643, -0.13917,
        -0.12187, -0.10453, -0.08716, -0.06976, -0.05234, -0.03490, -0.01745,
        -0.00000, 0.01745, 0.03490, 0.05234, 0.06976, 0.08716, 0.10453, 0.12187,
        0.13917, 0.15643, 0.17365, 0.19081, 0.20791, 0.22495, 0.24192, 0.25882,
        0.27564, 0.29237, 0.30902, 0.32557, 0.34202, 0.35837, 0.37461, 0.39073,
        0.40674, 0.42262, 0.43837, 0.45399, 0.46947, 0.48481, 0.50000, 0.51504,
        0.52992, 0.54464, 0.55919, 0.57358, 0.58779, 0.60182, 0.61566, 0.62932,
        0.64279, 0.65606, 0.66913, 0.68200, 0.69466, 0.70711, 0.71934, 0.73135,
        0.74314, 0.75471, 0.76604, 0.77715, 0.78801, 0.79864, 0.80902, 0.81915,
        0.82904, 0.83867, 0.84805, 0.85717, 0.86603, 0.87462, 0.88295, 0.89101,
        0.89879, 0.90631, 0.91355, 0.92050, 0.92718, 0.93358, 0.93969, 0.94552,
        0.95106, 0.95630, 0.96126, 0.96593, 0.97030, 0.97437, 0.97815, 0.98163,
        0.98481, 0.98769, 0.99027, 0.99255, 0.99452, 0.99619, 0.99756, 0.99863,
        0.99939, 0.99985, 1.00000
    ]

    def __init__(self, game):
        self.game = game
        self._ready = False
        self.fov = []

    def reset(self):
        self.fov = [[False for y in range(self.game.map.tile_height)] for x in range(self.game.map.tile_width)]
        self._ready = True

    def get_vision_matrix_for(self, entity, radius=None, flag_explored=False, ignore_entity_at=None):
        """
        The Field of View algo
        :param entity: the entity for which the algo is done
        :param radius: the number of tiles the user can go throught
        :param flag_explored: any unexplored tile will become explored (good for player, but not NPC)
        :param ignore_entity_at: will ignore any entity at positions (like player) - this is a list
        :return: the Field of view, with True for each tile that is visible
        """
        if not self._ready:
            self.reset()
        if radius is None:
            if hasattr(entity, "fighter"):
                radius = entity.vision

        # It works like this:
        # It starts at entity coordinates and cast 360 rays
        # (if step is 1, less is step is more than 1) in every direction,
        # until it hits a wall.
        # When ray hits floor, it is set as visible.

        # Ray is casted by adding to x (initialy it is player's x coord)
        # value of sin(i degrees) and to y (player's y) value of cos(i degrees),
        # RAD times, and checking for collision with wall every step.

        # First: the entity itself is visible!
        self.fov[entity.x][entity.y] = True  # Make tile visible
        if flag_explored:
            self.game.map.tiles[entity.x][entity.y].explored = True

        for i in range(0, FieldOfView.RAYS + 1, FieldOfView.STEP):
            ax = FieldOfView.SINTABLE[i]  # Get precalculated value sin(x / (180 / pi))
            ay = FieldOfView.COSTABLE[i]  # cos(x / (180 / pi))

            x = entity.x  # Entity x
            y = entity.y  # Entity y

            for z in range(radius):  # Cast the ray
                x += ax
                y += ay

                round_x = int(round(x))
                round_y = int(round(y))
                if round_x < 0 or round_y < 0 or round_x > self.game.map.tile_width or\
                                round_y > self.game.map.tile_height:  # Ray is out of range
                    break

                self.fov[round_x][round_y] = True  # Make tile visible
                if flag_explored:
                    self.game.map.tiles[round_x][round_y].explored = True
                if ignore_entity_at is not None:
                    if (round_x, round_y) not in ignore_entity_at and\
                            self.game.map.tiles[round_x][round_y].block_view_for(entity):
                        break
                elif self.game.map.tiles[round_x][round_y].block_view_for(entity):  # Stop ray if it hit
                    break

        self._ready = False

        return self.fov
