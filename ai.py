from math import sqrt


class AIEntity:
    # AI for an entity.
    def __init__(self, speed=1):
        self.speed = speed # the speed represents
        self.owner = None

    def move_towards(self, pos):
        # vector from this object to the target, and distance
        dx = pos[0] - self.owner.x
        dy = pos[1] - self.owner.y
        distance = sqrt(dx ** 2 + dy ** 2)

        # normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        return self.owner.move(dx, dy)

    def take_turn(self):
        # print( "The {} take turn".format(self.owner.name))
        if self.owner.view(self.owner.game.player):
            pass
            # self.owner.game.textbox.add = "The {} growls".format(self.owner.name)

        if self.owner.distance_to(self.owner.game.player) >= 2:
            self.move_towards(self.owner.game.player.pos)
        elif self.owner.fighter and self.owner.game.player.fighter.body_points > 0:
            self.owner.fighter.attack(self.owner.game.player.fighter)

        if self.owner.fighter and self.owner.fighter.hit_points > 0:
            self.owner.game.ticker.schedule_turn(self.speed, self)


