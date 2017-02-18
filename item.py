import constants as c
import settings as st
import random as rd
import utilities as ut

import entities


class ItemEntity:
    """
    Warning: this should never be instantiated directly, but more via the ItemHelper class
    Exception: in entity, when adding an equipment
    """

    FUNCTION_CANCELLED = 'cancelled'

    # an item that can be picked up and used.
    def __init__(self, use_function=None, identification=None, number_use=1):
        self.use_function = use_function
        self.owner = None
        self.identification = identification
        self.identified = self.identification is None
        self.number_use = number_use

    def pick_up(self):
        # add to the player's inventory and remove from the map
        result = "success"
        if len(self.owner.game.player.inventory) >= 60:
            result = "failure"
        else:
            self.owner.game.player.inventory.append(self.owner)
            self.owner.game.objects.remove(self.owner)
            for group in self.owner.game.all_groups:
                group.remove(self.owner)
        self.owner.game.bus.publish(self.owner, {"item": self.owner,
                                                 "result": result},
                                    main_category=c.P_CAT_ITEM,
                                    sub_category=c.AC_ITEM_GRAB)

        # special case: automatically equip, if the corresponding equipment slot is unused
        equipment = self.owner.equipment
        if equipment and self.owner.game.player.get_equipped_object_at(equipment.slot) is None:
            equipment.equip()

    def drop(self):
        # special case: if the object has the Equipment component, dequip it before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()

        # add to the map and remove from the player's inventory. also, place it at the player's coordinates
        self.owner.game.objects.append(self.owner)
        self.owner.game.player.inventory.remove(self.owner)
        self.owner.set_in_spritegroup(-1)
        self.owner.x = self.owner.game.player.x
        self.owner.y = self.owner.game.player.y
        self.owner.game.bus.publish(self.owner, {"item": self.owner},
                                    main_category=c.P_CAT_ITEM,
                                    sub_category=c.AC_ITEM_DUMP)

    def use(self):
        # special case: if the object has the Equipment component, the "use" action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        if self.use_function is None:
            self.owner.game.bus.publish(self.owner, {"item": self.owner, "result": c.FAILURE},
                                        main_category=c.P_CAT_ITEM,
                                        sub_category=c.AC_ITEM_USE)
        else:
            if self.use_function() != ItemEntity.FUNCTION_CANCELLED:
                self.number_use -= 1
                if self.number_use == 0:
                    self.owner.game.player.inventory.remove(self.owner)  # destroy after use, unless it was cancelled

    def identify(self, force=False):

        if self.identified:
            return True
        else:
            # TODO Make it real
            if not force:
                modifier = 0
                if c.IDENTIFICATION_MODIFIER in self.identification:
                    modifier = self.identification["identification_modifier"]

                # Test: can we identify
                roll = ut.roll(20) + modifier
                if roll > self.owner.game.player.mind:
                    print("Impossible to identify")
                    return False

            self.identified = True
            assert self.owner is not None, "Item doesn't seem to have an owner??"
            self.owner.long_desc = self.owner.long_desc_after
            self.owner.name = self.owner.name_after
            return True


class ItemHelper(entities.Entity):
    """
    Class used to create an Item
    """
    def __init__(self, game, name, pos, image_ref, use_function, long_desc=None, identification=None, number_use=1):
        """
        Initialization method
        :param game: reference to the game variable
        :param name: the name of the Item
        :param pos: the pos (as tuple) of the item
        :param image_ref: the reference for the image
        :param use_function: the function to be used
        :param long_desc: the full description of the item
        :param identification: the settings for identification
        :param number_use: the number of times the item can be used
        Sample: use_function=lambda player=self.player: Item.cast_heal(player)
        """
        entities.Entity.__init__(self, game, name, pos, image_ref, blocks=False,
                                 item=ItemEntity(use_function=use_function,
                                                 identification=identification,
                                                 number_use=number_use),
                                 long_desc=long_desc)
        self.set_in_spritegroup(-1)

    @staticmethod
    def cast_heal(entity, heal_amount=3, expression='FIX'):

        assert expression in ('FIX', 'PERCENTAGE'), "Cast heal works with FIX or PERCENTAGE argument"

        # heal the entity - if already at max xp we don't do anything
        if entity.fighter.hit_points == entity.base_hit_points:
            entity.game.bus.publish(entity, {"result": c.FAILURE,
                                             "message": 'You are already at full health.'},
                                    main_category=c.P_CAT_ITEM,
                                    sub_category=c.AC_ITEM_USE)
            return ItemEntity.FUNCTION_CANCELLED

        entity.game.bus.publish(entity, {"result": c.SUCCESS,
                                         "message": 'Your wounds start to feel better.'},
                                main_category=c.P_CAT_ITEM,
                                sub_category=c.AC_ITEM_USE)
        entity.fighter.heal(heal_amount)


