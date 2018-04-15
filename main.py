import socket
from server import Server

# Server
def threadfunc():
    # Setup the server, open a socket
    server = Server("127.0.0.1", 3333)

    # Connect to the client
    server.bot_connect()

    # Try to navigate
    server.bot_navigate()

    # Close the connection
    server.bot_close()

if __name__ == "__main__":
    # Simulate only a one thread
    threadfunc()
