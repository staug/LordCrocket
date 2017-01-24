import random as rd
import constants as c


class Ticker(object):
    """Simple timer for roguelike games."""

    def __init__(self):
        self.ticks = 0  # current ticks--sys.maxint is 2147483647
        self.schedule = {}  # this is the dict of things to do {ticks: [obj1, obj2, ...], ticks+1: [...], ...}
        self.ticks_to_advance = 0

    def schedule_turn(self, interval, obj):
        self.schedule.setdefault(self.ticks + interval, []).append(obj)

    def _advance_ticks(self, interval):
        for i in range(interval):
            things_to_do = self.schedule.pop(self.ticks, [])
            for obj in things_to_do:
                if obj is not None:
                    obj.take_turn()
            self.ticks += 1

    def advance_ticks(self):
        if self.ticks_to_advance > 0:
            self._advance_ticks(self.ticks_to_advance)
            self.ticks_to_advance = 0

    def unregister(self, obj):
        if obj is not None:
            for key in self.schedule.keys():
                while obj in self.schedule[key]:
                    # copy = self.schedule[key][:]
                    # copy.remove(obj)
                    # self.schedule[key] = copy[:]
                    self.schedule[key].remove(obj)


class Publisher(object):
    """
    Dispatch messages
    Messages have two categories (defined in constants):
    * Main: like log, fight, exploration, inventory
    * Sub: precises the main, optional.
    Messgae content is a dictionary
    """

    def __init__(self):
        self._specialized_list = {}  # Subscribe to main and a list of sub_category

    def register(self,
                 object_to_register,
                 main_category=c.P_ALL,
                 sub_category=c.P_ALL,
                 function_to_call=None):
        """
        Register an object so that we
        :param object_to_register: the object that will be notified.
        Note that the same object may be registered multiple time, with different functions to be called or
        different category of interest, so that we are effectively saving the method only
        :param main_category: one or multiple (in list) categories to register.
        :param sub_category: one or multiple (in list) specialized sub categories to register
        :param function_to_call: the method to be called.
        :return:
        """
        if function_to_call is None:
            assert hasattr(object_to_register, "notify"), \
                "Object {} has no notify method and has not precised the " \
                "function to be called".format(object_to_register)
            function_to_call = getattr(object_to_register, "notify")
        if type(sub_category) is not (list or tuple):
            sub_category = [sub_category]
        if type(main_category) is not (list or tuple):
            main_category = [main_category]
        for category in main_category:
            for sub in sub_category:
                key = "{}#{}".format(category, sub)
                if key not in self._specialized_list.keys():
                    self._specialized_list[key] = [function_to_call]
                elif function_to_call not in self._specialized_list[key]:
                    self._specialized_list[key].append(function_to_call)

    def unregister_all(self, object_to_unregister):
        # We need to parse all the lists..
        # and the same object may have been registered with different functions
        for key in self._specialized_list.keys():
            list_to_remove = []
            list_to_parse = self._specialized_list[key]
            for function in list_to_parse:
                if function.__self__ == object_to_unregister:
                    list_to_remove.append(function)
            for function in list_to_remove:
                self._specialized_list[key].remove(function)

    def publish(self, source, message, main_category=c.P_ALL, sub_category=c.P_ALL):
        assert type(message) is dict, "Message {} is not a dict".format(message)
        message["SOURCE"] = source
        broadcasted_list = []
        message["MAIN_CATEGORY"] = main_category
        message["SUB_CATEGORY"] = sub_category
        if type(sub_category) is not (list or tuple):
            sub_category = [sub_category]
        if type(main_category) is not (list or tuple):
            main_category = [main_category]

        # By default, we always broadcast to "ALL"
        if c.P_ALL not in main_category:
            main_category.append(c.P_ALL)
        if c.P_ALL not in sub_category:
            sub_category.append(c.P_ALL)

        for category in main_category:
            for sub in sub_category:
                message["BROADCAST_MAIN_CATEGORY"] = category
                message["BROADCAST_SUB_CATEGORY"] = category
                key = "{}#{}".format(category, sub)
                if key in self._specialized_list:
                    for function in self._specialized_list[key]:
                        if function not in broadcasted_list:  # Need to be sure not to send two times the message
                            function(message)
                            broadcasted_list.append(function)

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