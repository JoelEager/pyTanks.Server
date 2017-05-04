"""
Startup script for the pyTanks server

Requirements:
    Python 3.5 or newer
    websockets 3.3 (pip install websockets==3.3)

Usage:
    python start.py

    The pyTanks server uses the settings found in config.py to control how the server works. Those values can be
    changed directly or be overridden by appending one or more of these command line args:
        log=n - Overrides the default logging level. (See the usage section of the readme.)
        ip:port - Overrides the ip and port used to host the server.
        
    Args can also be placed in the PYTANKS_ARGS environment variable
    (They will be applied before the command line args) 
"""

import sys
import os

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
    args = os.environ.get("PYTANKS_ARGS", "").split(" ") + sys.argv
    for arg in args:
        if arg == sys.argv[0] or arg == "":
            continue
        elif arg.startswith("log="):
            try:
                config.server.logLevel = int(arg[-1:])
            except ValueError:
                print("Invalid log level")
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