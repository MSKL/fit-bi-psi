import socket
from server import Server

if __name__ == "__main__":
    server = Server("127.0.0.1", 3333)
    # Connect to the client
    server.bot_connect()

    # Close the connection
    server.bot_close()