import re
from enum import Enum
import socket
import traceback
import sys
from threading import Thread

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



def thread_func(sock):
    """Thread function runs in a thread"""
    while True:
        server = None
        try:
            # Wait for the connection
            sock.listen(0)

            # Accept the incoming connection
            conn, addr = sock.accept()

            # Do come debug printing
            color_print("YELLOW", "Accepted a connection to a socket.")

            # Initialise the server with given parameters
            server = Server(sock, conn, addr)

            # Connect to the client
            server.bot_connect()

            # Obtain the position and orientation
            server.bot_find_position_orientation()

            # Navigate to the origin and search the space
            server.bot_do_search()

            # Send the logout command
            server.bot_logout()

            # Close the socket
            server.bot_close()

        # Expected Exceptions
        except LoginFailedException as e:
            print("Exiting on the LoginFailedException %s." % str(e))
            server.send_msg(MSG.SERVER_LOGIN_FAILED)
            server.bot_close()
        except SyntaxErrorException as e:
            print("Exiting on the SyntaxErrorException %s." % str(e))
            server.send_msg(MSG.SERVER_SYNTAX_ERROR)
            server.bot_close()
        except LogicErrorException as e:
            print("Exiting on the LogicErrorException %s." % str(e))
            server.send_msg(MSG.SERVER_LOGIC_ERROR)
            server.bot_close()
        except TimeoutErrorException as e:
            print("Exiting on the TimeoutErrorException %s." % str(e))
            server.bot_close()

        # Unexpected exceptions
        except Exception as e:
            print("Caught exception %s. Exiting the server." % str(e))
            print(traceback.format_exc())
            if server is not None:
                server.bot_close()
        except:
            print("Unknown exception! Exiting the server.")
            print(traceback.format_exc())
            if server is not None:
                server.bot_close()


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 3333
    thread_count = 4

    if len(sys.argv) == 4:
        host = sys.argv[1]
        port = int(sys.argv[2])
        thread_count = int(sys.argv[3])
    elif len(sys.argv) == 1:
        print("Usage: app.py <host> <port> <# of threads>")
        print("Using the default values of: %s %d %d" % (host, port, thread_count))
    else:
        print("Usage: app.py <host> <port> <# of threads>")
        exit(3)

    color_print("GREEN", "Waiting for connection on %s:%d" % (host, port))
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
    except Exception as inst:
        msg = "Failed to create a socket with the error %s." % inst
        raise Exception(msg)

    for i in range(0, thread_count):
        t = Thread(target=thread_func, args=[sock])
        t.start()
class LoginFailedException(Exception):
    pass


class SyntaxErrorException(Exception):
    pass


class LogicErrorException(Exception):
    pass


class TimeoutErrorException(Exception):
    pass
class Position:
    """Stores the position"""
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


