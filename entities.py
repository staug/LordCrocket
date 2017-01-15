from settings import *
from pygame.sprite import Sprite
from pygame.surface import Surface
from item import ItemEntity, EquipmentEntity
from actionable import ActionableEntity
from fighter import MonsterFighter
from ai import AIEntity, FollowingAIEntity
from tilemap import FieldOfView
import pygame
import random as rd
from math import sqrt
import constants as c


class Entity(Sprite):
    """
    Generic Object of the game: player, enemy, object on floor, equipment, trap... that is to be drawn
    This should never be called directly, but rather instantiated throuhgt one of the helper class
    @:parameter game: reference to the game
    @:parameter name: the pretty name of the entity
    @:parameter pos: the position
    @:parameter groups: sprite group (in future will be used for drawing order!)
    @:parameter blocking_tile_list: a list of tile.Type that the entity cannot go over if it is a movable entity
    @:parameter blocking_view_list: a list of tile.Type that the entity cannot view beyond (not used yet)
    @:parameter blocks: is this a blocking object?
    @:parameter fighter: the fighter component if any
    @:parameter ai: the ai component if any
    @:parameter actionable: the actionable (remote or not) part if any
    """
    def __init__(self,
                 game,
                 name,
                 pos,
                 image_ref,
                 groups=None,
                 blocking_tile_list=None,
                 blocking_view_list=None,
                 vision=1,
                 blocks=False,
                 fighter=None,
                 ai=None,
                 item=None,
                 equipment=None,
                 actionable=None):

        Sprite.__init__(self)
        self.game = game
        self.name = name
        (self.x, self.y) = pos

        self.groups = groups
        self.image_ref = image_ref

        self.image = None
        self.animated = False
        self.init_graphics()

        # Blocking: what the object can go over, what it can see over, and if the object prevents movement upon itself
        self.blocking_tile_list = blocking_tile_list
        self.blocking_view_list = blocking_view_list
        self.blocks = blocks
        self.base_vision = vision

        # Components
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self
            self.game.ticker.schedule_turn(self.ai.speed, self.ai)

        self.item = item
        if self.item:  # let the Item component know who owns it
            self.item.owner = self

        self.equipment = equipment
        if self.equipment:  # let the Equipment component know who owns it
            self.equipment.owner = self
            # there must be an Item component for the Equipment component to work properly
            self.item = ItemEntity()
            self.item.owner = self

        self.actionable = actionable
        if self.actionable:
            self.actionable.owner = self

        # and we register ourselves
        self.game.objects.append(self)

    @property
    def pos(self):
        return self.x, self.y

    def move(self, dx=0, dy=0):
        """
        Try to move the entity. Return True if success
        :param dx: the delta in x
        :param dy: the delta in y
        :return: True if the move was successfull
        """
        # Action test
        for entity in self.game.objects:
            if entity != self and \
                            entity.actionable is not None and \
                            (self.x + dx, self.y + dy) in entity.actionable.action_field:
                self.x += dx
                self.y += dy
                entity.actionable.action(self)
                self.x -= dx
                self.y -= dy

        # collision test: map data (floor, water, lava...)
        if not self.game.map.tiles[self.x + dx][self.y + dy].block_for(self):
            # now test the list of objects
            for entity in self.game.objects:
                if entity != self and entity.blocks and entity.x == self.x + dx and entity.y == self.y + dy:
                    return False  # cannot move
            # success
            self.x += dx
            self.y += dy
            if self.animated and (dx != 0 or dy != 0):
                self.last_direction = (dx, dy)

            return True  # move
        return False  # cannot move

    @property
    def vision(self):
        # This is the default. Is improved for the player with attributes...
        return self.base_vision

    def view(self, other_entity):
        # First check: we make sure that the distance is less than the view before computing the FoV
        if self.distance_to(other_entity) > self.vision:
            return False

        vision_matrix = FieldOfView(self.game).get_vision_matrix_for(
            self, radius=self.vision, ignore_entity_at=[self.pos])
        return vision_matrix[other_entity.x][other_entity.y]

    def distance_to(self, other):
        # return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return sqrt(dx ** 2 + dy ** 2)

    # GRAPHICAL RELATED FUNCTIONS

    def init_graphics(self, in_inventory=False):
        """
        Initiate all graphical objects
        :return: Nothing
        """
        if self.groups is not None:
            for group in self.game.all_groups:
                self.remove(group)
            self.add(self.groups)
        elif not in_inventory:
            self.add(self.game.player_sprite_group)

        image = self.game.all_images[self.image_ref]
        if type(image) is tuple:
            # for decode purpose
            self.image = Surface((TILESIZE_SCREEN, TILESIZE_SCREEN))
            self.image.fill(image)
        elif type(image) is list or type(image) is dict:
            self.animated = True
            self.current_frame = 0
            self.last_update = 0
            if type(image) is list:
                self.list_image = image
                self.image = self.list_image[self.current_frame]
            else:
                self.last_direction = (1, 0)
                self.dict_image = image
                self.image = self.dict_image['E'][self.current_frame]
        else:
            self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = self.x * TILESIZE_SCREEN  # initial position for the camera
        self.rect.y = self.y * TILESIZE_SCREEN

    def clean_before_save(self, image_only=False):
        """
        Clean all graphical objects, remove from sprite dictionary and remove the game reference
        :return:
        """
        if self.groups is not None:
            self.remove(self.groups)
        else:
            self.remove(self.game.player_sprite_group)
        self.image = None
        self.animated = False
        if hasattr(self, "dict_image"):
            # self.dict_image = None
            delattr(self, "dict_image")
        if hasattr(self, "list_image"):
            self.list_image = None
            delattr(self, "list_image")
        if not image_only:
            self.game = None

    def animate(self):
        now = pygame.time.get_ticks()
        delta = 200
        if hasattr(self, "ai") and self.ai != None:
            if hasattr(self.ai, "speed"):
                delta = self.ai.speed * 30
        elif hasattr(self, "speed"):
            delta = self.speed * 30
        if now - self.last_update > delta:
            self.last_update = now
            reference = 'E'
            if hasattr(self, "dict_image"):
                if self.last_direction[0] < 0:
                    reference = 'W'
                if self.last_direction[0] > 0:
                    reference = 'E'
                if self.last_direction[1] < 0:
                    reference = 'N'
                if self.last_direction[1] > 0:
                    reference = 'S'

                self.current_frame = (self.current_frame + 1) % len(self.dict_image[reference])
                self.image = self.dict_image[reference][self.current_frame]
            else:
                self.current_frame = (self.current_frame + 1) % len(self.list_image)
                self.image = self.list_image[self.current_frame]

    def set_in_spritegroup(self, sprite_level):
        """
        Set the sprite in a correct sprite group
        :param sprite_level: integer between -2 and +2 inclusive. 0 is the player group
        :return: nothing
        """
        for group in self.game.all_groups:
            group.remove(self)
        self.game.all_groups[sprite_level + 2].add(self)

    def update(self):
        if self.animated:
            self.animate()
        self.rect.x = self.x * TILESIZE_SCREEN
        self.rect.y = self.y * TILESIZE_SCREEN

    def change(self, **kwargs):
        """
        This method updates the entity with as many parameters as required.
        :param kwargs: a dictionnary of attributes. All entity attributes are valid, except pos and game.
        :return: None
        """

        self.name = kwargs.pop("name", self.name)
        self.blocks = kwargs.pop("blocks", self.blocks)
        self.groups = kwargs.pop("groups", self.groups)
        self.blocking_view_list = kwargs.pop("blocking_view_list", self.blocking_view_list)
        self.blocking_tile_list = kwargs.pop("blocking_tile_list", self.blocking_tile_list)
        self.base_vision = kwargs.pop("vision", self.base_vision)

        # Now all components. We need to remove them from scheduler if any
        if "ai" in kwargs and self.ai is not None:
            # First, we remove any previous ai from the scheduler
            self.game.ticker.unregister(self.ai)
        self.ai = kwargs.pop("ai", self.ai)

        if "actionable" in kwargs and self.actionable is not None:
            self.game.ticker.unregister(self.actionable)
        self.actionable = kwargs.pop("actionable", self.actionable)

        if "equipment" in kwargs and self.equipment is not None:
            self.equipment.dequip()
            self.game.ticker.unregister(self.equipment)
        self.equipment = kwargs.pop("equipment", self.equipment)

        if "item" in kwargs and self.item is not None:
            self.game.ticker.unregister(self.item)
        self.item = kwargs.pop("item", self.item)

        if "fighter" in kwargs and self.fighter is not None:
            self.game.ticker.unregister(self.fighter)
        self.fighter = kwargs.pop("fighter", self.fighter)

        # Now handling the image ref
        if "image_ref" in kwargs and kwargs["image_ref"] != self.image_ref:
            self.clean_before_save(image_only=True)
            self.image_ref = kwargs.pop("image_ref")
            self.init_graphics()

        assert len(kwargs) == 0, "Attributes not changed: {}".format(kwargs)

    def remove_completely_object(self):
        """
        Properly remove the object: deregister the ai, remove from the sprite groups, remove from the game group,
        kill image
        :return:
        """
        # Deregister_ai
        self.game.ticker.unregister(self.equipment)
        self.game.ticker.unregister(self.ai)
        self.game.ticker.unregister(self.item)
        self.game.ticker.unregister(self.fighter)
        self.game.ticker.unregister(self.actionable)

        # Deregister components
        self.ai = self.equipment = self.item = self.fighter = self.actionable = None

        # Remove from spritegroup
        if self.groups is not None:
            self.remove(self.groups)
        else:
            self.remove(self.game.player_sprite_group)

        # Remove from all objects
        self.game.objects.remove(self)

        self.kill()

