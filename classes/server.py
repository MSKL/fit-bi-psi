import socket
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
    logged_in = False
    bot_conn = None
    bot_addr = None

    # The bots position
    position = Position()
    orientation = Orientation()

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
        message = self.receive_msg()

        # Calculate the hash
        username_hash = hash_username(message)
        server_hash = add_key(username_hash, self.SERVER_KEY)
        client_hash = add_key(username_hash, self.CLIENT_KEY)

        # Get the binary array
        self.send_msg(server_hash)

        # Receive the client's hash
        message = self.receive_msg()

        # Check the hash
        if message != str(client_hash):
            self.send_msg("SERVER_LOGIN_FAILED")
            self.bot_close()
        else:
            self.logged_in = True
            self.send_msg("SERVER_OK")

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
    def receive_msg(self):
        received = ""
        # Read until a delimiter comes
        while not received.endswith("\a\b"):
            try:
                data = self.bot_conn.recv(1)
                if not data:
                    break
                received += str(data, 'utf-8')
            except self.sock.timeout as err:
                print("Socket timeout %s" % str(err))
                self.bot_close()

        # Strip the ending characters and print the message
        received = end_strip(received)
        color_print("LIGHTMAGENTA", "<= Received: %s" % received)
        return received

    # Close a connection to a bot (if it exists)
    def bot_close(self):
        color_print("RED", "<=> Closing a connection.")
        if (self.bot_conn is None) or (not self.logged_in):
            print("Connection to be closed does not exist")
        self.logged_in = False
        self.bot_conn.close()

    # Do few moves to obtain the position and orientation of the bot
    def bot_find_position_orientation(self):
        last_pos = Position()
        while self.position.is_unknown() or self.orientation.is_unknown():
            self.send_msg("SERVER_MOVE")
            received = self.receive_msg()
            self.position = convert_to_position(received)

            # If the bot moved, calculate the direction
            if not last_pos.is_unknown() and not self.position.is_unknown() and last_pos != self.position:
                delta_x = self.position.x - last_pos.x
                delta_y = self.position.y - last_pos.y

                if delta_x > 0:
                    self.orientation = Facing.RIGHT
                elif delta_x < 0:
                    self.orientation = Facing.LEFT
                elif delta_y > 0:
                    self.orientation = Facing.UP
                elif delta_y < 0:
                    self.orientation = Facing.DOWN
                else:
                    color_print("RED", "Delta Error")

                print("The bot is %s" % str(self.orientation))
                break

            last_pos = self.position

    def bot_pickup(self):
        self.send_msg("SERVER_PICK_UP")
        self.receive_msg()

    def bot_logout(self):
        self.send_msg("SERVER_LOGOUT")
        self.bot_close()


    # Navigate the bot to the target area
    def bot_navigate(self):
        for i in range(0, 20):
            self.bot_forward()
