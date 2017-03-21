from math import sqrt
import constants as c
import random as rd


class AI:

    def __init__(self):
        self.owner = None

    def move_towards(self, pos):
        # vector from this object to the target, and distance
        dx = pos[0] - self.owner.x
        dy = pos[1] - self.owner.y
        distance = sqrt(dx ** 2 + dy ** 2)

        # normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        if distance != 0:
            dx = int(round(dx / distance))
            dy = int(round(dy / distance))
        else:
            dx = dy = 0
        return self.owner.move(dx, dy)

    def move_randomly(self):
        """
        Move by 1 around the current position. The destination should be non blocking.
        If no tiles match, then no move is taken.
        :return:
        """
        delta = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (0, -1), (1, -1), (1, 0), (1, 1)]
        rd.shuffle(delta)
        x, y = self.owner.pos
        while len(delta) > 0:
            dx, dy = delta.pop()
            if self.move_towards((x + dx, y + dy)):
                return


class AIEntity(AI):
    # AI for an entity.
    def __init__(self, speed=1, time_to_forget=3):
        AI.__init__(self)
        self.speed = speed  # the speed represents
        self.already_viewed_player = False
        self.time_since_view = 0  # this will make the monster "forgets" the player
        self.time_to_forget = time_to_forget

    def take_turn(self):

        # Is the player in the monster vision circle?
        # VIEWING MODE
        if self.owner.view(self.owner.game.player):
            if not self.already_viewed_player:
                message = rd.choice(("{} views {}".format(self.owner.name, self.owner.game.player.name),
                                     "{} growls when he sees {}".format(self.owner.name, self.owner.game.player.name),
                                     "{} looks at {}".format(self.owner.name, self.owner.game.player.name))
                                    )
                self.owner.game.bus.publish(self.owner,
                                            {"message": message},
                                            main_category=c.P_CAT_FIGHT,
                                            sub_category=c.AC_FIGHT_VARIOUS)
                self.already_viewed_player = True
            self.time_since_view = 0  # Reinit the counter since view...

            # If the monster is too far away, we try to get closer
            if self.owner.distance_to(self.owner.game.player) > c.MINIMUM_DISTANCE:
                # If we cannot get too close in straight line
                if not self.move_towards(self.owner.game.player.pos):
                    # We try moving randomly
                    self.move_randomly()
            # Else, we attack:
            elif self.owner.fighter and self.owner.game.player.fighter.body_points > 0:
                self.owner.fighter.attack(self.owner.game.player.fighter)

        # If not in vision, we try getting close or move randomly
        # WANDERING MODE
        else:
            if self.already_viewed_player:
                if not self.move_towards(self.owner.game.player.pos):
                    # We try moving randomly
                    self.move_randomly()
                self.time_since_view += 1
            else:
                self.move_randomly()

            if self.time_since_view == self.time_to_forget:
                # The monster forgot the player...
                message = rd.choice(("{} limited mind forgot {}".format(self.owner.name, self.owner.game.player.name),
                                     "{} escaped from {}".format(self.owner.game.player.name, self.owner.name))
                                    )
                self.owner.game.bus.publish(self.owner,
                                            {"message": message},
                                            main_category=c.P_CAT_FIGHT,
                                            sub_category=c.AC_FIGHT_VARIOUS)
                self.already_viewed_player = False
                self.time_since_view += 1  # This will prevent from sending again the message

        # In all cases, we schedule the next turn
        if self.owner.fighter and self.owner.fighter.hit_points > 0:
            self.owner.game.ticker.schedule_turn(self.speed, self)


class FollowingAIEntity(AI):
    # AI for an entity.
    def __init__(self, speed=10):
        AI.__init__(self)
        self.speed = speed

    def take_turn(self):
        if self.owner.distance_to(self.owner.game.player) > 2:
            self.move_towards(self.owner.game.player.pos)
        self.owner.game.ticker.schedule_turn(self.speed, self)


class CloseFightingCompanionAIEntity(AI):
    # AI for an entity.
    def __init__(self, speed=10):
        AI.__init__(self)
        self.speed = speed
        self.state = "FOLLOWING"
        self.targetted_monster = None

    def take_turn(self):
        """
        This entity will try to fight for the player
        - If no monster, will try getting close to the player -> FOLLOWING
        - If he sees a monster, will try getting closer until he can attack -> APPROACH
        - In appraoch state, if another monster is closer, switch target
        - After combat, will see if there are other enemies
        - If no other enemies, will go back to the player
        :return:
        """

        if self.owner.distance_to(self.owner.game.player) > 2:
            self.move_towards(self.owner.game.player.pos)
        self.owner.game.ticker.schedule_turn(self.speed, self)

