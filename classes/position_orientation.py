from enum import Enum


# Enum that stores the bot direction state
class Facing(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    UNKNOWN = 0


# Stores the position
class Position:
    def __init__(self, x = None, y = None):
        self.x = x
        self.y = y

    def is_unknown(self):
        if self.x is None or self.y is None:
            return True
        else:
            return False

    def __str__(self):
        return "bot_position: (%d, %d)" % (self.x, self.y)

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)


# Stores the orientation
class Orientation:
    facing = Facing.UNKNOWN

    def is_unknown(self):
        return self.facing == Facing.UNKNOWN