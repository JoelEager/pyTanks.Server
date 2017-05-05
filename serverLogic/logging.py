"""
Handles logging of events and provides utilities for generating log messages
"""

import math

import config

def logPrint(message, minLevel):
    """
    Log a message with the given level
    """
    if config.server.logLevel >= minLevel:
        print(message)

def round(num, precision):
    """
    :return: num rounded to the given number of digits after the decimal
    """
    return math.ceil(num * (10 ** precision)) / (10 ** precision)