import socket

import sys

from classes.position_orientation import *
from functions import *


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

    # Set the port and host in init and create a socket
    def __init__(self, host, port):
        self.port = port
        self.host = host
        color_print("GREEN", "Starting a server on %s:%d" % (host, port))
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((host, port))
        except Exception as inst:
            print("Failed to create or connect a socket with the error %s." % inst)

    # Connect to a bot. The connection was created when initialising
    def bot_connect(self):
        # Wait for the connection
        self.sock.listen(0)
        self.sock.settimeout(1000)

        # Accept the incoming connection
        (self.bot_conn, self.bot_addr) = self.sock.accept()
        color_print("RED", '<=> Connected by %s' % str(self.bot_addr))

        # Receive a message
        username = self.receive_msg(MSG.CLIENT_USERNAME)

        # Calculate the hash
        username_hash = hash_username(username)
        server_hash = add_key(username_hash, self.SERVER_KEY)
        client_hash_real = add_key(username_hash, self.CLIENT_KEY)

        # Get the binary array
        self.send_msg(server_hash)

        # Receive the client's hash
        client_confirmation = self.receive_msg(MSG.CLIENT_CONFIRMATION)

        # Check the hash
        if client_confirmation != str(client_hash_real):
            self.send_msg(MSG.SERVER_LOGIN_FAILED)
            self.bot_close()
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
        color_print("DARKCYAN", "=> Sent: %s" % msg)
        self.bot_conn.sendall(to_bytes(msg))

    # Receive a message from the bot's connection and strip the ending \a\b
    def receive_msg(self, expected_msg):
        received_raw = ""       # String that is being received
        a_came = False          # \a character came
        read_whole_msg = False  # If ended well == is correctly long

        # Setup timeouts based on the expected message
        if expected_msg == MSG.CLIENT_RECHARGING:
            self.sock.settimeout(5000)
        else:
            self.sock.settimeout(1000)

        debug_raw = ""

        # Try to read the message and throw an exception on error
        # Read until length exceeded
        while len(received_raw) <= (msg_len(expected_msg) - 2):
            # Read from socket
            data = self.bot_conn.recv(1)

            # If none end
            if not data:
                print("Data is none")
                break

            # Convert to ascii
            s = str(data, 'utf-8')
            debug_raw += s

            # Do checks for end
            if (s == "\a") and (not a_came):
                a_came = True
                continue
            elif (s == "\b") and a_came:
                read_whole_msg = True
                break
            elif (s != "\b") and a_came:
                raise Exception("Wrong input")

            # Add to the string
            received_raw += s

        # Raise an exception if ended too soon
        if not read_whole_msg:
            print("Raw debug: \"%s\"" % debug_raw)
            raise Exception("Message too long")

        # Print a debug message
        color_print("LIGHTMAGENTA", "<= Received: %s" % received_raw)
        return extract_message(received_raw, expected_msg)

    # Close a connection to a bot (if it exists)
    def bot_close(self):
        color_print("RED", "<=> Closing a connection.")
        try:
            self.bot_conn.close()
        except:
            print("Tried to close a connection but it threw an error but who cares.")

    # Logout from the client
    def bot_logout(self):
        self.send_msg(MSG.SERVER_LOGOUT)

    # Try to pickup an object
    def bot_pickup(self):
        self.send_msg(MSG.SERVER_PICK_UP)
        return self.receive_msg(MSG.CLIENT_MESSAGE)

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
            raise Exception("Can't rotate from unknown rotation.")

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
                    raise Exception("Problem in the orientation.")

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

    def bot_search_target_space(self):
        for y in range(-2, 3):
            for x in range(-2, 3):
                self.bot_go_to_position(x, y)
                message = self.receive_msg(MSG.CLIENT_MESSAGE)
                if message != "":
                    print("Found the message %s." % message)
                    return message
        # If not found raise an exception
        raise Exception("Message was not found")
