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


""" Generic finite state machine class
    Initialise the class with a list of tuples - or by adding transitions
    Tony Flury - November 2012
    Released under an MIT License - free to use so long as the author and other contributers are credited.
"""


class FiniteStateMachine(object):
    """ A simple to use finite state machine class.
        Allows definition of multiple states, condition functions from state to state and optional callbacks
    """

    def __init__(self, states=[]):
        self._states = states
        self._currentState = None

    def start(self, startState=None):
        """ Start the finite state machine
        """
        if not startState or not (startState in [x[0] for x in self._states]):
            raise ValueError("Not a valid start state")
        self._currentState = startState

    def stop(self):
        """ Stop the finite state machine
        """
        self._currentState = None

    def addTransition(self, fromState, toState, condition, callback=None):
        """ Add a state transition to the list, order is irellevant, loops are undetected
            Can only add a transition if the state machine isn't started.
        """
        if not self._currentState:
            raise ValueError("StateMachine already Started - cannot add new transitions")

        # add a transition to the state table
        self._states.append((fromState, toState, condition, callback))

    def event(self, value):
        """ Trigger a transition - return a tuple (<new_state>, <changed>)
            Raise an exception if no valid transition exists.
            Callee needs to determine if the value will be consumed or re-used
        """
        if not self._currentState:
            raise ValueError("StateMachine not Started - cannot process event")

        # get a list of transitions which are valid
        self.nextStates = [x for x in self._states
                           if x[0] == self._currentState
                           and (x[2] == True or (callable(x[2]) and x[2](value)))]

        if not self.nextStates:
            raise ValueError("No Transition defined from state {0} with value '{1}'".format(self._currentState, value))
        elif len(self.nextStates) > 1:
            raise ValueError("Ambiguous transitions from state {0} with value '{1}' ->  New states defined {2}".format(
                self._currentState, value, [x[0] for x in self.nextStates]))
        else:
            if len(self.nextStates[0]) == 4:
                current, next, condition, callback = self.nextStates[0]
            else:
                current, next, condition = self.nextStates[0]
                callback = None

            self._currentState, changed = (next, True) \
                if self._currentState != next else (next, False)

            # Execute the callback if defined
            if callable(callback):
                callback(self, value)

            return self._currentState, changed

    def currentState(self):
        """ Return the current State of the finite State machine
        """
        return self._currentState


# -------------------------------------------------------------------------------------------------
# Example classes to demonstrate the use of the Finite State Machine Class
# They implement a simple lexical tokeniser.
# These classes are not neccesary for the FSM class to work.
# -------------------------------------------------------------------------------------------------

# Simple storage object for each token
class token(object):
    def __init__(self, type):
        self.tokenType = type
        self.tokenText = ""

    def addCharacter(self, char):
        self.tokenText += char

    def __repr__(self):
        return "{0}<{1}>".format(self.tokenType, self.tokenText)


# Token list object - demonstrating the definition of state machine callbacks
class tokenList(object):
    def __init__(self):
        self.tokenList = []
        self.currentToken = None

    def StartToken(self, fss, value):
        self.currentToken = token(fss.currentState())
        self.currentToken.addCharacter(value)

    def addCharacter(self, fss, value):
        self.currentToken.addCharacter(value)

    def EndToken(self, fss, value):
        self.tokenList.append(self.currentToken)
        self.currentToken = None


# Example code - showing population of the state machine in the constructor
# the Machine could also be constructed by multiple calls to addTransition method
# Example code is a simple tokeniser
# Machine transitions back to the Start state whenever the end of a token is detected
if __name__ == "__main__":
    t = tokenList()

    fs = FiniteStateMachine([("Start", "Start", lambda x: x.isspace()),
                             ("Start", "Identifier", str.isalpha, t.StartToken),
                             ("Identifier", "Identifier", str.isalnum, t.addCharacter),
                             ("Identifier", "Start", lambda x: not x.isalnum(), t.EndToken),
                             ("Start", "Operator", lambda x: x in "=+*/-()", t.StartToken),
                             ("Operator", "Start", True, t.EndToken),
                             ("Start", "Number", str.isdigit, t.StartToken),
                             ("Number", "Number", lambda x: x.isdigit() or x == ".", t.addCharacter),
                             ("Number", "Start", lambda x: not x.isdigit() and x != ".", t.EndToken),
                             ("Start", "StartQuote", lambda x: x == "\'"),
                             ("StartQuote", "String", lambda x: x != "\'", t.StartToken),
                             ("String", "String", lambda x: x != "\'", t.addCharacter),
                             ("String", "EndQuote", lambda x: x == "\'", t.EndToken),
                             ("EndQuote", "Start", True)])

    fs.start("Start")

    a = "    x123=MyString+123.65-'hello'*value"
    c = 0
    while c < len(a):
        ret = fs.event(a[c])
        # Make sure a transition back to start (from something else) does not consume the character.
        if ret[0] != "Start" or (ret[0] == "Start" and ret[1] == False):
            c += 1
    ret = fs.event("")

    print(t.tokenList)
