import threading
import socket
from functions import *
from messages import *


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

    # Set the port and host in init and create a socket
    def __init__(self, host, port):
        self.port = port
        self.host = host
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((host, port))
        except Exception as inst:
            print("Failed to create or connect a socket with the error %s.", inst)

    def bot_connect(self):
        # Wait for the connection
        self.sock.listen(0)

        # Accept the incoming connection
        (self.bot_conn, self.bot_addr) = self.sock.accept()
        print('Connected by', self.bot_addr)

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
            self.bot_conn.close()
        else:
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
        self.bot_conn.sendall(to_bytes(msg))

    # Receive a message from the bot's connection and strip the ending \a\b
    def receive_msg(self):
        received = ""
        # Read until a delimiter comes
        while not received.endswith("\a\b"):
            data = self.bot_conn.recv(1)
            if not data:
                break
            received += str(data, 'utf-8')

        # Strip the ending characters and print the message
        received = end_strip(received)
        print("Received: %s" % received)
        return received

    def bot_close(self):
        if self.bot_conn is None:
            print("Connection to be closed does not exist")
        self.bot_conn.close()
