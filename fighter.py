import utilities as ut
import constants as c


class FighterEntity:
    """
    Combat Related properties and methods.
    Contains the following characteristics:
    * AC: the armor class
    * Hit points and Body points
    These will be redefined for the player!
    """

    # combat-related properties and methods (monster, player, NPC).
    def __init__(self, hit_points=0, body_points=0, death_function=None):
        self.owner = None

        self.hit_points = hit_points
        self.body_points = body_points

        self.death_function = death_function

    def attack(self, target):
        pass

    def heal(self, amount):
        pass

    def take_damage(self, damage):
        # apply damage if possible
        if damage > 0:
            if damage > self.hit_points:
                points_on_body = damage - self.hit_points
                self.hit_points = 0
                self.body_points -= points_on_body
            else:
                self.hit_points -= damage

        # check for death. if there's a death function, call it
        if self.hit_points <= 0 and self.body_points <= 0:
            function = self.death_function
            print("{} is dead".format(self.owner.name))
            if function is not None:
                print("Calling death function")
                function()


class MonsterFighter(FighterEntity):

    def __init__(self, armor_class=0, hit_dice=(1, 8, 0), attacks=None, morale=0, saving_throw=0,
                 specials=None, death_function=None):

        FighterEntity.__init__(self, hit_points=ut.roll(hit_dice[1], repeat=hit_dice[0]) + hit_dice[2],
                               death_function=death_function)

        if self.death_function is None:
            self.death_function = self.monster_death

        self.attack_bonus = hit_dice[0]
        self.armor_class = armor_class

        self.level = self.attack_bonus = hit_dice[0]
        self.attacks = attacks

        # The following are not used:
        self.morale = morale
        self.saving_throw = saving_throw
        self.special = specials

    @property
    def experience(self):
        # Experience is the monster hit dice squared time 5 + 50% by attacks
        xp = self.level ** 2 * 5
        for i in range(len(self.attacks)):
            xp *= 1.5
        return int(xp)

    def attack(self, other_fighter):
        # attack_rolls
        for attack in self.attacks:
            attack_roll = ut.roll(20) + self.attack_bonus
            if attack_roll > other_fighter.armor_class:
                # Hit
                damage = ut.roll(attack[1][1], repeat=attack[1][0]) + attack[1][2]
                self.owner.game.textbox.add = "{} attacks {} with {}, for {} damages".format(
                    self.owner.name.capitalize(), other_fighter.owner.name.capitalize(), attack[0], damage)
                other_fighter.take_damage(damage)
            else:
                self.owner.game.textbox.add = "{} attacks {} with {} but it was blocked!".format(
                    self.owner.name.capitalize(), other_fighter.owner.name.capitalize(), attack[0])



    def monster_death(self):
        print("GENERIC DEATH FUNCTION")
        # Attribute the xp
        self.owner.game.player.experience += self.experience
        # transform it into a nasty corpse! it doesn't block, can't be
        # attacked and doesn't move
        self.owner.game.textbox.add = self.owner.name.capitalize() + ' is dead!'
        self.owner.blocks = False
        self.owner.fighter = None
        self.owner.ai = None
        self.owner.animated = False
        self.owner.image = self.owner.game.all_images['REMAINS']
        self.owner.image_ref = 'REMAINS'
        self.owner.set_in_spritegroup(-1)
        self.owner.name = 'remains of ' + self.owner.name


class PlayerFighter(FighterEntity):

    def __init__(self, hit_points, body_points, physical_combat_bonus, magical_combat_bonus):
        FighterEntity.__init__(self, hit_points=hit_points, body_points=body_points, death_function=self.player_death)
        self.physical_combat_bonus = physical_combat_bonus
        self.magical_combat_bonus = magical_combat_bonus

    def heal(self, amount):
        # heal by the given amount, without going over the maximum
        self.hit_points += amount
        if self.hit_points > self.owner.base_hit_points:
            self.hit_points = self.owner.base_hit_points

    @property
    def armor_class(self):
        return 10 + self.owner.get_stat_bonus(self.owner.DEX_NAME) + self.owner.get_bonus(c.BONUS_ARMOR)

    def player_death(self):
        # the game ended!
        print('You died')
        self.owner.game.quit()

    def attack(self, other_fighter, attack_type="Melee"):
        # attack_rolls = 1D20 + attack bonus
        attack_bonus = self.owner.get_stat_bonus("strength") + self.physical_combat_bonus
        attack_roll = ut.roll(20) + attack_bonus
        if attack_roll > other_fighter.armor_class:
            # Hit: damage weapon (should be from inventory) + srtength bonus + class bonus
            damage = ut.roll(6) + self.owner.get_stat_bonus("strength")
            self.owner.game.textbox.add = "{} attacks {} with {}, for {} damages".format(
                self.owner.name.capitalize(), other_fighter.owner.name.capitalize(), "weapon", damage)
            other_fighter.take_damage(damage)
        else:
            self.owner.game.textbox.add = "{} attacks {} with {} but it was blocked!".format(
                self.owner.name.capitalize(), other_fighter.owner.name.capitalize(), "weapon")

    # @property
    # def vision(self):
    #     bonus = 0
    #     if hasattr(self, "owner") and hasattr(self.owner, "inventory"):
    #         bonus = sum(inv_object.equipment.vision_bonus for inv_object in self.owner.get_equipped_objects())
    #     return self.base_vision + bonus

