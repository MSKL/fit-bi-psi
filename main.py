from classes.server import *


# One thread equals one bot bitch
def thread_func():
    # Setup the server, open a socket
    server = Server("127.0.0.1", 3333)

    # Connect to the client
    server.bot_connect()

    # Obtain the position and orientation
    # server.bot_find_position_orientation()

    # Try to navigate
    # server.bot_navigate()

    server.bot_pickup()

    # Close the connection
    server.bot_command_logout()


if __name__ == "__main__":
    # Simulate only a one thread
    thread_func()
