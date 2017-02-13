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
import utilities as ut


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
                 long_desc=None,
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
        self.long_desc = long_desc

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
        self.rect.centerx = self.x * TILESIZE_SCREEN + int(TILESIZE_SCREEN / 2)  # initial position for the camera
        self.rect.centery = self.y * TILESIZE_SCREEN + int(TILESIZE_SCREEN / 2)

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
        self.rect.centerx = self.x * TILESIZE_SCREEN + int(TILESIZE_SCREEN / 2)
        self.rect.centery = self.y * TILESIZE_SCREEN + int(TILESIZE_SCREEN / 2)

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

        if "sprite_level" in kwargs:
            self.set_in_spritegroup(kwargs.pop("sprite_level"))

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
    def __init__(self, game, name, pos, image_ref, use_function, long_desc=None):
        """
        Initialization method
        :param game: reference to the game variable
        :param name: the name of the Item
        :param pos: the pos (as tuple) of the item
        :param image_ref: the reference for the image
        :param use_function: the function to be used.
        Sample: use_function=lambda player=self.player: Item.cast_heal(player)
        """
        Entity.__init__(self, game, name, pos, image_ref, blocks=False,
                        item=ItemEntity(use_function=use_function), long_desc=long_desc)
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
    def open_door(bus, door, entity_that_actioned):
        # By default doors are forced
        roll = ut.roll(20)
        if roll > entity_that_actioned.strength:
            # Failure when opening doors
            bus.publish(door, {"object": door, "operator": entity_that_actioned, "result": c.FAILURE},
                        main_category=c.P_CAT_ENV,
                        sub_category=c.AC_ENV_OPEN)
            return False

        # Door is successfully opened
        door.blocks = False
        door.actionable = None
        bus.publish(door, {"object": door, "operator": entity_that_actioned, "result":c.SUCCESS},
                                    main_category=c.P_CAT_ENV,
                                    sub_category=c.AC_ENV_OPEN)
        door.image_ref = door.image_refs[door.index + 1 % 4]
        door.image = door.game.all_images[door.image_ref]
        door.set_in_spritegroup(-1)
        return True

    def __str__(self):
        return "Door {} opened:{}".format(self.name, not self.blocks)


