from classes.server import *
from classes.exceptions import *
import traceback


# One thread equals one bot bitch
def thread_func():
    server = None

    try:
        sock, conn, addr = wait_for_connection("127.0.0.1", 3333)

        # Initialise the server with given parameters
        server = Server(sock, conn, addr)

        # Connect to the client
        server.bot_connect()

        # Obtain the position and orientation
        server.bot_find_position_orientation()

        # Go to the origin
        server.bot_go_to_target_square()

        # Pickup the message
        server.bot_pickup()

        # Close the connection
        server.bot_logout()

        # Close the socket
        server.bot_close()

    except LoginFailedException as e:
        print("Exiting on the LoginFailedException %s." % str(e))
        server.send_msg(MSG.SERVER_LOGIN_FAILED)
        server.bot_close()
    except SyntaxErrorException as e:
        print("Exiting on the SyntaxErrorException %s." % str(e))
        server.send_msg(MSG.SERVER_SYNTAX_ERROR)
        server.bot_close()
    except LogicErrorException as e:
        # TODO not implemented yet
        print("Exiting on the LogicErrorException %s." % str(e))
        server.send_msg(MSG.SERVER_LOGIC_ERROR)
        server.bot_close()
    except TimeoutErrorException as e:
        print(traceback.format_exc())
        print("Exiting on the TimeoutErrorException %s." % str(e))
        server.bot_close()
    except Exception as e:
        print("Caught exception %s. Exiting the server." % str(e))
        print(traceback.format_exc())
        if server is not None:
            server.bot_close()
        return False
    except:
        print("Unknown exception! Exiting the server.")
        print(traceback.format_exc())
        if server is not None:
            server.bot_close()
        return False

    return True


if __name__ == "__main__":
    # Simulate only a one thread
    while thread_func():
        pass
