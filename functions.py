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