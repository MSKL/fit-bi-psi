from classes.position_orientation import Position


def get_server_message(msg_name):
    server_messages = {
        "SERVER_CONFIRMATION": "%s\a\b",
        "SERVER_MOVE": "102 MOVE\a\b",
        "SERVER_TURN_LEFT": "103 TURN LEFT\a\b",
        "SERVER_TURN_RIGHT": "104 TURN RIGHT\a\b",
        "SERVER_PICK_UP": "105 GET MESSAGE\a\b",
        "SERVER_LOGOUT": "106 LOGOUT\a\b",
        "SERVER_OK": "200 OK\a\b",
        "SERVER_LOGIN_FAILED": "300 LOGIN FAILED\a\b",  # 16 chars
        "SERVER_SYNTAX_ERROR": "301 SYNTAX ERROR\a\b",  # 16 chars
        "SERVER_LOGIC_ERROR": "302 LOGIC ERROR\a\b"
    }
    # Get returns none if the key was not found
    return server_messages.get(msg_name)


def get_client_message(msg_name):
    client_messages = {
        "CLIENT_USERNAME": "%s\a\b",
        "CLIENT_CONFIRMATION": "%s\a\b",
        "CLIENT_OK": "OK %d %d\a\b",
        "CLIENT_RECHARGING": "RECHARGING\a\b",
        "CLIENT_FULL_POWER": "FULL POWER\a\b",
        "CLIENT_MESSAGE": "%s\a\b"
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