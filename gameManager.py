import math
import wsServer
import config

# This script takes care of the actual game state management

class tankState:
    def __init__(self, x, y, heading):
        self.x = x              # Current x position
        self.y = y              # Current y position
        self.heading = heading  # Current heading in radians from the +x axis

timeSinceLastUpdate = 0
aTank = tankState(config.mapSize.x / 2, config.mapSize.y / 2, math.pi / 4)

# Called once every frame by the server
#   elapsedTime:    The time elapsed in seconds since the last frame
def gameLoop(elapsedTime):
    global timeSinceLastUpdate

    # Print the messages received from the clients
    for clientID in wsServer.clients:
        while len(wsServer.clients[clientID].incoming) != 0:
            print(str(clientID) + ": " + wsServer.clients[clientID].incoming.pop())

    # Send an update to the clients every 5 seconds
    timeDelta = datetime.datetime.now() - lastLogTime
    timeDelta = timeDelta.seconds + (timeDelta.microseconds / 1000000)
    if timeDelta >= 5:
        message = "Number of clients: " + str(len(wsServer.clients))
        lastLogTime = datetime.datetime.now()
        wsServer.sendAll(message)