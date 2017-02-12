class ActionableEntity:
    """
    An actionable entity is an object which is triggered when something (player, monster...) is around (or directly in).
    This is typically a door, a trap...
    """
    def __init__(self, radius=0, actionable_by_player_only=True, function=None):
        self.radius = radius  # the speed represents
        self.owner = None
        self.actionable_by_player_only = actionable_by_player_only
        self._action_field = None
        self.function = function

    @property
    def action_field(self):
        if self._action_field is not None:
            return self._action_field
        else:
            if self.owner is not None:
                self._action_field = [self.owner.pos]
                for i in range(-self.radius, self.radius):
                    if (self.owner.pos[0] + i, self.owner.pos[1]) not in self._action_field:
                        self._action_field.append((self.owner.pos[0] + i, self.owner.pos[1]))
                    if (self.owner.pos[0], self.owner.pos[1] + i) not in self._action_field:
                        self._action_field.append((self.owner.pos[0], self.owner.pos[1] + i))
                return self._action_field
            else:
                return []

    def action(self, entity_that_actioned):
        if self.function is None:
            print("No function created")
        else:
            if self.actionable_by_player_only:
                if entity_that_actioned == self.owner.game.player:
                    self.function(self.owner.game.bus, self.owner, entity_that_actioned)
            else:
                self.function(self.owner.game.bus, entity_that_actioned)
