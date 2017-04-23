import sys

import config
from gameLogic import gameManager
from serverLogic import wsServer

# Main/startup script of the pyTanks server
#   This script checks any command line args provided, applies them to config.py, and then starts wsServer.py.
#
#   Requirements:
#       Python 3.5 or newer
#       websockets package (pip install websockets)
#
#   (See the below string for usage information.)

usage = """
Usage:
    python start.py

    The pyTanks server uses the settings found in config.py to control how the server works. Those values can be
    changed directly or be overridden by appending one or more of these command line args:
        log=n - Overrides the default logging level. (See the usage section of the readme.)
        ip:port - Overrides the ip and port used to host the server."""

if __name__ == "__main__":
    for arg in sys.argv:
        if arg == sys.argv[0]:
            continue
        elif arg.startswith("log="):
            try:
                config.server.logLevel = int(arg[-1:])
            except ValueError:
                print("Invalid log level")
                print(usage.strip())
                sys.exit()
        elif ":" in arg:
            config.server.ipAndPort = arg
        else:
            print(usage.strip())
            sys.exit()

    wsServer.runServer()