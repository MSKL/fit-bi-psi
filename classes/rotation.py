from enum import Enum


class Facing(Enum):
    """Enum that stores the bot direction state"""
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    UNKNOWN = 0


class Rotation:
    """Stores the orientation"""
    facing = Facing.UNKNOWN

    def is_unknown(self):
        return self.facing == Facing.UNKNOWN
