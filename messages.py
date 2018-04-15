def get_server_message(msg_name):
    server_messages = {
        "SERVER_CONFIRMATION": "%s\a\b",
        "SERVER_MOVE": "102 MOVE\a\b",
        "SERVER_TURN_LEFT": "103 TURN LEFT\a\b",
        "SERVER_TURN_RIGHT": "104 TURN RIGHT\a\b",
        "SERVER_PICK_UP": "105 GET MESSAGE\a\b",
        "SERVER_LOGOUT": "106 LOGOUT\a\b",
        "SERVER_OK": "200 OK\a\b",
        "SERVER_LOGIN_FAILED": "300 LOGIN FAILED\a\b",
        "SERVER_SYNTAX_ERROR": "301 SYNTAX ERROR\a\b",
        "SERVER_LOGIC_ERROR": "302 LOGIC ERROR\a\b"
    }
    # Get returns none if the key was not found
    return server_messages.get(msg_name)


def get_client_message(msg_name):
    client_messages = {
        "CLIENT_USERNAME": "%s\a\b",
        "CLIENT_CONFIRMATION": "%s\a\b",
        "CLIENT_OK": "OK <x> <y>\a\b",
        "CLIENT_RECHARGING": "RECHARGING\a\b",
        "CLIENT_FULL_POWER": "FULL POWER\a\b",
        "CLIENT_MESSAGE": "%s\a\b"
    }
    # Get returns none if the key was not found
    return client_messages.get(msg_name)