class SpecialVisualEffect(Entity):
    def __init__(self, game, pos, image, seconds):
        Entity.__init__(self, game, "Effect", pos, image, groups=game.player_plus1_sprite_group)
        now = pygame.time.get_ticks()
        self.end = now + 1000 * seconds

    def update(self):
        now = pygame.time.get_ticks()
        if now > self.end:
            self.game.player_plus1_sprite_group.remove(self)
            self.game.objects.remove(self)
            self.kill()
        else:
            if self.animated:
                self.animate()
            self.rect.x = self.x * TILESIZE_SCREEN
            self.rect.y = self.y * TILESIZE_SCREEN


class ItemHelper(Entity):
    """
    Class used to create an Item
    """
    def __init__(self, game, name, pos, image_ref, use_function):
        """
        Initialization method
        :param game: reference to the game variable
        :param name: the name of the Item
        :param pos: the pos (as tuple) of the item
        :param image_ref: the reference for the image
        :param use_function: the function to be used.
        Sample: use_function=lambda player=self.player: Item.cast_heal(player)
        """
        Entity.__init__(self, game, name, pos, image_ref, blocks=False, item=ItemEntity(use_function=use_function))
        self.set_in_spritegroup(-1)

    @staticmethod
    def cast_heal(entity, heal_amount=3, expression='FIX'):

        assert expression in ('FIX', 'PERCENTAGE'), "Cast heal works with FIX or PERCENTAGE argument"

        # heal the entity - if already at max xp we don't do anything
        if entity.fighter.hit_points == entity.base_hit_points:
            entity.game.textbox.add = 'You are already at full health.'
            return ItemEntity.FUNCTION_CANCELLED

        entity.game.textbox.add = 'Your wounds start to feel better!'
        entity.fighter.heal(heal_amount)


