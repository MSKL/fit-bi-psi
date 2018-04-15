from position import Position

def hash_username(username):
    char_sum = 0
    for ch in username:
        char_sum += ord(ch)
    return (char_sum * 1000) % 65536


def add_key(in_num, KEY):
    return (in_num + KEY) % 65536


def to_bytes(source):
    return bytes(str(source), 'utf-8')


def end_add(source):
    return str(source) + "\a\b"


def end_strip(source):
    return str(source).strip("\a\b")


def convert_to_position(source):
    s = source.split(" ")
    return Position(int(s[1]), int(s[2]))


def color_print(color, text):
    c = {
        "PURPLE": '\033[95m',
        "CYAN": '\033[96m',
        "DARKCYAN": '\033[36m',
        "BLUE": '\033[94m',
        "GREEN": '\033[92m',
        "YELLOW": '\033[93m',
        "RED": '\033[91m',
        "LIGHTMAGENTA": '\033[95m',
        "BOLD": '\033[1m',
        "UNDERLINE": '\033[4m',
        "END": '\033[0m'
    }
    col = c.get(color)
    print(col + text + c["END"])