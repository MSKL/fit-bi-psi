import socket
from classes.rotation import *
from classes.position import *
from functions import *
from classes.exceptions import *
import select

class Server:
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
        self.sock = sock
        self.bot_conn = bot_conn
        self.bot_addr = bot_addr

    # Do the login handshake
    def bot_connect(self):
        color_print("RED", '<=> Connected by %s' % str(self.bot_addr))

        # Receive a message
        username = self.receive_msg(MSG.CLIENT_USERNAME)

        # Calculate the hash
        username_hash = hash_username(username)
        server_hash = add_key(username_hash, self.SERVER_KEY)
        client_hash_real = add_key(username_hash, self.CLIENT_KEY)

        # Get the binary array
        self.send_msg(server_hash)

        # Receive the client's hash and strip it for confirmation
        client_confirmation = self.receive_msg(MSG.CLIENT_CONFIRMATION)
        client_confirmation = end_strip(client_confirmation)

        # Check the hash
        if client_confirmation != str(client_hash_real):
            raise LoginFailedException("Hashes do not match. %s != %s." % (str(repr(client_confirmation)), str(repr(client_hash_real))))
        else:
            self.send_msg(MSG.SERVER_OK)

    # Sends message from the server. Accepts either any string, or a server message
    def send_msg(self, msg):
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

    # Receive a message from the bot's connection and strip the ending \a\b
    def receive_msg(self, expected_msg):
        received = ""       # String that is being received
        whole_msg = False   # If ended well == is correctly long

        # Setup timeouts based on the expected message
        if expected_msg == MSG.CLIENT_RECHARGING:
            self.bot_conn.settimeout(5.0)
        else:
            self.bot_conn.settimeout(1.0)

        # Try to read the message and throw an exception on error
        # Read until length exceeded
        while len(received) <= (msg_len(expected_msg)):

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

            if len(received) == msg_len(expected_msg) and received.endswith("\a"):
                raise SyntaxErrorException("Message too long ends with\\a")

            # if received properly,...
            if received.endswith("\a\b"):
                whole_msg = True
                break

            # Invalid messages checking
            if expected_msg == MSG.CLIENT_RECHARGING:
                if not get_client_message(MSG.CLIENT_RECHARGING).startswith(received):
                    raise SyntaxErrorException("CLIENT_RECHARGING syntax error")
            elif expected_msg == MSG.CLIENT_FULL_POWER:
                if not get_client_message(MSG.CLIENT_FULL_POWER).startswith(received):
                    raise SyntaxErrorException("CLIENT_FULL_POWER syntax error")
            elif expected_msg == MSG.CLIENT_OK:
                split = received.strip("\a\b").split(" ")
                if len(split) > 3:
                    raise SyntaxErrorException("CLIENT_OK syntax error: Too many split parts")
                if len(split[0]) > 0 and not "OK".startswith(split[0]):
                    raise SyntaxErrorException("CLIENT_OK syntax error: Problem in the OK")
                try:
                    if len(split) > 1 and split[1] != "":
                        x = int(split[1])
                    if len(split) > 2 and split[2] != "":
                        x = int(split[2])
                except Exception as e:
                    raise SyntaxErrorException("CLIENT_OK syntax error: %s" % str(e))
            elif expected_msg == MSG.CLIENT_CONFIRMATION:
                if not re.match("^[0-9]{1,5}", received):
                    raise SyntaxErrorException("CLIENT_CONFIRMATION")

        # Raise an exception if ended too soon
        if not whole_msg:
            raise SyntaxErrorException("Message too long")

        # Print a debug message
        color_print("LIGHTMAGENTA", "<= Received: %s" % repr(received))
        return extract_message(received, expected_msg)

    # Close a connection to a bot (if it exists)
    def bot_close(self):
        color_print("RED", "<=> Closing a connection.")
        try:
            self.bot_conn.close()
            self.sock.close()
        except:
            print("Tried to close a connection but it threw an error but who cares.")
            exit(13)

    # Logout from the client
    def bot_logout(self):
        self.send_msg(MSG.SERVER_LOGOUT)

    # Try to pickup an object
    def bot_pickup(self):
        self.send_msg(MSG.SERVER_PICK_UP)
        message = self.receive_msg(MSG.CLIENT_MESSAGE)
        if message:
            print("Found the message %s." % message)
        else:
            raise Exception("Message was not found. This should not happen.")

    # Move one tile forward in the direction of current rotation
    def bot_move_forward(self):
        self.send_msg(MSG.SERVER_MOVE)
        self.position = self.receive_msg(MSG.CLIENT_OK)

    # Rotate right and set the proper state
    def bot_rotate(self):
        self.send_msg(MSG.SERVER_TURN_RIGHT)
        self.position = self.receive_msg(MSG.CLIENT_OK)

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

    # Do few moves to obtain the position and orientation of the bot
    def bot_find_position_orientation(self):
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

                print("The bot is %s" % str(self.rotation))
                break

            last_pos = self.position

    # Go to the position first on x, then on y axis
    def bot_go_to_position(self, new_x, new_y):
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

    def bot_go_to_target_square(self):
        target_y = clamp(self.position.y, -2, 2)
        target_x = clamp(self.position.x, -2, 2)
        self.bot_go_to_position(target_x, target_y)