class DoorHelper(Entity):
    """
    Class used to create an Item
    """
    def __init__(self, game, pos, image_refs, closed=True, open_function=None, name=None):
        """
        Initialization method
        :param game: reference to the game variable
        :param pos: the pos (as tuple) of the item
        :param image_refs: the reference for the images in this order:
         horizontal_door_closed, horizontal_door_open, vertical_door_closed, vertical_door_open
        :param open_function: the function to be used when open the door if any
        Sample: open_function=lambda player=self.player: Item.cast_heal(player)
        """
        assert type(image_refs) is tuple and len(image_refs) == 4, "Doors images must be a tuple of 4, containing" \
                                                                   "horizontal_door_closed, horizontal_door_open, " \
                                                                   "vertical_door_closed, vertical_door_open"
        self.index = 0
        self.image_refs = image_refs

        if game.map.tiles[pos[0]][pos[1]+1].tile_type == c.T_WALL:
            self.index += 2
        if not closed:
            self.index += 1

        if name is None:
            name = "Door"

        Entity.__init__(self, game, name, pos, image_refs[self.index], blocks=closed,
                        actionable=ActionableEntity(function=open_function))

    @staticmethod
    def open_door(door, entity_that_actioned):
        door.blocks = False
        door.actionable = None
        door.game.textbox.add = "The door {} has been opened by {}".format(door.name, entity_that_actioned.name)
        door.image_ref = door.image_refs[door.index + 1 % 4]
        door.image = door.game.all_images[door.image_ref]
        door.set_in_spritegroup(-1)

    def __str__(self):
        return "Door {} opened:{}".format(self.name, not self.blocks)


