import math
import json
import wsServer
import config
import random

# This script takes care of the actual game state management

class tankState:
    def __init__(self, x, y, heading):
        self.x = x              # Current x position
        self.y = y              # Current y position
        self.heading = heading  # Current heading in radians from the +x axis

timeSinceLastUpdate = 1 / config.serverSettings.updatesPerSecond
aTank = tankState(25, 25, math.pi / 4)

# Called once every frame by the server
#   elapsedTime:    The time elapsed in seconds since the last frame
def gameLoop(elapsedTime):
    global timeSinceLastUpdate

    # Randomize heading if command received from client
    for clientID in wsServer.clients:
        while len(wsServer.clients[clientID].incoming) != 0:
            if wsServer.clients[clientID].incoming.pop() == "change_heading":
                aTank.heading += random.uniform(math.pi / 4, math.pi)

    # Move the tank the correct distance
    totalDistance = config.tankProps.speed * elapsedTime
    aTank.x += math.cos(aTank.heading) * totalDistance
    aTank.y += math.sin(aTank.heading) * totalDistance

    # Send game state updates to clients
    timeSinceLastUpdate += elapsedTime
    if timeSinceLastUpdate >= 1 / config.serverSettings.updatesPerSecond:
        timeSinceLastUpdate = 0
        wsServer.sendAll(json.dumps(aTank.__dict__, separators=(',', ':')))