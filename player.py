from entities import Entity
from fighter import PlayerFighter
import utilities as ut
import random as rd

class PlayerHelper(Entity):
    """
    Microlite Swords and Sorcery Rules
    """

    STR_NAME = "strength"
    DEX_NAME = "dexterity"
    MIND_NAME = "mind"
    CHAR_NAME = "charisma"

    def __init__(self, game, pos):

        # Rolling base stats
        self.base_strength = ut.roll(6, 3)
        self.base_dexterity = ut.roll(6, 3)
        self.base_mind = ut.roll(6, 3)
        self.base_charisma = ut.roll(6, 3)
        # As a human, adding +1 to 2 random Characteristics
        characteristics = [PlayerHelper.CHAR_NAME, PlayerHelper.STR_NAME, PlayerHelper.DEX_NAME, PlayerHelper.MIND_NAME]
        rd.shuffle(characteristics)
        setattr(self, 'base_' + characteristics[0], getattr(self, characteristics[0]) + 1)
        setattr(self, 'base_' + characteristics[1], getattr(self, characteristics[1]) + 1)

        # Now starting as an adventurer
        self.base_hit_points = ut.roll(8) + self.strength
        self.base_body_points = 20

        self.saving_throw = 14

        self.experience = 0
        self.level = 1

        self.inventory = []
        self.speed = 10

        Entity.__init__(self, game, "Player", pos, "PLAYER", vision=4,
                        fighter=PlayerFighter(hit_points=self.base_hit_points, body_points=self.base_body_points,
                                              physical_combat_bonus=1, magical_combat_bonus=0))
        self.inventory_max = 100
        self.speed = 10

    @property
    def strength(self):
        return self.base_strength
    @property
    def dexterity(self):
        return self.base_dexterity
    @property
    def mind(self):
        return self.base_mind
    @property
    def charisma(self):
        return self.base_charisma

    @property
    def vision(self):
        return self.base_vision

    # BONUS: Stat bonus = (STAT-10)/3, round toward zero.
    def get_stat_bonus(self, stat):
        assert stat in (PlayerHelper.CHAR_NAME, PlayerHelper.STR_NAME, PlayerHelper.DEX_NAME, PlayerHelper.MIND_NAME)
        if stat == PlayerHelper.strength:
            return int((self.strength - 10) / 3)
        elif stat == PlayerHelper.dexterity:
            return int((self.dexterity - 10) / 3)
        elif stat == PlayerHelper.mind:
            return int((self.mind - 10) / 3)
        else:
            return int((self.charisma - 10) / 3)

    # FUNCTIONS

    def __str__(self):
        return ("{}, Position [{},{}], "
                "STR={} DEX={} MIND={} CHA={}, "
                "HP={}/{} BP={}/{} AC={} vision={}".format(self.name, self.x, self.y, self.strength, self.dexterity, self.mind, self.charisma,
                                                           self.fighter.hit_points, self.base_hit_points, self.fighter.body_points, self.base_body_points, self.fighter.armor_class, self.vision
                                                           ))

    def move(self, dx=0, dy=0):
        """Try to move the player. Return True if an action was done (either move or attack)"""
        # collision test: enemy
        for entity in self.game.objects:
            if entity != self and entity.fighter and entity.x == self.x + dx and entity.y == self.y + dy:
                self.fighter.attack(entity.fighter)
                return True

        # collision test: map data (floor, water, lava...)
        if not self.game.map.tiles[self.x + dx][self.y + dy].block_for(self):
            # now test the list of objects
            for entity in self.game.objects:
                if entity != self and entity.blocks and entity.x == self.x + dx and entity.y == self.y + dy:
                    return False
            # success
            self.x += dx
            self.y += dy
            if self.animated and (dx != 0 or dy != 0):
                self.last_direction = (dx, dy)

            return True

        return False

    # inventory functions

    def get_equipped_object_at(self, slot):
        for item in self.inventory:
            if item.equipment and item.equipment.slot == slot and item.equipment.is_equipped:
                return item
        return None

    def get_unequipped_objects(self, slot=None):
        """
        Return all equipments that are not equipped
        :param slot: a possible restriction in terms of slot
        :return: the list of inventory Items
        """
        unequipped = []
        for item in self.inventory:
            if item.equipment and not item.equipment.is_equipped:
                if slot is not None:
                    if item.equipment.slot == slot:
                        unequipped.append(item)
                else:
                    unequipped.append(item)
        return unequipped

    def get_equipped_objects(self, slot=None):
        """
        Return all equipments that are equipped
        :param slot: a possible restriction in terms of slot
        :return: the list of inventory Items
        """
        equipped = []
        for item in self.inventory:
            if item.equipment and item.equipment.is_equipped:
                if slot is not None:
                    if item.equipment.slot == slot:
                        equipped.append(item)
                else:
                    equipped.append(item)
        return equipped

    def get_non_equipment_objects(self):
        """
        Return all objects that are not equipments
        :return: the list of inventory Items
        """
        non_equipment = []
        for item in self.inventory:
            if not item.equipment or item.equipment == None:
                non_equipment.append(item)
        return non_equipment