class StairHelper(Entity):
    """
    Class used to create a STair
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
    def next_level(bus, stair, entity_that_actioned):
        stair.game.textbox.add = "The stair {} has been used by {}".format(stair.name, entity_that_actioned.name)
        stair.game.go_next_level()
        return True

    def __str__(self):
        return "Stairs {} to next level".format(self.name)


class OpenableObjectHelper(Entity):
    """
    Generic Object that can be Opened (chest, vase...)
    It is generally blocking while closed.
    """
    def __init__(self, game, pos, image_ref_closed, image_ref_opened, closed=True, name=None,
                 use_function=None, keep_blocking=False, long_desc=None):
        """
        Initialization method
        :param game: reference to the game variable
        :param pos: the pos (as tuple) of the item
        :param image_ref_closed: the reference for the image when closed
        :param image_ref_opened: the reference for the image when opened
        :param closed: the default starting state
        :param name: any specific name
        :param use_function: the function to be used when manipulating it
        :param keep_blocking: if set, it will be blocking even if it is manipulated
        """
        if name is None:
            name = "An openable object"

        if use_function is None:
            use_function = OpenableObjectHelper.manipulate

        self.closed = closed
        self.keep_blocking = keep_blocking
        self.closed_image = image_ref_closed
        self.opened_image = image_ref_opened

        image = image_ref_opened
        if closed:
            image = image_ref_closed

        Entity.__init__(self, game, name, pos, image, blocks=True, long_desc=long_desc,
                        actionable=ActionableEntity(function=use_function))
        self.set_in_spritegroup(-1)

    def __str__(self):
        return "{}".format(self.name)
    
    @staticmethod
    def _manipulate_generic(openable_object, entity_that_actioned):
        """
        This function will always be called by default
        :param openable_object:
        :param entity_that_actioned:
        :return:
        """
        openable_object.closed = not openable_object
        if not openable_object.keep_blocking:
            openable_object.blocks = False

        image = openable_object.opened_image
        if openable_object.closed:
            image = openable_object.closed_image
        openable_object.change(image_ref=image, sprite_level=-1, actionable=None)

    @staticmethod
    def manipulate(bus, openable_object, entity_that_actioned):
        OpenableObjectHelper._manipulate_generic(openable_object, entity_that_actioned)
        bus.publish(entity_that_actioned, {"result": c.SUCCESS,
                                           "operator": entity_that_actioned,
                                           "object":openable_object},
                             main_category=c.P_CAT_ENV,
                             sub_category=c.AC_ENV_OPEN)
        return True

    @staticmethod
    def manipulate_empty(bus, openable_object, entity_that_actioned):
        OpenableObjectHelper._manipulate_generic(openable_object, entity_that_actioned)
        openable_object.game.textbox.add = "The {} has been opened by {} but it was empty".format(openable_object.name, entity_that_actioned.name)
        return True

    @staticmethod
    def manipulate_trap(bus, openable_object, entity_that_actioned):
        OpenableObjectHelper._manipulate_generic(openable_object, entity_that_actioned)
        damage = rd.randint(1, 5)
        openable_object.game.textbox.add = "The {} has been opened by {} but it was a trap, causing {} damages".format(openable_object.name, entity_that_actioned.name, damage)
        entity_that_actioned.fighter.take_damage(damage)
        return True

    @staticmethod
    def manipulate_treasure(bus, openable_object, entity_that_actioned):
        OpenableObjectHelper._manipulate_generic(openable_object, entity_that_actioned)
        wealth = rd.randint(10, 50)
        openable_object.game.textbox.add = "The {} has been opened by {}, it contained {} wealth".format(openable_object.name, entity_that_actioned.name, wealth)
        entity_that_actioned.wealth += wealth
        return True

    @staticmethod
    def manipulate_vampire(bus, openable_object, entity_that_actioned):
        OpenableObjectHelper._manipulate_generic(openable_object, entity_that_actioned)
        openable_object.game.textbox.add = "The {} has been opened by {}, disturbing a vampire".format(openable_object.name, entity_that_actioned.name)
        pos = openable_object.game.map.get_close_available_tile(openable_object.pos,
                                                                c.T_FLOOR,
                                                                openable_object.game.objects)

        MonsterFactory.instantiate_monster(openable_object.game, "VAMPIRE_SLAVE", pos)
        return True


class EquipmentHelper(Entity):
    """
    Class used to create an Equipment
    """

    def __init__(self, game, name, pos, image_ref, slot, modifiers, long_desc=None):
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
                        equipment=EquipmentEntity(slot=slot, modifiers=modifiers),
                        long_desc=long_desc)
        self.set_in_spritegroup(-1)


class MonsterHelper(Entity):
    """
    Class used to create a Monster
    """

    def __init__(self,
                 game,
                 name,
                 pos,
                 image_ref,
                 armor=None,
                 hit_dice=None,
                 attacks=None,
                 morale=None,
                 saving_throw=None,
                 death_function=None,
                 special=None,
                 blocking_tile_list=None,
                 blocking_view_list=None,
                 vision=5,
                 speed=1,
                 long_desc=None,
                 monster_type=None):
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
        assert armor is not None, "Armor not defined for " + name
        assert hit_dice is not None, "Hit dice not defined for " + name
        assert attacks is not None, "Attacks not defined for " + name
        assert morale is not None, "Morale not defined for " + name
        assert saving_throw is not None, "Saving throw not defined for " + name

        ai = AIEntity(speed=speed)
        Entity.__init__(self, game, name, pos, image_ref, vision=vision, blocks=True,
                        blocking_tile_list=blocking_tile_list, blocking_view_list=blocking_view_list,
                        long_desc=long_desc,
                        ai=ai,
                        fighter=MonsterFighter(armor_class=armor, hit_dice=hit_dice, attacks=attacks, morale=morale,
                                               saving_throw=saving_throw, specials=special,
                                               death_function=death_function))
        self.monster_type = monster_type # the monster type is used during quest
        # the long desc is used for special boss.
        # For other, a generic is given according to the type
        if self.long_desc is None:
            if self.monster_type in MonsterFactory.long_description:
                self.long_desc = MonsterFactory.long_description[self.monster_type]
            else:
                self.long_desc = "nobody has encountered this type of creature yet"


class MonsterFactory:
    """
    Used to generate a list of Monster
    """
    long_description = {
        "BAT": "a pair of wings, and more to damage you; come in various colors",
        "DOG": "supposed to be your best friend, but in another life",
        "RAT": "skweek skweek in the night"
    }


    def __init__(self, game, seed=None):

        rd.seed(seed)
        self.game = game

        # chance of each monster
        self.monster_chances = {}
        if IMG_STYLE == c.IM_STYLE_ORYX:
            self.monster_chances["BAT"] = 10
            self.monster_chances["GREY_RAT"] = 10
            self.monster_chances["BROWN_RAT"] = 10
            self.monster_chances["DOG"] = self.from_dungeon_level([[10, 3], [15, 5]])
            self.monster_chances["SKELETON"] = 10
            self.monster_chances["SKELETON_WARRIOR"] = 8
        elif IMG_STYLE == c.IM_STYLE_DAWNLIKE:
            self.monster_chances["GIANT_ANT"] = self.from_dungeon_level([[60, 3], [15, 5]])
            self.monster_chances["BABOON"] = 20  # always shows up, even if all other monsters have 0 chance
            self.monster_chances["BADGER"] = 10  # blaireau

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

        print("Total number of monsters requested: {}".format(number_monster))
        for i in range(number_monster):
            monster = MonsterFactory.random_choice(self.monster_chances)
            MonsterFactory.instantiate_monster(self.game, monster, pos_list.pop())

    @staticmethod
    def instantiate_monster(game, monster, pos):
        if monster == "GIANT_ANT":
            MonsterHelper(game, "Giant Ant", pos, 'GIANT_ANT',
                          armor=16,
                          hit_dice=(3, 8, 0),
                          attacks=[("bite", (1, 6, 3))],
                          morale=12,
                          saving_throw=16,
                          vision=2,
                          speed=8,
                          monster_type=monster)
        elif monster == "BABOON":
            MonsterHelper(game, "Baboon", pos, 'BABOON',
                          armor=12, hit_dice=(1, 8, 0),
                          attacks=[("bite", (1, 4, 1))],
                          morale=6, saving_throw=18,
                          vision=3, speed=7, monster_type=monster)
        elif monster == "BADGER":
            MonsterHelper(game, "Badger", pos, 'BADGER', armor=15, hit_dice=(1, 8, 0),
                          attacks=[("bite", (1, 3, 1)), ("claws", (1, 2, 1))],
                          morale=7, saving_throw=18, vision=2, speed=10, monster_type=monster)
        elif monster == "BAT":
            MonsterHelper(game, "Bat", pos, 'BAT', armor=10, hit_dice=(1, 4, 0),
                          attacks=[("bite", (1, 2, 1))],
                          morale=6, saving_throw=19, vision=3, speed=6, monster_type=monster)
        elif monster == "GREY_RAT":
            MonsterHelper(game, "Giant poisounous rat", pos, 'GREY_RAT', armor=12, hit_dice=(1, 8, 0),
                          attacks=[("bite", (1, 3, 1))],
                          morale=8, saving_throw=18, vision=3, speed=8, monster_type=monster, special=[
                    lambda player=game.player: MonsterSpecials.poison_player(player, 5)])
        elif monster == "BROWN_RAT":
            MonsterHelper(game, "Giant super poisonous rat", pos, 'BROWN_RAT', armor=12, hit_dice=(1, 8, 0),
                          attacks=[("bite", (1, 3, 1))],
                          morale=8, saving_throw=18, vision=3, speed=8, monster_type=monster, special=[
                    lambda player=game.player: MonsterSpecials.poison_player(player, 20)])
        elif monster == "DOG":
            MonsterHelper(game, "Dog", pos, 'DOG', armor=11, hit_dice=(1, 8, 0),
                          attacks=[("bite", (1, 4, 1))],
                          morale=7, saving_throw=18, vision=5, speed=9, monster_type=monster)
        elif monster == "SKELETON":
            MonsterHelper(game, "Skeleton", pos, 'SKELETON', armor=12, hit_dice=(1, 8, 0),
                          attacks=[rd.choice([("club", (1, 6, 1)), ("rapier", (1, 6, 1))])],
                          morale=12, saving_throw=18, vision=4, speed=10, monster_type=monster)
        elif monster == "SKELETON_WARRIOR":
            MonsterHelper(game, "Skeleton guardian", pos, 'SKELETON_WARRIOR', armor=12, hit_dice=(1, 8, 0),
                          attacks=[rd.choice([("longsword", (1, 8, 2)), ("scimitar", (1, 6, 3))])],
                          morale=12, saving_throw=18, vision=4, speed=10, monster_type=monster)
        elif monster == "VAMPIRE_SLAVE":
            MonsterHelper(game, "Vampire Underling", pos, 'VAMPIRE', armor=17, hit_dice=(9, 8, 0),
                          attacks=[("bite", (1, 6, 9))],
                          morale=8, saving_throw=11, vision=2, speed=20, monster_type=monster)


class MonsterSpecials:

    @staticmethod
    def poison_player(player, chance_percentage):
        if rd.randint(1, 100) <= chance_percentage:
            # TODO define the function
            print("PLAYER IS POISONNNNNNNNED")

class ItemFactory:
    """
    Used to generate a list of Items
    """
    def __init__(self, game, seed=None):

        rd.seed(seed)
        self.game = game

        # chance of each monster
        self.item_chances = {}
        if IMG_STYLE == c.IM_STYLE_ORYX:
            # Chests and other openable objects
            self.item_chances["CHEST_GOLD"] = 40  # always shows up, even if all other items have 0 chance
            self.item_chances["CHEST_EMPTY"] = 10
            self.item_chances["CHEST_TRAP"] = 5
            self.item_chances["COFFIN"] = self.from_dungeon_level([[10, 3], [15, 5]])
            # Potions
            self.item_chances["HEALING_POTION_S"] = 20
            self.item_chances["HEALING_POTION_N"] = self.from_dungeon_level([[15, 1], [20, 2], [10, 3]])
            self.item_chances["HEALING_POTION_L"] = self.from_dungeon_level([[10, 2], [20, 3], [25, 5]])
            # Equipments
            self.item_chances["BASIC_SWORD"] = 10
            self.item_chances["BASIC_HELMET"] = 10
            self.item_chances["BASIC_CAPE"] = self.from_dungeon_level([[10, 2], [15, 5]])
            self.item_chances["BASIC_RING"] = self.from_dungeon_level([[15, 2], [20, 5]])

        elif IMG_STYLE == c.IM_STYLE_DAWNLIKE:
            pass

    @staticmethod
    def random_choice(chances_dict):
        # choose one option from dictionary of chances, returning its key
        chances = chances_dict.values()
        strings = list(chances_dict.keys())
        return strings[ItemFactory.random_choice_index(chances)]

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

    def build_list(self, number_item):
        pos_list = self.game.map.get_all_available_isolated_tiles(c.T_FLOOR, self.game.objects,
                                                                  without_objects=True,
                                                                  surrounded=7,
                                                                  max=number_item+1)
        assert number_item < len(pos_list), \
            "Number of item generated {} must be greater than available positions {}".format(number_item,
                                                                                                len(pos_list))

        print("Total number of item requested: {}".format(number_item))
        for i in range(number_item):
            item = ItemFactory.random_choice(self.item_chances)
            ItemFactory.instantiate_item(self.game, item, pos_list.pop())

    @staticmethod
    def instantiate_item(game, item, pos):
        if item == "CHEST_GOLD":
            OpenableObjectHelper(game, pos, "CHEST_CLOSED", "CHEST_OPEN_GOLD", name="Chest",
                                 use_function=OpenableObjectHelper.manipulate_treasure)
        elif item == "CHEST_TRAP":
            OpenableObjectHelper(game, pos, "CHEST_CLOSED", "CHEST_OPEN_TRAP", name="Chest",
                                 use_function=OpenableObjectHelper.manipulate_trap)
        elif item == "CHEST_EMPTY":
            OpenableObjectHelper(game, pos, "CHEST_CLOSED", "CHEST_OPEN_EMPTY", name="Chest",
                                 use_function=OpenableObjectHelper.manipulate_empty)
        elif item == "COFFIN":
            OpenableObjectHelper(game, pos, "COFFIN_CLOSED", "COFFIN_OPEN", name="Chest",
                                 use_function=OpenableObjectHelper.manipulate_vampire)
        # Potions
        elif item == "HEALING_POTION_S":
            ItemHelper(game, "Small Healing Potion", pos, "POTION_R_S",
                       use_function=lambda player=game.player, value=rd.randint(3, 8):
                       ItemHelper.cast_heal(player, heal_amount=value),
                       long_desc="A red glow is a promise of a small healing")
        elif item == "HEALING_POTION_N":
            ItemHelper(game, "Healing Potion", pos, "POTION_R_N",
                       use_function=lambda player=game.player, value=rd.randint(5, 11):
                       ItemHelper.cast_heal(player, heal_amount=value),
                       long_desc="Better for your health in large than in small")
        elif item == "HEALING_POTION_L":
            ItemHelper(game, "Large Healing Potion", pos, "POTION_R_L",
                       use_function=lambda player=game.player, value=rd.randint(6, 14):
                       ItemHelper.cast_heal(player, heal_amount=value),
                       long_desc="The best money can buy, don't waste it")
        # Equipments
        elif item == "BASIC_SWORD":
            EquipmentHelper(game, "Basic Sword", pos, "SWORD", slot=c.SLOT_HAND_RIGHT, modifiers={c.BONUS_STR: 2})
        elif item == "BASIC_HELMET":
            EquipmentHelper(game, "Basic Helmet", pos, "HELMET", slot=c.SLOT_HEAD, modifiers={c.BONUS_STR: -1})
        elif item == "BASIC_CAPE":
            EquipmentHelper(game, "Cape", pos, "CAPE", slot=c.SLOT_CAPE, modifiers={c.BONUS_STR: 2})
        elif item == "BASIC_RING":
            EquipmentHelper(game, "Ring", pos, "RING", slot=c.SLOT_RING, modifiers={c.BONUS_STR: -1})

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
