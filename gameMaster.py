import math
import json
import wsServer
import config
import random

# Main script of the pyTanks server
#   This script starts wsServer.py with a callback to its gameLoop() function
#   The gameLoop() function is called once a frame so it can maintain the game state

# Placeholder game state data structure
class tankState:
    def __init__(self, x, y, heading):
        self.x = x              # Current x position
        self.y = y              # Current y position
        self.heading = heading  # Current heading in radians from the +x axis

aTank = tankState(25, 25, math.pi / 4)

# Run the logic to maintain the game state and apply commands from player clients
#   (Called once every frame by wsServer.py)
#   elapsedTime:    The time elapsed in seconds since the last frame
def gameLoop(elapsedTime):

    # Randomize heading if command received from client
    for clientID in wsServer.clients:
        while len(wsServer.clients[clientID].incoming) != 0:
            message = wsServer.clients[clientID].incoming.pop()
            if message == "change_heading":
                aTank.heading += random.uniform(math.pi / 4, math.pi)
            else:
                aTank.heading += float(message)

    # Move the tank the correct distance
    totalDistance = config.gameSettings.tankProps.speed * elapsedTime
    aTank.x += math.cos(aTank.heading) * totalDistance
    aTank.y += math.sin(aTank.heading) * totalDistance

# Send game state updates to clients
#   (Called every time an update is due to be sent by wsServer.py)
def updateClients():
    wsServer.sendAll(json.dumps(aTank.__dict__, separators=(',', ':')))

# Start the server with references to the callback functions
wsServer.runServer(gameLoop, updateClients)