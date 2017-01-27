import math
import json
import wsServer
import config

# This script takes care of the actual game state management

class tankState:
    def __init__(self, x, y, heading):
        self.x = x              # Current x position
        self.y = y              # Current y position
        self.heading = heading  # Current heading in radians from the +x axis

timeSinceLastUpdate = 1 / config.serverSettings.updatesPerSecond
aTank = tankState(config.mapSize.x / 2, config.mapSize.y / 2, math.pi / 4)

# Called once every frame by the server
#   elapsedTime:    The time elapsed in seconds since the last frame
def gameLoop(elapsedTime):
    global timeSinceLastUpdate

    # Print the messages received from the clients
    for clientID in wsServer.clients:
        while len(wsServer.clients[clientID].incoming) != 0:
            print(str(clientID) + ": " + wsServer.clients[clientID].incoming.pop())

    # Move the tank the correct distance
    totalDistance = config.tankProps.speed * elapsedTime
    aTank.x += math.cos(aTank.heading) * totalDistance
    aTank.y += math.sin(aTank.heading) * totalDistance

    # Send game state updates to clients
    timeSinceLastUpdate += elapsedTime
    if timeSinceLastUpdate >= 1 / config.serverSettings.updatesPerSecond:
        timeSinceLastUpdate = 0
        wsServer.sendAll(json.dumps(aTank.__dict__, separators=(',', ':')))