class StairHelper(Entity):
    """
    Class used to create an Item
    """
    def __init__(self, game, pos, image_ref, use_function=None, name=None):
        """
        Initialization method
        :param game: reference to the game variable
        :param pos: the pos (as tuple) of the item
        :param image_ref: the reference for the images
        :param use_function: the function to be used when open the door if any
        Sample: use_function=lambda player=self.player: StairHelper.next_lever(player)
        """

        if name is None:
            name = "Stair to next level"

        if use_function is None:
            use_function = StairHelper.next_level

        Entity.__init__(self, game, name, pos, image_ref, blocks=True,
                        actionable=ActionableEntity(function=use_function))

    @staticmethod
    def next_level(stair, entity_that_actioned):
        stair.game.textbox.add = "The stair {} has been used by {}".format(stair.name, entity_that_actioned.name)
        stair.game.go_next_level()

    def __str__(self):
        return "Door {} opened:{}".format(self.name, not self.blocks)




class EquipmentHelper(Entity):
    """
    Class used to create an Equipment
    """

    def __init__(self, game, name, pos, image_ref, slot, modifiers):
        """
        Initialization method
        :param game: reference to the game variable
        :param name: the name of the Item
        :param pos: the pos (as tuple) of the item
        :param image_ref: the reference for the image
        :param slot: where the equipment is equipped
        :param modifiers: a dictionary of effect
        Sample: {"AC": 2}
        """
        Entity.__init__(self, game, name, pos, image_ref, blocks=False,
                        equipment=EquipmentEntity(slot=slot, modifiers=modifiers))
        self.set_in_spritegroup(-1)


class MonsterHelper(Entity):
    """
    Class used to create a Monster
    """
    def __init__(self, game, name, pos, image_ref,
                 armor, hit_dice, attacks, morale, saving_throw, death_function=None, special=None,
                 blocking_tile_list=None, blocking_view_list=None, vision=5,
                 speed=1):
        """
        Initialization method
        :param game: reference to the game variable
        :param name: the name of the Item
        :param pos: the pos (as tuple) of the item
        :param image_ref: the reference for the image
        :param armor: the armor class as a number
        :param hit_dice: the hitpoints, as a roll dice (ex: (1,8,2) for 1d8+2)
        :param attacks: the list of attacks, as name and roll dice (ex: ("claw", (2,3,1) for claw using 2d3+1)
        :param morale: the morale as number
        :param saving_throw: the saving throw as number
        :param blocking_tile_list: a list of tile.Type that the entity cannot go over if it is a movable entity
        :param blocking_view_list: a list of tile.Type that the entity cannot view beyond (not used yet)
        :param vision: the vision of the beast
        :param death_function:
        :param special:
        """
        ai = AIEntity(speed=speed)
        Entity.__init__(self, game, name, pos, image_ref, vision=vision, blocks=True,
                        blocking_tile_list=blocking_tile_list, blocking_view_list=blocking_view_list,
                        ai=ai,
                        fighter=MonsterFighter(armor_class=armor, hit_dice=hit_dice, attacks=attacks, morale=morale,
                                               saving_throw=saving_throw, specials=special,
                                               death_function=death_function))

