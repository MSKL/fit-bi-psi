from enum import Enum


# Enum that stores the bot direction state
class Facing(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    UNKNOWN = 0


# Stores the orientation
class Rotation:
    facing = Facing.UNKNOWN

    def is_unknown(self):
        return self.facing == Facing.UNKNOWN