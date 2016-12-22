import pygame as pg
from settings import *
import random
from os import path

class Tile:
    """
    A tile of the map and its properties
    """

    # Type of Tiles
    VOID = '0'
    WALL = '1'
    FLOOR = '2'

    def __init__(self, tile_type=VOID, room=None):
        self.tile_type = tile_type
        self.explored = False
        self.room = room

    def block_for(self, entity):
        if entity.blocking_tile_list:
            if self.tile_type in entity.blocking_tile_list:
                return True
            else:
                return False
        elif self.tile_type in (Tile.VOID, Tile.WALL):
            return True
        return False

    def block_view_for(self, entity):
        if hasattr(entity, "blocking_view_tile_list"):
            if self.tile_type in entity.blocking_view_tile_list:
                return True
            else:
                return False
        elif self.tile_type in (Tile.VOID, Tile.WALL):
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
        room_name_part2 = ('room', 'hall', 'place', 'pit', 'shamble', 'crossing', 'location', 'center', 'cavity','cell',
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


class Map:
    """
    The Map, representing a level. Mainly holds a reference to a set of tiles, as well as dimensions.
    """
    def __init__(self, game, name, filename=None, dimension=(80, 120),
                 room_size_range=((8,10), (12,17)), max_num_room=50):

        self.game = game
        self.name = name
        self._background = None
        self.tilewidth = self.tileheight = 0
        self.width = self.height = 0

        self.rooms = []

        if filename is not None:
            self._generate_from_filename(filename)
        else:
            # self._generate_room_type_dungeon(seed=None, dimension=dimension,
            #  room_size_range=room_size_range, max_num_room=max_num_room)
            # self._generate_pure_maze_dungeon()
            # self._generate_cave_type_dungeon()
            self._generate_maze_type_dungeon()

    @property
    def background(self):
        if self._background is None:
            self._build_background()
        return self._background

    def clean_before_save(self):
        self._background = None
        self.game = None

    def wall_weight(self, x, y, door_list):
        """
        Taken from http://www.angryfishstudios.com/2011/04/adventures-in-bitmasking/
        :param x:
        :param y:
        :return:
        """
        weight = 0
        if y - 1 > 0 and (self.tiles[x][y-1].tile_type == Tile.WALL or (x, y-1) in door_list):
            weight += 1
        if x - 1 > 0 and (self.tiles[x-1][y].tile_type == Tile.WALL or (x - 1, y) in door_list):
            weight += 8
        if y+1 < self.tileheight and (self.tiles[x][y+1].tile_type == Tile.WALL or (x, y+1) in door_list):
            weight += 4
        if x+1 < self.tilewidth and (self.tiles[x+1][y].tile_type == Tile.WALL or (x + 1, y) in door_list):
            weight += 2
        return weight

    def _generate_room_type_dungeon(self, seed=None, dimension=(80, 120), room_size_range=((6, 6), (9, 9)),
                                    max_num_room=60, tunnel=False):
        """
        Run the dungeon generation program.
        :param seed: the seed to initialize the dungeon
        :param dimension:
        :param room_size_range:
        :param max_num_room:
        :param tunnel: if True, we may connect rooms via tunnels
        :return:
        """
        if seed is not None:
            random.seed(a=seed)

        self.tilewidth = dimension[0]  # width of map, expressed in tiles
        self.tileheight = dimension[1] # height of map, expressed in tiles
        self.width = self.tilewidth * TILESIZE_SCREEN  # width in pixel
        self.height = self.tileheight * TILESIZE_SCREEN  # height in pixel

        self.tiles = [[Tile(Tile.VOID)
                       for y in range(self.tileheight)]
                      for x in range(self.tilewidth)]

        self.rooms = []
        # generate the dungeon
        self.rooms.append(self._generate_room(room_size_range[0], room_size_range[1]))
        self._place_room(self.rooms[-1],
                        (int(self.tilewidth / 2 - (self.rooms[-1].size[0] / 2)),
                         int(self.tileheight / 2 - (self.rooms[-1].size[1] / 2))))

        for i in range (self.tilewidth * self.tileheight * 2):
            if len(self.rooms) == max_num_room:
                break
            branching_room = random.choice(self.rooms)
            choice_wall = self._get_branching_position_direction(branching_room)
            branching_pos = (choice_wall[0], choice_wall[1])
            branching_dir = choice_wall[2]
            new_room = self._generate_room(room_size_range[0], room_size_range[1])
            tunnel_length = random.randint(1, 4)
            #TODO: add tunnel length below
            if branching_dir == 'N':
                new_room_pos = (int(branching_pos[0] - (new_room.size[0] / 2)),
                                int(branching_pos[1] - new_room.size[1] + 1))
            elif branching_dir == 'E':
                new_room_pos = (int(branching_pos[0]),
                                int(branching_pos[1] - (new_room.size[1] / 2)))
            elif branching_dir == 'S':
                new_room_pos = (int(branching_pos[0] - (new_room.size[0] / 2)),
                                int(branching_pos[1]))
            elif branching_dir == 'W':
                new_room_pos = (int(branching_pos[0] - (new_room.size[0]) + 1),
                                int(branching_pos[1] - (new_room.size[1] / 2)))

            if self._space_for_new_room(new_room.size, new_room_pos):
                self._place_room(new_room, new_room_pos)
                self.rooms.append(new_room)
                # Now connecting room
                # No tunnel, easy case:
                new_room.doors.append(branching_pos)
                self.tiles[branching_pos[0]][branching_pos[1]].tile_type = Tile.FLOOR
                new_room.connecting_room.append(branching_room)
                branching_room.connecting_room.append(new_room)

    def _generate_cave_type_dungeon(self, seed=None, dimension=(125, 81)):
        # dimensions doivent être impair!
        assert dimension[0] % 2 == 1 and dimension[1] % 2 == 1, "Maze dimensions must be odd"

        self.tilewidth = dimension[0]  # width of map, expressed in tiles
        self.tileheight = dimension[1]  # height of map, expressed in tiles
        self.width = self.tilewidth * TILESIZE_SCREEN  # width in pixel
        self.height = self.tileheight * TILESIZE_SCREEN  # height in pixel

        self.tiles = [[Tile(Tile.FLOOR)
                       for y in range(self.tileheight)]
                      for x in range(self.tilewidth)]

        # Initial Random Noise
        for y in range(self.tileheight):
            for x in range(self.tilewidth):
                if x in [0, self.tilewidth-1] or y in [0, self.tileheight-1] or random.randint(0,100) <= 30:
                    self.tiles[x][y].tile_type = Tile.WALL

        for repeat in range(5):
             for y in range(1 , self.tileheight - 1):
                 for x in range(1, self.tilewidth -1):
                     count = self._count_wall_tile(x, y)
                     if count >= 5 or count <= 1:
                         self.tiles[x][y].tile_type = Tile.WALL
                     else:
                         self.tiles[x][y].tile_type = Tile.FLOOR

        for repeat in range(3):
            for y in range(1, self.tileheight - 1):
                for x in range(1, self.tilewidth - 1):
                    count = self._count_wall_tile(x, y)
                    if count >= 5:
                        self.tiles[x][y].tile_type = Tile.WALL
                    else:
                        self.tiles[x][y].tile_type = Tile.FLOOR

    def _count_wall_tile(self, posx, posy):
        count = 0

        for x in [posx-1, posx, posx+1]:
            for y in [posy-1, posy, posy+1]:
                if self.tiles[x][y].tile_type == Tile.WALL:
                    count+=1

        return count

    def _generate_maze_type_dungeon(self, seed=None, dimension=(101, 87)):
        # dimensions doivent être impair!
        assert dimension[0] % 2 == 1 and dimension[1] % 2 == 1, "Maze dimensions must be odd"
        dungeon_ok = False

        while not dungeon_ok:
            print("DUNGEON MAZE: Initialization")
            dungeon_ok = True

            self.tilewidth = dimension[0]  # width of map, expressed in tiles
            self.tileheight = dimension[1]  # height of map, expressed in tiles
            self.width = self.tilewidth * TILESIZE_SCREEN  # width in pixel
            self.height = self.tileheight * TILESIZE_SCREEN  # height in pixel
            self.rooms = []
            # We use algorithm at http://journal.stuffwithstuff.com/2014/12/21/rooms-and-mazes/
            self.tiles = [[Tile(Tile.WALL)
                           for y in range(self.tileheight)]
                          for x in range(self.tilewidth)]

            # We place a bunch of room
            count_explored = 0
            for i in range(int(self.tilewidth * self.tileheight / 2)):
                # We generate a room
                new_room = self._generate_room((5,5), (17,17), modulo_rest=1)
                pos = [random.randint(0, self.tilewidth), random.randint(0, self.tileheight)]
                if pos[0] % 2 == 1: pos[0] += 1
                if pos[1] % 2 == 1: pos[1] += 1

                if self._space_for_new_room(new_room.size, pos):
                    self._place_room(new_room, pos)
                    self.rooms.append(new_room)
                    tile_list = new_room.get_tile_list()
                    for (x, y) in tile_list:
                        self.tiles[x][y].explored = True
                        count_explored += 1
            print("DUNGEON MAZE: Rooms placed")

            # Now we fill almost everything else with maze
            self._flood_maze(to_explore=(self.tilewidth * self.tileheight - count_explored) / 4)
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
                        if self.tiles[x+dx][y+dy].tile_type == Tile.FLOOR:
                            if self.tiles[x+dx][y+dy] not in room_tile_list:
                                if self.tiles[x+dx][y+dy].room is None:
                                    if room not in connected_external_list:
                                        connected_external_list.append(room)
                                else:
                                    other_room = self.tiles[x+dx][y+dy].room
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
                        self.tiles[x][y].tile_type = Tile.WALL
            print("DUNGEON MAZE: Non connected rooms removed")

            # Now, we want to remove some dead end
            spareness = random.randint(1, 5)
            for i in range(spareness):
                for x in range(1, self.tilewidth - 1):
                    for y in range(1, self.tileheight - 1):
                        if self.tiles[x][y].tile_type == Tile.FLOOR:
                            delta = [(0, -1), (0, 1), (1, 0), (-1, 0)]
                            count = 0
                            for (dx, dy) in delta:
                                if self.tiles[x + dx][y + dy].tile_type == Tile.FLOOR:
                                    count += 1
                            if count <= 1:
                                self.tiles[x][y].tile_type = Tile.WALL

            print("DUNGEON MAZE: Dead ends removed")

            # And we replace the big walls blocks by Void..
            self._remove_extra_walls()

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

    def _remove_extra_walls(self):
        for x in range(0, self.tilewidth):
            for y in range(0, self.tileheight):
                if self.tiles[x][y].tile_type == Tile.WALL:
                    delta = [(0, -1), (0, 1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
                    count = 0
                    for (dx, dy) in delta:
                        if x + dx < 0 or x + dx >= self.tilewidth or y + dy < 0 or y + dy >= self.tileheight:
                            count += 1
                        elif self.tiles[x + dx][y + dy].tile_type in (Tile.WALL, Tile.VOID):
                            count += 1
                    if count == 8:
                        self.tiles[x][y].tile_type = Tile.VOID

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
            if 0 <= after_door_pos_x < self.tilewidth and 0 <= after_door_pos_y < self.tileheight:
                if self.tiles[after_door_pos_x][after_door_pos_y].tile_type == Tile.FLOOR:
                    room.doors.append(branching_pos)
                    self.tiles[branching_pos[0]][branching_pos[1]].tile_type = Tile.FLOOR
                    return branching_dir
            trials -= 1
        return None

    def _generate_pure_maze_dungeon(self, seed=None, dimension=(47, 51), spareness=3, remove_extra_walls=True):
        # dimensions doivent être impair!
        assert dimension[0] % 2 == 1 and dimension[1] % 2 == 1, "Maze dimensions must be odd"

        print(" MAZE: Initialization")

        self.tilewidth = dimension[0]  # width of map, expressed in tiles
        self.tileheight = dimension[1]  # height of map, expressed in tiles
        self.width = self.tilewidth * TILESIZE_SCREEN  # width in pixel
        self.height = self.tileheight * TILESIZE_SCREEN  # height in pixel

        # We use algorithm at http://www.brainycode.com/downloads/RandomDungeonGenerator.pdf
        # Starting with walls everywhere, and all not explored
        self.tiles = [[Tile(Tile.WALL)
                       for y in range(self.tileheight)]
                      for x in range(self.tilewidth)]
        self._flood_maze(to_explore=(self.tilewidth - 1) * (self.tileheight - 1) / 4)

        # Now, we want to remove some dead end
        for i in range(spareness):
            for x in range(1, self.tilewidth - 1):
                for y in range(1, self.tileheight - 1):
                    if self.tiles[x][y].tile_type == Tile.FLOOR:
                        delta = [(0, -1), (0, 1), (1, 0), (-1, 0)]
                        count = 0
                        for (dx, dy) in delta:
                            if self.tiles[x + dx][y + dy].tile_type == Tile.FLOOR:
                                count += 1
                        if count <= 1:
                            self.tiles[x][y].tile_type = Tile.WALL

        if remove_extra_walls:
            self._remove_extra_walls()

    def _flood_maze(self, to_explore=0):
        # 2. We pick a random cell, and flag it explored. Demarrage sur un impair!
        found = False
        current_x = current_y = 0
        forbidden_tiles = []
        if hasattr(self, "rooms"):
            for room in self.rooms:
                forbidden_tiles = forbidden_tiles + room.get_tile_list()
        while not found:
            current_x = int(random.randint(0, self.tilewidth) / 2)
            if current_x % 2 == 0:
                current_x += 1
            current_y = int(random.randint(0, self.tilewidth) / 2)
            if current_y % 2 == 0:
                current_y += 1
            if not self.tiles[current_x][current_y].explored and not (current_x, current_y) in forbidden_tiles:
                self.tiles[current_x][current_y].explored = True
                found = True

        self.tiles[current_x][current_y].tile_type = Tile.FLOOR
        explored = [(current_x, current_y)]

        trials = 0
        while len(explored) < to_explore and trials < (self.tilewidth * self.tileheight)/4:
            current_cell = self.tiles[current_x][current_y]
            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            # 3. We pick a random direction
            random.shuffle(directions)
            found = False
            (dir_x, dir_y) = (0, 0)

            while not found and len(directions) > 0:
                (dir_x, dir_y) = directions.pop()
                # 3A: we test if this new cell is valid and not explored
                if 0 < current_x + dir_x < self.tilewidth and 0 < current_y + dir_y < self.tileheight:
                    if not self.tiles[current_x + dir_x][current_y + dir_y].explored:
                        if not (current_x + dir_x, current_y + dir_y) in forbidden_tiles:
                            found = True

            if found:
                # 4. we create a corridor
                self.tiles[current_x + int(dir_x / 2)][current_y + int(dir_y / 2)].tile_type = Tile.FLOOR
                current_x = current_x + dir_x
                current_y = current_y + dir_y
                self.tiles[current_x][current_y].tile_type = Tile.FLOOR
                self.tiles[current_x][current_y].explored = True
                explored.append((current_x, current_y))
            else:
                (current_x, current_y) = random.choice(explored)
            trials += 1

        for x in range(self.tilewidth):
            for y in range(self.tileheight):
                self.tiles[x][y].explored = False

    def _space_for_new_room(self, new_room_size, new_room_position, tiles_blocking=Tile.FLOOR):
        for y in range(new_room_position[1],
                       new_room_position[1] + new_room_size[1]):
            for x in range(new_room_position[0],
                           new_room_position[0] + new_room_size[0]):
                if x < 0 or x > self.tilewidth - 1:
                    return False
                if y < 0 or y > self.tileheight - 1:
                    return False
                if self.tiles[x][y].tile_type in tiles_blocking:
                    return False
        return True

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

    def _place_room(self, room, grid_position):
        room.position = grid_position
        for y in range(grid_position[1], grid_position[1] + room.size[1]):
            for x in range(grid_position[0], grid_position[0] + room.size[0]):
                self.tiles[x][y].room = room
                if y in (grid_position[1], grid_position[1] + room.size[1] -1) or \
                                x in (grid_position[0], grid_position[0] + room.size[0] -1):
                    self.tiles[x][y].tile_type = Tile.WALL
                else:
                    self.tiles[x][y].tile_type = Tile.FLOOR

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
                if not (self.tiles[x - 1][y].tile_type == Tile.FLOOR or self.tiles[x + 1][y].tile_type == Tile.FLOOR):
                    return (x, y, dir)
            if dir in ('E', 'W'):
                if not (self.tiles[x][y-1].tile_type == Tile.FLOOR or self.tiles[x][y+1].tile_type == Tile.FLOOR):
                    return (x, y, dir)

    def _generate_from_filename(self, filename):
        file_data = []
        with open(filename, 'rt') as f:
            for line in f:
                file_data.append(line.strip())

        self.tilewidth = len(file_data[0]) # width of map, expressed in tiles
        self.tileheight = len(file_data) # height of map, expressed in tiles
        self.width = self.tilewidth * TILESIZE_SCREEN # width in pixel
        self.height = self.tileheight * TILESIZE_SCREEN # height in pixel

        self.tiles = [[Tile(Tile.FLOOR)
                      for y in range(self.tileheight)]
                     for x in range(self.tilewidth)]

        # Parse the file
        for row, tiles in enumerate(file_data):
            for col, tile in enumerate(tiles):
                if tile == str(Tile.WALL):
                    self.tiles[col][row].tile_type = Tile.WALL
                elif tile == str(Tile.FLOOR):
                    self.tiles[col][row].tile_type = Tile.FLOOR
                else:
                    self.tiles[col][row].tile_type = Tile.VOID

    def get_random_available_tile(self, tile_type):
        """
        Return a tile matching the characteristics: given tile type
        Used to get a spawning position...
        :param tile_type: the type of tile that we look for
        :return: a tile position (tuple)
        """
        while True:
            x = random.randint(0, self.tilewidth - 1)
            y = random.randint(0, self.tileheight - 1)
            if self.tiles[x][y].tile_type == tile_type:
                return (x, y)

    @property
    def doors_pos(self):
        pos = []
        for room in self.rooms:
            for door in room.doors:
                if door not in pos:
                    pos.append(door)
        return pos

    def get_all_available_tiles(self, tile_type, without_objects=False):
        """
        Return all tile matching the characteristics: given tile type
        Used to get a spawning position...
        :param tile_type: the type of tile that we look for
        :param without_objects: set to True to remove objects overlap
        :return: a list of tile positions (tuple)
        """
        listing = []
        entity_pos_listing = []

        if without_objects:
            for entity in self.game.objects:
                entity_pos_listing.append((entity.x, entity.y))

        doors = self.doors_pos

        for x in range(self.tilewidth):
            for y in range(self.tileheight):
                if self.tiles[x][y].tile_type == tile_type:
                    if without_objects and (x, y) not in entity_pos_listing and (x, y) not in doors:
                        listing.append((x, y))
        random.shuffle(listing)
        return listing

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
            self._background = pg.Surface((self.width, self.height))
            self._background.fill(BGCOLOR)

            complex_walls = type(self.game.all_images['WALLS']) is list

            floor_serie = random.randint(0, len(self.game.all_images['FLOOR']) - 1)
            if complex_walls:
                wall_series = random.randint(0, len(self.game.all_images['WALLS']) - 1)
            for y in range(self.tileheight):
                for x in range(self.tilewidth):
                    if self.tiles[x][y].tile_type == Tile.FLOOR:
                        if random.randint(0, 100) >= 85:
                            floor_image = random.randint(0, len(self.game.all_images['FLOOR_EXT'][floor_serie]) - 1)
                        else:
                            floor_image = random.randint(0, len(self.game.all_images['FLOOR'][floor_serie]) - 1)
                        self._background.blit(self.game.all_images['FLOOR'][floor_serie][floor_image],
                                              (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))

                    elif self.tiles[x][y].tile_type == Tile.WALL:
                        if not complex_walls:
                            self._background.blit(self.game.all_images['WALLS'],
                                                  (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                        else:
                            # First, we copy an image of teh floor to make it look better
                            floor_image = random.randint(0, len(self.game.all_images['FLOOR'][floor_serie]) - 1)
                            self._background.blit(self.game.all_images['FLOOR'][floor_serie][floor_image],
                                                  (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))
                            # Then the wall
                            door_list = []
                            # build door list - except if we are in a pure maze
                            if hasattr(self, "rooms") and self.rooms is not None:
                                 for room in self.rooms:
                                     for door_pos in room.doors:
                                         door_list.append(door_pos)
                            weight = self.wall_weight(x, y, door_list)
                            self._background.blit(self.game.all_images['WALLS'][wall_series][weight],
                                                  (x * TILESIZE_SCREEN, y * TILESIZE_SCREEN))

        if name is not None:
            pg.image.save(self._background, path.dirname(__file__) + '/' + name)


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
        x =-target.rect.x + int(PLAYABLE_WIDTH / 2)
        y =-target.rect.y + int(PLAYABLE_HEIGHT / 2)
        # limit scrolling to map size
        x = min(0, x) # left
        y = min(0, y) # up
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
        self._background = pg.Surface((self.game.map.tilewidth * zoom_factor, self.game.map.tileheight * zoom_factor))
        backpixels = pg.PixelArray(self._background)
        for x in range(self.game.map.tilewidth):
            for y in range(self.game.map.tileheight):
                if (self.game.map.tiles[x][y].explored):
                    tile_type = self.game.map.tiles[x][y].tile_type
                    if tile_type == Tile.WALL:
                        backpixels[x*zoom_factor:x*zoom_factor+1, y*zoom_factor:y*zoom_factor+1] = RED
                    elif tile_type == Tile.FLOOR:
                        backpixels[x * zoom_factor:x * zoom_factor + 1, y * zoom_factor:y * zoom_factor + 1] = WHITE
        # Now we add a big cross at the player position
        if hasattr(self.game, "player"):
            pos_x = self.game.player.x
            pos_y = self.game.player.y
            backpixels[(pos_x - 1) * zoom_factor:(pos_x + 1) * zoom_factor + 1,
            pos_y * zoom_factor:pos_y * zoom_factor + 1] = GREEN
            backpixels[pos_x * zoom_factor:pos_x * zoom_factor + 1,
            (pos_y - 1) * zoom_factor:(pos_y + 1 )* zoom_factor + 1] = GREEN

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
        self.fov = [[False for y in range(self.game.map.tileheight)] for x in range(self.game.map.tilewidth)]
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
                if round_x < 0 or round_y < 0 or round_x > self.game.map.tilewidth or\
                                round_y > self.game.map.tileheight:  # Ray is out of range
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
