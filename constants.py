# This file holds all the constants for all the game.
# Contrary to settings, these are things that should not be changed.

# Image Styles
IM_STYLE_DAWNLIKE = "DAWNLIKE"
IM_STYLE_ORYX = "ORYX"
IM_STYLE_PIXEL = "PIXEL"

# Utilities - class Publisher
P_ALL = "ALL"
P_CAT_LOG = "LOG"
P_CAT_INFO = "INFO"

# Game - Game States
GAME_STATE_PLAYING = 'Playing'
GAME_STATE_INVENTORY = 'Inventory'
GAME_STATE_MAP = 'Minimap'
GAME_STATE_CHARACTER = 'Character'

# Tilemap - Tiles
# Type of Tiles
T_VOID = '0'
T_WALL = '1'
T_FLOOR = '2'

# Item
SLOT_HEAD = "Head"
SLOT_CAPE = "Cape"
SLOT_TORSO = "Torso"
SLOT_LEG = "Leg"
SLOT_FOOT = "Foot"
SLOT_HAND_LEFT = "Left Hand"
SLOT_HAND_RIGHT = "Right Hand"
SLOT_BOW = "Bow"
SLOT_GLOVE = "Glove"
SLOT_QUIVER = "Quiver"
SLOT_RING = "Ring"
SLOT_NECKLACE = "Necklace"

BONUS_STR = "Strength"
BONUS_DEX = "Dexterity"
BONUS_MIND = "Mind"
BONUS_CHARISMA = "Charisma"
BONUS_VISION = "Vision"
BONUS_SPEED = "Speed"
BONUS_ARMOR = "Armor"

# Player

STR_NAME = "strength"
DEX_NAME = "dexterity"
MIND_NAME = "mind"
CHAR_NAME = "charisma"

FAILURE = "failure"
SUCCESS = "success"

# Action type
AC_MOVE = "move"
AC_FIGHT = "fight"  # A fight message will always have the name of the attacked ("attacker_name"),
# defender ("defender_name"), position ("pos"), room ("room")
# -> Sub:
ACS_KILL = "kill"  # In that case, register xp gained ("xp") and gold ("gold")
ACS_HIT = "hit"  # In that case, register attack type ("attack_type"), amount of damage ("damage"), result ("result")
ACS_VARIOUS = "various"  # Misc actions, like flee the combat or other

AC_SPELL = "cast"
# -> Sub for item
AC_ITEM = "ITEM"
AC_ITEM_GRAB = "GRAB"
AC_ITEM_DUMP = "DUMP"
AC_ITEM_EQUIP = "EQUIP"
AC_ITEM_UNEQUIP = "UNEQUIP"
AC_ITEM_USE = "USE"