class Server:
    """Implements the handling of the TCP server"""
    # Constants
    SERVER_KEY = 54621
    CLIENT_KEY = 45328

    # Set when initializing
    port = None
    host = None

    # The server's socket
    sock = None

    # Connection to the client
    bot_conn = None
    bot_addr = None

    # The bots position
    position = Position()
    rotation = Rotation()

    def __init__(self, sock, bot_conn, bot_addr):
        """
        Initialise the server class.
        :param sock: socket
        :param bot_conn: connection
        :param bot_addr: address
        """
        self.sock = sock
        self.bot_conn = bot_conn
        self.bot_addr = bot_addr

    def bot_connect(self):
        """Do the login handshake"""
        color_print("RED", '<=> Connected by %s' % str(self.bot_addr))

        # Receive a message
        username = self.receive_handler(MSG.CLIENT_USERNAME)

        # Calculate the hash
        username_hash = hash_username(username)
        server_hash = add_key(username_hash, self.SERVER_KEY)
        client_hash_real = add_key(username_hash, self.CLIENT_KEY)

        # Get the binary array
        self.send_msg(server_hash)

        # Receive the client's hash and strip it for confirmation
        client_confirmation = self.receive_handler(MSG.CLIENT_CONFIRMATION)
        client_confirmation = end_strip(client_confirmation)

        # Check the hash
        if client_confirmation != str(client_hash_real):
            raise LoginFailedException(
                "Hashes do not match. %s != %s." % (str(repr(client_confirmation)), str(repr(client_hash_real))))
        else:
            self.send_msg(MSG.SERVER_OK)

    def send_msg(self, msg):
        """Sends message from the server. Accepts either any string, or a server message"""
        # Try to get the message from the known ones
        known = get_server_message(msg)
        if known is not None:
            msg = known

        # Convert to string to make sure
        msg = str(msg)

        # Check if the message ends with delimiters, if not add them
        if not msg.endswith("\a\b"):
            msg = end_add(msg)

        # Convert the message to bytes and send it
        color_print("DARKCYAN", "=> Sent: %s" % str(repr(msg)))
        self.bot_conn.sendall(to_bytes(msg))

    def receive_handler(self, expected_msg):
        """Wraps the receive msg and handles the recharging."""
        received = self.receive_msg(expected_msg)

        # If not RECHARGING message, return it
        if str(received) != get_client_message(MSG.CLIENT_RECHARGING):
            return received

        # Receive the confirmation. It is checked in extract.
        self.receive_msg(MSG.CLIENT_FULL_POWER)

        # Get the real message that was originally expected
        return self.receive_msg(expected_msg)

    def receive_msg(self, expected_msg):
        """Receive a message from the bot's connection and strip the ending \a\b"""
        received = ""  # String that is being received

        # Setup timeouts based on the expected message
        if expected_msg == MSG.CLIENT_FULL_POWER:
            self.bot_conn.settimeout(5.0)
        else:
            self.bot_conn.settimeout(1.0)

        # Try to read the message and throw an exception on error
        # Read until length exceeded
        # len(received) <= (msg_len(expected_msg))
        while True:
            # Read from socket
            try:
                data = self.bot_conn.recv(1)
            except:
                raise TimeoutErrorException("Connection timed out.") from None

            # If none end
            if not data:
                raise Exception("Nothing came.")

            # Convert to ASCII and add to the string
            received += str(data, 'utf-8')

            # Checking if ended properly
            if received.endswith("\a\b"):
                break

            # Handle the fucking recharging:
            if get_client_message(MSG.CLIENT_RECHARGING).startswith(received):
                # Length checking if recharging
                if len(received) == (msg_len(MSG.CLIENT_RECHARGING) - 1):
                    if not received.endswith("\a"):
                        raise SyntaxErrorException("CLIENT_RECHARGING too long not ending with \\a")
                elif len(received) == (msg_len(MSG.CLIENT_RECHARGING) - 0):
                    if not received.endswith("\a\b"):
                        raise SyntaxErrorException("CLIENT_RECHARGING too long not ending with \\a\\b.")
            elif not get_client_message(MSG.CLIENT_RECHARGING).startswith(received):
                # Length checking if not recharging
                if len(received) == (msg_len(expected_msg) - 1):
                    if not received.endswith("\a"):
                        raise SyntaxErrorException("Message too long not ending with \\a")
                elif len(received) == (msg_len(expected_msg) - 0):
                    if not received.endswith("\a\b"):
                        raise SyntaxErrorException("Message too long not ending with \\a\\b.")

                # Invalid messages checking
                if expected_msg == MSG.CLIENT_RECHARGING:
                    if not get_client_message(MSG.CLIENT_RECHARGING).startswith(received):
                        raise SyntaxErrorException("CLIENT_RECHARGING syntax error")
                elif expected_msg == MSG.CLIENT_CONFIRMATION:
                    if not re.match("^[0-9]{1,5}", received):
                        raise SyntaxErrorException("CLIENT_CONFIRMATION")
                elif expected_msg == MSG.CLIENT_OK:
                    split = received.strip("\a\b").split(" ")

                    if len(split) > 3:
                        raise SyntaxErrorException("CLIENT_OK syntax error: Too many split parts")
                    if len(split[0]) > 0:
                        if not "OK".startswith(split[0]):
                            raise SyntaxErrorException("CLIENT_OK syntax error: Problem in the OK")

                    # Try to convert the integral party to the integer. If failed it will raise an exception.
                    try:
                        if len(split) > 1 and split[1] != "" and split[1] != "-":
                            int(split[1])
                        if len(split) > 2 and split[2] != "" and split[2] != "-":
                            int(split[2])
                    except Exception as e:
                        raise SyntaxErrorException("CLIENT_OK syntax error: %s" % str(e)) from None

        # Print a debug message
        color_print("LIGHTMAGENTA", "<= Received: %s" % repr(received))

        # Return the extracted message
        return extract_message(received, expected_msg)

    def bot_close(self):
        """Close a connection to a bot (if it exists) """
        color_print("RED", "<=> Closing a connection.")
        try:
            self.bot_conn.close()
        except:
            print("Tried to close a connection but it threw an error but who cares.")
            exit(13)

    def bot_logout(self):
        """Logout from the client"""
        self.send_msg(MSG.SERVER_LOGOUT)

    def bot_pickup(self):
        """Try to pickup an object"""
        self.send_msg(MSG.SERVER_PICK_UP)
        return self.receive_handler(MSG.CLIENT_MESSAGE)

    def bot_move_forward(self):
        """Move one tile forward in the direction of current rotation"""
        self.send_msg(MSG.SERVER_MOVE)
        self.position = self.receive_handler(MSG.CLIENT_OK)

    def bot_rotate(self):
        """Rotate right and set the proper state"""
        self.send_msg(MSG.SERVER_TURN_RIGHT)
        self.position = self.receive_handler(MSG.CLIENT_OK)

        # Set the proper next rotation
        if self.rotation == Facing.UP:
            self.rotation = Facing.RIGHT
        elif self.rotation == Facing.RIGHT:
            self.rotation = Facing.DOWN
        elif self.rotation == Facing.DOWN:
            self.rotation = Facing.LEFT
        elif self.rotation == Facing.LEFT:
            self.rotation = Facing.UP
        else:
            raise Exception("Can't rotate from unknown rotation. This should not happen.")

    def bot_find_position_orientation(self):
        """Do few moves to obtain the position and orientation of the bot"""
        last_pos = Position()
        while self.position.is_unknown() or self.rotation.is_unknown():
            self.bot_move_forward()

            # If the bot moved, calculate the direction
            if not last_pos.is_unknown() and not self.position.is_unknown() and last_pos != self.position:
                delta_x = self.position.x - last_pos.x
                delta_y = self.position.y - last_pos.y

                if delta_x > 0:
                    self.rotation = Facing.RIGHT
                elif delta_x < 0:
                    self.rotation = Facing.LEFT
                elif delta_y > 0:
                    self.rotation = Facing.UP
                elif delta_y < 0:
                    self.rotation = Facing.DOWN
                else:
                    raise Exception("Problem in the orientation. This should not happen.")

                print("The bot is %s in the beginning." % str(self.rotation))
                break

            last_pos = self.position

    def bot_go_to_position(self, new_x, new_y):
        """Go to the position first on x, then on y axis"""
        np = Position(new_x, new_y)
        while self.position != np:
            # Move towards the target first on X and then on Y
            if np.x != self.position.x:
                delta_x = np.x - self.position.x
                if (delta_x > 0 and self.rotation != Facing.RIGHT) or (delta_x < 0 and self.rotation != Facing.LEFT):
                    self.bot_rotate()
                else:
                    self.bot_move_forward()
            else:
                delta_y = np.y - self.position.y
                if (delta_y > 0 and self.rotation != Facing.UP) or (delta_y < 0 and self.rotation != Facing.DOWN):
                    self.bot_rotate()
                else:
                    self.bot_move_forward()

    def bot_do_search(self):
        """First navigate to (-2, -2) and then do simple search"""
        self.bot_go_to_position(-2, -2)

        # Search the space
        for y in range(-2, 3):
            if y % 2 == 0:
                for x in range(-2, 3):
                    self.bot_go_to_position(x, y)
                    if self.bot_pickup() != "\a\b":
                        return
            else:
                for x in range(2, -3, -1):
                    self.bot_go_to_position(x, y)
                    if self.bot_pickup() != "\a\b":
                        return

        raise Exception("Bot did not found a message in all tiles. This should not happen.")