class MonsterFactory:
    """
    Used to generate a list of Monster
    """
    def __init__(self, game, seed=None):

        rd.seed(seed)
        self.game = game

        # chance of each monster
        self.monster_chances = {}
        if IMG_STYLE == c.IM_STYLE_ORYX:
            self.monster_chances["BAT"] = 55
            self.monster_chances["DOG"] = 8
        elif IMG_STYLE == c.IM_STYLE_DAWNLIKE:
            self.monster_chances["GIANT_ANT"] = self.from_dungeon_level([[60, 3], [15, 5]])
            self.monster_chances["BABOON"] = 20  # always shows up, even if all other monsters have 0 chance
            self.monster_chances["BADGER"] = 10  # blaireau
        # self.monster_chances["DOG_WAR"] = self.from_dungeon_level([[15, 2], [25, 6]])
        # self.monster_chances["RAT_GIANT"] = 9
        # self.monster_chances["HAWK"] = 10
        # self.monster_chances["CHEETAH"] = self.from_dungeon_level([[25, 3], [40, 6]])

    @staticmethod
    def random_choice(chances_dict):
        # choose one option from dictionary of chances, returning its key
        chances = chances_dict.values()
        strings = list(chances_dict.keys())
        return strings[MonsterFactory.random_choice_index(chances)]

    @staticmethod
    def random_choice_index(chances):  # choose one option from list of chances, returning its index
        # the dice will land on some number between 1 and the sum of the chances
        dice = rd.randint(1, sum(chances))

        # go through all chances, keeping the sum so far
        running_sum = 0
        choice = 0
        for w in chances:
            running_sum += w

            # see if the dice landed in the part that corresponds to this choice
            if dice <= running_sum:
                return choice
            choice += 1

    def from_dungeon_level(self, table):
        # returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
        for (value, level) in reversed(table):
            if self.game.level >= level:
                return value
        return 0

    def build_list(self, number_monster):
        pos_list = self.game.map.get_all_available_tiles(c.T_FLOOR, self.game.objects, without_objects=True)
        assert number_monster < len(pos_list), \
            "Number of monster generated {} must be greater than available positions {}".format(number_monster,
                                                                                                len(pos_list))

        print("Total number of mosnter requested: {}".format(number_monster))
        for i in range(number_monster):
            monster = MonsterFactory.random_choice(self.monster_chances)
            if monster == "GIANT_ANT":
                MonsterHelper(self.game, "Giant Ant " + str(i), pos_list.pop(), 'GIANT_ANT', 16, (3, 8, 0),
                              [("bite", (1, 6, 3))],
                              12, 16, vision=2, speed=8)
            elif monster == "BABOON":
                MonsterHelper(self.game, "Baboon " + str(i), pos_list.pop(), 'BABOON', 12, (1, 8, 0),
                              [("bite", (1, 4, 1))],
                              6, 18, vision=3, speed=7)
            elif monster == "BADGER":
                MonsterHelper(self.game, "Badger " + str(i), pos_list.pop(), 'BADGER', 15, (1, 8, 0),
                              [("bite", (1, 3, 1)), ("claws", (1, 2, 1))],
                              7, 18, vision=2, speed=10)
            elif monster == "BAT":
                MonsterHelper(self.game, "Bat " + str(i), pos_list.pop(), 'BAT', 10, (1, 4, 0),
                              [("bite", (1, 2, 1))],
                              6, 19, vision=3, speed=6)
            elif monster == "DOG":
                MonsterHelper(self.game, "Dog " + str(i), pos_list.pop(), 'DOG', 11, (1, 8, 0),
                              [("bite", (1, 4, 1))],
                              7, 18, vision=4, speed=9)

class NPCHelper(Entity):

    def __init__(self, game, name, pos, image_ref):
        ai = FollowingAIEntity(speed=game.player.speed)
        Entity.__init__(self, game, name, pos, image_ref, ai=ai)


class ThrowableHelper(Entity):

    TARGET_NPC = "target_NPC"
    TARGET_MONSTER = "target_monster"
    TARGET_FIGHTER = "target_fighter"

    def __init__(self, game, pos, image_ref, direction, function_hit, target_list=None, stopped_by=None):
        if target_list is None:
            target_list = []
        if stopped_by is None:
            stopped_by = []

        Entity.__init__(self, game, "", pos, image_ref)
        self.direction = direction
        self.function_hit = function_hit
        self.target_list = target_list
        self.stopped_by = stopped_by

        Entity.__init__(self, game, "", pos, image_ref)
        self.set_in_spritegroup(1)
        self.next_motion = pygame.time.get_ticks() - 1

    def update(self):
        now = pygame.time.get_ticks()
        if now > self.next_motion:
            self.x += self.direction[0]
            self.y += self.direction[1]

            # Test if next position is valid
            if not (0 <= self.x < self.game.map.tile_width) and (0 <= self.y < self.game.map.tile_height):
                self.remove_object()
                return
            if self.game.map.tiles[self.x][self.y].tile_type in self.stopped_by:
                self.remove_object()
                return

            # Now testing if in target list!
            # TODO Proper testing between NPC and monster
            for entity in self.game.objects:
                # last check is to avoid "remains" of monster to act like entities...
                # TODO remove the last check, by transferring entities to new objects instead
                if entity.pos == self.pos and isinstance(entity, MonsterHelper) and entity.fighter is not None:
                    self.function_hit(entity)
                    self.remove_object()
                    return

            self.next_motion = now + 200
        else:
            if self.animated:
                self.animate()
            self.rect.x = self.x * TILESIZE_SCREEN
            self.rect.y = self.y * TILESIZE_SCREEN

    def remove_object(self):
        self.game.player_plus1_sprite_group.remove(self)
        self.game.objects.remove(self)
        self.kill()

    @staticmethod
    def light_damage(target):
        target.fighter.take_damage(20)
