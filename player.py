from entities import Entity
from fighter import PlayerFighter
import utilities as ut
import random as rd
import constants as c


class PlayerHelper(Entity):
    """
    Microlite Swords and Sorcery Rules
    """

    def __init__(self, game, pos):

        self.inventory = []

        # Rolling base stats
        self.base_strength = ut.roll(6, 3)
        self.base_dexterity = ut.roll(6, 3)
        self.base_mind = ut.roll(6, 3)
        self.base_charisma = ut.roll(6, 3)
        # As a human, adding +1 to 2 random Characteristics
        characteristics = [c.CHAR_NAME, c.STR_NAME, c.DEX_NAME, c.MIND_NAME]
        rd.shuffle(characteristics)
        setattr(self, 'base_' + characteristics[0], getattr(self, characteristics[0]) + 1)
        setattr(self, 'base_' + characteristics[1], getattr(self, characteristics[1]) + 1)

        # Now starting as an adventurer
        self.base_hit_points = ut.roll(8) + self.strength
        self.base_body_points = 20

        self.saving_throw = 14

        self.experience = 0
        self.level = 1

        self.base_speed = 10

        Entity.__init__(self, game, "Player", pos, "PLAYER", vision=4,
                        fighter=PlayerFighter(hit_points=self.base_hit_points, body_points=self.base_body_points,
                                              physical_combat_bonus=1, magical_combat_bonus=0))
        self.inventory_max = 100
        self.base_speed = 10

        self.invalidate_fog_of_war = True

    @property
    def strength(self):
        return self.base_strength + self.get_bonus(c.BONUS_STR)

    @property
    def dexterity(self):
        return self.base_dexterity + self.get_bonus(c.BONUS_DEX)

    @property
    def mind(self):
        return self.base_mind + self.get_bonus(c.BONUS_MIND)

    @property
    def charisma(self):
        return self.base_charisma + self.get_bonus(c.BONUS_CHARISMA)

    @property
    def speed(self):
        return self.base_speed + self.get_bonus(c.BONUS_SPEED)

    @property
    def vision(self):
        return self.base_vision + self.get_bonus(c.BONUS_VISION)

    # BONUS: Stat bonus = (STAT-10)/3, round toward zero.
    def get_stat_bonus(self, stat):
        assert stat in (c.CHAR_NAME, c.STR_NAME, c.DEX_NAME, c.MIND_NAME)
        if stat == PlayerHelper.strength:
            return int((self.strength - 10) / 3)
        elif stat == PlayerHelper.dexterity:
            return int((self.dexterity - 10) / 3)
        elif stat == PlayerHelper.mind:
            return int((self.mind - 10) / 3)
        else:
            return int((self.charisma - 10) / 3)

    # FUNCTIONS

    def get_bonus(self, bonus_type):
        bonus = 0
        for equipped_object in self.get_equipped_objects():
            bonus += equipped_object.equipment.modifiers.get(bonus_type, 0)
        return bonus

    def __str__(self):
        return ("{}, Position [{},{}], "
                "STR={} DEX={} MIND={} CHA={}, "
                "HP={}/{} BP={}/{} AC={} vision={}".format(self.name, self.x, self.y, self.strength,
                                                           self.dexterity, self.mind, self.charisma,
                                                           self.fighter.hit_points, self.base_hit_points,
                                                           self.fighter.body_points, self.base_body_points,
                                                           self.fighter.armor_class, self.vision
                                                           ))

    def speed_cost_for(self, action):
        # Assume base 1 = move
        if action == c.AC_MOVE:
            return self.speed
        elif action == c.AC_FIGHT:
            return int(self.speed * 0.8)
        elif action == c.AC_SPELL:
            return int(self.speed * 2)
        else:
            assert 0, "Action speed not recognized - action type {}".format(action)

    def move(self, dx=0, dy=0):
        """Try to move the player. Return True if an action was done (either move or attack)"""
        # Action test
        for entity in self.game.objects:
            if entity != self and entity.actionable is not None and\
                            (self.x + dx, self.y + dy) in entity.actionable.action_field:
                self.x += dx
                self.y += dy
                entity.actionable.action(self)
                self.x -= dx
                self.y -= dy

        # collision test: enemy
        for entity in self.game.objects:
            if entity != self and entity.fighter and entity.x == self.x + dx and entity.y == self.y + dy:
                self.fighter.attack(entity.fighter)
                self.game.ticker.ticks_to_advance += self.speed_cost_for(c.AC_FIGHT)
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

            self.invalidate_fog_of_war = True

            self.game.ticker.ticks_to_advance += self.speed_cost_for(c.AC_MOVE)
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
            if not item.equipment or item.equipment is None:
                non_equipment.append(item)
        return non_equipment
