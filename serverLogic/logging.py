"""
Handles logging of events
"""

import config

def logPrint(message, minLevel):
    """
    Log a message with the given level
    """
    if config.server.logLevel >= minLevel:
        print(message)