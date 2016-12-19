import random as rd


class Ticker(object):
    """Simple timer for roguelike games."""

    def __init__(self):
        self.ticks = 0  # current ticks--sys.maxint is 2147483647
        self.schedule = {}  # this is the dict of things to do {ticks: [obj1, obj2, ...], ticks+1: [...], ...}

    def schedule_turn(self, interval, obj):
        self.schedule.setdefault(self.ticks + interval, []).append(obj)

    def advance_ticks(self, interval):
        for i in range(interval):
            # print("Turn {}".format(self.ticks))
            things_to_do = self.schedule.pop(self.ticks, [])
            for obj in things_to_do:
                if obj is not None:
                    obj.take_turn()
            self.ticks += 1


"""
Utilities Functions.
"""


def roll(dice, repeat=1):
    """
    Roll one or multiple dice(s)
    :param dice: the type of dice - 6 for d6, 8 for d8...
    :param repeat: the number of dices of same tye to roll
    :return: the value
    """
    res = 0
    for i in range(repeat):
        res += rd.randint(1, dice)
    return res
