
class Position:
    x = None
    y = None

    def __init__(self, x = None, y = None):
        self.x = x
        self.y = y

    def is_set(self):
        if self.x is None or self.y is None:
            return False
        else:
            return True

    def __str__(self):
        return "bot_position: %d %d" % (self.x, self.y)