class ItemFactory:
    """
    Used to generate a list of Items
    """
    def __init__(self, game, seed=None):

        rd.seed(seed)
        self.game = game

        # chance of each monster
        self.item_chances = {}
        if st.IMG_STYLE == c.IM_STYLE_ORYX:
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

        elif st.IMG_STYLE == c.IM_STYLE_DAWNLIKE:
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
            entities.OpenableObjectHelper(game, pos, "CHEST_CLOSED", "CHEST_OPEN_GOLD", name="Chest",
                                          use_function=entities.OpenableObjectHelper.manipulate_treasure)
        elif item == "CHEST_TRAP":
            entities.OpenableObjectHelper(game, pos, "CHEST_CLOSED", "CHEST_OPEN_TRAP", name="Chest",
                                          use_function=entities.OpenableObjectHelper.manipulate_trap)
        elif item == "CHEST_EMPTY":
            entities.OpenableObjectHelper(game, pos, "CHEST_CLOSED", "CHEST_OPEN_EMPTY", name="Chest",
                                          use_function=entities.OpenableObjectHelper.manipulate_empty)
        elif item == "COFFIN":
            entities.OpenableObjectHelper(game, pos, "COFFIN_CLOSED", "COFFIN_OPEN", name="Chest",
                                          use_function=entities.OpenableObjectHelper.manipulate_vampire)
        # Potions: 70% chance 1 dose, otherwise 1d6 dose
        elif item == "HEALING_POTION_S":
            dose = 1
            long_desc = "a red glow is a promise of a small healing"
            if ut.roll(100) > 70:
                dose = ut.roll(5) + 1
                long_desc = "a red glow is a promise of a small healing, enough for {} uses".format(dose)

            ItemHelper(game, "Small Healing Potion", pos, "POTION_R_S",
                       use_function=lambda player=game.player, value=rd.randint(3, 8):
                       ItemHelper.cast_heal(player, heal_amount=value),
                       long_desc="a red glow is a promise of a small healing",
                       number_use=dose,
                       identification={c.NOT_IDENTIFIED_NAME: "potion",
                                       c.NOT_IDENTIFIED_DESC: "reddish liquid",
                                       c.IDENTIFICATION_MODIFIER: -2})
        elif item == "HEALING_POTION_N":
            ItemHelper(game, "Healing Potion", pos, "POTION_R_N",
                       use_function=lambda player=game.player, value=rd.randint(5, 11):
                       ItemHelper.cast_heal(player, heal_amount=value),
                       long_desc="better for your health in large than in small",
                       identification={c.NOT_IDENTIFIED_NAME: "potion",
                                       c.NOT_IDENTIFIED_DESC: "large quantity of reddish liquid"})
        elif item == "HEALING_POTION_L":
            ItemHelper(game, "Large Healing Potion", pos, "POTION_R_L",
                       use_function=lambda player=game.player, value=rd.randint(6, 14):
                       ItemHelper.cast_heal(player, heal_amount=value),
                       long_desc="the best money can buy, don't waste it",
                       identification={c.NOT_IDENTIFIED_NAME: "potion",
                                       c.NOT_IDENTIFIED_DESC: "slightly red",
                                       c.IDENTIFICATION_MODIFIER: 4})
        # Equipments
        elif item == "BASIC_SWORD":
            EquipmentHelper(game, "Basic Sword", pos, "SWORD", slot=c.SLOT_HAND_RIGHT, modifiers={c.BONUS_STR: 2})
        elif item == "BASIC_HELMET":
            EquipmentHelper(game, "Basic Helmet", pos, "HELMET", slot=c.SLOT_HEAD, modifiers={c.BONUS_STR: -1})
        elif item == "BASIC_CAPE":
            EquipmentHelper(game, "Cape", pos, "CAPE", slot=c.SLOT_CAPE, modifiers={c.BONUS_STR: 2})
        elif item == "BASIC_RING":
            EquipmentHelper(game, "Ring", pos, "RING", slot=c.SLOT_RING, modifiers={c.BONUS_STR: -1})


class EquipmentHelper(entities.Entity):
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
        entities.Entity.__init__(self, game, name, pos, image_ref, blocks=False,
                                 equipment=EquipmentEntity(slot=slot, modifiers=modifiers),
                                 long_desc=long_desc)
        self.set_in_spritegroup(-1)


class EquipmentEntity:

    # an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self, slot, modifiers):

        self.slot = slot
        self.is_equipped = False
        self.modifiers = modifiers

        # an equipment has an item object attached
        self.item = ItemEntity()

        self.owner = None

    def toggle_equip(self):  # toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        # if the slot is already being used, dequip whatever is there first
        old_equipment = self.owner.game.player.get_equipped_object_at(self.slot)
        if old_equipment is not None:
            old_equipment.equipment.dequip()

        # equip object and show a message about it
        self.is_equipped = True
        self.owner.game.bus.publish(self.owner, {"item": self.owner, "slot": self.slot},
                                    main_category=c.P_CAT_ITEM,
                                    sub_category=c.AC_ITEM_EQUIP)

    def dequip(self):
        # dequip object and show a message about it
        if not self.is_equipped:
            return
        self.is_equipped = False
        self.owner.game.bus.publish(self.owner, {"item": self.owner, "slot": self.slot},
                                    main_category=c.P_CAT_ITEM,
                                    sub_category=c.AC_ITEM_UNEQUIP)
