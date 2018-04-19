from classes.server import *
from classes.exceptions import *
import traceback


def wait_for_connection(host, port):
    """Waits for connection and returns socket, connection and address"""
    color_print("GREEN", "Waiting for connection on %s:%d" % (host, port))
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
    except Exception as inst:
        msg = "Failed to create or connect a socket with the error %s." % inst
        raise Exception(msg)

    # Wait for the connection
    sock.listen(0)

    # Accept the incoming connection
    (bot_conn, bot_addr) = sock.accept()
    return sock, bot_conn, bot_addr


def thread_func():
    """One thread equals one bot bitch"""
    server = None

    try:
        sock, conn, addr = wait_for_connection("127.0.0.1", 3333)

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
        print(traceback.format_exc())
        server.send_msg(MSG.SERVER_SYNTAX_ERROR)
        server.bot_close()
    except LogicErrorException as e:
        # TODO not implemented yet
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
