# Stores the position
class Position:
    def __init__(self, x=None, y=None):
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