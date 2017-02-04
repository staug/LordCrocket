import constants as c

class ItemEntity:
    """
    Warning: this should never be instantiated directly, but more via the ItemHelper class
    """

    FUNCTION_CANCELLED = 'cancelled'

    # an item that can be picked up and used.
    def __init__(self, use_function=None):
        self.use_function = use_function
        self.owner = None

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
                                                 "result":result},
                                    main_category=c.AC_ITEM,
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
        self.owner.game.player_min1_sprite_group.append(self.owner)
        self.owner.x = self.owner.game.player.x
        self.owner.y = self.owner.game.player.y
        self.owner.game.bus.publish(self.owner, {"item": self.owner},
                                    main_category=c.AC_ITEM,
                                    sub_category=c.AC_ITEM_DUMP)

    def use(self):
        # special case: if the object has the Equipment component, the "use" action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        if self.use_function is None:
            self.owner.game.bus.publish(self.owner, {"item": self.owner, "result": c.FAILURE},
                                        main_category=c.AC_ITEM,
                                        sub_category=c.AC_ITEM_USE)
        else:
            if self.use_function() != ItemEntity.FUNCTION_CANCELLED:
                self.owner.game.player.inventory.remove(self.owner)  # destroy after use, unless it was cancelled


class EquipmentEntity:

    # an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self, slot, modifiers):

        self.slot = slot
        self.is_equipped = False
        self.modifiers = modifiers

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
                                    main_category=c.AC_ITEM,
                                    sub_category=c.AC_ITEM_EQUIP)

    def dequip(self):
        # dequip object and show a message about it
        if not self.is_equipped:
            return
        self.is_equipped = False
        self.owner.game.bus.publish(self.owner, {"item": self.owner, "slot": self.slot},
                                    main_category=c.AC_ITEM,
                                    sub_category=c.AC_ITEM_UNEQUIP)




