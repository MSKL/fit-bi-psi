from classes.server import *


# One thread equals one bot bitch
def thread_func():
    server = None

    try:
        # Setup the server, open a socket
        server = Server("127.0.0.1", 3333)

        # Connect to the client
        server.bot_connect()

        # Obtain the position and orientation
        server.bot_find_position_orientation()

        # Go to the origin
        server.bot_search_target_space()

        # Close the connection
        server.bot_logout()
    except (Exception) as e:
        print("Caught exception %s. Exiting the server" % str(e))
        server.bot_close()
    except server.sock.timeout:
        print("Caught timeout excetion. Exiting the server")
        server.bot_close()


if __name__ == "__main__":
    # Simulate only a one thread
    thread_func()
