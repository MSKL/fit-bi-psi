from classes.position_orientation import Position
from enum import Enum


class MSG(Enum):
    SERVER_CONFIRMATION = 0
    SERVER_MOVE = 1
    SERVER_TURN_LEFT = 2
    SERVER_TURN_RIGHT = 3
    SERVER_PICK_UP = 4
    SERVER_LOGOUT = 5
    SERVER_OK = 6
    SERVER_LOGIN_FAILED = 7
    SERVER_SYNTAX_ERROR = 8
    SERVER_LOGIC_ERROR = 9
    CLIENT_USERNAME = 10
    CLIENT_CONFIRMATION = 11
    CLIENT_OK = 12
    CLIENT_RECHARGING = 13
    CLIENT_FULL_POWER = 14
    CLIENT_MESSAGE = 15


# Get the length of the client's message
def msg_len(msg = MSG.CLIENT_OK):
    if msg == MSG.CLIENT_OK:
        return 12
    elif msg == MSG.CLIENT_CONFIRMATION:
        return 7
    elif msg == MSG.CLIENT_USERNAME:
        return 12
    elif msg == MSG.CLIENT_RECHARGING:
        return 12
    elif msg == MSG.CLIENT_FULL_POWER:
        return 12
    elif msg == MSG.CLIENT_MESSAGE:
        return 100
    else:
        raise Exception("Unknown message!")


def get_server_message(msg_name):
    server_messages = {
        MSG.SERVER_CONFIRMATION: "%s\a\b",
        MSG.SERVER_MOVE: "102 MOVE\a\b",
        MSG.SERVER_TURN_LEFT: "103 TURN LEFT\a\b",
        MSG.SERVER_TURN_RIGHT: "104 TURN RIGHT\a\b",
        MSG.SERVER_PICK_UP: "105 GET MESSAGE\a\b",
        MSG.SERVER_LOGOUT: "106 LOGOUT\a\b",
        MSG.SERVER_OK: "200 OK\a\b",
        MSG.SERVER_LOGIN_FAILED: "300 LOGIN FAILED\a\b",  # 16 chars
        MSG.SERVER_SYNTAX_ERROR: "301 SYNTAX ERROR\a\b",  # 16 chars
        MSG.SERVER_LOGIC_ERROR: "302 LOGIC ERROR\a\b"
    }
    # Get returns none if the key was not found
    return server_messages.get(msg_name)


def get_client_message(msg_name):
    client_messages = {
        MSG.CLIENT_USERNAME: "%s\a\b",
        MSG.CLIENT_CONFIRMATION: "%s\a\b",
        MSG.CLIENT_OK: "OK %d %d\a\b",
        MSG.CLIENT_RECHARGING: "RECHARGING\a\b",
        MSG.CLIENT_FULL_POWER: "FULL POWER\a\b",
        MSG.CLIENT_MESSAGE: "%s\a\b"
    }
    # Get returns none if the key was not found
    return client_messages.get(msg_name)

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