from classes.position_orientation import Position
from enum import Enum


# Enum containing all possible types of messages that are used in the communication
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
def msg_len(msg):
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


# Get the content of the message from server
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


# Get the content of the message fro the client
def get_client_message(msg_name):
    client_messages = {
        MSG.CLIENT_USERNAME: "%s",
        MSG.CLIENT_CONFIRMATION: "%s",
        MSG.CLIENT_OK: "OK %d %d",
        MSG.CLIENT_RECHARGING: "RECHARGING",
        MSG.CLIENT_FULL_POWER: "FULL POWER",
        MSG.CLIENT_MESSAGE: "%s"
    }
    # Get returns none if the key was not found
    return client_messages.get(msg_name)


# Create a hash form the given username
def hash_username(username):
    char_sum = 0
    for ch in username:
        char_sum += ord(ch)
    return (char_sum * 1000) % 65536


# Add a key to the hash
def add_key(in_num, KEY):
    return (in_num + KEY) % 65536


# Convert string -> bytes
def to_bytes(source):
    return bytes(str(source), 'utf-8')


# Add the ending separator
def end_add(source):
    return str(source) + "\a\b"


# Remove the ending separator
def end_strip(source):
    return str(source).strip("\a\b")


# Print in a colored terminal
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


# Extract data from a message. If faulty throw an an exception.
def extract_message(raw_msg, client_msg):
    raw_msg = end_strip(raw_msg)

    # Check the length TODO: Should not be needed
    if len(raw_msg) > (msg_len(client_msg) - 2):
        raise Exception("Too many characters")

    if len(raw_msg) == 0 and client_msg != MSG.CLIENT_MESSAGE:
        raise Exception("Input string length is 0")

    if client_msg == MSG.CLIENT_OK:
        s = raw_msg.split(" ")
        if s[0] != "OK" or s[1] == "" or s[2] == "":
            raise Exception("CLIENT_OK Exception")
        return Position(int(s[1]), int(s[2]))

    if client_msg == MSG.CLIENT_RECHARGING:
        if raw_msg != get_client_message(MSG.CLIENT_RECHARGING):
            raise Exception("CLIENT_RECHARGING Exception")
        return raw_msg

    if client_msg == MSG.CLIENT_FULL_POWER:
        if raw_msg != get_client_message(MSG.CLIENT_FULL_POWER):
            raise Exception("CLIENT_FULL_POWER Exception")
        return raw_msg

    if client_msg == MSG.CLIENT_CONFIRMATION:
        return raw_msg

    if client_msg == MSG.CLIENT_MESSAGE:
        return raw_msg

    if client_msg == MSG.CLIENT_USERNAME:
        return raw_msg








