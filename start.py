"""
Startup script for the pyTanks server

Requirements:
    Python 3.5 or newer
    websockets 7.0 (pip install websockets==7.0)

Usage:
    python start.py

    The pyTanks server uses the settings found in config.py to control how the server works. Those values can be
    changed directly or be overridden by appending one or more of these command line args:
        log=n - Overrides the default logging level. (See the usage section of the readme.)
        ip:port - Overrides the ip and port used to host the server.
"""

import sys

import config

def main():
    """
    Check the environment, apply any command line args to config.py, and start wsServer.py
    """
    # Check Python version
    if sys.version_info[0] < 3 or sys.version_info[1] < 5:
        print("Python 3.5 or newer is required to run the pyTanks server")
        return

    # Check for websockets
    from importlib import util
    if util.find_spec("websockets") is None:
        print("The websockets module is required to run the pyTanks server")
        return

    # Import the code that requires the above things
    from serverLogic.wsServer import runServer

    # Parse and apply the args
    for arg in sys.argv:
        if arg == sys.argv[0] or arg == "":
            continue
        elif arg.startswith("log="):
            try:
                config.server.logLevel = int(arg[-1:])
            except ValueError:
                print("Invalid log level")
                return
        elif arg.startswith("minPlayers="):
            try:
                num = int(arg[-1:])
                if num <= 1:
                    print("minPlayers must be greater than 1")
                    return
                config.server.minPlayers = int(arg[-1:])
            except ValueError:
                print("Invalid min player count")
                return
        elif ":" in arg:
            config.server.ipAndPort = arg
        else:
            print(__doc__[__doc__.index("Usage:"):].strip())
            return

    # Start the server
    runServer()

if __name__ == "__main__":
    main()
