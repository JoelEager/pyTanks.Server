import config

# Handles logging of events
def logPrint(message, minLevel):
    if config.server.logLevel >= minLevel:
        print(message)