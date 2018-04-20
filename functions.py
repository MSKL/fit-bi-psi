from classes.position import Position
from classes.exceptions import *
from enum import Enum
import re


class MSG(Enum):
    """Enum containing all possible types of messages that are used in the communication"""
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


def msg_len(msg):
    """Get the length of the client's message"""
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
    """Get the content of the message from server"""
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
    """Get the content of the message from the client"""
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
    """Create a hash form the given username"""
    stripped = end_strip(username)
    char_sum = 0
    for ch in stripped:
        char_sum += ord(ch)
    return (char_sum * 1000) % 65536


def add_key(in_num, KEY):
    """Add a key to the hash"""
    return (in_num + KEY) % 65536


def to_bytes(source):
    """Convert string to bytes"""
    return bytes(str(source), 'utf-8')


def end_add(source):
    """Add the ending separator"""
    return str(source) + "\a\b"


def end_strip(source):
    """Remove the ending separator"""
    return str(source).rstrip("\a\b")


def color_print(color, text):
    """Print in a colored terminal"""
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


def extract_message(raw_msg, client_msg):
    """Check the whole message. Extract the Position data if necessary."""
    # If received recharging, don't do any checks
    if raw_msg == get_client_message(MSG.CLIENT_RECHARGING):
        return raw_msg

    # Check the length
    if len(raw_msg) == 0 and client_msg != MSG.CLIENT_MESSAGE:
        raise SyntaxErrorException("Input string length is 0")

    if client_msg == MSG.CLIENT_OK:
        if not re.match("^OK -?[0-9]{1,7} -?[0-9]{1,7}\x07\x08$", raw_msg):
            raise SyntaxErrorException("CLIENT_OK")
        s = end_strip(raw_msg)
        s = s.split(" ")
        return Position(int(s[1]), int(s[2]))
    elif client_msg == MSG.CLIENT_FULL_POWER:
        if raw_msg != get_client_message(MSG.CLIENT_FULL_POWER):
            raise LogicErrorException("CLIENT_FULL_POWER confirmation does not match. %s != %s"
                                % (raw_msg, get_client_message(MSG.CLIENT_FULL_POWER)))
        return raw_msg
    elif client_msg == MSG.CLIENT_CONFIRMATION:
        if not re.match("^[0-9]{1,5}\x07\x08$", raw_msg):
            raise SyntaxErrorException("CLIENT_CONFIRMATION: on string %s" % str(raw_msg))
        return raw_msg
    elif client_msg == MSG.CLIENT_MESSAGE:
        return raw_msg
    elif client_msg == MSG.CLIENT_USERNAME:
        return raw_msg


def clamp(val, m_min, m_max):
    """Clamps a value between min and max"""
    return max(min(val, m_max), m_min)

