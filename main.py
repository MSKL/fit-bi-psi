from classes.server import *
from classes.exceptions import *
import traceback
import sys
from threading import Thread



def thread_func(sock):
    """One thread equals one bot bitch"""
    while True:
        server = None
        try:
            # Wait for the connection
            sock.listen(0)

            # Accept the incoming connection
            conn, addr = sock.accept()

            # Do come debug printing
            color_print("YELLOW", "Accepted a connection to a socket.")

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
            server.send_msg(MSG.SERVER_SYNTAX_ERROR)
            server.bot_close()
        except LogicErrorException as e:
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
        except:
            print("Unknown exception! Exiting the server.")
            print(traceback.format_exc())
            if server is not None:
                server.bot_close()


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 3333
    thread_count = 4

    if len(sys.argv) == 4:
        host = sys.argv[1]
        port = int(sys.argv[2])
        thread_count = int(sys.argv[3])
    elif len(sys.argv) == 1:
        print("Usage: app.py <host> <port> <# of threads>")
        print("Using the default values of: %s %d %d" % (host, port, thread_count))
    else:
        print("Usage: app.py <host> <port> <# of threads>")
        exit(3)

    color_print("GREEN", "Waiting for connection on %s:%d" % (host, port))
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
    except Exception as inst:
        msg = "Failed to create a socket with the error %s." % inst
        raise Exception(msg)

    for i in range(0, thread_count):
        t = Thread(target=thread_func, args=[sock])
        t.start()
